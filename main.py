import os
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)


def main():
    

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


    # relationship_query = ''

    # try:
    #     relationships = db._execute(relationship_query)
    #     print("relationships fetched successfully.")
    # except Exception as e:
    #     print("An error occurred:", e)

    print("Generating system prompt...")

    system_prefix = f"""You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query.
Only generate queries, don't execute them. The schema of the database is 

{schema}

The relationships in the database are



"""

    # Chunk the entire system prompt
    system_prompt_chunks = [
        system_prefix[i : i + 4096] for i in range(0, len(system_prefix), 4096)
    ]

    # Create system message templates from system prompt chunks
    system_messages = []
    for chunk in system_prompt_chunks:
        system_messages.append(SystemMessage(content=chunk))

    # Create full prompt
    full_prompt = ChatPromptTemplate.from_messages(
        system_messages
        + [
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    agent = create_sql_agent(
        llm=llm,
        db=db,
        prompt=full_prompt,
        verbose=True,
        agent_type="openai-tools",
    )

    while True:
        query = input("Enter your query: ")
        agent.invoke({"input": query})
        choice = input("Do you want to quit? (y/n): ")
        if choice == "y":
            break


if __name__ == "__main__":
    main()
