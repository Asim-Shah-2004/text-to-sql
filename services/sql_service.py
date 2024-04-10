from langchain_community.utilities.sql_database import SQLDatabase
from config.sql_config import DB_USER, DB_PASSWORD, DB_HOST

global_db_connection = None
db_name = None  

def get_sql_database():
    global global_db_connection, db_name
    if global_db_connection:
        return global_db_connection
    else:
        name = input("Enter database name :")
        set_db_name(name)

    try:
        print("Connecting to database...")
        global_db_connection = SQLDatabase.from_uri(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{db_name}")
        return global_db_connection
    except Exception as e:
        print("An error occurred:", e)

# Function to set the database name
def set_db_name(name):
    global db_name
    db_name = name

# Example usage:
# set_db_name("your_db_name")  # Set the database name
# db = get_sql_database()  # Get the database connection
# Now you can use 'db' throughout your program without needing to pass the database name again
