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
    def __init__(self):
        self.GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
        self.GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
        self.REDIRECT_URI = settings.REDIRECT_URI

    def process_google_auth(self, code: str):
        """
        Exchange Google auth code for user details.
        """
        try:
            # Exchange code for access token
            token_response = requests.post(settings.TOKEN_URL, data={
                "code": code,
                "client_id": self.GOOGLE_CLIENT_ID,
                "client_secret": self.GOOGLE_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": 'http://localhost:5173/home'
            })

            if token_response.status_code != 200:
                logger.error(f"Failed to exchange code: {token_response.text}")
                return None
            else:
                logger.info(f"Auth Code:{token_response.json()}")

            access_token = token_response.json().get("access_token")

            # Fetch user details
            user_info_response = requests.get(settings.USER_INFO_URL, headers={
                "Authorization": f"Bearer {access_token}"
            })

            if user_info_response.status_code != 200:
                logger.error(f"Failed to fetch user info: {user_info_response.json()}")
                return None

            return user_info_response.json()

        except Exception as e:
            logger.error(f"Error in process_google_auth: {e}")
            return None
        
authservice = AuthService()