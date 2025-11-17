"""
JSON manipulation tool.
"""

import logging
import json
from langchain.tools import Tool

logger = logging.getLogger(__name__)


def json_operations(query: str) -> str:
    """
    Perform JSON operations.

    Format: operation:json_data[:key]
    Supported operations:
    - validate:json - Validate JSON
    - pretty:json - Pretty print JSON
    - get:json:key - Get value by key
    - keys:json - Get all keys

    Args:
        query: Query string

    Returns:
        Result as string
    """
    try:
        if ":" not in query:
            return "Error: Invalid format. Use 'operation:json_data' format"

        parts = query.split(":", 1)
        operation = parts[0].strip().lower()

        if operation == "validate":
            json_str = parts[1]
            try:
                json.loads(json_str)
                result = "Valid JSON"
                logger.info(f"JSON validation: {result}")
                return result
            except json.JSONDecodeError as e:
                return f"Invalid JSON: {str(e)}"

        elif operation == "pretty":
            json_str = parts[1]
            try:
                data = json.loads(json_str)
                result = json.dumps(data, indent=2)
                logger.info("Pretty printed JSON")
                return result
            except json.JSONDecodeError as e:
                return f"Invalid JSON: {str(e)}"

        elif operation == "get":
            subparts = parts[1].split(":", 1)
            if len(subparts) != 2:
                return "Error: get requires format 'get:json:key'"
            json_str = subparts[0]
            key = subparts[1]
            try:
                data = json.loads(json_str)
                if key in data:
                    result = str(data[key])
                    logger.info(f"Got key '{key}': {result}")
                    return result
                else:
                    return f"Key '{key}' not found in JSON"
            except json.JSONDecodeError as e:
                return f"Invalid JSON: {str(e)}"

        elif operation == "keys":
            json_str = parts[1]
            try:
                data = json.loads(json_str)
                if isinstance(data, dict):
                    result = str(list(data.keys()))
                    logger.info(f"JSON keys: {result}")
                    return result
                else:
                    return "Error: JSON is not an object"
            except json.JSONDecodeError as e:
                return f"Invalid JSON: {str(e)}"

        elif operation == "length":
            json_str = parts[1]
            try:
                data = json.loads(json_str)
                if isinstance(data, (list, dict)):
                    result = str(len(data))
                    logger.info(f"JSON length: {result}")
                    return result
                else:
                    return "Error: JSON is not an array or object"
            except json.JSONDecodeError as e:
                return f"Invalid JSON: {str(e)}"

        else:
            return f"Error: Unsupported operation '{operation}'. Supported: validate, pretty, get, keys, length"

    except Exception as e:
        logger.error(f"JSON operation error: {str(e)}")
        return f"Error: {str(e)}"


def get_json_tool() -> Tool:
    """
    Get the JSON manipulation tool.

    Returns:
        JSON Tool instance
    """
    return Tool(
        name="JSONOperations",
        func=json_operations,
        description="""Useful for JSON data manipulation.
Format: operation:json_data[:key]
Supported operations:
- validate:json - Check if valid JSON
- pretty:json - Format JSON with indentation
- get:json:key - Extract value by key
- keys:json - List all keys
- length:json - Get array/object length
Examples:
- 'validate:{"name":"John"}'
- 'pretty:{"a":1,"b":2}'
- 'get:{"name":"Alice","age":30}:name'
- 'keys:{"x":1,"y":2,"z":3}'
"""
    )
