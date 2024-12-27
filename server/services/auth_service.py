from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from config.settings import settings
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class AuthService:
    AUTH_URL = settings.AUTH_URL

    
    def __init__(self):
        
        self.GOOGLE_TOKEN_URI = settings.TOKEN_URL or "https://oauth2.googleapis.com/token"
        self.GOOGLE_USER_INFO_URI = settings.USER_INFO_URL or "https://www.googleapis.com/oauth2/v3/userinfo"
        self.GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID 
        self.GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET 
        self.REDIRECT_URI = settings.REDIRECT_URI or "http://localhost:5173"

    async def get_request_uri(self):
        self.flow.redirect_uri = self.REDIRECT_URI
        auth_url, state = self.flow.authorization_url(prompt='consent', include_granted_scopes='true')
        return auth_url, state

    async def get_user(self, auth_code: str):
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
                raise Exception(f"Token exchange failed: {token_response.text}")
            
            tokens = token_response.json()
            access_token = tokens.get('access_token')

            # Get user info using access token
            headers = {'Authorization': f'Bearer {access_token}'}
            user_info_response = requests.get(self.GOOGLE_USER_INFO_URI, headers=headers)
            
            if user_info_response.status_code != 200:
                raise Exception("Failed to get user info")

            return user_info_response.json()

        except Exception as e:
            logger.error(f"Auth error: {str(e)}")
            return None


    # def process_google_auth(self, code: str):
    #     """
    #     Exchange Google auth code for user details.
    #     """
    #     try:
    #         # Exchange code for access token
    #         token_response = requests.post(settings.TOKEN_URL, data={
    #             "code": code,
    #             "client_id": self.GOOGLE_CLIENT_ID,
    #             "client_secret": self.GOOGLE_CLIENT_SECRET,
    #             "grant_type": "authorization_code",
    #             "redirect_uri": self.REDIRECT_URI
    #         },
    #         headers={"Content-Type": "application/x-www-form-urlencoded"},
    #     )

    #         if token_response.status_code != 200:
    #             logger.error(f"Failed to exchange code: {token_response.text}")
    #             return None
    #         else:
    #             logger.info(f"Auth Code:{token_response.json()}")

    #         access_token = token_response.json().get("access_token")

    #         # Fetch user details
    #         user_info_response = requests.get(
    #             settings.USER_INFO_URL, 
    #             headers={"Authorization": f"Bearer {access_token}"}
    #         )

    #         if user_info_response.status_code != 200:
    #             logger.error(f"Failed to fetch user info: {user_info_response.json()}")
    #             return None

    #         return user_info_response.json()

    #     except Exception as e:
    #         logger.error(f"Error in process_google_auth: {e}")
    #         return None
        
authservice = AuthService()