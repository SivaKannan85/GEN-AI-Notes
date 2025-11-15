"""
Vector store management using FAISS.
"""
import logging
import os
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from app.config import get_settings

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages FAISS vector store operations."""

    def __init__(self):
        """Initialize vector store manager."""
        self.settings = get_settings()
        self.embeddings = OpenAIEmbeddings(
            model=self.settings.openai_embedding_model,
            openai_api_key=self.settings.openai_api_key
        )
        self.vectorstore: Optional[FAISS] = None
        self._load_or_create_vectorstore()

    def _load_or_create_vectorstore(self):
        """Load existing vectorstore or create a new one."""
        vectorstore_path = self.settings.vector_store_path

        if os.path.exists(vectorstore_path):
            try:
                logger.info(f"Loading existing vectorstore from {vectorstore_path}")
                self.vectorstore = FAISS.load_local(
                    vectorstore_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("Vectorstore loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load vectorstore: {e}. Creating new one.")
                self.vectorstore = None
        else:
            logger.info("No existing vectorstore found. Will create on first document upload.")
            self.vectorstore = None

    def add_documents(self, documents: List[Document]) -> int:
        """
        Add documents to the vector store.

        Args:
            documents: List of Document objects to add

        Returns:
            Number of documents added
        """
        if not documents:
            logger.warning("No documents provided to add")
            return 0

        logger.info(f"Adding {len(documents)} documents to vectorstore")

        if self.vectorstore is None:
            # Create new vectorstore
            logger.info("Creating new vectorstore")
            self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        else:
            # Add to existing vectorstore
            self.vectorstore.add_documents(documents)

        # Save to disk
        self.save()

        logger.info(f"Successfully added {len(documents)} documents")
        return len(documents)

    def similarity_search(
        self,
        query: str,
        k: int = 3,
        score_threshold: Optional[float] = None
    ) -> List[tuple]:
        """
        Search for similar documents.

        Args:
            query: Search query
            k: Number of results to return
            score_threshold: Minimum similarity score (optional)

        Returns:
            List of (document, score) tuples
        """
        if self.vectorstore is None:
            logger.warning("Vectorstore not initialized. No documents to search.")
            return []

        logger.info(f"Searching for: {query} (top_k={k})")

        # Perform similarity search with scores
        results = self.vectorstore.similarity_search_with_score(query, k=k)

        # Filter by score threshold if provided
        if score_threshold is not None:
            # FAISS returns distance (lower is better), not similarity
            # For L2 distance, we can use a threshold
            results = [(doc, score) for doc, score in results if score <= score_threshold]

        logger.info(f"Found {len(results)} results")
        return results

    def get_document_count(self) -> int:
        """Get the number of documents in the vectorstore."""
        if self.vectorstore is None:
            return 0
        return self.vectorstore.index.ntotal

    def is_initialized(self) -> bool:
        """Check if vectorstore is initialized."""
        return self.vectorstore is not None and self.get_document_count() > 0

    def save(self):
        """Save vectorstore to disk."""
        if self.vectorstore is not None:
            logger.info(f"Saving vectorstore to {self.settings.vector_store_path}")
            self.vectorstore.save_local(self.settings.vector_store_path)

    def clear(self):
        """Clear the vectorstore."""
        logger.info("Clearing vectorstore")
        self.vectorstore = None
        # Remove saved vectorstore files
        if os.path.exists(self.settings.vector_store_path):
            import shutil
            shutil.rmtree(self.settings.vector_store_path)
            logger.info("Vectorstore files removed")


# Global vectorstore manager instance
_vectorstore_manager: Optional[VectorStoreManager] = None


def get_vectorstore_manager() -> VectorStoreManager:
    """Get the global vectorstore manager instance."""
    global _vectorstore_manager
    if _vectorstore_manager is None:
        _vectorstore_manager = VectorStoreManager()
    return _vectorstore_manager
