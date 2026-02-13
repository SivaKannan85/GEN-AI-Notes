"""FAISS vector store manager with persistence and metadata filtering."""
import logging
import os
import shutil
from typing import Dict, List, Optional

from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from app.config import get_settings

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages FAISS lifecycle and retrieval behavior."""

    def __init__(self):
        self.settings = get_settings()
        self.embeddings = OpenAIEmbeddings(
            model=self.settings.openai_embedding_model,
            openai_api_key=self.settings.openai_api_key,
        )
        self.vectorstore: Optional[FAISS] = None
        self._load_existing_store()

    def _load_existing_store(self) -> None:
        if os.path.exists(self.settings.vector_store_path):
            try:
                self.vectorstore = FAISS.load_local(
                    self.settings.vector_store_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True,
                )
                logger.info("Loaded existing vector store from %s", self.settings.vector_store_path)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Unable to load existing vector store: %s", exc)

    def add_documents(self, documents: List[Document]) -> int:
        if not documents:
            return 0

        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vectorstore.add_documents(documents)

        self.save()
        return len(documents)

    def similarity_search(self, query: str, k: int, metadata_filter: Optional[Dict] = None) -> List[Document]:
        if self.vectorstore is None:
            return []
        search_kwargs = {"k": k}
        if metadata_filter:
            search_kwargs["filter"] = metadata_filter
        return self.vectorstore.similarity_search(query=query, **search_kwargs)

    def get_document_count(self) -> int:
        if self.vectorstore is None:
            return 0
        return int(self.vectorstore.index.ntotal)

    def is_initialized(self) -> bool:
        return self.vectorstore is not None and self.get_document_count() > 0

    def save(self) -> None:
        if self.vectorstore is not None:
            os.makedirs(self.settings.vector_store_path, exist_ok=True)
            self.vectorstore.save_local(self.settings.vector_store_path)

    def clear(self) -> None:
        self.vectorstore = None
        if os.path.exists(self.settings.vector_store_path):
            shutil.rmtree(self.settings.vector_store_path)


_vectorstore_manager: VectorStoreManager | None = None


def get_vectorstore_manager() -> VectorStoreManager:
    """Return singleton vectorstore manager."""
    global _vectorstore_manager
    if _vectorstore_manager is None:
        _vectorstore_manager = VectorStoreManager()
    return _vectorstore_manager
