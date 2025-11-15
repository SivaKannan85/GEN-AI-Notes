"""
Document processing utilities for chunking and loading documents.
"""
import logging
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from app.config import get_settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles document loading and chunking."""

    def __init__(self):
        """Initialize document processor."""
        self.settings = get_settings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def process_text(self, content: str, metadata: dict = None) -> List[Document]:
        """
        Process text content into chunks.

        Args:
            content: Text content to process
            metadata: Optional metadata to attach to chunks

        Returns:
            List of Document objects with chunks
        """
        logger.info(f"Processing text of length {len(content)}")

        # Create initial document
        doc = Document(
            page_content=content,
            metadata=metadata or {}
        )

        # Split into chunks
        chunks = self.text_splitter.split_documents([doc])

        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks

    def process_documents(self, documents: List[tuple]) -> List[Document]:
        """
        Process multiple documents.

        Args:
            documents: List of (content, metadata) tuples

        Returns:
            List of Document chunks
        """
        all_chunks = []
        for content, metadata in documents:
            chunks = self.process_text(content, metadata)
            all_chunks.extend(chunks)

        logger.info(f"Processed {len(documents)} documents into {len(all_chunks)} chunks")
        return all_chunks


# Global processor instance
_processor: DocumentProcessor = None


def get_document_processor() -> DocumentProcessor:
    """Get the global document processor instance."""
    global _processor
    if _processor is None:
        _processor = DocumentProcessor()
    return _processor
