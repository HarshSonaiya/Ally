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
    TOKEN_URL = settings.TOKEN_URL
    USER_INFO_URL = settings.USER_INFO_URL
    GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
    REDIRECT_URI = settings.REDIRECT_URI
    
    def __init__(self):
        self.flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.GOOGLE_CLIENT_ID,
                    "client_secret": self.GOOGLE_CLIENT_SECRET,
                    "auth_uri": self.AUTH_URL,
                    "token_uri": self.TOKEN_URL,
                    "redirect_uris": [self.REDIRECT_URI],
                }
            },
            scopes=["openid", "email", "profile"]
        )

    async def get_request_uri(self):
        self.flow.redirect_uri = self.REDIRECT_URI
        auth_url, state = self.flow.authorization_url(prompt='consent', include_granted_scopes='true')
        return auth_url, state

    async def get_user(self, auth_token):
        self.flow.fetch_token(code=auth_token.code)
        credentials = self.flow.credentials
        response = requests.get(self.USER_INFO_URI, headers={"Authorization": f"Bearer {credentials.token}"})
        if response.status_code == 200:
            return response.json()
        logger.error(f"Failed to retrieve user information {response.text} {response.status_code}")
        raise Exception("Failed to retrieve user information") 

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