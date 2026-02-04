from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
import os

_MONGO_CLIENT: AsyncMongoClient | None = None


def get_mongo_client() -> AsyncMongoClient:
    """
    Returns a singleton AsyncMongoClient
    """
    global _MONGO_CLIENT

    if _MONGO_CLIENT is None:
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise RuntimeError("MONGO_URI not set")

        _MONGO_CLIENT = AsyncMongoClient(
            mongo_uri,
            maxPoolSize=20,
            minPoolSize=5,
            serverSelectionTimeoutMS=5000,
        )

    return _MONGO_CLIENT


def get_database() -> AsyncDatabase:
    """
    Returns the async database instance
    """
    db_name = os.getenv("MONGO_DB_NAME")
    if not db_name:
        raise RuntimeError("MONGO_DB_NAME not set")

    client = get_mongo_client()
    return client[db_name]
