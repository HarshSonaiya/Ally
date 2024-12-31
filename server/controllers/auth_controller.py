import logging
import time 

from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse

from models.pydantic_models import GoogleAuthRequest

from services.auth_service import authservice
from utils.helper import send_response, handle_exception
from config import get_es_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("authcontroller")

class AuthController:
    def __init__(self):
        self.es_client = get_es_client()
        pass

    async def google_auth(self, google_auth_request: GoogleAuthRequest):
        """
        Handle Google Authentication request by exchanging authorization and access tokens
        and fetch user information, to be stored in elastic.

        Args:
            GoogleAuthRequest: Accept the authentication code (str) from frontend.

        Returns:
            dict: A structured response containing success message, user data, and a unique verification code. 
        """
        try:
            auth_code = google_auth_request.code

            if not auth_code:
                raise HTTPException(status_code=400, detail="Authorization code is required")
            
            logger.info(f"Login request with code: {auth_code}")
            
            # Get access token from Google
            access_token = await authservice.get_access_token(auth_code).get("access_token")
            
            logger.info(f"Access token received : {access_token}")
            if not access_token:
                raise HTTPException(status_code=401, detail="Token Exchange failed.")

            # Get user information from Google
            user_info = await authservice.get_user_info(access_token)

            if not user_info:
                raise HTTPException(status_code=401, detail="No user information received.")

            # Extract email and Google ID from user info
            email = user_info.get("email")
            google_id = user_info.get("sub")  
            
            logger.info(f"Email: {email}, Google ID: {google_id}")

            if not email or not google_id:
                raise HTTPException(status_code=400, detail="Incomplete user info from Google")

            # Check if user exists in Elasticsearch
            query = {
                "query": {
                    "term": {"email": email}
                }
            }
            response = self.es_client.search(index="users", body=query)
            user_exists = response["hits"]["total"]["value"] > 0

            if user_exists:
                logger.info(f"User found: {email}")
                user = response["hits"]["hits"][0]["_source"]
                # Update last login timestamp
                user["last_login"] = int(time.time() * 1000)
                self.es_client.index(index="users", id=user["google_id"], document=user)
            else:
                logger.info(f"New user sign-up: {email}")
                # Add new user to Elasticsearch
                user_info["google_id"] = google_id
                user_info["created_at"] = int(time.time() * 1000)
                user_info["last_login"] = int(time.time() * 1000)
                self.es_client.index(index="users", id=google_id, document=user_info)

            return {"message": "Authentication successful", "user": user_info}

        except Exception as e:
            logger.error(f"Error in Google auth: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def logout(self, request: Request):
        """
        Handles the logout request.
        """
        try:
            logger.info(f"Logout request from {request.client.host}")
            response = JSONResponse(content={"message": "Logged out successfully"})
            response.delete_cookie(key="access_token")  
            return response
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def user_session_status(self, request: Request):
        """
        Check if the user is logged in based on the auth token.
        """
        access_token = request.cookies.get("access_token")
        if access_token:
            try:
                user = authservice.verify_token(access_token)  
                if user:
                    return JSONResponse(content={"userLoggedIn": True, "userName": user["username"]})
            except Exception:
                pass

        return JSONResponse(content={"userLoggedIn": False}, status_code=200)
    
auth_controller = AuthController()