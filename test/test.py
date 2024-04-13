import re
import os
from openai import OpenAI
from langchain_community.utilities.sql_database import SQLDatabase

def generate_sample_questions(schema, relationships):
    questions = []
    prompt = f"""
    You are an SQL query tester. You are provided with the schema and relationships of a database.
    Your task is to generate 10 challenging questions to test an SQL query generator.
    
    The schema is:
    {schema}
    
    The relationships are:
    {relationships}
    
    end every question with double new line escape character
    """
    os.environ["OPENAI_API_KEY"] = "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"
    
    client = OpenAI(
        api_key="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",
    )
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}]
    )
    
    questions = re.findall(r'\d+\.\s(.+?)\n\n', response.choices[0].message.content.strip())
    
    return questions

def generete_and_execute_queries(schema, relationships, sample_questions, db):
    system_prompt = f"""
    You are an expert MYSQL db developer. Below is the schema and 
    relationship for the same. I want you to generete syntatically correct MYSQL queries.
    Make sure that you will not write any DDL or delete, update queries.
    All the queries have to be of type select. Don't execute these queries 
    just provide us the query.

    The schema of the database is:

    {schema}

    and the relationships are:

    {relationships}
    """
    
    client = OpenAI(
        api_key="",
    )
    
    for i, question in enumerate(sample_questions, 1):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
        )
        query = response.choices[0].message.content.strip()
        print(f"Query {i}:")
        print(query)
        
        print("Output:")
        output = db._execute(query)
        print(output)
        print("\n")

def test():
    DB_USER = "root"
    DB_HOST = "localhost"
    name = input("Enter database name: ")
    db = SQLDatabase.from_uri(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{name}")
    schema = db._execute(f"""SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = '{name}'  
    ORDER BY TABLE_NAME, ORDINAL_POSITION;""")
    
    relationships = db._execute("""SELECT 
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
        AND `REFERENCED_TABLE_NAME` IS NOT NULL;""")
     
    sample_questions = generate_sample_questions(schema, relationships)    
    print("Generated Sample Questions are:")
    for i, question in enumerate(sample_questions, 1):
        print(f"{i}. {question}")
    generete_and_execute_queries(schema, relationships, sample_questions, db)

test()
