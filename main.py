import os
import pymongo
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)


def main():
    
    
    
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client.Users
    collection = db.sessions

    username = input("Enter your username: ")
    password = input("Enter your password: ")

# Querying the database for the user
    user = collection.find_one({"username": username})

    if user:
    # User exists, now check if the password matches
        if user["password"] == password:
            print("Login successful!")
        else:
            print("Incorrect password.")
    else:
        print("User not found.")    
    
    db_user = "root"
    
    db_host = "localhost"
    db_name = input("Enter the database name: ")
    print("Connecting to database...")
    try:
        db = SQLDatabase.from_uri(
            f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
        )
        print("Connection established successfully.")
    except Exception as e:
        print("An error occurred:", e)

    dialect = input("Enter the dialect you want the database to be in: ")

    schema_query = f"""SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = '{db_name}'  
    ORDER BY TABLE_NAME, ORDINAL_POSITION;"""

    print("Fetching database schema...")

    try:
        schema = db._execute(schema_query)
        print("Schema fetched successfully.")
    except Exception as e:
        print("An error occurred:", e)


    relationship_query = """SELECT 
  `TABLE_SCHEMA`,                          
  `TABLE_NAME`,                            
  `COLUMN_NAME`,                           
  `REFERENCED_TABLE_SCHEMA`,               
  `REFERENCED_TABLE_NAME`,                
  `REFERENCED_COLUMN_NAME`                
FROM
  `INFORMATION_SCHEMA`.`KEY_COLUMN_USAGE`  
WHERE
  `TABLE_SCHEMA` = SCHEMA()                
  AND `REFERENCED_TABLE_NAME` IS NOT NULL;"""

    print("Fetching relationships")

    try:
        relationships = db._execute(relationship_query)
        print("relationships fetched successfully.")
    except Exception as e:
        print("An error occurred:", e)

    print("Generating system prompt...")

    system_prefix = f"""You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query. just create
the query dont execute it
"""

    
    system_prompt_chunks = [
        system_prefix[i : i + 4096] for i in range(0, len(system_prefix), 4096)
    ]

    
    system_messages = []
    for chunk in system_prompt_chunks:
        system_messages.append(SystemMessage(content=chunk))

    
    full_prompt = ChatPromptTemplate.from_messages(
        system_messages
        + [
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    memory = ConversationBufferMemory(
                                input_key="input", 
                                output_key='output',
                                memory_key="chat_history",
                                return_messages= True
                                  )
                                  
    
    agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    prompt=full_prompt,
    verbose=True,
    agent_type="openai-tools",
    )
    
    chat_history = user.get("chat_history", [])
    while True:
        query = input("Enter your query: ")
        # Include chat history as context
        agent_response = agent_executor.invoke({"input":query})
        print(chat_history)
        chat_history.append({"chat": agent_response})
        choice = input("Do you want to quit? (y/n): ")
        if choice == "y":
            break

    collection.update_one({"_id": user["_id"]}, {"$set": {"chat_history": chat_history}})

if __name__ == "__main__":
    main()