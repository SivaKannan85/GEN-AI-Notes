"""
Calculator tool for mathematical operations.
"""

import logging
from langchain.tools import Tool
from typing import Union

logger = logging.getLogger(__name__)


def safe_calculate(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.

    Args:
        expression: Mathematical expression to evaluate

    Returns:
        Result as string
    """
    try:
        # Remove any potentially dangerous characters
        allowed_chars = set('0123456789+-*/.()**% ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Expression contains invalid characters. Only numbers and operators (+, -, *, /, **, %, .) are allowed."

        # Evaluate the expression safely
        result = eval(expression, {"__builtins__": {}}, {})

        logger.info(f"Calculated: {expression} = {result}")
        return str(result)

    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        return f"Error: {str(e)}"


def get_calculator_tool() -> Tool:
    """
    Get the calculator tool.

    Returns:
        Calculator Tool instance
    """
    return Tool(
        name="Calculator",
        func=safe_calculate,
        description="""Useful for performing mathematical calculations.
Input should be a valid mathematical expression using numbers and operators (+, -, *, /, **, %, .).
Examples:
- "10 + 5"
- "100 * 0.15"
- "2 ** 8"
- "10000 * (1 + 0.05) ** 3"
Always return the numerical result."""
    )
