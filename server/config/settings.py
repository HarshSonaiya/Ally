import os 

from dotenv import load_dotenv

class AppSettings:
    """
    A class to store the application settings
    """

    def __init__(self):
        load_dotenv()
        self.ELASTIC_URL = os.getenv("ELASTIC_URL")
        self.GOOGLE_CLIENT_ID = os.getenv("CLIENT_ID")
        self.GOOGLE_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        self.TOKEN_URL = os.getenv("TOKEN_URL")
        self.AUTH_URL = os.getenv("AUTH_URL")  
        self.REDIRECT_URI = os.getenv("REDIRECT_URI")

settings = AppSettings()