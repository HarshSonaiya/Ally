import logging
import time 

from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse

from models.google_auth_req import GoogleAuthRequest

from services.auth_service import authservice
# from config.elastic_search import get_es_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("authcontroller")

class AuthController:
    def __init__(self):
        # self.es_client = get_es_client()
        pass

    async def google_auth(self, google_auth_request: GoogleAuthRequest):
        try:
            code = google_auth_request.code

            if not code:
                raise HTTPException(status_code=400, detail="Authorization code is required")
            logger.info(f"Login request with code: {code}")

            # Get user info from Google
            external_user = await authservice.get_user(code)
            
            logger.info(f"External user: {external_user}")
            if not external_user:
                raise HTTPException(status_code=401, detail="Google authentication failed.")

            # Extract email and Google ID from user info
            email = external_user.get("email")
            google_id = external_user.get("sub")  # 'sub' is the unique ID from Google
            
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
                external_user["google_id"] = google_id
                external_user["created_at"] = int(time.time() * 1000)
                external_user["last_login"] = int(time.time() * 1000)
                self.es_client.index(index="users", id=google_id, document=external_user)

            return {"message": "Authentication successful", "user": external_user}

        except Exception as e:
            logger.error(f"Error in Google auth: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def login_redirect(self, auth_provider: str):
        
        logger.info(f"Redirecting to Google login: {auth_provider}")
        logger.info(f"Redirecting to Google login: {request_uri}")
        if auth_provider == "google-oidc":
            request_uri, state_csrf_token = await authservice.get_request_uri()
            response = RedirectResponse(url=request_uri)
            response.set_cookie(key="state", value=f"Bearer {state_csrf_token}", httponly=True)
            return response
    
        return JSONResponse(content={"error": "Unsupported provider"}, status_code=400)

    async def google_login_callback(self, google_auth_request: GoogleAuthRequest):
        """
        Endpoint to handle Google login response
        """
        try:
            code = google_auth_request.code

            if not code:
                raise HTTPException(status_code=400, detail="Authorization code is required")
            logger.info(f"Login request with code: {code}")

            # Get user info from Google
            external_user = authservice.get_user(google_auth_request)
            if not external_user:
                raise HTTPException(status_code=401, detail="Google authentication failed.")

            # Extract email and Google ID from user info
            email = external_user.get("email")
            google_id = external_user.get("sub")  # 'sub' is the unique ID from Google

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
                external_user["google_id"] = google_id
                external_user["created_at"] = int(time.time() * 1000)
                external_user["last_login"] = int(time.time() * 1000)
                self.es_client.index(index="users", id=google_id, document=external_user)

            return {"message": "Authentication successful", "user": external_user}

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
            response.delete_cookie(key="access_token")  # Remove the token from the cookie
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
                user = authservice.verify_token(access_token)  # Verify the token
                if user:
                    return JSONResponse(content={"userLoggedIn": True, "userName": user["username"]})
            except Exception:
                pass

        return JSONResponse(content={"userLoggedIn": False}, status_code=200)