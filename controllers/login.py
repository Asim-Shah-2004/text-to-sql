from services.mongo_service import get_mongo_client

def login(use_defaults=False):
    client = get_mongo_client()
    db = client.Users
    collection = db.sessions
    
    if use_defaults:
        username = "test"
        password = "abcd"
    else:
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
