"""
Vector store manager with metadata filtering support.
"""
import logging
import os
import json
from typing import List, Optional, Dict, Any, Tuple
from collections import defaultdict

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from app.config import get_settings

logger = logging.getLogger(__name__)


class EnhancedVectorStoreManager:
    """Enhanced vector store manager with metadata tracking."""

    def __init__(self):
        """Initialize vector store manager."""
        self.settings = get_settings()
        self.embeddings = OpenAIEmbeddings(
            model=self.settings.openai_embedding_model,
            openai_api_key=self.settings.openai_api_key
        )
        self.vectorstore: Optional[FAISS] = None
        self.document_registry: Dict[str, Dict[str, Any]] = {}
        self._load_or_create_vectorstore()
        self._load_document_registry()

    def _load_or_create_vectorstore(self):
        """Load existing vectorstore or create new one."""
        vectorstore_path = self.settings.vector_store_path

        if os.path.exists(vectorstore_path):
            try:
                logger.info(f"Loading vectorstore from {vectorstore_path}")
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
            logger.info("No existing vectorstore found")
            self.vectorstore = None

    def _load_document_registry(self):
        """Load document registry from disk."""
        registry_path = os.path.join(self.settings.vector_store_path, "document_registry.json")

        if os.path.exists(registry_path):
            try:
                with open(registry_path, 'r') as f:
                    self.document_registry = json.load(f)
                logger.info(f"Loaded registry with {len(self.document_registry)} documents")
            except Exception as e:
                logger.warning(f"Failed to load document registry: {e}")
                self.document_registry = {}
        else:
            self.document_registry = {}

    def _save_document_registry(self):
        """Save document registry to disk."""
        os.makedirs(self.settings.vector_store_path, exist_ok=True)
        registry_path = os.path.join(self.settings.vector_store_path, "document_registry.json")

        try:
            with open(registry_path, 'w') as f:
                json.dump(self.document_registry, f, indent=2, default=str)
            logger.info("Document registry saved")
        except Exception as e:
            logger.error(f"Failed to save document registry: {e}")

    def add_documents(
        self,
        documents: List[Document],
        document_id: str,
        document_metadata: Dict[str, Any]
    ) -> int:
        """
        Add documents to vectorstore with tracking.

        Args:
            documents: List of document chunks
            document_id: Unique document identifier
            document_metadata: Metadata about the document

        Returns:
            Number of documents added
        """
        if not documents:
            logger.warning("No documents provided to add")
            return 0

        logger.info(f"Adding {len(documents)} chunks for document {document_id}")

        # Add document_id to each chunk's metadata
        for doc in documents:
            doc.metadata["document_id"] = document_id

        # Add to vectorstore
        if self.vectorstore is None:
            logger.info("Creating new vectorstore")
            self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vectorstore.add_documents(documents)

        # Register document
        self.document_registry[document_id] = {
            **document_metadata,
            "chunk_count": len(documents)
        }

        # Save
        self.save()
        self._save_document_registry()

        logger.info(f"Successfully added {len(documents)} chunks")
        return len(documents)

    def similarity_search_with_filter(
        self,
        query: str,
        k: int = 4,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Document, float]]:
        """
        Search with optional metadata filtering.

        Args:
            query: Search query
            k: Number of results
            filter_metadata: Metadata filters to apply

        Returns:
            List of (document, score) tuples
        """
        if self.vectorstore is None:
            logger.warning("Vectorstore not initialized")
            return []

        logger.info(f"Searching for: {query} (top_k={k})")
        if filter_metadata:
            logger.info(f"Applying filters: {filter_metadata}")

        # Perform similarity search with scores
        if filter_metadata:
            # FAISS doesn't support native filtering, so we retrieve more and filter client-side
            results = self.vectorstore.similarity_search_with_score(query, k=k*3)

            # Filter results
            filtered_results = []
            for doc, score in results:
                if self._matches_filter(doc.metadata, filter_metadata):
                    filtered_results.append((doc, score))
                    if len(filtered_results) >= k:
                        break

            results = filtered_results
        else:
            results = self.vectorstore.similarity_search_with_score(query, k=k)

        logger.info(f"Found {len(results)} results")
        return results

    def _matches_filter(self, metadata: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        """
        Check if metadata matches filter criteria.

        Args:
            metadata: Document metadata
            filter_dict: Filter criteria

        Returns:
            True if metadata matches all filters
        """
        for key, value in filter_dict.items():
            if key not in metadata:
                return False

            meta_value = metadata[key]

            # Handle list matching (for tags, etc.)
            if isinstance(value, list):
                if not isinstance(meta_value, list):
                    return False
                # Check if any filter value is in metadata list
                if not any(v in meta_value for v in value):
                    return False
            else:
                # Exact match
                if meta_value != value:
                    return False

        return True

    def get_document_count(self) -> int:
        """Get total number of chunks in vectorstore."""
        if self.vectorstore is None:
            return 0
        return self.vectorstore.index.ntotal

    def get_unique_document_count(self) -> int:
        """Get number of unique documents."""
        return len(self.document_registry)

    def get_documents_by_type(self) -> Dict[str, int]:
        """Get document count by file type."""
        counts = defaultdict(int)
        for doc_info in self.document_registry.values():
            file_type = doc_info.get("file_type", "unknown")
            counts[file_type] += 1
        return dict(counts)

    def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific document."""
        return self.document_registry.get(document_id)

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents with their metadata."""
        return [
            {"document_id": doc_id, **info}
            for doc_id, info in self.document_registry.items()
        ]

    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document (note: FAISS doesn't support deletion easily).
        This only removes from registry.

        Args:
            document_id: Document to delete

        Returns:
            True if document was in registry
        """
        if document_id in self.document_registry:
            del self.document_registry[document_id]
            self._save_document_registry()
            logger.info(f"Removed document {document_id} from registry")
            logger.warning("Note: Chunks remain in FAISS vectorstore (FAISS doesn't support deletion)")
            return True
        return False

    def is_initialized(self) -> bool:
        """Check if vectorstore is initialized."""
        return self.vectorstore is not None and self.get_document_count() > 0

    def save(self):
        """Save vectorstore to disk."""
        if self.vectorstore is not None:
            os.makedirs(self.settings.vector_store_path, exist_ok=True)
            logger.info(f"Saving vectorstore to {self.settings.vector_store_path}")
            self.vectorstore.save_local(self.settings.vector_store_path)

    def clear(self):
        """Clear vectorstore and registry."""
        logger.info("Clearing vectorstore and document registry")
        self.vectorstore = None
        self.document_registry = {}

        # Remove files
        if os.path.exists(self.settings.vector_store_path):
            import shutil
            shutil.rmtree(self.settings.vector_store_path)
            logger.info("Vectorstore files removed")


# Global instance
_vectorstore_manager: Optional[EnhancedVectorStoreManager] = None


def get_vectorstore_manager() -> EnhancedVectorStoreManager:
    """Get global vectorstore manager instance."""
    global _vectorstore_manager
    if _vectorstore_manager is None:
        _vectorstore_manager = EnhancedVectorStoreManager()
    return _vectorstore_manager
