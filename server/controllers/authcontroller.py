import logging
import time 

from fastapi import Request, HTTPException
from pydantic import BaseModel

from services.authservice import authservice
from config.elasticsearch import get_es_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("authcontroller")

# Define a request body model
class GoogleAuthRequest(BaseModel):
    code: str  # The authorization code sent from the frontend


class AuthController:
    def __init__(self):
        self.es_client = get_es_client()

    async def login(self, google_auth_request: GoogleAuthRequest):
        """
        Endpoint to handle Google login response
        """
        try:
            code = google_auth_request.code

            if not code:
                raise HTTPException(status_code=400, detail="Authorization code is required")

            logger.info(f"Login request with code: {code}")
            # Get user info from Google
            user_info = authservice.process_google_auth(code)

            if not user_info:
                raise HTTPException(status_code=401, detail="Invalid Google authentication code")

            # Extract email and Google ID from user info
            email = user_info.get("email")
            google_id = user_info.get("sub")  # 'sub' is the unique ID from Google

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

    def logout(self, request):
        logging.info(f"Logout request: {request}")
        time.sleep(2)
        return "Bye"