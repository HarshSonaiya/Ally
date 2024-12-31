import logging
import time

from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse

from models.pydantic_models import GoogleAuthRequest

from services.auth_service import authservice
from utils.helper import send_response, handle_exception
from config import get_es_client, settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("authcontroller")


class AuthController:
    def __init__(self):
        self.es_client = get_es_client()

    async def google_auth(self):
        """
        Redirects the user to Google's OAuth 2.0 authorization endpoint.
        """
        google_oauth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?response_type=code"
            f"&client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={settings.REDIRECT_URI}"
            f"&scope=openid email profile"
        )
        return RedirectResponse(google_oauth_url)

    async def google_callback(self, request: Request):

        try:
            auth_code = request.query_params.get("code")

            if not auth_code:
                raise HTTPException(
                    status_code=400, detail="Authorization code is required."
                )

            logger.info(f"Login request with code: {auth_code}")

            # Get access token from Google
            access_token_response = await authservice.get_access_token(auth_code)
            access_token = access_token_response.get("access_token")

            logger.info(f"Access token received : {access_token}")
            if not access_token:
                raise HTTPException(status_code=401, detail="Token Exchange failed.")

            # Get user information from Google
            user_info = await authservice.get_user_info(access_token)

            if not user_info:
                raise HTTPException(
                    status_code=401, detail="No user information received."
                )

            # Extract email and Google ID from user info
            email = user_info.get("email")
            google_id = user_info.get("sub")

            logger.info(f"Email: {email}, Google ID: {google_id}")

            if not email or not google_id:
                raise HTTPException(
                    status_code=400, detail="Incomplete user info from Google"
                )

            # Store records in mongodb and return success message with username -> pending.

            # Redirect to the frontend with the success message in URL query parameters
            redirect_url = f"http://localhost:5173/home?message=Authentication+successful"
            return RedirectResponse(url=redirect_url)
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
                    return JSONResponse(
                        content={"userLoggedIn": True, "userName": user["username"]}
                    )
            except Exception:
                pass

        return JSONResponse(content={"userLoggedIn": False}, status_code=200)


auth_controller = AuthController()
