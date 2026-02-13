# POC 6: RAG System with Multiple Document Types

Production-ready RAG API built with FastAPI, LangChain, OpenAI, and FAISS.

## Features

- Multi-document ingestion for **TXT, Markdown, PDF, and DOCX**.
- Flexible payload support (`content` text or `file_base64` bytes).
- Recursive chunking with configurable chunking parameters.
- Metadata normalization (`source`, `document_type`, timestamps, custom metadata).
- Metadata-aware retrieval filters during question answering.
- Persistent FAISS vector store with load/save/clear lifecycle.
- API validation, structured error handling, and unit tests.

## Project Structure

```text
poc-06-rag-multi-document-types/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── document_processor.py
│   ├── vectorstore_manager.py
│   └── qa_chain.py
├── tests/
│   └── test_main.py
├── data/
│   └── sample_notes.md
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

```bash
cd intermediate/poc-06-rag-multi-document-types
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

- `GET /health`
- `POST /documents/upload`
- `POST /ask`
- `GET /vectorstore/info`
- `DELETE /vectorstore/clear`

## Example Upload

```json
{
  "documents": [
    {
      "filename": "engineering_notes.md",
      "document_type": "md",
      "content": "# Notes\nRAG combines retrieval with generation.",
      "metadata": {"team": "platform", "tags": ["rag", "notes"]}
    }
  ]
}
```

## Example Ask

```json
{
  "question": "What does RAG combine?",
  "top_k": 4,
  "filters": {
    "document_type": "md",
    "source": "engineering_notes.md"
  }
}
```
