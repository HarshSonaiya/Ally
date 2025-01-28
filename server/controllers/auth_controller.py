import logging
from datetime import datetime, timezone

from fastapi import HTTPException, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse

from pymongo.errors import DuplicateKeyError
from models.user_model import UserModel

from services.auth_service import authservice
from utils.helper import send_response, handle_exception
from config import get_es_client, settings, db_instance

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("authcontroller")


class AuthController:
    def __init__(self):
        self.es_client = get_es_client()
        self.user_collection = db_instance.get_collection(
            settings.MONGO_INITDB_DATABASE, "users"
        )

    async def store_user(self, user_data: dict) -> dict:
        try:
            # Validate user data using Pydantic
            user = UserModel(**user_data)

            # Insert user into MongoDB
            self.user_collection.insert_one(user_data)
            return {"message": "User created successfully", "user": user_data}

        except DuplicateKeyError:
            # If the user already exists, update the last login timestamp
            existing_user = self.user_collection.find_one_and_update(
                {"email": user_data["email"]},
                {
                    "$set": {
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                        "is_new": False,
                        "access_token": user["access_token"],
                        "refresh_token": user["refresh_token"]
                    }
                },
                return_document=True,
            )
            if not existing_user:
                raise HTTPException(
                    status_code=500, detail="Failed to update user data."
                )
            return {
                "message": "User already exists, updated successfully",
                "user": existing_user,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error storing user: {str(e)}")

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
            f"&access_type=offline"
            f"&include_granted_scopes=true"
            f"&prompt=consent"
        )
        return RedirectResponse(google_oauth_url)

    async def google_callback(self, request: Request, response: Response):

        try:
            auth_code = request.query_params.get("code")

            if not auth_code:
                raise HTTPException(
                    status_code=400, detail="Authorization code is required."
                )

            logger.info(f"Login request with code: {auth_code}")

            # Get access token from Google
            token_response = await authservice.get_access_token(auth_code)
            access_token = token_response.get("access_token")
            refresh_token = token_response.get("refresh_token")
            expires_in = token_response.get("expires_in")

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

            # Store records in mongodb and return success message with username
            user_data = {
                "email": email,
                "google_id": google_id,
                "username": user_info.get("name"),
                "profile_picture": user_info.get("picture"),
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in" : expires_in
            }

            user_storage_result = await self.store_user(user_data)
            logger.info(f"User storage result: {user_storage_result}")

            # Redirect to the frontend with the success message in URL query parameters
            # Redirect to the frontend with the success message in URL query parameters
            redirect_url = (
                f"http://localhost:5173/chat"
                f"?message=Authentication+successful"
                f"&username={user_info.get('name')}"
                f"&email={email}"
                f"&profile_picture={user_info.get('picture')}"
                f"&access_token={access_token}"
            )
            
            # Set the refresh token in an HTTP-only cookie
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=60 * 60 * 24 * 30,
            )

            return RedirectResponse(url=redirect_url, headers=response.headers)
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
