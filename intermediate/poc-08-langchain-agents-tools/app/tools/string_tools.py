"""
String manipulation tools.
"""

import logging
from langchain.tools import Tool
import json

logger = logging.getLogger(__name__)


def string_operations(query: str) -> str:
    """
    Perform string operations.

    Format: operation:text
    Supported operations:
    - upper:text - Convert to uppercase
    - lower:text - Convert to lowercase
    - reverse:text - Reverse the string
    - length:text - Get string length
    - count:text:substring - Count occurrences of substring
    - replace:text:old:new - Replace old with new

    Args:
        query: Query string in format "operation:text"

    Returns:
        Result as string
    """
    try:
        if ":" not in query:
            return "Error: Invalid format. Use 'operation:text' format"

        parts = query.split(":", 1)
        operation = parts[0].strip().lower()

        if operation == "upper":
            text = parts[1]
            result = text.upper()
            logger.info(f"Uppercase: '{text}' -> '{result}'")
            return result

        elif operation == "lower":
            text = parts[1]
            result = text.lower()
            logger.info(f"Lowercase: '{text}' -> '{result}'")
            return result

        elif operation == "reverse":
            text = parts[1]
            result = text[::-1]
            logger.info(f"Reverse: '{text}' -> '{result}'")
            return result

        elif operation == "length":
            text = parts[1]
            result = str(len(text))
            logger.info(f"Length of '{text}': {result}")
            return result

        elif operation == "count":
            subparts = parts[1].split(":", 1)
            if len(subparts) != 2:
                return "Error: count requires format 'count:text:substring'"
            text = subparts[0]
            substring = subparts[1]
            result = str(text.count(substring))
            logger.info(f"Count '{substring}' in '{text}': {result}")
            return result

        elif operation == "replace":
            subparts = parts[1].split(":", 2)
            if len(subparts) != 3:
                return "Error: replace requires format 'replace:text:old:new'"
            text = subparts[0]
            old = subparts[1]
            new = subparts[2]
            result = text.replace(old, new)
            logger.info(f"Replace '{old}' with '{new}' in '{text}': '{result}'")
            return result

        elif operation == "split":
            subparts = parts[1].split(":", 1)
            if len(subparts) != 2:
                return "Error: split requires format 'split:text:delimiter'"
            text = subparts[0]
            delimiter = subparts[1]
            result = str(text.split(delimiter))
            logger.info(f"Split '{text}' by '{delimiter}': {result}")
            return result

        elif operation == "trim":
            text = parts[1]
            result = text.strip()
            logger.info(f"Trim '{text}' -> '{result}'")
            return result

        else:
            return f"Error: Unsupported operation '{operation}'. Supported: upper, lower, reverse, length, count, replace, split, trim"

    except Exception as e:
        logger.error(f"String operation error: {str(e)}")
        return f"Error: {str(e)}"


def get_string_tool() -> Tool:
    """
    Get the string manipulation tool.

    Returns:
        String Tool instance
    """
    return Tool(
        name="StringOperations",
        func=string_operations,
        description="""Useful for string manipulation operations.
Format: operation:text
Supported operations:
- upper:text - Convert to uppercase
- lower:text - Convert to lowercase
- reverse:text - Reverse string
- length:text - Get string length
- count:text:substring - Count occurrences
- replace:text:old:new - Replace substring
- split:text:delimiter - Split string
- trim:text - Remove whitespace
Examples:
- "upper:hello world"
- "length:OpenAI"
- "replace:hello world:world:universe"
- "count:banana:a"
"""
    )
