"""
Weather tool (mock implementation for demonstration).
In production, this would integrate with a real weather API.
"""

import logging
import random
from langchain.tools import Tool

logger = logging.getLogger(__name__)


def get_weather(location: str) -> str:
    """
    Get weather information for a location (mock).

    Args:
        location: City or location name

    Returns:
        Weather information as string
    """
    try:
        location = location.strip()

        # Mock weather data
        conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Clear"]
        temperature = random.randint(15, 30)
        condition = random.choice(conditions)
        humidity = random.randint(40, 80)
        wind_speed = random.randint(5, 25)

        result = f"Weather in {location}: {condition}, {temperature}°C, Humidity: {humidity}%, Wind: {wind_speed} km/h"

        logger.info(f"Weather query for {location}: {result}")

        # Note: This is mock data for demonstration
        result += "\n(Note: This is simulated weather data for demonstration purposes)"

        return result

    except Exception as e:
        logger.error(f"Weather query error: {str(e)}")
        return f"Error: Unable to get weather for {location}"


def get_weather_tool() -> Tool:
    """
    Get the weather tool.

    Returns:
        Weather Tool instance
    """
    return Tool(
        name="Weather",
        func=get_weather,
        description="""Useful for getting weather information for a location.
Input should be a city or location name.
Returns current weather conditions including temperature, humidity, and wind speed.
Examples:
- "New York"
- "London"
- "Tokyo"
Note: This is a mock implementation for demonstration. In production, integrate with a real weather API."""
    )
