import logging
from datetime import datetime, timezone
from fastapi import HTTPException, Request, Response, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from pymongo.errors import DuplicateKeyError
from models.user_model import UserModel
from services.auth_service import authservice
from utils.helper import send_response, handle_exception
from config import get_es_client, settings, db_instance

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("authcontroller")

class AuthController:
    def __init__(self):
        self.es_client = get_es_client()
        self.user_collection = db_instance.get_collection(settings.MONGO_INITDB_DATABASE, "users")

    async def google_auth(self):
        """
        Redirects user to Google OAuth consent screen.
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
                raise HTTPException(status_code=400, detail="Authorization code is required.")

            logger.info(f"Login request with code: {auth_code}")

            # Exchange auth code for tokens
            token_response = await authservice.get_access_token(auth_code)
            access_token = token_response.get("access_token")
            refresh_token = token_response.get("refresh_token")
            id_token = token_response.get("id_token")

            if not access_token:
                raise HTTPException(status_code=401, detail="Token Exchange failed.")

            # Extract user info from ID token (frontend will decode this too)
            user_info = await authservice.get_user_info(id_token)
            email = user_info.get("email")
            google_id = user_info.get("sub")

            if not email or not google_id:
                raise HTTPException(status_code=400, detail="Incomplete user info from Google")

            # Store user records in MongoDB
            user_data = {
                "email": email,
                "google_id": google_id,
                "username": user_info.get("name"),
                "profile_picture": user_info.get("picture"),
                "access_token": access_token,
                "refresh_token": refresh_token,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }

            await self.store_user(user_data)

            # Set refresh token in HTTP-only cookie
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=60 * 60 * 24 * 30,  # 30 days
            )

            return JSONResponse(content={"message": "Authentication successful", "id_token": id_token, "access_token": access_token})
        except Exception as e:
            logger.error(f"Error in Google auth: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def refresh_token(self, request: Request):
        """
        Refresh access token using stored refresh token.
        """
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="No refresh token found")
        
        try:
            new_access_token = await authservice.refresh_access_token(refresh_token)
            if new_access_token:
                return JSONResponse(content={"access_token": new_access_token})
            else:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error refreshing token: {str(e)}")

    async def logout(self):
        """
        Logout user by invalidating refresh token and clearing cookies.
        """
        try:
            response = JSONResponse(content={"message": "Logged out successfully"})
            response.delete_cookie(key="refresh_token")
            return response
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def store_user(self, user_data: dict):
        try:
            user = UserModel(**user_data)
            self.user_collection.update_one(
                {"email": user_data["email"]},
                {"$set": user_data},
                upsert=True
            )
        except DuplicateKeyError:
            raise HTTPException(status_code=500, detail="User already exists.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error storing user: {str(e)}")

auth_controller = AuthController()
