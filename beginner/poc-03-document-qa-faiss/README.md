# POC 3: Document QA with FAISS

A production-ready document question-answering system built with FAISS vector database, LangChain, and FastAPI. Demonstrates RAG (Retrieval-Augmented Generation) for answering questions based on uploaded documents.

## Overview

This POC showcases:
- Document upload and chunking with RecursiveCharacterTextSplitter
- FAISS vector database for efficient similarity search
- OpenAI embeddings for document vectorization
- RAG-based question answering with LangChain
- Persistent vector store with save/load capabilities
- FastAPI endpoints for document and QA operations
- Comprehensive error handling and logging
- Unit tests with mocked components

## Tech Stack

- **FastAPI**: Web framework for API endpoints
- **LangChain**: Framework for RAG and QA chains
- **FAISS**: Facebook AI Similarity Search for vector storage
- **OpenAI**: Text embeddings and GPT-3.5-turbo for answers
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server

## Project Structure

```
poc-03-document-qa-faiss/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application and endpoints
│   ├── models.py                # Pydantic models
│   ├── config.py                # Configuration management
│   ├── document_processor.py    # Document chunking and processing
│   ├── vectorstore_manager.py   # FAISS vectorstore management
│   └── qa_chain.py              # LangChain QA chain
├── tests/
│   ├── __init__.py
│   └── test_main.py             # Unit tests
├── data/
│   └── sample_document.txt      # Sample document for testing
├── vector_store/                # FAISS index storage (created at runtime)
├── .env.example                 # Example environment variables
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Features

### 1. Document Processing
- **RecursiveCharacterTextSplitter**: Intelligently splits documents
- **Configurable chunking**: Control chunk size and overlap
- **Metadata preservation**: Attach metadata to document chunks
- **Multiple document support**: Upload and process multiple documents

### 2. Vector Storage (FAISS)
- **Efficient similarity search**: Fast nearest-neighbor search
- **Persistent storage**: Save and load vectorstore from disk
- **In-memory or on-disk**: FAISS-CPU for simplicity
- **Document management**: Add, retrieve, and clear documents

### 3. RAG (Retrieval-Augmented Generation)
- **RetrievalQA chain**: LangChain QA with document retrieval
- **Custom prompts**: Tailored prompts for factual answers
- **Source attribution**: Returns source documents with answers
- **Configurable retrieval**: Adjust number of documents (top_k)

### 4. API Endpoints
- `POST /documents/upload`: Upload and process documents
- `POST /ask`: Ask questions about uploaded documents
- `GET /vectorstore/info`: Get vectorstore statistics
- `DELETE /vectorstore/clear`: Clear all documents
- `GET /health`: Health check with vectorstore status

### 5. Production Features
- Environment-based configuration
- Structured logging
- Comprehensive error handling
- Request/response validation
- Unit tests with mocks
- Automatic API documentation

## Setup

### Prerequisites

- Python 3.9 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Navigate to this POC:**
   ```bash
   cd beginner/poc-03-document-qa-faiss
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

   Example `.env` file:
   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   OPENAI_MODEL=gpt-3.5-turbo
   OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
   CHUNK_SIZE=1000
   CHUNK_OVERLAP=200
   VECTOR_STORE_PATH=./vector_store
   DEFAULT_TOP_K=3
   LOG_LEVEL=INFO
   ```

## Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or simply:
```bash
python -m app.main
```

The API will be available at: `http://localhost:8000`

### API Documentation

FastAPI provides automatic interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Health Check

**GET** `/health`

Check service status and vectorstore state.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "vectorstore_initialized": true
}
```

### 2. Upload Document

**POST** `/documents/upload`

Upload and process a document into the vectorstore.

**Request Body:**
```json
{
  "content": "Python is a high-level programming language...",
  "metadata": {
    "source": "python_docs.txt",
    "category": "programming"
  }
}
```

**Parameters:**
- `content` (required): Document text content
- `metadata` (optional): Custom metadata for the document

**Response:**
```json
{
  "message": "Documents uploaded successfully",
  "document_count": 15,
  "chunks_added": 5
}
```

### 3. Ask Question

**POST** `/ask`

Ask a question about the uploaded documents using RAG.

**Request Body:**
```json
{
  "question": "What is Python?",
  "top_k": 3
}
```

**Parameters:**
- `question` (required): Question to ask (1-500 characters)
- `top_k` (optional): Number of relevant chunks to retrieve (1-10, default: 3)

**Response:**
```json
{
  "question": "What is Python?",
  "answer": "Python is a high-level, interpreted programming language known for its simplicity and readability...",
  "source_documents": [
    {
      "content": "Python is a high-level programming language...",
      "metadata": {"source": "python_docs.txt"},
      "relevance_score": null
    }
  ]
}
```

### 4. Get Vector Store Info

**GET** `/vectorstore/info`

Get information about the vectorstore.

**Response:**
```json
{
  "document_count": 15,
  "is_initialized": true
}
```

### 5. Clear Vector Store

**DELETE** `/vectorstore/clear`

Clear all documents from the vectorstore.

**Response:**
```json
{
  "message": "Vector store cleared successfully"
}
```

## Usage Examples

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Upload a document
curl -X POST http://localhost:8000/documents/upload \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Python is a high-level programming language known for simplicity.",
    "metadata": {"source": "intro.txt"}
  }'

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Python known for?",
    "top_k": 3
  }'

# Get vectorstore info
curl http://localhost:8000/vectorstore/info

# Clear vectorstore
curl -X DELETE http://localhost:8000/vectorstore/clear
```

### Using Python requests

```python
import requests

base_url = "http://localhost:8000"

# Upload a document
with open("data/sample_document.txt", "r") as f:
    content = f.read()

response = requests.post(
    f"{base_url}/documents/upload",
    json={
        "content": content,
        "metadata": {"source": "sample_document.txt"}
    }
)
print(f"Uploaded: {response.json()}")

# Ask a question
response = requests.post(
    f"{base_url}/ask",
    json={
        "question": "What are the key features of Python?",
        "top_k": 3
    }
)
result = response.json()
print(f"Question: {result['question']}")
print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['source_documents'])} documents")

# Get vectorstore info
response = requests.get(f"{base_url}/vectorstore/info")
print(f"Vectorstore: {response.json()}")
```

### Complete Workflow Example

```python
import requests

base_url = "http://localhost:8000"

# Step 1: Upload multiple documents
documents = [
    {
        "content": "Python is a high-level programming language...",
        "metadata": {"source": "python_intro.txt", "topic": "basics"}
    },
    {
        "content": "FastAPI is a modern web framework for Python...",
        "metadata": {"source": "fastapi_intro.txt", "topic": "web"}
    }
]

for doc in documents:
    response = requests.post(f"{base_url}/documents/upload", json=doc)
    print(f"Uploaded: {response.json()['chunks_added']} chunks")

# Step 2: Ask questions
questions = [
    "What is Python?",
    "What is FastAPI?",
    "How are Python and FastAPI related?"
]

for question in questions:
    response = requests.post(
        f"{base_url}/ask",
        json={"question": question, "top_k": 2}
    )
    result = response.json()
    print(f"\nQ: {question}")
    print(f"A: {result['answer']}")
    print(f"Sources: {[doc['metadata'].get('source') for doc in result['source_documents']]}")

# Step 3: Check vectorstore stats
response = requests.get(f"{base_url}/vectorstore/info")
info = response.json()
print(f"\nTotal documents in vectorstore: {info['document_count']}")
```

### Using the Sample Document

```bash
# Upload the sample document
curl -X POST http://localhost:8000/documents/upload \
  -H "Content-Type: application/json" \
  -d "{
    \"content\": \"$(cat data/sample_document.txt)\",
    \"metadata\": {\"source\": \"sample_document.txt\"}
  }"

# Ask questions about it
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key features of Python?"
  }'
```

## Running Tests

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=app --cov-report=html
```

## How It Works

### Document Upload Flow

1. **Client sends document** with content and optional metadata
2. **DocumentProcessor** splits content into chunks
   - Uses RecursiveCharacterTextSplitter
   - Configurable chunk size (default: 1000) and overlap (default: 200)
3. **VectorStoreManager** creates embeddings
   - Uses OpenAI text-embedding-ada-002
   - Stores vectors in FAISS index
4. **FAISS index saved** to disk for persistence
5. **Response returned** with chunk count and total documents

### Question Answering Flow (RAG)

1. **Client sends question** with optional top_k parameter
2. **VectorStoreManager** performs similarity search
   - Embeds the question using OpenAI embeddings
   - Searches FAISS index for most similar chunks
   - Returns top_k relevant documents
3. **QAChain** generates answer
   - Combines retrieved chunks as context
   - Creates prompt with context + question
   - Sends to GPT-3.5-turbo for answer generation
4. **Response returned** with answer and source documents

### RAG Architecture

```
User Question
     ↓
 [Embedding]
     ↓
 [FAISS Similarity Search] → Retrieve top_k documents
     ↓
 [Context Assembly]
     ↓
 [Prompt: Context + Question]
     ↓
 [GPT-3.5-turbo]
     ↓
 Generated Answer + Sources
```

## Key Concepts

### 1. Document Chunking

Documents are split into smaller chunks to:
- Fit within embedding model limits
- Improve retrieval precision
- Enable fine-grained relevance matching

```python
# Example chunking configuration
chunk_size = 1000      # Characters per chunk
chunk_overlap = 200    # Overlap between chunks
```

### 2. Vector Embeddings

Text is converted to high-dimensional vectors:
- OpenAI text-embedding-ada-002: 1536 dimensions
- Captures semantic meaning
- Enables similarity search

### 3. FAISS Index

FAISS provides efficient similarity search:
- Fast nearest-neighbor search
- Scalable to millions of vectors
- CPU-based for simplicity (GPU available for large-scale)

### 4. Retrieval-Augmented Generation (RAG)

RAG combines retrieval and generation:
1. Retrieve relevant context from vectorstore
2. Augment prompt with retrieved context
3. Generate answer based on context
4. Reduces hallucinations
5. Provides source attribution

## Configuration

### Chunking Parameters

- `CHUNK_SIZE`: Number of characters per chunk (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- Larger chunks: More context, but less precise retrieval
- Smaller chunks: More precise, but may lose context

### Retrieval Parameters

- `DEFAULT_TOP_K`: Default number of chunks to retrieve (default: 3)
- `SIMILARITY_THRESHOLD`: Minimum similarity score (optional)
- More chunks: More context, but potentially more noise
- Fewer chunks: Faster, but may miss relevant info

### Vector Store

- `VECTOR_STORE_PATH`: Path to save FAISS index (default: `./vector_store`)
- Index is saved automatically after document uploads
- Loaded on application startup if exists

## Differences from Previous POCs

| Feature | POC 1 (Basic FastAPI) | POC 2 (LangChain Chatbot) | POC 3 (Document QA) |
|---------|----------------------|---------------------------|---------------------|
| Framework | Direct OpenAI API | LangChain Conversation | LangChain RAG |
| Memory | None | ConversationBufferMemory | FAISS Vector Store |
| Context | Single message | Multi-turn chat | Document corpus |
| Knowledge | None (only LLM) | Chat history | Uploaded documents |
| Use Case | One-off queries | Conversations | Document Q&A |
| Retrieval | No | No | Yes (similarity search) |

## Limitations

1. **In-Memory Index**: FAISS index loaded fully in memory
2. **CPU-only**: Using faiss-cpu (slower than GPU version)
3. **No Authentication**: Anyone can upload/query documents
4. **Simple Chunking**: Uses character-based splitting only
5. **No Metadata Filtering**: Cannot filter by metadata during retrieval
6. **Single Vectorstore**: All users share same vectorstore

## Next Steps

After completing this POC, consider:
1. Supporting multiple file formats (PDF, DOCX, etc.) - see POC 6
2. Adding metadata filtering during retrieval
3. Implementing multi-query retrieval - see POC 9
4. Adding conversational QA with memory - see POC 7
5. Implementing hybrid search (semantic + keyword) - see POC 14
6. Using GPU-accelerated FAISS for large-scale
7. Adding user authentication and multi-tenancy

## Troubleshooting

### Common Issues

1. **"No documents in vectorstore"**
   - Upload documents first using `/documents/upload`
   - Check vectorstore status with `/vectorstore/info`

2. **"Failed to load vectorstore"**
   - Delete `vector_store/` directory and restart
   - Check file permissions

3. **Poor answer quality**
   - Increase `top_k` to retrieve more context
   - Adjust chunk size/overlap for better granularity
   - Ensure documents contain relevant information

4. **Slow performance**
   - Reduce `top_k` for faster retrieval
   - Consider using faiss-gpu for large datasets
   - Batch document uploads

5. **Module not found errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

## Performance Considerations

- **Embedding Cost**: Each document chunk requires embedding (costs OpenAI tokens)
- **Index Size**: FAISS index grows with document count
- **Query Speed**: FAISS provides fast search, but scales with index size
- **Memory Usage**: Entire index loaded in memory

### Optimization Tips

1. **Chunk Size**: Balance between context and precision
2. **Batch Uploads**: Upload multiple documents together
3. **Index Persistence**: Save/load to avoid re-embedding
4. **top_k Selection**: Use minimum needed for accurate answers

## Security Notes

- Never commit `.env` file with real API keys
- Implement authentication in production
- Sanitize uploaded document content
- Rate limit API requests
- Consider content moderation for user-uploaded docs
- Validate file sizes and types

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [FAISS Documentation](https://faiss.ai/)
- [LangChain RAG](https://python.langchain.com/docs/use_cases/question_answering/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## License

MIT License - See root repository for details.
