import pymongo
from config.mongo_config import MONGO_URL

def get_mongo_client():
    try:
        print("Connecting to mongo DB")
        client = pymongo.MongoClient(MONGO_URL)
        print("Connection established")
        return client
    except Exception as e:
        print("An error occurred:", e)
    