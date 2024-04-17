# import os
# import argparse
# from controllers.login import login
# from services.agent_executor_service import get_agent_executor
# from services.mongo_service import get_sessions

# def main():
#     parser = argparse.ArgumentParser(description="Your script description here")
#     parser.add_argument("-y", "--yes", action="store_true", help="Use default answers")
#     args = parser.parse_args()
#     os.environ["OPENAI_API_KEY"] = "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" #put in config
#     #put mongo and sql in db folder
#     #make prompt folder
#     user = login(args.yes)
#     collection = get_sessions()
#     agent_executor = get_agent_executor()
    
#     if user and "chat_history" in user:
#         chat_history = user["chat_history"]
#     else:
#         chat_history = []

#     while True:
#         query = input("Enter your query: ")
#         if chat_history:
#             previous_query = chat_history[-1]["input"]
#             context = f"{previous_query}\n\n{query}"
#         else:
#             context = query

#         agent_response = str(agent_executor.invoke({"input": query, "context": context}))
#         # print(agent_response)

#         chat_history.append({"input": query, "response": agent_response})

#         choice = input("Do you want to quit? (y/n): ")
#         if choice.lower() == "y":
#             break
    
#     collection.update_one({"_id": user["_id"]}, {"$set": {"chat_history": chat_history}})

# if __name__ == "__main__":
#     main()

import os
import argparse
from fuzzywuzzy import fuzz
from controllers.login import login
from services.agent_executor_service import get_agent_executor
from services.mongo_service import get_sessions
from langchain.callbacks.base import BaseCallbackHandler


def main():
    parser = argparse.ArgumentParser(description="Your script description here")
    parser.add_argument("-y", "--yes", action="store_true", help="Use default answers")
    args = parser.parse_args()
    
    #put mongo and sql in db folder
    #make prompt folder
    user = login(args.yes)
    collection = get_sessions()
    agent_executor = get_agent_executor()
    
    if user and "chat_history" in user:
        chat_history = user["chat_history"]
    else:
        chat_history = []

    # Import questions and expected outputs
    with open("sample_questions.txt", "r", encoding='utf-8') as file:
        lines = file.readlines()
        sample_questions = []
        expected_outputs = []
        i = 0
        while i < len(lines):
            if lines[i].startswith("Question"):
                sample_questions.append(lines[i].split(":")[1].strip())
            elif lines[i].startswith("Expected Output"):
                expected_output = lines[i+1].strip()
                # Check if expected output is not empty and is not "None"
                if expected_output and expected_output != "None":
                    # Parse the expected output string into Python object
                    expected_output = eval(expected_output)
                else:
                    # If "None", set expected output to None
                    expected_output = None
                expected_outputs.append(expected_output)
            i += 1

    for i, question in enumerate(sample_questions, 1):
        # Prepare context with previous query and current question
        if chat_history:
            previous_query = chat_history[-1]["input"]
            context = f"{previous_query}\n\n{question}"
        else:
            context = question

        # Get response from SQL agent
        
        agent_response = str(agent_executor.invoke({"input": question, "context": context}))
        
        # Check if expected output exists for the current question
        if len(expected_outputs) >= i:
            # Calculate similarity between response and expected output
            print(agent_response)
            similarity_score = fuzz.partial_ratio(agent_response, str(expected_outputs[i - 1]))
            # Print match status based on similarity score
            if similarity_score >= 90:  # Adjust the threshold as needed
                print(f"Query {i}: MATCH")
            else:
                print(f"Query {i}: NO MATCH (Similarity Score: {similarity_score})")
        else:
            print(f"No expected output found for question {i}")

        # Append to chat history
        chat_history.append({"input": question, "response": agent_response})

    # Update chat history in the database
    collection.update_one({"_id": user["_id"]}, {"$set": {"chat_history": chat_history}})

if __name__ == "__main__":
    main()
