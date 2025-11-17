"""
DateTime tool for date and time operations.
"""

import logging
from datetime import datetime, timedelta
from langchain.tools import Tool
import json

logger = logging.getLogger(__name__)


def datetime_operations(query: str) -> str:
    """
    Perform date and time operations.

    Supported queries:
    - "current" - Get current date and time
    - "date" - Get current date only
    - "time" - Get current time only
    - "add:N:days" - Add N days to current date
    - "subtract:N:days" - Subtract N days from current date
    - "add:N:hours" - Add N hours to current time
    - "format:YYYY-MM-DD" - Format current date

    Args:
        query: Query string

    Returns:
        Result as string
    """
    try:
        query = query.strip().lower()
        now = datetime.now()

        if query == "current":
            result = now.strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"Current datetime: {result}")
            return result

        elif query == "date":
            result = now.strftime("%Y-%m-%d")
            logger.info(f"Current date: {result}")
            return result

        elif query == "time":
            result = now.strftime("%H:%M:%S")
            logger.info(f"Current time: {result}")
            return result

        elif query.startswith("add:"):
            parts = query.split(":")
            if len(parts) != 3:
                return "Error: Invalid format. Use 'add:N:days' or 'add:N:hours'"

            amount = int(parts[1])
            unit = parts[2]

            if unit == "days":
                new_date = now + timedelta(days=amount)
                result = new_date.strftime("%Y-%m-%d %H:%M:%S")
            elif unit == "hours":
                new_date = now + timedelta(hours=amount)
                result = new_date.strftime("%Y-%m-%d %H:%M:%S")
            elif unit == "weeks":
                new_date = now + timedelta(weeks=amount)
                result = new_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                return f"Error: Unsupported unit '{unit}'. Use 'days', 'hours', or 'weeks'"

            logger.info(f"Added {amount} {unit}: {result}")
            return result

        elif query.startswith("subtract:"):
            parts = query.split(":")
            if len(parts) != 3:
                return "Error: Invalid format. Use 'subtract:N:days' or 'subtract:N:hours'"

            amount = int(parts[1])
            unit = parts[2]

            if unit == "days":
                new_date = now - timedelta(days=amount)
                result = new_date.strftime("%Y-%m-%d %H:%M:%S")
            elif unit == "hours":
                new_date = now - timedelta(hours=amount)
                result = new_date.strftime("%Y-%m-%d %H:%M:%S")
            elif unit == "weeks":
                new_date = now - timedelta(weeks=amount)
                result = new_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                return f"Error: Unsupported unit '{unit}'. Use 'days', 'hours', or 'weeks'"

            logger.info(f"Subtracted {amount} {unit}: {result}")
            return result

        elif query == "day_of_week":
            result = now.strftime("%A")
            logger.info(f"Day of week: {result}")
            return result

        elif query == "month":
            result = now.strftime("%B")
            logger.info(f"Month: {result}")
            return result

        elif query == "year":
            result = str(now.year)
            logger.info(f"Year: {result}")
            return result

        else:
            return f"Error: Unsupported query '{query}'. Supported: current, date, time, add:N:days, subtract:N:days, day_of_week, month, year"

    except ValueError as e:
        return f"Error: Invalid number format - {str(e)}"
    except Exception as e:
        logger.error(f"DateTime operation error: {str(e)}")
        return f"Error: {str(e)}"


def get_datetime_tool() -> Tool:
    """
    Get the datetime tool.

    Returns:
        DateTime Tool instance
    """
    return Tool(
        name="DateTime",
        func=datetime_operations,
        description="""Useful for date and time operations.
Supported queries:
- "current" - Get current date and time
- "date" - Get current date
- "time" - Get current time
- "add:N:days" - Add N days to current date
- "subtract:N:days" - Subtract N days
- "add:N:hours" - Add N hours
- "day_of_week" - Get current day name
- "month" - Get current month name
- "year" - Get current year
Examples:
- "current"
- "add:7:days"
- "subtract:2:hours"
- "day_of_week"
"""
    )
