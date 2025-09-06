from typing import Dict, Any, Optional


user_name = "Not currently known. Maybe if you ask, the user will tell you their name.\nYou can the ask the grimorium for a spell to save the user's name."

def weather_forecast() -> Dict[str, Any]:
    """Gets the current weather forecast for the user's location.
    
    Note:
        This function automatically detects the user's location and does not require
        explicit location input.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the request was successful
            - message (str): The weather forecast message
            
    Example:
        >>> weather_forecast()
        {'success': True, 'message': 'The current weather is sunny...'}
    """
    return {"success": True, "message": "The current weather is sunny with a temperature of 80 degrees Fahrenheit."}

def get_user_name() -> Dict[str, Any]:
    """Retrieves the name of the currently authenticated user.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the request was successful
            - message (str): The user's full name
            
    Example:
        >>> get_user_name()
        {'success': True, 'message': 'John Doe'}
    """
    return {"success": True, "message": user_name}

def save_user_name(first_name: str, last_name: Optional[str] = None) -> Dict[str, Any]:
    """Saves the name of the currently authenticated user.
    
    Args:
        first_name (str): The user's first name
        last_name (str): The user's last name

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the request was successful
            - message (str): The user's full name
            
    Example:
        >>> save_user_name("John", "Doe")
        {'success': True, 'message': 'User name saved successfully as John Doe'}
    """
    global user_name
    user_name = f"{first_name} {last_name}"
    return {"success": True, "message": f"User name saved successfully as {user_name}"}
    

def log_out_fb() -> Dict[str, Any]:
    """Logs out the currently authenticated user from Facebook.
    
    This function will terminate the current Facebook session and require
    re-authentication for subsequent Facebook operations.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the logout was successful
            - message (str): Status message indicating the result
            
    Example:
        >>> log_out_fb()
        {'success': True, 'message': 'You have been logged out of facebook.'}
    """
    return {"success": True, "message": "You have been logged out of facebook."}
