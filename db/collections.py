from pymongo.asynchronous.collection import AsyncCollection
from .mongo import get_database


def users_collection() -> AsyncCollection:
    return get_database()["users"]

def refresh_tokens_collection() -> AsyncCollection:
    return get_database()["refresh_tokens"]

def event_collection() -> AsyncCollection:
    return get_database()["events"]