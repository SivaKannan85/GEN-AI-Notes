# POC 5: Basic APM Integration

A production-ready FastAPI application integrated with ElasticAPM for comprehensive application performance monitoring, distributed tracing, and error tracking.

## Overview

This POC demonstrates:
- ElasticAPM integration with FastAPI
- Automatic transaction tracking for all HTTP requests
- Custom spans for detailed performance monitoring
- Error tracking and exception capture
- Custom context and labels for enriched traces
- Performance metrics collection
- Distributed tracing support
- Production-ready monitoring setup

## Tech Stack

- **FastAPI**: Modern web framework
- **ElasticAPM**: Application Performance Monitoring
- **Pydantic**: Data validation and settings
- **Uvicorn**: ASGI server

## Project Structure

```
poc-05-basic-apm-integration/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI app with APM
│   ├── models.py            # Pydantic models
│   ├── config.py            # APM configuration
│   └── apm_utils.py         # APM utility functions
├── tests/
│   ├── __init__.py
│   └── test_main.py         # Unit tests
├── .env.example             # Example environment variables
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Features

### 1. Automatic Transaction Tracking
- **HTTP requests**: Every request automatically creates a transaction
- **Request metadata**: Method, URL, headers, body (configurable)
- **Response tracking**: Status codes, response times
- **Distributed tracing**: Trace ID propagation across services

### 2. Custom Spans
- **Database operations**: Track DB query performance
- **External API calls**: Monitor third-party API latency
- **Business logic**: Measure custom operation performance
- **Batch processing**: Track individual item processing

### 3. Error Tracking
- **Exception capture**: Automatically capture unhandled exceptions
- **Stack traces**: Full stack traces for debugging
- **Error context**: Custom data attached to errors
- **Error correlation**: Link errors to traces via trace ID

### 4. Custom Context & Labels
- **Transaction context**: Add custom data to transactions
- **User context**: Track user information
- **Labels**: Tag transactions for filtering/grouping
- **Custom metrics**: Track business metrics

### 5. Performance Monitoring
- **Response times**: Track request/response latency
- **Throughput**: Monitor requests per second
- **Error rates**: Track error percentages
- **Slow transactions**: Identify performance bottlenecks

## Setup

### Prerequisites

- Python 3.9 or higher
- ElasticAPM Server (or Elastic Cloud)
  - Option 1: Use Elastic Cloud (free tier available)
  - Option 2: Run local APM Server with Docker (instructions below)

### Installation

1. **Navigate to this POC:**
   ```bash
   cd beginner/poc-05-basic-apm-integration
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
   # Edit .env with your APM server details
   ```

   Example `.env` file:
   ```env
   ELASTIC_APM_ENABLED=true
   ELASTIC_APM_SERVICE_NAME=poc-05-apm-demo
   ELASTIC_APM_SERVER_URL=http://localhost:8200
   ELASTIC_APM_ENVIRONMENT=development
   APM_TRANSACTION_SAMPLE_RATE=1.0
   LOG_LEVEL=INFO
   ```

### Running Local APM Server with Docker

If you don't have an APM server:

```bash
# Run Elasticsearch
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0

# Run Kibana
docker run -d \
  --name kibana \
  -p 5601:5601 \
  --link elasticsearch:elasticsearch \
  docker.elastic.co/kibana/kibana:8.11.0

# Run APM Server
docker run -d \
  --name apm-server \
  -p 8200:8200 \
  --link elasticsearch:elasticsearch \
  docker.elastic.co/apm/apm-server:8.11.0 \
  --strict.perms=false \
  -e output.elasticsearch.hosts=["elasticsearch:9200"]
```

Access Kibana at: http://localhost:5601

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

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Health Check

**GET** `/health`

Check service status and APM configuration.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "apm_enabled": true,
  "timestamp": "2024-01-15T10:30:00"
}
```

### 2. Application Metrics

**GET** `/metrics`

Get application performance metrics.

**Response:**
```json
{
  "total_requests": 1250,
  "avg_response_time_ms": 125.5,
  "error_count": 3
}
```

### 3. Create Task

**POST** `/tasks`

Create a task (demonstrates transaction tracking and custom spans).

**Request:**
```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive docs",
  "priority": "high"
}
```

**Response:**
```json
{
  "id": "task-abc123",
  "title": "Complete project documentation",
  "description": "Write comprehensive docs",
  "priority": "high",
  "created_at": "2024-01-15T10:30:00",
  "processing_time_ms": 85.3
}
```

**APM Features Demonstrated:**
- Automatic transaction tracking
- Custom context (task details)
- Labels (priority, operation type)
- Custom spans (database, notification)

### 4. Process Data

**POST** `/process`

Process batch data (demonstrates performance monitoring).

**Request:**
```json
{
  "items": ["item1", "item2", "item3"],
  "delay_ms": 100
}
```

**Response:**
```json
{
  "processed_count": 3,
  "total_time_ms": 305.7,
  "items": ["ITEM1", "ITEM2", "ITEM3"]
}
```

**APM Features Demonstrated:**
- Batch processing spans
- Individual item tracking
- Performance measurement

### 5. Trigger Test Error

**GET** `/error/test`

Trigger an error for APM testing.

**APM Features Demonstrated:**
- Exception capture
- Stack trace collection
- Error context
- Trace ID correlation

### 6. Slow Endpoint

**GET** `/slow`

Intentionally slow endpoint for performance testing.

**APM Features Demonstrated:**
- Slow transaction detection
- Performance bottleneck identification
- Span duration tracking

## Usage Examples

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Review code",
    "priority": "high"
  }'

# Process data
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "items": ["apple", "banana", "cherry"],
    "delay_ms": 50
  }'

# Get metrics
curl http://localhost:8000/metrics

# Test error tracking
curl http://localhost:8000/error/test

# Test slow endpoint
curl http://localhost:8000/slow
```

### Using Python requests

```python
import requests

base_url = "http://localhost:8000"

# Create a task
response = requests.post(
    f"{base_url}/tasks",
    json={
        "title": "Important task",
        "description": "This is important",
        "priority": "high"
    }
)
print(response.json())

# Process data
response = requests.post(
    f"{base_url}/process",
    json={
        "items": ["data1", "data2"],
        "delay_ms": 100
    }
)
print(response.json())

# Get metrics
response = requests.get(f"{base_url}/metrics")
print(response.json())
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

**Note**: Tests run with APM disabled (`ELASTIC_APM_ENABLED=false`) to avoid requiring an APM server for testing.

## APM Features Explained

### Transaction Tracking

Every HTTP request creates a transaction:

```
GET /tasks
├── Transaction: GET /tasks
│   ├── Duration: 85.3ms
│   ├── Status: 201
│   ├── Labels: {priority: "high", operation: "create_task"}
│   └── Context: {task_title: "...", task_priority: "high"}
```

### Custom Spans

Track specific operations within a transaction:

```python
@capture_span("database.create_task", "db.create")
async def _create_task_in_database(request):
    # This operation will appear as a span in APM
    await asyncio.sleep(0.05)
    return task_id
```

Appears in APM as:
```
Transaction: POST /tasks (85.3ms)
├── Span: database.create_task (50ms)
└── Span: notification.send_task_created (30ms)
```

### Custom Context

Add business context to transactions:

```python
set_custom_context({
    "task_title": request.title,
    "task_priority": request.priority,
    "user_id": "user-123"
})
```

### Labels

Tag transactions for filtering:

```python
label_transaction(
    priority=request.priority,
    operation="create_task",
    environment="production"
)
```

### Error Tracking

Capture exceptions with context:

```python
try:
    # Some operation
    raise ValueError("Something went wrong")
except Exception as e:
    capture_exception(
        e,
        custom={"additional": "context"},
        handled=True
    )
```

## Viewing APM Data

### In Kibana

1. **Navigate to APM**: http://localhost:5601/app/apm
2. **Select your service**: `poc-05-apm-demo`
3. **View metrics**:
   - Transactions per minute
   - Average response time
   - Error rate
4. **Explore transactions**:
   - Click on transaction to see details
   - View spans and timeline
   - See custom context and labels
5. **Analyze errors**:
   - View error rate
   - See stack traces
   - Correlate with transactions

### Key Metrics to Monitor

1. **Throughput**: Requests per second
2. **Latency**: Average response time (p50, p95, p99)
3. **Error Rate**: Percentage of failed requests
4. **Slow Transactions**: Transactions exceeding threshold
5. **Span Performance**: Database queries, API calls

## Configuration Options

### APM Settings

- `ELASTIC_APM_ENABLED`: Enable/disable APM (default: true)
- `ELASTIC_APM_SERVICE_NAME`: Service identifier
- `ELASTIC_APM_SERVER_URL`: APM server URL
- `ELASTIC_APM_ENVIRONMENT`: Environment (dev, staging, prod)
- `APM_TRANSACTION_SAMPLE_RATE`: Sample rate (0.0-1.0)
- `APM_CAPTURE_BODY`: Capture request bodies (all, errors, transactions, off)
- `APM_CAPTURE_HEADERS`: Capture HTTP headers
- `APM_SPAN_FRAMES_MIN_DURATION`: Minimum duration for stack frames

### Sampling

Control what data is sent to APM:

```python
# Sample 50% of transactions
APM_TRANSACTION_SAMPLE_RATE=0.5

# Sample all transactions (100%)
APM_TRANSACTION_SAMPLE_RATE=1.0
```

## Production Considerations

### 1. Performance Impact

- APM has minimal performance impact (~1-5ms overhead)
- Use sampling in high-traffic environments
- Disable body capture if not needed

### 2. Data Volume

- Lower sample rate for high-traffic services
- Set appropriate span frame duration
- Disable header capture if sensitive

### 3. Security

- Don't capture sensitive data in context
- Use secret token for APM server auth
- Filter sensitive headers

### 4. Monitoring

- Set up alerts for error rates
- Monitor APM agent health
- Track APM data volume

## Differences from Previous POCs

| Feature | POC 1-4 | POC 5 (APM) |
|---------|---------|-------------|
| Monitoring | Logs only | Full APM |
| Tracing | None | Distributed tracing |
| Performance | Manual timing | Automatic tracking |
| Errors | Exception handling | Error tracking + correlation |
| Metrics | None | Built-in metrics |
| Debugging | Logs | Traces + spans + context |

## Common Use Cases

### 1. Performance Debugging

- Identify slow database queries
- Find bottlenecks in code
- Compare performance across deployments

### 2. Error Investigation

- View stack traces
- See error context
- Correlate errors with user actions

### 3. SLA Monitoring

- Track response time percentiles
- Monitor error rates
- Alert on SLA violations

### 4. Capacity Planning

- Analyze traffic patterns
- Identify peak hours
- Plan scaling needs

## Troubleshooting

### APM Server Connection Issues

1. **Check APM server is running:**
   ```bash
   curl http://localhost:8200/
   ```

2. **Verify configuration:**
   - Check `ELASTIC_APM_SERVER_URL` in `.env`
   - Ensure APM server is accessible

3. **Check logs:**
   - Look for APM connection errors in application logs

### No Data in Kibana

1. **Verify APM is enabled:**
   - Check `ELASTIC_APM_ENABLED=true` in `.env`

2. **Check sampling rate:**
   - Ensure `APM_TRANSACTION_SAMPLE_RATE > 0`

3. **Generate some traffic:**
   - Make requests to your API
   - Check Kibana after 30 seconds

### High Overhead

1. **Reduce sampling:**
   - Lower `APM_TRANSACTION_SAMPLE_RATE`

2. **Disable body capture:**
   - Set `APM_CAPTURE_BODY=off`

3. **Increase span threshold:**
   - Increase `APM_SPAN_FRAMES_MIN_DURATION`

## Resources

- [ElasticAPM Python Documentation](https://www.elastic.co/guide/en/apm/agent/python/current/index.html)
- [ElasticAPM FastAPI Integration](https://www.elastic.co/guide/en/apm/agent/python/current/starlette-support.html)
- [APM Server Setup](https://www.elastic.co/guide/en/apm/guide/current/apm-quick-start.html)
- [Kibana APM UI](https://www.elastic.co/guide/en/kibana/current/xpack-apm.html)

## License

MIT License - See root repository for details.
