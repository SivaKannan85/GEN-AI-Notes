"""FAISS vectorstore manager for RAG retrieval."""
from langchain_community.embeddings import FakeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from app.config import get_settings


class VectorStoreManager:
    """Manage lifecycle and retrieval operations for FAISS index."""

    def __init__(self):
        self.settings = get_settings()
        self.embeddings = self._build_embeddings()
        self._vectorstore: FAISS | None = None

    def _build_embeddings(self):
        if self.settings.openai_api_key:
            return OpenAIEmbeddings(
                api_key=self.settings.openai_api_key,
                model=self.settings.openai_embedding_model,
            )
        return FakeEmbeddings(size=256)

    def add_documents(self, docs: list[Document]) -> int:
        if not docs:
            return 0
        if self._vectorstore is None:
            self._vectorstore = FAISS.from_documents(docs, self.embeddings)
        else:
            self._vectorstore.add_documents(docs)
        return len(docs)

    def similarity_search(self, query: str, k: int) -> list[Document]:
        if self._vectorstore is None:
            return []
        return self._vectorstore.similarity_search(query, k=k)

    def is_initialized(self) -> bool:
        return self._vectorstore is not None

    def total_chunks(self) -> int:
        if self._vectorstore is None:
            return 0
        return self._vectorstore.index.ntotal

    def clear(self) -> None:
        self._vectorstore = None
