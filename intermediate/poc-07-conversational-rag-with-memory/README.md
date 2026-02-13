# POC 7: Conversational RAG with Memory

This POC implements a session-aware conversational Retrieval-Augmented Generation (RAG) API using FastAPI, LangChain, and FAISS.

## Features

- Session lifecycle APIs (`create`, `read`, `delete`)
- Per-session in-memory chat history
- FAISS-backed retrieval over indexed document chunks
- Conversational query composition using recent history
- Citation metadata in chat responses
- Prompt-injection-resistant instructions for optional OpenAI generation

## Project Structure

```
poc-07-conversational-rag-with-memory/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── document_processor.py
│   ├── vectorstore_manager.py
│   ├── memory_manager.py
│   └── retrieval_chain.py
├── tests/
│   └── test_main.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

```bash
cd intermediate/poc-07-conversational-rag-with-memory
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

- `GET /health`
- `POST /sessions`
- `GET /sessions/{session_id}`
- `DELETE /sessions/{session_id}`
- `POST /documents/index`
- `POST /chat`

## Notes

- By default, generation uses a local deterministic fallback response to keep the POC runnable without external API credentials.
- To enable OpenAI answer generation, set:
  - `ENABLE_OPENAI_GENERATION=true`
  - `OPENAI_API_KEY=<your-key>`
