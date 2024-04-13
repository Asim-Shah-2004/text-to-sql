import os
from controllers.login import login
from services.agent_executor_service import get_agent_executor
from services.mongo_service import get_sessions

def main():
     #put in config
    #put mongo and sql in db folder
    #make prompt folder
    user = login()
    collection = get_sessions()
    agent_executor = get_agent_executor()
    
    if user and "chat_history" in user:
        chat_history = user["chat_history"]
    else:
        chat_history = []

    while True:
        query = input("Enter your query: ")
        if chat_history:
            previous_query = chat_history[-1]["input"]
            context = f"{previous_query}\n\n{query}"
        else:
            context = query

        agent_response = str(agent_executor.invoke({"input": query, "context": context}))
        # print(agent_response)

        chat_history.append({"input": query, "response": agent_response})

        choice = input("Do you want to quit? (y/n): ")
        if choice.lower() == "y":
            break
    
    collection.update_one({"_id": user["_id"]}, {"$set": {"chat_history": chat_history}})

if __name__ == "__main__":
    main()
