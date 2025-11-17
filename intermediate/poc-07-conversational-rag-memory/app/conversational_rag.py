"""
Conversational RAG Chain - combines chat history with document retrieval.
"""

import logging
from typing import List, Optional, Dict, Any
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.schema import Document

from app.session_manager import Session
from app.models import SourceDocument, MessageRole

logger = logging.getLogger(__name__)


class ConversationalRAGChain:
    """
    Conversational RAG chain that combines chat history with document retrieval.
    """

    def __init__(
        self,
        vectorstore,
        openai_api_key: str,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_context_messages: int = 10,
    ):
        """
        Initialize the conversational RAG chain.

        Args:
            vectorstore: FAISS vectorstore instance
            openai_api_key: OpenAI API key
            model_name: OpenAI model name
            temperature: Temperature for generation
            max_context_messages: Maximum context messages to use
        """
        self.vectorstore = vectorstore
        self.max_context_messages = max_context_messages

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=openai_api_key,
        )

        # Custom prompt template for conversational RAG
        system_template = """You are a helpful AI assistant that answers questions based on provided documents and conversation history.

Use the following context from documents to help answer the question. Also consider the conversation history to provide contextually relevant responses.

If you don't know the answer based on the provided context, just say that you don't know, don't try to make up an answer.
Always cite which documents you're referring to when you use information from them.
Be conversational and remember what was discussed earlier in the conversation.

Context from documents:
{context}

Conversation so far:
{chat_history}"""

        human_template = "{question}"

        # Create the prompt
        messages = [
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template),
        ]
        self.qa_prompt = ChatPromptTemplate.from_messages(messages)

        logger.info(f"Initialized ConversationalRAGChain with model: {model_name}")

    def ask(
        self,
        session: Session,
        question: str,
        use_retrieval: bool = True,
        top_k: int = 4,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, List[SourceDocument], bool]:
        """
        Ask a question with conversation context.

        Args:
            session: Conversation session
            question: User's question
            use_retrieval: Whether to use document retrieval
            top_k: Number of documents to retrieve
            filter_metadata: Optional metadata filters

        Returns:
            Tuple of (answer, source_documents, retrieval_used)
        """
        try:
            logger.info(f"Processing question in session {session.session_id}: {question[:100]}...")

            # Get conversation history
            chat_history = self._format_chat_history(session)

            if use_retrieval and self.vectorstore is not None:
                # Use retrieval with conversation context
                answer, sources = self._ask_with_retrieval(
                    question=question,
                    chat_history=chat_history,
                    top_k=top_k,
                    filter_metadata=filter_metadata,
                )
                retrieval_used = True
            else:
                # Pure conversational response without retrieval
                answer = self._ask_without_retrieval(
                    question=question,
                    chat_history=chat_history,
                )
                sources = []
                retrieval_used = False

            logger.info(f"Generated answer (retrieval: {retrieval_used})")

            return answer, sources, retrieval_used

        except Exception as e:
            logger.error(f"Error in conversational RAG: {str(e)}")
            raise

    def _ask_with_retrieval(
        self,
        question: str,
        chat_history: str,
        top_k: int,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, List[SourceDocument]]:
        """
        Ask with document retrieval.

        Args:
            question: User's question
            chat_history: Formatted chat history
            top_k: Number of documents to retrieve
            filter_metadata: Optional metadata filters

        Returns:
            Tuple of (answer, source_documents)
        """
        # Retrieve relevant documents
        if filter_metadata:
            # Apply metadata filtering
            docs_with_scores = self.vectorstore.similarity_search_with_score(question, k=top_k * 3)
            # Filter by metadata
            filtered_docs = []
            for doc, score in docs_with_scores:
                if self._matches_filter(doc.metadata, filter_metadata):
                    filtered_docs.append((doc, score))
                if len(filtered_docs) >= top_k:
                    break
        else:
            docs_with_scores = self.vectorstore.similarity_search_with_score(question, k=top_k)
            filtered_docs = docs_with_scores

        if not filtered_docs:
            return "I couldn't find any relevant documents to answer your question. Could you try rephrasing or ask something else?", []

        # Extract documents and scores
        docs = [doc for doc, score in filtered_docs]
        scores = [float(score) for doc, score in filtered_docs]

        # Build context from documents
        context = self._build_context(docs)

        # Generate answer using the prompt
        prompt_text = self.qa_prompt.format_messages(
            context=context,
            chat_history=chat_history,
            question=question,
        )

        response = self.llm.invoke(prompt_text)
        answer = response.content

        # Build source documents
        sources = []
        for doc, score in zip(docs, scores):
            source = SourceDocument(
                source=doc.metadata.get("source", "Unknown"),
                content=doc.page_content[:500],  # Truncate for response
                metadata=doc.metadata,
                relevance_score=score,
            )
            sources.append(source)

        return answer, sources

    def _ask_without_retrieval(
        self,
        question: str,
        chat_history: str,
    ) -> str:
        """
        Ask without document retrieval (pure conversation).

        Args:
            question: User's question
            chat_history: Formatted chat history

        Returns:
            Answer string
        """
        prompt = f"""You are a helpful AI assistant. Based on the conversation history below, please respond to the user's latest message.

Conversation history:
{chat_history}

User: {question}

Assistant Response"""

        response = self.llm.invoke(prompt)
        return response.content

    def _format_chat_history(self, session: Session) -> str:
        """
        Format chat history for the prompt.

        Args:
            session: Conversation session

        Returns:
            Formatted chat history string
        """
        if not session.messages:
            return "No previous conversation."

        # Get recent messages (up to max_context_messages)
        recent_messages = session.messages[-self.max_context_messages:]

        history_lines = []
        for msg in recent_messages:
            role_label = "User" if msg.role == MessageRole.USER else "Assistant"
            history_lines.append(f"{role_label}: {msg.content}")

        return "\n".join(history_lines)

    def _build_context(self, docs: List[Document]) -> str:
        """
        Build context from retrieved documents.

        Args:
            docs: List of retrieved documents

        Returns:
            Formatted context string
        """
        context_parts = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "Unknown")
            context_parts.append(f"[Document {i+1} - {source}]\n{doc.page_content}\n")

        return "\n".join(context_parts)

    def _matches_filter(self, metadata: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        """
        Check if metadata matches all filter conditions.

        Args:
            metadata: Document metadata
            filter_dict: Filter conditions

        Returns:
            True if matches, False otherwise
        """
        for key, value in filter_dict.items():
            if key not in metadata:
                return False
            if metadata[key] != value:
                return False
        return True
