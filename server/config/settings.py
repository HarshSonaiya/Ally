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
        self.AUTH_URL = os.getenv("AUTH_URL")
        self.TOKEN_URI = os.getenv("TOKEN_URI")  
        self.REDIRECT_URI = os.getenv("REDIRECT_URI")
        self.USER_INFO_URI = os.getenv("USER_INFO_URI")

        self.HOST = os.getenv("MAIL_HOST")
        self.PORT = os.getenv("MAIL_PORT")
        self.USERNAME = os.getenv("MAIL_USERNAME")
        self.PASSWORD = os.getenv("MAIL_PASSWORD")

        self.GROQ_LLM_NAME = os.getenv("GROQ_MODEL_NAME")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL_NAME") 
        self.DIARIZATION_MODEL_NAME = os.getenv("DIARIZATION_MODEL_NAME")
        self.HUGGING_FACE_ACCESS_TOKEN = os.getenv("HUGGING_FACE_ACCESS_TOKEN")
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

settings = AppSettings()
