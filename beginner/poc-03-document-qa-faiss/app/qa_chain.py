"""
Question-answering chain using LangChain and FAISS.
"""
import logging
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from app.config import get_settings
from app.vectorstore_manager import get_vectorstore_manager

logger = logging.getLogger(__name__)


class QAChain:
    """Question-answering chain with document retrieval."""

    def __init__(self):
        """Initialize QA chain."""
        self.settings = get_settings()
        self.vectorstore_manager = get_vectorstore_manager()

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            temperature=0.0,  # Use 0 for factual QA
            openai_api_key=self.settings.openai_api_key,
            request_timeout=self.settings.openai_timeout
        )

        # Define QA prompt template
        self.prompt_template = """Use the following pieces of context to answer the question at the end.
If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.
Keep the answer concise and relevant.

Context:
{context}

Question: {question}

Answer:"""

        self.prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"]
        )

    def answer_question(self, question: str, top_k: int = 3) -> Dict:
        """
        Answer a question using document retrieval.

        Args:
            question: Question to answer
            top_k: Number of documents to retrieve

        Returns:
            Dictionary containing answer and source documents
        """
        if not self.vectorstore_manager.is_initialized():
            raise ValueError("No documents in vectorstore. Please upload documents first.")

        logger.info(f"Answering question: {question}")

        # Create retriever
        retriever = self.vectorstore_manager.vectorstore.as_retriever(
            search_kwargs={"k": top_k}
        )

        # Create RetrievalQA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",  # Simple stuffing strategy
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt}
        )

        # Get answer
        result = qa_chain.invoke({"query": question})

        # Extract answer and source documents
        answer = result["result"]
        source_docs = result["source_documents"]

        logger.info(f"Generated answer with {len(source_docs)} source documents")

        return {
            "answer": answer,
            "source_documents": source_docs
        }

    def get_relevant_documents(self, question: str, top_k: int = 3) -> List:
        """
        Get relevant documents without generating an answer.

        Args:
            question: Question/query
            top_k: Number of documents to retrieve

        Returns:
            List of relevant documents with scores
        """
        if not self.vectorstore_manager.is_initialized():
            return []

        logger.info(f"Retrieving relevant documents for: {question}")

        results = self.vectorstore_manager.similarity_search(
            query=question,
            k=top_k
        )

        return results


# Global QA chain instance
_qa_chain: QAChain = None


def get_qa_chain() -> QAChain:
    """Get the global QA chain instance."""
    global _qa_chain
    if _qa_chain is None:
        _qa_chain = QAChain()
    return _qa_chain
