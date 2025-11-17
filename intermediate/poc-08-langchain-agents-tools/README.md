# POC 8: LangChain Agents with Tools

A production-ready implementation of LangChain's ReAct (Reasoning + Acting) agent with custom tools for intelligent task execution. The agent can reason about tasks, select appropriate tools, and execute multi-step solutions autonomously.

## Features

- **ReAct Agent**: Implements the Reasoning and Acting paradigm for intelligent task solving
- **Custom Tools**: 5 production-ready tools for various operations
- **Step-by-Step Reasoning**: Full visibility into the agent's thought process
- **RESTful API**: FastAPI-based endpoints for task execution
- **Extensible Architecture**: Easy to add new tools
- **Error Handling**: Robust error handling and retry logic
- **Testing Suite**: Comprehensive unit and integration tests

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                  Agent Executor Service                      │
│  ┌────────────────────────────────────────────────────┐     │
│  │             ReAct Agent (LangChain)                │     │
│  │                                                     │     │
│  │   Question → Thought → Action → Observation        │     │
│  │                  ↓                                  │     │
│  │               Tool Selection                        │     │
│  │                  ↓                                  │     │
│  │            Tool Execution                           │     │
│  │                  ↓                                  │     │
│  │            Final Answer                             │     │
│  └────────────────────────────────────────────────────┘     │
└────────────────────────┬─────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────┐            ┌──────────────────┐
│  Custom Tools   │            │   LLM (GPT-3.5)  │
│  • Calculator   │            │  • Reasoning     │
│  • DateTime     │            │  • Planning      │
│  • String Ops   │            │  • Execution     │
│  • JSON Ops     │            └──────────────────┘
│  • Weather      │
└─────────────────┘
```

## Tech Stack

- **LangChain**: Agent framework and orchestration
- **FastAPI**: Web framework
- **OpenAI**: GPT-3.5-turbo for reasoning
- **Pydantic**: Data validation

## Available Tools

### 1. Calculator
Perform mathematical calculations.

**Operations:**
- Basic arithmetic (+, -, *, /)
- Exponentiation (**)
- Modulo (%)
- Complex expressions

**Examples:**
```python
"10 + 5"  # → 15
"2 ** 10"  # → 1024
"10000 * (1 + 0.05) ** 3"  # → 11576.25 (compound interest)
```

### 2. DateTime
Date and time operations.

**Operations:**
- Get current date/time
- Add/subtract days/hours/weeks
- Get day of week, month, year

**Examples:**
```python
"current"  # → 2024-01-15 10:30:00
"date"  # → 2024-01-15
"add:7:days"  # → 2024-01-22 10:30:00
"day_of_week"  # → Monday
```

### 3. StringOperations
String manipulation.

**Operations:**
- upper, lower, reverse
- length, count, replace
- split, trim

**Examples:**
```python
"upper:hello world"  # → HELLO WORLD
"length:OpenAI"  # → 6
"replace:hello world:world:universe"  # → hello universe
"count:banana:a"  # → 3
```

### 4. JSONOperations
JSON data manipulation.

**Operations:**
- validate, pretty print
- get value by key
- list keys, get length

**Examples:**
```python
'validate:{"name":"John"}'  # → Valid JSON
'get:{"name":"Alice","age":25}:name'  # → Alice
'keys:{"x":1,"y":2}'  # → ['x', 'y']
```

### 5. Weather
Get weather information (mock for demonstration).

**Examples:**
```python
"London"  # → Weather in London: Sunny, 22°C, Humidity: 65%, Wind: 15 km/h
"Tokyo"  # → Weather in Tokyo: ...
```

## Installation

### Prerequisites

- Python 3.9+
- OpenAI API key
- Virtual environment (recommended)

### Setup

1. **Navigate to the POC directory:**

```bash
cd intermediate/poc-08-langchain-agents-tools
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
OPENAI_TEMPERATURE=0.0
MAX_ITERATIONS=10
AGENT_VERBOSE=True
```

## Usage

### Starting the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

### API Endpoints

#### 1. List Available Tools

```bash
curl http://localhost:8000/tools
```

**Response:**
```json
{
  "tools": [
    {
      "name": "Calculator",
      "description": "Useful for performing mathematical calculations...",
      "parameters": {}
    },
    {
      "name": "DateTime",
      "description": "Useful for date and time operations...",
      "parameters": {}
    }
  ],
  "total_tools": 5
}
```

#### 2. Execute Task

Execute a task using the ReAct agent:

```bash
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Calculate the compound interest on $10,000 at 5% annual rate for 3 years",
    "max_iterations": 10,
    "verbose": true
  }'
```

**Response:**
```json
{
  "task": "Calculate the compound interest on $10,000 at 5% annual rate for 3 years",
  "result": "The compound interest is $1,576.25, making the final amount $11,576.25",
  "steps": [
    {
      "step_number": 1,
      "thought": "I need to use the compound interest formula: A = P(1 + r)^t",
      "action": "Calculator",
      "action_input": "10000 * (1 + 0.05) ** 3",
      "observation": "11576.25"
    },
    {
      "step_number": 2,
      "thought": "Now I need to calculate just the interest amount",
      "action": "Calculator",
      "action_input": "11576.25 - 10000",
      "observation": "1576.25"
    }
  ],
  "total_steps": 2,
  "success": true,
  "execution_time_seconds": 2.45
}
```

## Example Tasks

### Mathematical Calculations

```bash
# Simple calculation
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "What is 2 raised to the power of 16?"}'

# Complex calculation
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "If I invest $5000 at 7% annual interest for 5 years, what will be the final amount?"}'
```

### Date/Time Operations

```bash
# Current date
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "What is today date?"}'

# Date calculations
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "What day will it be 30 days from now?"}'
```

### String Manipulation

```bash
# String operations
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "Convert the text HELLO WORLD to lowercase and tell me its length"}'

# Complex string task
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "Count how many times the letter a appears in the word banana"}'
```

### Multi-Step Tasks

```bash
# Combining multiple tools
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "Calculate 100 * 5, then reverse the result as a string"}'

# Complex reasoning
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "If today is Monday, what day will it be in 100 days? Then calculate 100 divided by 7"}'
```

## How the ReAct Agent Works

The ReAct (Reasoning + Acting) agent follows this loop:

1. **Thought**: Analyzes the task and decides what to do next
2. **Action**: Selects a tool to use
3. **Action Input**: Determines the input for the tool
4. **Observation**: Receives the result from the tool
5. **Repeat**: Goes back to step 1 until the task is complete
6. **Final Answer**: Provides the final result

### Example Agent Execution

**Task:** "Calculate 15% tip on a $85 bill"

**Step 1:**
- Thought: "I need to calculate 15% of 85"
- Action: Calculator
- Action Input: "85 * 0.15"
- Observation: "12.75"

**Step 2:**
- Thought: "I now know the final answer"
- Final Answer: "The 15% tip on a $85 bill is $12.75"

## Adding Custom Tools

To add a new tool:

1. **Create tool file** in `app/tools/`:

```python
# app/tools/my_tool.py
from langchain.tools import Tool

def my_function(input: str) -> str:
    # Your tool logic here
    return result

def get_my_tool() -> Tool:
    return Tool(
        name="MyTool",
        func=my_function,
        description="Description of what this tool does"
    )
```

2. **Register in agent_executor.py**:

```python
from app.tools.my_tool import get_my_tool

def _initialize_tools(self) -> List[Tool]:
    tools = []
    # ... existing tools
    tools.append(get_my_tool())
    return tools
```

3. **Add configuration** in `.env`:

```env
ENABLE_MY_TOOL=True
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_main.py -v

# Run tool tests only
pytest tests/test_main.py::test_calculator_addition -v
```

## Project Structure

```
poc-08-langchain-agents-tools/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── models.py                  # Pydantic models
│   ├── config.py                  # Configuration
│   ├── agent_executor.py          # ReAct agent implementation
│   └── tools/
│       ├── __init__.py
│       ├── calculator.py          # Math calculations
│       ├── datetime_tool.py       # Date/time operations
│       ├── string_tools.py        # String manipulation
│       ├── json_tool.py           # JSON operations
│       └── weather_tool.py        # Weather info (mock)
├── tests/
│   ├── __init__.py
│   └── test_main.py               # Comprehensive tests
├── .env.example                   # Environment template
├── .gitignore
├── requirements.txt
└── README.md
```

## Configuration

### Environment Variables

| Variable                      | Description                      | Default       |
|-------------------------------|----------------------------------|---------------|
| OPENAI_API_KEY                | OpenAI API key                   | (required)    |
| OPENAI_MODEL                  | Model for agent reasoning        | gpt-3.5-turbo |
| OPENAI_TEMPERATURE            | Temperature (0 = deterministic)  | 0.0           |
| MAX_ITERATIONS                | Maximum agent steps              | 10            |
| AGENT_VERBOSE                 | Enable verbose logging           | True          |
| AGENT_EARLY_STOPPING_METHOD   | Stopping method (generate/force) | generate      |
| ENABLE_CALCULATOR             | Enable calculator tool           | True          |
| ENABLE_DATETIME               | Enable datetime tool             | True          |
| ENABLE_STRING_TOOLS           | Enable string/JSON tools         | True          |

## Troubleshooting

### Agent Reaches Max Iterations

**Problem:** Agent stops before completing task

**Solutions:**
- Increase `MAX_ITERATIONS` in `.env`
- Simplify the task description
- Check if the task requires tools that aren't available

### Tool Errors

**Problem:** Tools return errors

**Solutions:**
- Check input format matches tool's expected format
- Review tool descriptions in `/tools` endpoint
- Enable verbose mode to see detailed execution

### Poor Quality Answers

**Problem:** Agent gives incorrect results

**Solutions:**
- Lower temperature to 0.0 for more deterministic responses
- Ensure tools are working correctly (run unit tests)
- Provide more specific task descriptions

## Best Practices

1. **Task Descriptions**: Be specific and clear
   - ✅ "Calculate 15% of 100"
   - ❌ "Do some math"

2. **Tool Selection**: Design tools to be:
   - Single-purpose
   - Well-documented
   - Error-resistant

3. **Performance**:
   - Set appropriate max_iterations
   - Use lower temperature for factual tasks
   - Enable verbose mode only when debugging

4. **Error Handling**:
   - Tools should return descriptive error messages
   - Validate inputs before processing
   - Log errors for debugging

## Comparison with Other POCs

| Feature              | POC 7 (Conversational RAG) | POC 8 (Agents with Tools) |
|----------------------|----------------------------|---------------------------|
| Autonomous reasoning | ❌                         | ✅                        |
| Tool selection       | ❌                         | ✅                        |
| Multi-step execution | Limited                    | ✅                        |
| Conversation memory  | ✅                         | ❌ (single-turn)          |
| Document retrieval   | ✅                         | ❌ (can be added)         |
| Task decomposition   | ❌                         | ✅                        |

## Use Cases

1. **Data Processing**: Calculate statistics, transform data, analyze patterns
2. **Automation**: Multi-step workflows requiring different tools
3. **Information Retrieval**: Answer questions using various data sources
4. **Code Generation**: Generate code snippets using tool combinations
5. **Research Assistant**: Gather and synthesize information from multiple sources

## Next Steps

### Enhancements

- Add memory to make agent conversational
- Integrate with POC 6's RAG capabilities
- Add more specialized tools (SQL, API calls, file operations)
- Implement tool chaining for complex workflows
- Add streaming for real-time responses

### Production Readiness

- [ ] Add authentication
- [ ] Implement rate limiting
- [ ] Add request queuing for long-running tasks
- [ ] Implement tool result caching
- [ ] Add monitoring and observability
- [ ] Create tool marketplace/registry

## Resources

- [LangChain Agents Documentation](https://python.langchain.com/docs/modules/agents/)
- [ReAct Paper](https://arxiv.org/abs/2210.03629)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## License

MIT License - See root repository for details

---

**POC 8 Status**: ✅ Complete

**Previous POC**: POC 7 - Conversational RAG with Memory
**Next POC**: POC 9 - Multi-Query Retrieval Strategies
