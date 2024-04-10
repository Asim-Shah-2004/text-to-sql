import json
import os
import pymongo
from services.mongo_service import get_mongo_client
from services.sql_service import get_sql_database
from controllers.system_prefix import get_system_prefix
from services.sql_service import get_sql_database
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
    
    
    
    client = get_mongo_client()
    db_mongo = client.Users
    collection = db_mongo.sessions

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
        
    system_prefix = get_system_prefix()

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
    db=get_sql_database(),
    prompt=full_prompt,
    verbose=True,
    agent_type="openai-tools",
    agent_executor_kwargs={
        "memory": memory
    }
)

    
    if user and "chat_history" in user:
        chat_history = user["chat_history"]
    else:
        chat_history = []

    while True:
        query = input("Enter your query: ")

        # Pass both current and previous queries as context
        if chat_history:
            previous_query = chat_history[-1]["input"]
            context = f"{previous_query}\n\n{query}"
        else:
            context = query

        agent_response = agent_executor.invoke({"input": query, "context": context})
        print(agent_response)

        # Store current query in chat history
        chat_history.append({"input": query, "response": agent_response})

        choice = input("Do you want to quit? (y/n): ")
        if choice.lower() == "y":
            break

    collection.update_one({"_id": user["_id"]}, {"$set": {"chat_history": chat_history}})

if __name__ == "__main__":
    main()

