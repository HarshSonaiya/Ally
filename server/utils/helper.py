import logging
import random
import string
import time
import json
from fastapi import HTTPException
from datetime import datetime
import hashlib

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
        "status_code": status_code,
        "message": message,
        "data": data or None
    }
    return response

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

def generate_verification_code():
    """
    Generates a secure verification code that will be sent to the frontend for user verification.

    Returns:
        str: A unique, secure verification code
    """
    # Random string of letters and digits for the verification code
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return code

def get_current_timestamp():
    """
    Helper function to get the current timestamp in milliseconds.

    Returns:
        int: Current timestamp in milliseconds
    """
    return int(time.time() * 1000)

def hash_string(input_string: str):
    """
    Helper function to securely hash strings, e.g., for the verification code.

    Args:
        input_string (str): Input string to hash.

    Returns:
        str: SHA256 hash of the input string.
    """
    return hashlib.sha256(input_string.encode()).hexdigest()
