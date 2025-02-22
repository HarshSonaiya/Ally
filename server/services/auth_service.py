from config import settings
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class AuthService:
    
    def __init__(self):
        
        self.GOOGLE_TOKEN_URI = settings.TOKEN_URI
        self.GOOGLE_USER_INFO_URI = settings.USER_INFO_URI 
        self.GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID 
        self.GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET 
        self.REDIRECT_URI = settings.REDIRECT_URI 

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
                raise Exception(f"Token exchange failed: {token_response.text}")
            print(f"Token exchanged successfully {token_response}")
            
            tokens = token_response.json()
            access_token = tokens.get('access_token')
            refresh_token = tokens.get('refresh_token')
            expires_in = tokens.get('expires_in')

            return {
                "access_token":access_token,
                "refresh_token":refresh_token,
                "expires_in":expires_in
            }
        except Exception as e:
            logger.error(f"Error occured: {e}")
            raise e

    async def get_user_info(self, access_token: str) -> dict:
        """
        Get user information like first name, familt name, gmail, etc. from google.

        Args: 
            access_token(str): A unique token to be excehanged to get user information.

        Returns:
            dict: Containing user information like first name, family name, etc. 
        """
        try:
            # Get user info using access token
            headers = {'Authorization': f'Bearer {access_token}'}
            user_info_response = requests.get(self.GOOGLE_USER_INFO_URI, headers=headers)
            
            if user_info_response.status_code != 200:
                raise Exception("Failed to get user info")

            return user_info_response.json()

        except Exception as e:
            logger.error(f"Error while fetching user information: {str(e)}")
            raise e
        