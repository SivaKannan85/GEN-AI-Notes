# POC 7: Conversational RAG with Memory

A production-ready conversational RAG system that combines chat history with document retrieval to provide context-aware, intelligent responses across multiple conversation sessions.

## Features

- **Conversation Sessions**: Create and manage multiple isolated conversation sessions
- **Chat History**: Maintain conversation context across multiple turns
- **Document Retrieval**: Optional RAG capabilities for document-based Q&A
- **Context-Aware Responses**: Responses consider both conversation history and retrieved documents
- **Session Management**: Automatic session timeout and cleanup
- **Flexible Retrieval**: Choose when to use document retrieval vs pure conversation
- **RESTful API**: FastAPI-based endpoints with automatic OpenAPI documentation

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Application                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────────┐                   ┌──────────────────┐
│  Session Manager │                   │  Document Upload │
│  • Create        │                   │  • Load docs     │
│  • Track         │                   │  • Chunk         │
│  • Cleanup       │                   │  • Embed         │
└────────┬─────────┘                   └────────┬─────────┘
         │                                      │
         ▼                                      ▼
┌─────────────────────────────────────────────────────┐
│           Conversational RAG Chain                  │
│  ┌──────────────────┐   ┌──────────────────┐       │
│  │  Chat History    │   │  FAISS Retrieval │       │
│  │  (LangChain      │   │  (Optional)      │       │
│  │   Memory)        │   │                  │       │
│  └────────┬─────────┘   └────────┬─────────┘       │
│           │                      │                  │
│           └──────────┬───────────┘                  │
│                      ▼                              │
│           ┌────────────────────┐                    │
│           │  LLM (GPT-3.5)     │                    │
│           │  • Generate answer │                    │
│           │  • Context-aware   │                    │
│           └────────────────────┘                    │
└─────────────────────────────────────────────────────┘
```

## Tech Stack

- **FastAPI**: Web framework
- **LangChain**: Conversation memory and RAG
- **OpenAI**: LLM (GPT-3.5) and embeddings
- **FAISS**: Vector similarity search
- **Pydantic**: Data validation

## Installation

### Prerequisites

- Python 3.9+
- OpenAI API key
- Virtual environment (recommended)

### Setup

1. **Navigate to the POC directory:**

```bash
cd intermediate/poc-07-conversational-rag-memory
```

2. **Create and activate virtual environment:**

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

Edit `.env` with your configuration:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
SESSION_TIMEOUT_MINUTES=60
MAX_HISTORY_MESSAGES=20
MAX_CONTEXT_MESSAGES=10
```

## Usage

### Starting the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

### API Endpoints

#### 1. Create Session

Create a new conversation session:

```bash
curl -X POST "http://localhost:8000/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "session_name": "Q4 Analysis Discussion",
    "metadata": {"user_id": "user123"}
  }'
```

**Response:**
```json
{
  "session_id": "sess-abc123def456",
  "session_name": "Q4 Analysis Discussion",
  "created_at": "2024-01-15T10:30:00Z",
  "message": "Session 'sess-abc123def456' created successfully"
}
```

#### 2. Chat (Without Retrieval)

Pure conversation without document retrieval:

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess-abc123def456",
    "message": "Hello! I want to discuss Q4 results.",
    "use_retrieval": false
  }'
```

**Response:**
```json
{
  "session_id": "sess-abc123def456",
  "message": "Hello! I'd be happy to discuss Q4 results with you. What specific aspects would you like to explore?",
  "sources": [],
  "conversation_context_used": true,
  "retrieval_used": false,
  "timestamp": "2024-01-15T10:31:00Z"
}
```

#### 3. Upload Document

Upload a document for retrieval:

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@sample_documents/sample_report.txt"
```

**Response:**
```json
{
  "message": "Document 'sample_report.txt' processed successfully",
  "filename": "sample_report.txt",
  "chunks_created": 12
}
```

#### 4. Chat (With Retrieval)

Chat with document retrieval enabled:

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess-abc123def456",
    "message": "What was the total revenue in Q4?",
    "use_retrieval": true,
    "top_k": 4
  }'
```

**Response:**
```json
{
  "session_id": "sess-abc123def456",
  "message": "According to the Q4 2024 report, the total revenue was $12.5 million, representing a 23% increase year-over-year.",
  "sources": [
    {
      "source": "sample_report.txt",
      "content": "Total revenue: $12.5 million...",
      "metadata": {"source": "sample_report.txt"},
      "relevance_score": 0.89
    }
  ],
  "conversation_context_used": true,
  "retrieval_used": true,
  "timestamp": "2024-01-15T10:32:00Z"
}
```

#### 5. Get Session History

Retrieve all messages in a session:

```bash
curl http://localhost:8000/sessions/sess-abc123def456/history
```

**Response:**
```json
{
  "session_id": "sess-abc123def456",
  "messages": [
    {
      "role": "user",
      "content": "Hello! I want to discuss Q4 results.",
      "timestamp": "2024-01-15T10:31:00Z"
    },
    {
      "role": "assistant",
      "content": "Hello! I'd be happy to discuss Q4 results...",
      "timestamp": "2024-01-15T10:31:05Z"
    }
  ],
  "total_messages": 2
}
```

#### 6. List Sessions

List all active sessions:

```bash
curl http://localhost:8000/sessions
```

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "sess-abc123def456",
      "session_name": "Q4 Analysis Discussion",
      "created_at": "2024-01-15T10:30:00Z",
      "last_activity": "2024-01-15T10:32:00Z",
      "message_count": 4,
      "metadata": {"user_id": "user123"}
    }
  ],
  "total_sessions": 1
}
```

#### 7. Delete Session

Delete a conversation session:

```bash
curl -X DELETE "http://localhost:8000/sessions/sess-abc123def456"
```

**Response:**
```json
{
  "message": "Session 'sess-abc123def456' deleted successfully"
}
```

## Example Conversation Flow

Here's a complete example showing the power of conversational memory:

```bash
# 1. Create session
SESSION_ID=$(curl -s -X POST "http://localhost:8000/sessions" \
  -H "Content-Type: application/json" \
  -d '{"session_name": "Business Analysis"}' \
  | jq -r '.session_id')

# 2. Upload document
curl -X POST "http://localhost:8000/upload" \
  -F "file=@sample_documents/sample_report.txt"

# 3. First question with retrieval
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"message\": \"What was the Q4 revenue?\",
    \"use_retrieval\": true
  }"
# Response: "The Q4 revenue was $12.5 million..."

# 4. Follow-up question (no retrieval needed - uses conversation memory)
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"message\": \"How does that compare to Q3?\",
    \"use_retrieval\": true
  }"
# Response: "Q4 revenue of $12.5M represents a 35% increase from Q3..."
# (The assistant remembers we were discussing Q4 revenue)

# 5. Switch topic within same conversation
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"message\": \"What about customer satisfaction?\",
    \"use_retrieval\": true
  }"
# Response: "Customer satisfaction improved significantly in Q4..."

# 6. Reference previous topic
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"message\": \"Is there a correlation between revenue growth and satisfaction?\",
    \"use_retrieval\": false
  }"
# Response: "Yes, there appears to be a correlation. The 23% revenue growth
# we discussed earlier aligns with the improved NPS score of 72..."
```

## Key Concepts

### Conversation Memory

The system maintains conversation history for each session using LangChain's `ConversationBufferMemory`. This allows:

- **Context Continuity**: The assistant remembers previous messages
- **Reference Resolution**: Understanding "it", "that", "the revenue" based on context
- **Topic Tracking**: Following conversation threads across multiple turns

### Hybrid Mode: Memory + Retrieval

The unique feature of this POC is combining:

1. **Conversation History**: What was discussed in this session
2. **Document Retrieval**: Relevant information from uploaded documents

This creates responses that are both:
- **Contextually aware**: Understands the conversation flow
- **Factually grounded**: Based on actual document content

### Session Management

- **Isolation**: Each session maintains separate conversation history
- **Timeout**: Sessions automatically expire after inactivity (default: 60 minutes)
- **Cleanup**: Expired sessions are automatically removed
- **Persistence**: History is maintained in memory (not persisted to disk)

## Configuration

### Environment Variables

| Variable                 | Description                          | Default       |
|-------------------------|--------------------------------------|---------------|
| OPENAI_API_KEY          | OpenAI API key                       | (required)    |
| OPENAI_MODEL            | Model for generation                 | gpt-3.5-turbo |
| OPENAI_TEMPERATURE      | Temperature for responses            | 0.7           |
| SESSION_TIMEOUT_MINUTES | Session timeout in minutes           | 60            |
| MAX_HISTORY_MESSAGES    | Max messages stored per session      | 20            |
| MAX_CONTEXT_MESSAGES    | Max messages sent to LLM             | 10            |
| CHUNK_SIZE              | Document chunk size                  | 1000          |
| CHUNK_OVERLAP           | Overlap between chunks               | 200           |

### Tuning Tips

**For More Conversational Responses:**
- Increase `OPENAI_TEMPERATURE` (0.7-1.0)
- Increase `MAX_CONTEXT_MESSAGES` for more context

**For More Factual Responses:**
- Decrease `OPENAI_TEMPERATURE` (0.0-0.3)
- Always use `use_retrieval: true`

**For Longer Conversations:**
- Increase `MAX_HISTORY_MESSAGES`
- Increase `SESSION_TIMEOUT_MINUTES`

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_main.py -v
```

## Project Structure

```
poc-07-conversational-rag-memory/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── models.py                  # Pydantic models
│   ├── config.py                  # Configuration
│   ├── session_manager.py         # Session management
│   ├── conversational_rag.py      # RAG with conversation context
│   └── document_loader.py         # Document loading
├── tests/
│   ├── __init__.py
│   └── test_main.py               # API tests
├── sample_documents/
│   └── sample_report.txt          # Sample document
├── .env.example                   # Environment template
├── .gitignore
├── requirements.txt
└── README.md
```

## Comparison with POC 6

| Feature                    | POC 6 (Multi-Doc RAG) | POC 7 (Conversational RAG) |
|---------------------------|-----------------------|----------------------------|
| Document upload           | ✅                    | ✅                         |
| Multiple doc formats      | ✅                    | ✅                         |
| Vector search             | ✅                    | ✅                         |
| Metadata filtering        | ✅                    | ✅                         |
| **Conversation memory**   | ❌                    | ✅                         |
| **Session management**    | ❌                    | ✅                         |
| **Context-aware chat**    | ❌                    | ✅                         |
| **Multi-turn dialogue**   | ❌                    | ✅                         |
| Optional retrieval        | ❌                    | ✅                         |

## Use Cases

1. **Customer Support Bot**: Maintain conversation context while retrieving from knowledge base
2. **Research Assistant**: Discuss documents with follow-up questions
3. **Data Analysis**: Explore reports conversationally
4. **Educational Tutor**: Teach concepts with contextual follow-ups
5. **Document Q&A**: Natural dialogue about uploaded documents

## Troubleshooting

### Session Not Found

**Problem:** Getting 404 errors for session operations

**Solutions:**
- Check session hasn't expired (default 60 min timeout)
- Verify session_id is correct
- List active sessions with `GET /sessions`

### Responses Don't Remember Context

**Problem:** Assistant doesn't recall previous messages

**Solutions:**
- Verify using same `session_id` for all messages
- Check `MAX_CONTEXT_MESSAGES` isn't too low
- Ensure session hasn't been deleted

### Poor Quality Answers

**Problem:** Answers aren't relevant or accurate

**Solutions:**
- Upload relevant documents first
- Use `use_retrieval: true` for factual questions
- Increase `top_k` to retrieve more context
- Lower temperature for more focused answers

## Best Practices

1. **Session Naming**: Use descriptive session names for easier tracking
2. **Document Upload**: Upload documents before asking questions about them
3. **Retrieval Control**: Use `use_retrieval: false` for general chat, `true` for factual questions
4. **Session Cleanup**: Delete sessions when done to free resources
5. **Error Handling**: Always check response status codes
6. **Context Management**: Keep conversations focused; create new sessions for new topics

## Next Steps

### Enhancements

- **POC 9**: Add multi-query retrieval strategies
- **POC 13**: Implement LangGraph for complex workflows
- **POC 16**: Add production-ready APM monitoring
- **POC 17**: Implement caching layer

### Production Readiness

- [ ] Add authentication (JWT)
- [ ] Implement rate limiting
- [ ] Persist sessions to database
- [ ] Add WebSocket support for streaming
- [ ] Implement conversation export
- [ ] Add conversation summarization
- [ ] Create user feedback mechanism

## Resources

- [LangChain Conversation Memory](https://python.langchain.com/docs/modules/memory/)
- [FAISS Documentation](https://faiss.ai/)
- [OpenAI Chat API](https://platform.openai.com/docs/guides/chat)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## License

MIT License - See root repository for details

---

**POC 7 Status**: ✅ Complete

**Previous POC**: POC 6 - RAG System with Multiple Document Types
**Next POC**: POC 8 - LangChain Agents with Tools
