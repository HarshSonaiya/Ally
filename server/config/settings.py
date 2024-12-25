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
        self.USER_INFO_URL = os.getenv("USER_INFO_URL")
        self.WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL_NAME") 
        self.HOST = os.getenv("MAIL_HOST")
        self.PORT = os.getenv("MAIL_PORT")
        self.USERNAME = os.getenv("MAIL_USERNAME")
        self.PASSWORD = os.getenv("MAIL_PASSWORD")
        self.ELASTICSEARCH_HOST = os.getenv("ELASTIC_URL")

settings = AppSettings()
