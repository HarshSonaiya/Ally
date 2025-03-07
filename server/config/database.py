from pymongo import MongoClient
from elasticsearch import Elasticsearch
import urllib.parse
from config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("database")

class DatabaseManager:
    def __init__(self):
        self.mongo_client = None
        self.es_client = None
    
    def connect(self):
        try: 

            username = urllib.parse.quote_plus(settings.MONGO_USERNAME)
            password = urllib.parse.quote_plus(settings.MONGO_PASSWORD)
            self.mongo_client = MongoClient(settings.DATABASE_URL % (username, password))
            self.mongo_client.admin.command("ping")
            conn_info = self.mongo_client.server_info()
            logger.info(f"Connected to MongoDB: Version {conn_info.get('version')}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise Exception(f"Unable to connect to MongoDB: {str(e)}")
        
        try:
            self.es_client = Elasticsearch(settings.ELASTIC_URL)
            # if not self.es_client.ping():
            #     raise Exception("Elasticsearch is unreachable")
            logger.info("Elasticsearch connected successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            raise Exception("Elasticsearch is unavailable")

    def close(self):

        if self.mongo_client:
            self.mongo_client.close()
            logger.info("MongoDB connection closed.")
        if self.es_client:
            self.es_client.close()
            logger.info("Elasticsearch connection closed.")

    def get_mongo_client(self):
        if not self.mongo_client:
            raise Exception("MongoDB client is not initialized")
        return self.mongo_client

    def get_es_client(self):
        if not self.es_client:
            raise Exception("Elasticsearch client is not initialized")
        return self.es_client

# Create a database manager
db_manager = DatabaseManager()
