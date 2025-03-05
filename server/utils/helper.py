import logging
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

def send_response(status_code: int, message: str, data: dict = None):
    """
    Standardizes the response sent to the frontend.

    Args:
        status_code (int): HTTP status code
        message (str): A message for the response
        data (dict): Data to be sent with the response (default is None)

    Returns:
        dict: A structured response object
    """
    response = {
        "success": True,
        "message": message,
        "data": data or None
    }
    
    logger.info(response)
    
    return JSONResponse(content=response, status_code=status_code)

def handle_exception(error: Exception, status_code: int = 500):
    """
    Centralizes exception handling. Logs the error and formats the response.

    Args:
        error (Exception): The exception that was raised
        status_code (int): The HTTP status code to return for the error

    Returns:
        dict: A structured error response
    """
    logger.error(f"Error occurred: {str(error)}")
    return send_response(status_code, "An error occurred", data=None)
