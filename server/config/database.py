from pymongo import MongoClient
import urllib.parse
import pymongo
from settings import settings

username = urllib.parse.quote_plus(settings.MONGO_USERNAME)
password = urllib.parse.quote_plus(settings.MONGO_PASSWORD)

client = MongoClient(settings.DATABASE_URL % (username, password))

try:
    conn = client.server_info()
    print(f'Connected to MongoDB {conn.get("version")}')
except Exception:
    print("Unable to connect to the MongoDB server.")

db = client[settings.MONGO_INITDB_DATABASE]
User = db.users
User.create_index([("email", pymongo.ASCENDING)], unique=True)

