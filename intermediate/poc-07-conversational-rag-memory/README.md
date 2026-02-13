# POC 7: Conversational RAG with Memory

A lightweight FastAPI service that combines retrieval-augmented responses with per-session chat memory.

## Features
- Document ingestion endpoint
- Session-aware `/chat/ask` endpoint
- In-memory retrieval with top-k context selection
- In-memory conversation memory per session

## Run
```bash
cd intermediate/poc-07-conversational-rag-memory
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test
```bash
pytest -q
```
