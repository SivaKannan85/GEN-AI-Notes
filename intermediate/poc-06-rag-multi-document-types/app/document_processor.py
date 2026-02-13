"""Document parsing and chunking for multiple file types."""
import base64
import io
import logging
from datetime import datetime, timezone
from typing import List

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import get_settings
from app.models import UploadDocumentRequest

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Parses input documents and chunks them into LangChain Documents."""

    def __init__(self):
        self.settings = get_settings()
        separators = self.settings.separators.split("|")
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            separators=separators,
        )

    def process_uploads(self, uploads: List[UploadDocumentRequest]) -> List[Document]:
        """Process uploads and return chunked documents."""
        all_chunks: List[Document] = []

        for upload in uploads:
            text = self._extract_text(upload)
            metadata = {
                "source": upload.filename,
                "document_type": upload.document_type.value,
                "ingested_at": datetime.now(timezone.utc).isoformat(),
                **upload.metadata,
            }

            chunks = self.splitter.create_documents([text], [metadata])
            for idx, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = idx
                chunk.metadata["chunk_count"] = len(chunks)
            all_chunks.extend(chunks)

        logger.info("Processed %s documents into %s chunks", len(uploads), len(all_chunks))
        return all_chunks

    def _extract_text(self, upload: UploadDocumentRequest) -> str:
        if upload.content:
            return upload.content.strip()

        payload = self._decode_base64(upload.file_base64 or "")

        if upload.document_type.value in {"txt", "md"}:
            return payload.decode("utf-8").strip()
        if upload.document_type.value == "pdf":
            return self._extract_pdf_text(payload)
        if upload.document_type.value == "docx":
            return self._extract_docx_text(payload)

        raise ValueError(f"Unsupported document type: {upload.document_type}")

    @staticmethod
    def _decode_base64(value: str) -> bytes:
        try:
            return base64.b64decode(value)
        except Exception as exc:  # noqa: BLE001
            raise ValueError("Invalid base64 payload provided") from exc

    @staticmethod
    def _extract_pdf_text(payload: bytes) -> str:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(payload))
        content = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
        if not content:
            raise ValueError("No extractable text found in PDF")
        return content

    @staticmethod
    def _extract_docx_text(payload: bytes) -> str:
        from docx import Document as DocxDocument

        doc = DocxDocument(io.BytesIO(payload))
        content = "\n".join(p.text for p in doc.paragraphs if p.text).strip()
        if not content:
            raise ValueError("No extractable text found in DOCX")
        return content


_document_processor: DocumentProcessor | None = None


def get_document_processor() -> DocumentProcessor:
    """Return singleton document processor instance."""
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor()
    return _document_processor
