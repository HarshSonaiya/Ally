import logging
import httpx
from datetime import datetime, timezone
from fastapi import HTTPException, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
from pymongo.errors import DuplicateKeyError
from models.user_model import UserModel
from services import AuthService
from utils.helper import send_response, handle_exception
from config import get_es_client, settings, db_instance

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AuthController:
    def __init__(self):
        self.auth_service = AuthService()
        self.es_client = get_es_client()
        self.user_collection = db_instance.get_collection(
            settings.MONGO_INITDB_DATABASE, "users"
        )

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
        logger.info("Request to signup or lgoin received.")
        return RedirectResponse(google_oauth_url)

    async def google_callback(self, request: Request):
        try:
            auth_code = request.query_params.get("code")
            if not auth_code:
                raise HTTPException(
                    status_code=400, detail="Authorization code is required."
                )

            logger.info(f"Authorization code received from Google. {auth_code}")
            return RedirectResponse(
                url=f"http://localhost:5173?auth_code={auth_code}",
                status_code=303
            )
        except Exception as e:
            logger.error(f"Error in Google auth: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def exchange_token(self, auth_code: str, response: Response):
        """
        Exchanges the authorization code for access token and refresh token and stores the user data.
        """
        try: 
            if not auth_code: 
                raise HTTPException(status_code=400, detail="Authorization Code is required.")
            
            # Exchange auth code for tokens
            token_response = await self.auth_service.get_access_token(auth_code)
            access_token = token_response.get("access_token")
            refresh_token = token_response.get("refresh_token")
            expires_at = token_response.get("expires_at")

            if not access_token or not refresh_token or not expires_at:
                raise HTTPException(status_code=401, detail="Token Exchange failed.")

            logger.info(f"Access and Refresh token received from Google. {access_token} and {refresh_token}")

            # Extract user info from ID token (frontend will decode this too)
            user_info = await self.auth_service.get_user_info(access_token)
            email = user_info.get("email")
            google_id = user_info.get("sub")

            if not email or not google_id:
                raise HTTPException(
                    status_code=400, detail="Incomplete user info from Google"
                )

            logger.info(f"User information received from Google.")
            # Store user records in MongoDB
            user_data = {
                "email": email,
                "username": user_info.get("name"),
                "google_id": google_id,
                "profile_picture": user_info.get("picture"),
                "access_token": access_token,
                "refresh_token": refresh_token,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(f"Storing user data.")
            if await self.store_user(user_data):
                logger.info(f"User data stored succcessfully.")
            else:
                logger.info(f"Failed to store user data.")

            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=False,
                max_age=60 * 60 * 24 * 30,
            )
            data = {
                "access_token": access_token,
                "expires_at": expires_at
                }
            return send_response(200, "Authentication Successfully.", data)
        except Exception as e: 
            logger.error(f"Error exchagning tokens: {e}", exc_info=True)
            return HTTPException(status_code=500, detail=f"Server Error: {e}.")
        
    # async def refresh_token(self, request: Request):
    #     """
    #     Refresh access token using stored refresh token.
    #     """
    #     refresh_token = request.cookies.get("refresh_token")
    #     if not refresh_token:
    #         raise HTTPException(status_code=401, detail="No refresh token found")

    #     try:
    #         new_access_token = await authservice.refresh_access_token(refresh_token)
    #         if new_access_token:
    #             return JSONResponse(content={"access_token": new_access_token})
    #         else:
    #             raise HTTPException(status_code=401, detail="Invalid refresh token")
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=f"Error refreshing token: {str(e)}")

    async def logout(self, request: Request, response: Response):
        """
        Logout user by invalidating refresh token and clearing cookies.
        """
        try:
            # Invalidate the access token
            async with httpx.AsyncClient() as client:
                google_response = await client.post(
                    "https://oauth2.googleapis.com/revoke",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={"token": request.state.access_token},
                )
                if google_response.status_code != 200:
                    raise HTTPException(
                        status_code=400, detail="Error revoking access token."
                    )
            response.delete_cookie(key="refresh_token", path="/", domain="localhost")
            # return JSONResponse(content={"message": "Logout successful."}, status_code=200)
            return send_response(200, "Logout successful.")
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def store_user(self, user_data: dict):
        try:
            user = UserModel(**user_data)
            self.user_collection.update_one(
                {"email": user.email}, {"$set": user.model_dump()}, upsert=True
            )
            return True
        except DuplicateKeyError:
            raise HTTPException(status_code=500, detail="User already exists.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error storing user: {str(e)}")
