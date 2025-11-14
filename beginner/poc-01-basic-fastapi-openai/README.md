# POC 1: Basic FastAPI + OpenAI Integration

A production-ready REST API demonstrating FastAPI integration with OpenAI's Chat Completion API, featuring Pydantic validation, comprehensive error handling, and proper logging.

## Overview

This POC showcases:
- FastAPI application structure with proper separation of concerns
- OpenAI Chat Completion API integration
- Pydantic models for request/response validation
- Comprehensive error handling for various failure scenarios
- Production-ready logging and configuration management
- Unit tests with mocked OpenAI responses

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **OpenAI**: GPT-3.5-turbo for chat completions
- **Pydantic**: Data validation and settings management
- **Uvicorn**: Lightning-fast ASGI server

## Project Structure

```
poc-01-basic-fastapi-openai/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application and endpoints
│   ├── models.py            # Pydantic models for validation
│   └── config.py            # Configuration management
├── tests/
│   ├── __init__.py
│   └── test_main.py         # Unit tests
├── .env.example             # Example environment variables
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Features

### 1. Pydantic Models
- **ChatRequest**: Validates user input with constraints
  - Message length validation (1-4000 characters)
  - Temperature range (0.0-2.0)
  - Max tokens constraint (1-4000)
- **ChatResponse**: Structured response with metadata
- **HealthResponse**: Service health status
- **ErrorResponse**: Standardized error format

### 2. Error Handling
- Rate limit errors (HTTP 429)
- API connection errors (HTTP 503)
- OpenAI API errors (HTTP 502)
- General errors (HTTP 500)
- Request validation errors (HTTP 422)

### 3. Configuration Management
- Environment-based configuration using `pydantic-settings`
- Cached settings for performance
- Support for `.env` files

### 4. Logging
- Structured logging with timestamps
- Request/response logging
- Error tracking with stack traces

## Setup

### Prerequisites

- Python 3.9 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository and navigate to this POC:**
   ```bash
   cd beginner/poc-01-basic-fastapi-openai
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

FastAPI provides automatic interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Health Check

**GET** `/health`

Check if the service is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Chat Completion

**POST** `/chat`

Generate a chat completion using OpenAI.

**Request Body:**
```json
{
  "message": "What is FastAPI?",
  "system_prompt": "You are a helpful assistant.",
  "temperature": 0.7,
  "max_tokens": 500
}
```

**Parameters:**
- `message` (required): User message (1-4000 characters)
- `system_prompt` (optional): System prompt to guide AI behavior (default: "You are a helpful assistant.")
- `temperature` (optional): Sampling temperature 0.0-2.0 (default: 0.7)
- `max_tokens` (optional): Maximum tokens to generate 1-4000 (default: 500)

**Response:**
```json
{
  "response": "FastAPI is a modern, fast web framework for building APIs with Python...",
  "model": "gpt-3.5-turbo",
  "tokens_used": 45,
  "finish_reason": "stop"
}
```

## Usage Examples

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Chat completion
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain what FastAPI is in one sentence",
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

### Using Python requests

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Chat completion
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "What is FastAPI?",
        "system_prompt": "You are a helpful programming assistant.",
        "temperature": 0.7,
        "max_tokens": 200
    }
)
print(response.json())
```

### Using httpx (async)

```python
import httpx
import asyncio

async def test_chat():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/chat",
            json={"message": "What is FastAPI?"}
        )
        print(response.json())

asyncio.run(test_chat())
```

## Running Tests

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=app --cov-report=html
```

## Error Handling Examples

### Rate Limit Error
```json
{
  "detail": "OpenAI API rate limit exceeded. Please try again later."
}
```

### Connection Error
```json
{
  "detail": "Unable to connect to OpenAI API. Please try again later."
}
```

### Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

## Key Learnings

### 1. FastAPI Best Practices
- Use lifespan events for startup/shutdown logic
- Separate models, config, and business logic
- Leverage automatic OpenAPI documentation
- Use dependency injection for shared resources

### 2. Pydantic Validation
- Field validators with constraints (min/max length, ranges)
- Default values and optional fields
- Custom validation error messages
- JSON schema examples for documentation

### 3. OpenAI Integration
- Proper error handling for different failure scenarios
- Rate limiting considerations
- Token usage tracking
- Timeout configuration

### 4. Production Readiness
- Structured logging
- Environment-based configuration
- Comprehensive error handling
- Unit testing with mocks

## Next Steps

After completing this POC, consider:
1. Adding authentication (API keys, OAuth)
2. Implementing request rate limiting
3. Adding response caching
4. Implementing conversation history
5. Adding streaming responses (see POC 10)
6. Integrating APM monitoring (see POC 5)

## Troubleshooting

### Common Issues

1. **"OpenAI API key not found"**
   - Ensure `.env` file exists and contains `OPENAI_API_KEY`
   - Check that the API key is valid

2. **"Rate limit exceeded"**
   - Wait a few seconds and retry
   - Consider implementing exponential backoff

3. **"Module not found" errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

## License

MIT License - See root repository for details.
