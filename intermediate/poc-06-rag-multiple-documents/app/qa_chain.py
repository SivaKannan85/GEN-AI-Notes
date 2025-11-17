"""
QA Chain for Multi-Document RAG System

This module implements the question-answering chain with metadata filtering support.
"""

import logging
from typing import Dict, Any, Optional, List
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from app.vectorstore_manager import EnhancedVectorStoreManager
from app.models import QuestionResponse, SourceDocument

logger = logging.getLogger(__name__)


class MultiDocumentQAChain:
    """
    Question-Answering chain for multi-document RAG system with metadata filtering
    """

    def __init__(
        self,
        vectorstore_manager: EnhancedVectorStoreManager,
        openai_api_key: str,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.0,
    ):
        """
        Initialize the QA chain

        Args:
            vectorstore_manager: The vectorstore manager instance
            openai_api_key: OpenAI API key
            model_name: Name of the OpenAI model to use
            temperature: Temperature for response generation
        """
        self.vectorstore_manager = vectorstore_manager
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=openai_api_key,
        )

        # Custom prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful assistant answering questions based on the provided context.

Use the following pieces of context to answer the question at the end.
If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.
Always cite which document the information came from when providing your answer.

Context:
{context}

Question: {question}

Answer: """
        )

        logger.info(f"Initialized MultiDocumentQAChain with model: {model_name}")

    def ask(
        self,
        question: str,
        filter_metadata: Optional[Dict[str, Any]] = None,
        top_k: int = 4,
    ) -> QuestionResponse:
        """
        Ask a question and get an answer with source documents

        Args:
            question: The question to ask
            filter_metadata: Optional metadata filters for document retrieval
            top_k: Number of documents to retrieve

        Returns:
            QuestionResponse with answer and sources
        """
        try:
            logger.info(f"Asking question: {question[:100]}...")
            if filter_metadata:
                logger.info(f"Applying filters: {filter_metadata}")

            # Retrieve relevant documents with filtering
            retrieved_docs = self.vectorstore_manager.similarity_search_with_filter(
                query=question,
                k=top_k,
                filter_metadata=filter_metadata,
            )

            if not retrieved_docs:
                return QuestionResponse(
                    question=question,
                    answer="I couldn't find any relevant documents to answer this question. Please try uploading relevant documents first or adjust your filters.",
                    sources=[],
                    total_sources=0,
                )

            # Extract documents and scores
            docs = [doc for doc, score in retrieved_docs]
            scores = [float(score) for doc, score in retrieved_docs]

            # Build context from retrieved documents
            context_parts = []
            for i, doc in enumerate(docs):
                source_name = doc.metadata.get("source", "Unknown")
                file_type = doc.metadata.get("file_type", "Unknown")
                context_parts.append(
                    f"[Document {i+1} - {source_name} ({file_type})]\n{doc.page_content}\n"
                )

            context = "\n".join(context_parts)

            # Generate answer using LLM
            prompt = self.prompt_template.format(context=context, question=question)
            answer = self.llm.predict(prompt)

            # Build source documents
            source_documents = []
            for i, (doc, score) in enumerate(zip(docs, scores)):
                source_doc = SourceDocument(
                    source=doc.metadata.get("source", "Unknown"),
                    content=doc.page_content[:500],  # Truncate for response
                    metadata=doc.metadata,
                    relevance_score=score,
                )
                source_documents.append(source_doc)

            logger.info(f"Generated answer with {len(source_documents)} sources")

            return QuestionResponse(
                question=question,
                answer=answer,
                sources=source_documents,
                total_sources=len(source_documents),
            )

        except Exception as e:
            logger.error(f"Error in QA chain: {str(e)}")
            raise

    def get_relevant_documents(
        self,
        query: str,
        filter_metadata: Optional[Dict[str, Any]] = None,
        top_k: int = 4,
    ) -> List[SourceDocument]:
        """
        Get relevant documents without generating an answer

        Args:
            query: The search query
            filter_metadata: Optional metadata filters
            top_k: Number of documents to retrieve

        Returns:
            List of SourceDocument objects
        """
        try:
            retrieved_docs = self.vectorstore_manager.similarity_search_with_filter(
                query=query,
                k=top_k,
                filter_metadata=filter_metadata,
            )

            source_documents = []
            for doc, score in retrieved_docs:
                source_doc = SourceDocument(
                    source=doc.metadata.get("source", "Unknown"),
                    content=doc.page_content,
                    metadata=doc.metadata,
                    relevance_score=float(score),
                )
                source_documents.append(source_doc)

            return source_documents

        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise
