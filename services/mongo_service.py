import pymongo
from config.mongo_config import MONGO_URL

mongo_client = None

def get_mongo_client():
    global mongo_client
    if mongo_client:
        return mongo_client
    try:
        client = pymongo.MongoClient(MONGO_URL)
        mongo_client = client
        return mongo_client
    except Exception as e:
        print("An error occurred:", e)

def get_sessions():
    client = get_mongo_client()
    db = client.Users
    return db.sessions