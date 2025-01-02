from pymongo import MongoClient
import urllib.parse
from config import settings

class Database:
    def __init__(self):
        username = urllib.parse.quote_plus(settings.MONGO_USERNAME)
        password = urllib.parse.quote_plus(settings.MONGO_PASSWORD)
        try:
            self.client = MongoClient(settings.DATABASE_URL % (username, password))
            conn_info = self.client.server_info()
            print(f"Connected to MongoDB: Version {conn_info.get('version')}")
        except Exception as e:
            raise ConnectionError(f"Unable to connect to MongoDB: {str(e)}")

    def get_database(self, db_name: str):
        return self.client[db_name]

    def get_collection(self, db_name: str, collection_name: str):
        db = self.get_database(db_name)
        return db[collection_name]

# Initialize database instance
db_instance = Database()
