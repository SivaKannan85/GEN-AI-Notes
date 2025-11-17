"""
Tests for POC 8: LangChain Agents with Tools
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# Import individual tool functions for unit testing
from app.tools.calculator import safe_calculate
from app.tools.datetime_tool import datetime_operations
from app.tools.string_tools import string_operations
from app.tools.json_tool import json_operations
from app.tools.weather_tool import get_weather


# ============================================================================
# Tool Unit Tests
# ============================================================================

def test_calculator_addition():
    """Test calculator tool with addition"""
    result = safe_calculate("10 + 5")
    assert result == "15"


def test_calculator_multiplication():
    """Test calculator tool with multiplication"""
    result = safe_calculate("7 * 8")
    assert result == "56"


def test_calculator_power():
    """Test calculator tool with exponentiation"""
    result = safe_calculate("2 ** 10")
    assert result == "1024"


def test_calculator_compound_interest():
    """Test calculator with compound interest formula"""
    result = safe_calculate("10000 * (1 + 0.05) ** 3")
    assert float(result) == pytest.approx(11576.25, rel=0.01)


def test_calculator_invalid_chars():
    """Test calculator with invalid characters"""
    result = safe_calculate("10 + import")
    assert "Error" in result


def test_datetime_current():
    """Test datetime tool - current time"""
    result = datetime_operations("current")
    assert len(result) > 0
    assert "-" in result  # Date format includes hyphens


def test_datetime_date():
    """Test datetime tool - current date"""
    result = datetime_operations("date")
    assert len(result) == 10  # YYYY-MM-DD format


def test_datetime_add_days():
    """Test datetime tool - add days"""
    result = datetime_operations("add:7:days")
    assert "Error" not in result


def test_datetime_day_of_week():
    """Test datetime tool - day of week"""
    result = datetime_operations("day_of_week")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    assert result in days


def test_string_upper():
    """Test string tool - uppercase"""
    result = string_operations("upper:hello world")
    assert result == "HELLO WORLD"


def test_string_lower():
    """Test string tool - lowercase"""
    result = string_operations("lower:HELLO WORLD")
    assert result == "hello world"


def test_string_reverse():
    """Test string tool - reverse"""
    result = string_operations("reverse:hello")
    assert result == "olleh"


def test_string_length():
    """Test string tool - length"""
    result = string_operations("length:OpenAI")
    assert result == "6"


def test_string_replace():
    """Test string tool - replace"""
    result = string_operations("replace:hello world:world:universe")
    assert result == "hello universe"


def test_string_count():
    """Test string tool - count"""
    result = string_operations("count:banana:a")
    assert result == "3"


def test_json_validate_valid():
    """Test JSON tool - validate valid JSON"""
    result = json_operations('validate:{"name":"John","age":30}')
    assert result == "Valid JSON"


def test_json_validate_invalid():
    """Test JSON tool - validate invalid JSON"""
    result = json_operations('validate:{invalid}')
    assert "Invalid JSON" in result


def test_json_get_key():
    """Test JSON tool - get value by key"""
    result = json_operations('get:{"name":"Alice","age":25}:name')
    assert result == "Alice"


def test_json_keys():
    """Test JSON tool - get keys"""
    result = json_operations('keys:{"x":1,"y":2,"z":3}')
    assert "x" in result
    assert "y" in result
    assert "z" in result


def test_weather_tool():
    """Test weather tool"""
    result = get_weather("London")
    assert "London" in result
    assert "°C" in result


# ============================================================================
# API Integration Tests
# ============================================================================

@pytest.fixture
def mock_agent_service():
    """Mock agent service"""
    mock = Mock()
    mock.tools = [Mock(name="Calculator"), Mock(name="DateTime")]
    mock.get_available_tools = Mock(return_value=[
        ("Calculator", "Useful for math"),
        ("DateTime", "Useful for dates")
    ])
    mock.execute_task = Mock(return_value=Mock(
        task="Test task",
        result="42",
        steps=[],
        total_steps=0,
        success=True,
        execution_time_seconds=1.5
    ))
    return mock


@pytest.fixture
def client(mock_agent_service):
    """Test client with mocked dependencies"""
    with patch('app.main.agent_service', mock_agent_service):
        from app.main import app
        with TestClient(app) as test_client:
            yield test_client


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "available_tools" in data


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_tools(client, mock_agent_service):
    """Test listing tools"""
    response = client.get("/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert "total_tools" in data
    assert data["total_tools"] >= 0


def test_execute_task(client, mock_agent_service):
    """Test executing a task"""
    request_data = {
        "task": "Calculate 10 + 5",
        "max_iterations": 10,
        "verbose": False
    }

    response = client.post("/execute", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert "task" in data
    assert "result" in data
    assert "steps" in data
    assert "success" in data


def test_execute_task_minimal(client):
    """Test executing with minimal parameters"""
    request_data = {
        "task": "What is the current date?"
    }

    response = client.post("/execute", json=request_data)

    assert response.status_code == 200


def test_execute_task_empty():
    """Test executing with empty task"""
    from app.main import app
    with TestClient(app) as test_client:
        request_data = {
            "task": ""
        }

        response = test_client.post("/execute", json=request_data)

        assert response.status_code == 422  # Validation error


@pytest.mark.parametrize("task", [
    "Calculate 5 * 8",
    "What is the current date?",
    "Convert HELLO to lowercase",
    "Get weather for Tokyo"
])
def test_execute_various_tasks(client, task):
    """Test executing various tasks"""
    request_data = {
        "task": task,
        "verbose": False
    }

    response = client.post("/execute", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert "result" in data
