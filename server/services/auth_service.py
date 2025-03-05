from config import settings
import requests
import logging
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta
from pymongo.errors import DuplicateKeyError
from models.user_model import UserModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class AuthService:
    
    def __init__(self, mongo_client):
        
        self.GOOGLE_TOKEN_URI = settings.TOKEN_URI
        self.GOOGLE_USER_INFO_URI = settings.USER_INFO_URI 
        self.GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID 
        self.GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET 
        self.REDIRECT_URI = settings.REDIRECT_URI 
        self.user_collection = mongo_client[settings.MONGO_INITDB_DATABASE][settings.USERS_COLLECTION]

    async def store_user(self, user_info: dict):
        """Stores the users records in the MongoDB collection."""
        try:
            user_data = {
                "email": user_info.get("email"),
                "username": user_info.get("name"),
                "google_id": user_info.get("sub"),
                "profile_picture": user_info.get("picture"),
                "access_token": user_info.get("access_token"),
                "refresh_token": user_info.get("refresh_token"),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            user = UserModel(**user_data)
            self.user_collection.update_one(
                {"email": user.email}, {"$set": user.model_dump()}, upsert=True
            )
            return True
        except DuplicateKeyError:
            raise HTTPException(status_code=500, detail="User already exists.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error storing user: {str(e)}")
    
    async def get_user_info(self, auth_code: str) -> dict:
        """
        Get user information like first name, familt name, gmail, etc. from google.

        Args: 
            access_token(str): A unique token to be excehanged to get user information.

        Returns:
            dict: Containing user information like first name, family name, etc. 
        """
        try:
            # Exchange auth_code for access tokens
            token_response = await self.get_access_token(auth_code)
            access_token = token_response.get("access_token")

            if not access_token: 
                raise HTTPException(status_code=401, detail="Token Exchange failed.")
            
            # Get user info using access token
            headers = {'Authorization': f'Bearer {access_token}'}
            user_info_response = requests.get(self.GOOGLE_USER_INFO_URI, headers=headers)
            
            if user_info_response.status_code == 200:
                user_info = user_info_response.json()  # Convert response to dict
                user_info.update(token_response)  # Merge user info with token response
            else:
                raise Exception("Failed to fetch user info from Google")

            return user_info

        except Exception as e:
            logger.error(f"Error while fetching user information: {str(e)}")
            raise e
  
    async def get_access_token(self, auth_code: str) -> dict:
        """
        Exchange authentication code for access token.

        Args:
            auth_code (str): The authorization code received from frontend.
    
        Returns: 
            dict: A unique google token to user information from google. 
        """
        try:
            # Exchange auth code for tokens
            token_data = {
                'code': auth_code,
                'client_id': self.GOOGLE_CLIENT_ID,
                'client_secret': self.GOOGLE_CLIENT_SECRET,
                'redirect_uri': self.REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
            
            token_response = requests.post(self.GOOGLE_TOKEN_URI, data=token_data)
            if token_response.status_code != 200:
                raise HTTPException(status_code=401, detail=f"Token exchange failed: {token_response.text}")
            
            token_created_at = datetime.now(timezone.utc)
            print(f"Token exchanged successfully {token_response}")
            
            tokens = token_response.json()
            logger.info(f"Tokens: {tokens}")
            access_token = tokens.get('access_token')
            refresh_token = tokens.get('refresh_token')
            expires_in = tokens.get('expires_in')
            expires_at = (token_created_at + timedelta(seconds=expires_in)).isoformat() # Convert to string.

            return {
                "access_token":access_token,
                "refresh_token":refresh_token,
                "expires_at":expires_at
            }
        except Exception as e:
            logger.error(f"Error occured: {e}")
            raise e
      