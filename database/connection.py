from pymongo import AsyncMongoClient
from database.config import MONGODB_URI, MONGODB_DB_NAME


client = None
db = None


async def connect_to_mongo():
    global client, db

    try:
        client = AsyncMongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        await client.admin.command("ping")
        db = client[MONGODB_DB_NAME]
        print("Connected to MongoDB successfully!")
        return db
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        db = None
        return None


def get_database():
    return db


async def close_mongo_connection():
    global client, db

    if client is not None:
        client.close()
        client = None
        db = None
        print("MongoDB connection closed.")