
from services.mongo_service import get_mongo_client


def login():
    
    client = get_mongo_client()
    db = client.Users
    collection = db.sessions
    
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    user = collection.find_one({"username": username})

    if user:
        if user["password"] == password:
            print("Login successful!")
            return user
        else:
            print("Incorrect password.")
            return None
    else:
        print("User not found.")    
        return None
    

