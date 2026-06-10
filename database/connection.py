from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from database.config import MONGODB_URI, MONGODB_DB_NAME

client = None
db = None


def connect_to_mongo():
    global client, db

    try:
        client = MongoClient(MONGODB_URI)
        client.admin.command("ping")
        db = client[MONGODB_DB_NAME]
        print("Connected to MongoDB successfully!")
        return db
    except ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")
        return None


def get_database():
    return db