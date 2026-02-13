"""Document processing and chunking utilities."""
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.models import DocumentInput


class DocumentProcessor:
    """Split input documents into chunked LangChain Documents."""

    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk_documents(self, inputs: list[DocumentInput]) -> list[Document]:
        chunks: list[Document] = []
        for doc_index, doc in enumerate(inputs):
            split_text = self.splitter.split_text(doc.content)
            for chunk_index, text in enumerate(split_text):
                metadata = {
                    "source": doc.source,
                    "chunk_id": f"doc{doc_index}_chunk{chunk_index}",
                    **doc.metadata,
                }
                chunks.append(Document(page_content=text, metadata=metadata))
        return chunks
