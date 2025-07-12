import re
import httpx
import logging
from langchain.tools import tool
from ..core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

@tool
def get_weather(location: str) -> str:
    """
    Get current weather information for a specific location.
    
    Args:
        location: The city or location to get weather for (e.g., "Paris", "Tokyo", "New York")
    
    Returns:
        A string describing the current weather conditions
    """
    logger.info(f"🌤️  Getting weather for location: {location}")
    
    try:
        if not settings.OPENWEATHER_API_KEY:
            logger.warning("⚠️  OpenWeather API key not configured, using mock data")
            return f"Weather API key not configured. Mock data: It's sunny and 24°C in {location}."
        
        with httpx.Client() as client:
            params = {
                "q": location,
                "appid": settings.OPENWEATHER_API_KEY,
                "units": "metric"
            }
            
            logger.debug(f"🌐 Making API request to OpenWeather for {location}")
            response = client.get(settings.OPENWEATHER_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            country = data["sys"]["country"]
            
            result = f"It's {description} and {temp}°C in {location}, {country}."
            logger.info(f"✅ Weather result: {result}")
            return result
            
    except Exception as e:
        error_msg = f"Unable to fetch weather data for {location}: {str(e)}"
        logger.error(f"❌ Weather API error: {error_msg}")
        return error_msg


def extract_location_from_query(query: str) -> str:
    """Extract location from weather query for fallback"""
    patterns = [
        r"weather (?:in|for|at) (\w+(?:\s+\w+)*)",
        r"weather (?:like|today) (?:in|for|at) (\w+(?:\s+\w+)*)",
        r"(\w+(?:\s+\w+)*) weather",
        r"temperature (?:in|for|at) (\w+(?:\s+\w+)*)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            location = re.sub(r'\b(?:weather|like|today|temperature)\b', '', location, flags=re.IGNORECASE).strip()
            if location:
                return location
    
    return "San Francisco" 