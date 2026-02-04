import os
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv

from magetools.spell_registry import register_spell

# Load environment variables
load_dotenv()

user_name = "Not currently known. Maybe if you ask, the user will tell you their name.\nYou can the ask the grimorium for a spell to save the user's name."


@register_spell
async def get_user_location() -> Dict[str, Any]:
    """Gets the user's current location based on their IP address.

    Returns:
        Dict[str, Any]: A dictionary containing location details:
            - success (bool): Whether the request was successful
            - data (dict): A dictionary with location data (city, country, etc.)
            - message (str): A summary message.

    Example:
        >>> await get_user_location()
        {'success': True, 'data': {'city': 'Mountain View', ...}, 'message': 'Your current location is Mountain View, United States.'}
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://ip-api.com/json")
            response.raise_for_status()
            location_data = response.json()
            return {
                "success": True,
                "data": location_data,
                "message": f"Your current location is {location_data.get('city')}, {location_data.get('country')}.",
            }
    except httpx.RequestError as e:
        return {
            "success": False,
            "data": None,
            "message": f"An error occurred while fetching location: {e}",
        }


@register_spell
async def weather_forecast(city: Optional[str] = None) -> Dict[str, Any]:
    """Gets the current weather forecast for a specified city.
    If no city is provided, the user's current location will be used.


    Args:
        city (Optional[str]): The city for which to fetch the weather forecast. If not provided, the user's location will be used.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the request was successful
            - data (dict): A dictionary with weather data (city, temperature, description, etc.)
            - message (str): A summary message.

    Example:
        >>> await weather_forecast("Mountain View")
        {'success': True, 'data': {'city': 'Mountain View', ...}, 'message': 'The current weather in Mountain View is sunny with a temperature of 72F.'}
        >>> await weather_forecast()
        {'success': True, 'data': {'city': <users_city>, ...}, 'message': 'The current weather in <users_city> is sunny with a temperature of 72F.'}
    """
    api_key = os.getenv("WEATHER_API_KEY")
    if city is None:
        result = await get_user_location()
        city = str(
            result.get("data", {}).get("city", "Unknown")
        )  # ideally use get_user_location to get the user's city
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            weather_data = response.json()
            temperature = weather_data["main"]["temp"]
            description = weather_data["weather"][0]["description"]
            return {
                "success": True,
                "data": weather_data,
                "message": f"The current weather in {city} is {description} with a temperature of {temperature}F.",
            }
    except httpx.RequestError as e:
        return {
            "success": False,
            "data": None,
            "message": f"An error occurred while fetching weather data: {e}",
        }
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "data": None,
            "message": f"An error occurred while fetching weather data: {e}. Please provide a valid city name.",
        }


@register_spell
async def get_user_name() -> Dict[str, Any]:
    """Retrieves the name of the currently authenticated user.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the request was successful
            - data (str): The user's full name
            - message (str): A summary message.

    Example:
        >>> get_user_name()
        {'success': True, 'data': 'John Doe', 'message': 'User name is John Doe'}
    """
    return {"success": True, "data": user_name, "message": f"User name is {user_name}"}
