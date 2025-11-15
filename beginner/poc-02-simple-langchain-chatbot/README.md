# POC 2: Simple LangChain Chatbot

A production-ready conversational AI chatbot built with LangChain, featuring conversation memory, session management, and FastAPI integration.

## Overview

This POC demonstrates:
- LangChain ConversationChain with memory management
- Session-based conversation tracking
- Custom prompt templates for consistent AI behavior
- FastAPI endpoints for chat and session management
- In-memory session storage with automatic cleanup
- Comprehensive error handling and logging
- Unit tests with mocked LangChain components

## Tech Stack

- **FastAPI**: Web framework for API endpoints
- **LangChain**: Framework for LLM application development
- **OpenAI**: GPT-3.5-turbo for chat completions
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server

## Project Structure

```
poc-02-simple-langchain-chatbot/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI application and endpoints
│   ├── models.py             # Pydantic models
│   ├── config.py             # Configuration management
│   ├── chatbot.py            # LangChain chatbot implementation
│   └── session_manager.py    # Session and memory management
├── tests/
│   ├── __init__.py
│   └── test_main.py          # Unit tests
├── .env.example              # Example environment variables
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Features

### 1. Conversation Memory
- **ConversationBufferMemory**: Maintains full conversation history per session
- **Session-based isolation**: Each user has independent conversation context
- **Automatic cleanup**: Old sessions are removed based on timeout

### 2. LangChain Integration
- **ConversationChain**: Manages conversation flow with memory
- **Custom Prompt Templates**: Defines AI assistant behavior
- **MessagesPlaceholder**: Integrates chat history into prompts
- **ChatOpenAI**: OpenAI LLM integration

### 3. Session Management
- **Unique session IDs**: Track conversations per user
- **Session info endpoint**: Query session metadata
- **Clear sessions**: Reset conversation history
- **Configurable timeouts**: Auto-expire inactive sessions
- **Max sessions limit**: Prevent memory overflow

### 4. API Endpoints
- `POST /chat`: Send message and get AI response
- `GET /session/{session_id}`: Get session information
- `POST /session/clear`: Clear a session's history
- `GET /health`: Health check with active session count

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
   cd beginner/poc-02-simple-langchain-chatbot
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
   OPENAI_TIMEOUT=30
   MAX_TOKEN_LIMIT=4000
   MEMORY_KEY=chat_history
   SESSION_TIMEOUT_MINUTES=30
   MAX_SESSIONS=100
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

Check service status and active sessions count.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "active_sessions": 3
}
```

### 2. Chat

**POST** `/chat`

Send a message and receive AI response with conversation history.

**Request Body:**
```json
{
  "session_id": "user-123",
  "message": "What is LangChain?",
  "temperature": 0.7
}
```

**Parameters:**
- `session_id` (required): Unique identifier for the conversation session
- `message` (required): User's message (1-4000 characters)
- `temperature` (optional): Sampling temperature 0.0-2.0 (default: 0.7)

**Response:**
```json
{
  "session_id": "user-123",
  "message": "LangChain is a framework for developing applications powered by language models...",
  "conversation_history": [
    {
      "role": "user",
      "content": "What is LangChain?",
      "timestamp": "2024-01-01T12:00:00"
    },
    {
      "role": "assistant",
      "content": "LangChain is a framework for...",
      "timestamp": "2024-01-01T12:00:01"
    }
  ],
  "tokens_used": 85
}
```

### 3. Get Session Info

**GET** `/session/{session_id}`

Get information about a specific session.

**Response:**
```json
{
  "session_id": "user-123",
  "message_count": 10,
  "created_at": "2024-01-01T12:00:00",
  "last_activity": "2024-01-01T12:30:00"
}
```

### 4. Clear Session

**POST** `/session/clear`

Clear a session's conversation history.

**Request Body:**
```json
{
  "session_id": "user-123"
}
```

**Response:**
```json
{
  "session_id": "user-123",
  "message": "Session cleared successfully"
}
```

## Usage Examples

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Start a conversation
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-alice",
    "message": "Hello! What can you help me with?"
  }'

# Continue the conversation
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-alice",
    "message": "Tell me about Python"
  }'

# Get session info
curl http://localhost:8000/session/user-alice

# Clear session
curl -X POST http://localhost:8000/session/clear \
  -H "Content-Type: application/json" \
  -d '{"session_id": "user-alice"}'
```

### Using Python requests

```python
import requests

base_url = "http://localhost:8000"
session_id = "user-alice"

# Start conversation
response = requests.post(
    f"{base_url}/chat",
    json={
        "session_id": session_id,
        "message": "Hello! Who are you?"
    }
)
print(response.json()["message"])

# Continue conversation (context is maintained)
response = requests.post(
    f"{base_url}/chat",
    json={
        "session_id": session_id,
        "message": "What did I just ask you?"
    }
)
print(response.json()["message"])
# The bot remembers the previous message!

# Get session info
response = requests.get(f"{base_url}/session/{session_id}")
print(f"Messages in session: {response.json()['message_count']}")

# Clear session
response = requests.post(
    f"{base_url}/session/clear",
    json={"session_id": session_id}
)
print(response.json()["message"])
```

### Conversational Example

```python
import requests

def chat(session_id, message):
    """Send a chat message."""
    response = requests.post(
        "http://localhost:8000/chat",
        json={"session_id": session_id, "message": message}
    )
    data = response.json()
    return data["message"]

# Multi-turn conversation
session = "demo-session"

print(chat(session, "Hi! My name is Alice."))
# "Hello Alice! Nice to meet you. How can I help you today?"

print(chat(session, "What's my name?"))
# "Your name is Alice, as you just told me!"

print(chat(session, "I like Python programming."))
# "That's great! Python is a wonderful programming language..."

print(chat(session, "What do I like?"))
# "You mentioned that you like Python programming!"
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

### Conversation Flow

1. **User sends message** with a `session_id`
2. **Session Manager** retrieves or creates memory for that session
3. **LangChain Chatbot** processes the message:
   - Loads conversation history from memory
   - Combines system prompt + history + new message
   - Sends to OpenAI for completion
   - Saves response to memory
4. **Response returned** with full conversation history
5. **Session updated** with new activity timestamp

### Memory Management

- **In-Memory Storage**: Sessions stored in Python dict (fast but non-persistent)
- **Automatic Cleanup**: Old sessions removed when max limit reached
- **Timeout-based**: Sessions inactive for 30 minutes are eligible for cleanup
- **Thread-safe**: Single global session manager instance

### Prompt Template

```python
System: You are a helpful and friendly AI assistant.
Your goal is to provide accurate, helpful, and engaging responses.
Be conversational and maintain context from previous messages.

[Chat History]
Human: Previous message 1
AI: Previous response 1
Human: Previous message 2
AI: Previous response 2

[New Message]
Human: {input}
```

## Key Learnings

### 1. LangChain Concepts
- **ConversationChain**: Simplifies building conversational AI
- **Memory**: Critical for maintaining context across turns
- **Prompt Templates**: Control AI behavior consistently
- **Message Placeholders**: Integrate dynamic content (chat history)

### 2. Session Management
- Sessions must be isolated per user
- Cleanup strategies prevent memory leaks
- Timeout-based expiration for inactive sessions
- Session metadata useful for monitoring

### 3. Conversation Design
- System prompts set AI personality
- Memory allows contextual responses
- Temperature affects response creativity
- Token estimation helps with cost tracking

### 4. Production Considerations
- In-memory storage is fast but non-persistent
- Consider Redis/database for production persistence
- Session limits prevent resource exhaustion
- Logging helps debug conversation issues

## Differences from POC 1

| Feature | POC 1 (Basic FastAPI) | POC 2 (LangChain Chatbot) |
|---------|----------------------|---------------------------|
| Framework | Direct OpenAI API | LangChain |
| Memory | None (stateless) | ConversationBufferMemory |
| Sessions | No session tracking | Full session management |
| Context | Single message | Multi-turn conversations |
| Prompts | Simple system message | Structured prompt templates |
| Use Case | One-off queries | Conversational chat |

## Limitations

1. **In-Memory Storage**: Sessions lost on restart
2. **No Persistence**: Conversations not saved to database
3. **Single Server**: Won't scale across multiple instances
4. **Token Estimation**: Approximate, not exact
5. **No User Auth**: Anyone can access any session

## Next Steps

After completing this POC, consider:
1. Adding persistent storage (Redis, PostgreSQL)
2. Implementing user authentication
3. Adding conversation export functionality
4. Implementing different memory types (Summary, Buffer Window)
5. Adding streaming responses (see POC 10)
6. Integrating with document retrieval (see POC 3, 6, 7)
7. Adding multi-modal support (POC 18)

## Troubleshooting

### Common Issues

1. **"Session not found" after waiting**
   - Sessions expire after 30 minutes of inactivity
   - Create a new session or adjust `SESSION_TIMEOUT_MINUTES`

2. **"Max sessions limit reached"**
   - Too many active sessions
   - Increase `MAX_SESSIONS` or decrease timeout

3. **Conversation doesn't remember context**
   - Verify same `session_id` is used
   - Check session wasn't cleared or expired

4. **"Module not found" errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

## Performance Considerations

- **Memory Usage**: Each session stores full conversation history
- **Token Costs**: Longer conversations = more tokens sent to OpenAI
- **Response Time**: Increases with conversation length
- **Concurrency**: Multiple sessions can be processed in parallel

## Security Notes

- Never commit `.env` file with real API keys
- Implement authentication in production
- Sanitize user inputs (already done via Pydantic)
- Rate limit requests to prevent abuse
- Consider PII in conversation logs

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [LangChain Memory](https://python.langchain.com/docs/modules/memory/)
- [LangChain Chains](https://python.langchain.com/docs/modules/chains/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

## License

MIT License - See root repository for details.