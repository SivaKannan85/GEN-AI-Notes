# POC 6: RAG System with Multiple Document Types

A production-ready Retrieval-Augmented Generation (RAG) system that supports multiple document formats (PDF, TXT, DOCX, Markdown) with advanced metadata filtering capabilities.

## Features

- **Multi-Format Support**: Process PDF, TXT, DOCX, and Markdown documents
- **Flexible Chunking**: Multiple chunking strategies (recursive, sentence, character-based)
- **Metadata Filtering**: Filter documents by type, category, tags, or custom metadata
- **Vector Search**: Efficient similarity search using FAISS
- **RESTful API**: FastAPI-based endpoints with automatic OpenAPI documentation
- **Production Ready**: Comprehensive error handling, logging, and testing

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ HTTP
       ▼
┌─────────────────────────────────────────┐
│          FastAPI Application            │
│  ┌───────────────────────────────────┐  │
│  │  Document Upload Endpoint         │  │
│  └────────────┬──────────────────────┘  │
│               │                          │
│               ▼                          │
│  ┌───────────────────────────────────┐  │
│  │  Document Loaders                 │  │
│  │  • PDF (PyPDF2)                   │  │
│  │  • TXT (TextLoader)               │  │
│  │  • DOCX (python-docx)             │  │
│  │  • Markdown (UnstructuredMarkdown)│  │
│  └────────────┬──────────────────────┘  │
│               │                          │
│               ▼                          │
│  ┌───────────────────────────────────┐  │
│  │  Document Chunker                 │  │
│  │  • Recursive splitting            │  │
│  │  • Sentence splitting             │  │
│  │  • Character splitting            │  │
│  └────────────┬──────────────────────┘  │
│               │                          │
│               ▼                          │
│  ┌───────────────────────────────────┐  │
│  │  Embedding (OpenAI)               │  │
│  │  text-embedding-ada-002           │  │
│  └────────────┬──────────────────────┘  │
│               │                          │
│               ▼                          │
│  ┌───────────────────────────────────┐  │
│  │  FAISS Vector Store               │  │
│  │  • Similarity search              │  │
│  │  • Metadata filtering             │  │
│  │  • Persistence                    │  │
│  └────────────┬──────────────────────┘  │
│               │                          │
│               ▼                          │
│  ┌───────────────────────────────────┐  │
│  │  QA Chain (LangChain)             │  │
│  │  • Context building               │  │
│  │  • LLM generation (GPT-3.5)       │  │
│  │  • Source attribution             │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Tech Stack

- **FastAPI**: Web framework for building APIs
- **LangChain**: Framework for LLM applications
- **OpenAI**: Embeddings and language models
- **FAISS**: Vector similarity search
- **Pydantic**: Data validation and settings management
- **PyPDF2**: PDF document processing
- **python-docx**: DOCX document processing
- **unstructured**: Markdown processing

## Installation

### Prerequisites

- Python 3.9 or higher
- OpenAI API key
- Virtual environment (recommended)

### Setup

1. **Clone the repository and navigate to the POC directory:**

```bash
cd intermediate/poc-06-rag-multiple-documents
```

2. **Create and activate a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
OPENAI_TEMPERATURE=0.0

UPLOAD_DIRECTORY=./uploads
VECTORSTORE_PATH=./vectorstore
MAX_FILE_SIZE_MB=10

CHUNK_SIZE=1000
CHUNK_OVERLAP=200

LOG_LEVEL=INFO
```

## Usage

### Starting the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### API Endpoints

#### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "All systems operational"
}
```

#### 2. Upload Document

Upload and process a document:

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@sample_documents/sample_report.txt" \
  -F "chunking_strategy=recursive"
```

**Supported file types:** `.pdf`, `.txt`, `.docx`, `.md`

**Chunking strategies:**
- `recursive` (default): Splits recursively by characters, preserving paragraphs and sentences
- `sentence`: Splits by sentences
- `character`: Splits by character count

**Response:**
```json
{
  "message": "Document 'sample_report.txt' processed successfully",
  "document_metadata": {
    "filename": "sample_report.txt",
    "file_type": "txt",
    "upload_timestamp": "2024-01-15T10:30:00.000Z",
    "file_size_bytes": 2048,
    "page_count": null,
    "category": null,
    "tags": [],
    "custom_metadata": {}
  },
  "chunks_created": 15
}
```

#### 3. Ask Question

Ask a question against uploaded documents:

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What was the total revenue in Q4 2024?",
    "top_k": 4
  }'
```

**With metadata filtering:**

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What was the total revenue in Q4 2024?",
    "top_k": 4,
    "filter_metadata": {
      "file_type": "txt"
    }
  }'
```

**Response:**
```json
{
  "question": "What was the total revenue in Q4 2024?",
  "answer": "According to the Q4 2024 business report, the total revenue was $12.5 million, representing a 23% year-over-year increase.",
  "sources": [
    {
      "source": "sample_report.txt",
      "content": "Total revenue: $12.5 million...",
      "metadata": {
        "source": "sample_report.txt",
        "file_type": "txt"
      },
      "relevance_score": 0.89
    }
  ],
  "total_sources": 4
}
```

#### 4. List Documents

List all uploaded documents:

```bash
curl http://localhost:8000/documents
```

**Response:**
```json
{
  "total_documents": 2,
  "documents": [
    {
      "filename": "sample_report.txt",
      "file_type": "txt",
      "upload_timestamp": "2024-01-15T10:30:00.000Z",
      "file_size_bytes": 2048
    },
    {
      "filename": "technical_guide.md",
      "file_type": "markdown",
      "upload_timestamp": "2024-01-15T11:00:00.000Z",
      "file_size_bytes": 5120
    }
  ],
  "stats": {
    "total_documents": 2,
    "documents_by_type": {
      "txt": 1,
      "markdown": 1
    }
  }
}
```

## Advanced Features

### Metadata Filtering

Filter documents by any metadata field:

```python
{
  "question": "What are the technical requirements?",
  "filter_metadata": {
    "file_type": "markdown",
    "category": "documentation"
  }
}
```

### Custom Chunking Configuration

Adjust chunking parameters in `.env`:

```env
CHUNK_SIZE=1500        # Larger chunks for more context
CHUNK_OVERLAP=300      # More overlap for better continuity
```

### Supported Document Formats

| Format   | Extension | Loader           | Features                |
|----------|-----------|------------------|-------------------------|
| PDF      | `.pdf`    | PyPDF2           | Multi-page support      |
| Text     | `.txt`    | TextLoader       | Encoding detection      |
| DOCX     | `.docx`   | python-docx      | Formatting preserved    |
| Markdown | `.md`     | Unstructured     | Structure preserved     |

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_main.py

# Run with verbose output
pytest -v
```

## Project Structure

```
poc-06-rag-multiple-documents/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application
│   ├── models.py                # Pydantic models
│   ├── config.py                # Configuration management
│   ├── document_loaders.py      # Document loading logic
│   ├── vectorstore_manager.py   # FAISS vectorstore management
│   └── qa_chain.py              # Question-answering chain
├── tests/
│   ├── __init__.py
│   └── test_main.py             # API endpoint tests
├── sample_documents/
│   ├── sample_report.txt        # Sample business report
│   └── technical_guide.md       # Sample technical doc
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Configuration

### Environment Variables

| Variable                 | Description                        | Default                   |
|-------------------------|------------------------------------|---------------------------|
| OPENAI_API_KEY          | OpenAI API key                     | (required)                |
| OPENAI_MODEL            | OpenAI model for generation        | gpt-3.5-turbo             |
| OPENAI_EMBEDDING_MODEL  | OpenAI embedding model             | text-embedding-ada-002    |
| OPENAI_TEMPERATURE      | Temperature for generation         | 0.0                       |
| UPLOAD_DIRECTORY        | Directory for uploaded files       | ./uploads                 |
| VECTORSTORE_PATH        | Directory for FAISS index          | ./vectorstore             |
| MAX_FILE_SIZE_MB        | Maximum file size in MB            | 10                        |
| CHUNK_SIZE              | Chunk size in characters           | 1000                      |
| CHUNK_OVERLAP           | Overlap between chunks             | 200                       |
| LOG_LEVEL               | Logging level                      | INFO                      |

## Performance Considerations

### Chunking Strategy

- **Recursive** (recommended): Balances context preservation and chunk size
- **Sentence**: Best for question-answering tasks
- **Character**: Most predictable, but may break sentences

### Chunk Size

- **Small (500-800)**: Better precision, more API calls
- **Medium (1000-1500)**: Balanced (recommended)
- **Large (2000-3000)**: More context, may include irrelevant info

### Vector Store

- FAISS persists to disk automatically
- Index rebuilds on application restart
- For production, consider using a dedicated vector database (Pinecone, Weaviate)

## Troubleshooting

### Common Issues

#### 1. "Unsupported file type" Error

**Problem:** File extension not recognized

**Solution:** Ensure file has one of these extensions: `.pdf`, `.txt`, `.docx`, `.md`

#### 2. "File size exceeds maximum" Error

**Problem:** File is too large

**Solution:** Increase `MAX_FILE_SIZE_MB` in `.env` or split the document

#### 3. Low Quality Answers

**Problem:** Answers are not relevant or accurate

**Solutions:**
- Increase `CHUNK_SIZE` for more context
- Increase `top_k` in query (retrieve more chunks)
- Improve document quality and formatting
- Use metadata filtering to target specific documents

#### 4. Slow Performance

**Problem:** Queries take too long

**Solutions:**
- Reduce `CHUNK_OVERLAP` to create fewer chunks
- Use smaller documents
- Consider upgrading to GPU-accelerated FAISS (`faiss-gpu`)
- Implement caching for common queries

#### 5. OpenAI API Errors

**Problem:** Rate limits or API errors

**Solutions:**
- Check API key in `.env`
- Verify OpenAI account has credits
- Implement exponential backoff retry logic
- Consider using smaller embedding model

## Cost Estimation

### OpenAI API Costs (as of January 2024)

**Embeddings (text-embedding-ada-002):**
- $0.0001 per 1K tokens
- Average document (2000 words) ≈ 2500 tokens ≈ $0.00025

**Generation (gpt-3.5-turbo):**
- $0.0015 per 1K tokens (input)
- $0.002 per 1K tokens (output)
- Average query with 4 chunks ≈ 3000 input tokens + 500 output tokens ≈ $0.0055

**Example: 100 documents + 1000 queries/month**
- Embedding: 100 docs × $0.00025 = $0.025
- Generation: 1000 queries × $0.0055 = $5.50
- **Total: ~$5.53/month**

## Best Practices

1. **Document Preparation**
   - Clean and format documents before upload
   - Add meaningful metadata (categories, tags)
   - Split very large documents into logical sections

2. **Query Optimization**
   - Use specific questions rather than broad queries
   - Leverage metadata filtering for targeted searches
   - Adjust `top_k` based on query complexity

3. **Production Deployment**
   - Use environment-specific `.env` files
   - Implement authentication and authorization
   - Add rate limiting and request validation
   - Monitor costs and usage with ElasticAPM (see POC 16)
   - Set up backup for vectorstore directory

4. **Security**
   - Never commit `.env` files
   - Validate and sanitize all user inputs
   - Implement file type and size restrictions
   - Scan uploads for malware
   - Use HTTPS in production

## Next Steps

### Enhancements (See Advanced POCs)

- **POC 7**: Add conversational memory for multi-turn Q&A
- **POC 9**: Implement multi-query retrieval strategies
- **POC 14**: Add hybrid search (semantic + keyword)
- **POC 16**: Integrate production-ready APM monitoring
- **POC 17**: Implement semantic caching layer

### Production Readiness

- [ ] Add authentication (JWT, OAuth)
- [ ] Implement rate limiting
- [ ] Add request/response logging
- [ ] Set up monitoring and alerting
- [ ] Create Docker container
- [ ] Write deployment documentation
- [ ] Implement backup strategy
- [ ] Add user feedback mechanism

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [FAISS Documentation](https://faiss.ai/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)

## License

MIT License - See root repository for details

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the test cases for examples
3. Consult the API documentation at `/docs`
4. Refer to related POCs in this repository

---

**POC 6 Status**: ✅ Complete

**Next POC**: POC 7 - Conversational RAG with Memory
