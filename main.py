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
from langchain.agents import create_openai_tools_agent

os.environ['OPENAI_API_KEY'] = "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"

db_user = "root"
db_password = "AsimShah%402751"
db_host = "localhost"
db_name = "pratice"
db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")



system_prefix = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the given tools. Only use the information returned by the tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

USE the information provided here to generete Queries

The database contains the following tables

countries
departments
employees
jobs
locations


The schema of each table is as follows

countries

+--------------+---------------+------+-----+---------+-------+
| Field        | Type          | Null | Key | Default | Extra |
+--------------+---------------+------+-----+---------+-------+
| COUNTRY_ID   | varchar(2)    | NO   | PRI | NULL    |       |
| COUNTRY_NAME | varchar(40)   | YES  |     | NULL    |       |
| REGION_ID    | decimal(10,0) | YES  | MUL | NULL    |       |
+--------------+---------------+------+-----+---------+-------+

departments

+-----------------+--------------+------+-----+---------+-------+
| Field           | Type         | Null | Key | Default | Extra |
+-----------------+--------------+------+-----+---------+-------+
| DEPARTMENT_ID   | decimal(4,0) | NO   | PRI | 0       |       |
| DEPARTMENT_NAME | varchar(30)  | NO   |     | NULL    |       |
| MANAGER_ID      | decimal(6,0) | YES  | MUL | NULL    |       |
| LOCATION_ID     | decimal(4,0) | YES  | MUL | NULL    |       |
+-----------------+--------------+------+-----+---------+-------+

employees

+----------------+--------------+------+-----+---------+-------+
| Field          | Type         | Null | Key | Default | Extra |
+----------------+--------------+------+-----+---------+-------+
| EMPLOYEE_ID    | decimal(6,0) | NO   | PRI | 0       |       |
| FIRST_NAME     | varchar(20)  | YES  |     | NULL    |       |
| LAST_NAME      | varchar(25)  | NO   | MUL | NULL    |       |
| EMAIL          | varchar(25)  | NO   | UNI | NULL    |       |
| PHONE_NUMBER   | varchar(20)  | YES  |     | NULL    |       |
| HIRE_DATE      | date         | NO   |     | NULL    |       |
| JOB_ID         | varchar(10)  | NO   | MUL | NULL    |       |
| SALARY         | decimal(8,2) | YES  |     | NULL    |       |
| COMMISSION_PCT | decimal(2,2) | YES  |     | NULL    |       |
| MANAGER_ID     | decimal(6,0) | YES  | MUL | NULL    |       |
| DEPARTMENT_ID  | decimal(4,0) | YES  | MUL | NULL    |       |
+----------------+--------------+------+-----+---------+-------+

jobs

+------------+--------------+------+-----+---------+-------+
| Field      | Type         | Null | Key | Default | Extra |
+------------+--------------+------+-----+---------+-------+
| JOB_ID     | varchar(10)  | NO   | PRI |         |       |
| JOB_TITLE  | varchar(35)  | NO   |     | NULL    |       |
| MIN_SALARY | decimal(6,0) | YES  |     | NULL    |       |
| MAX_SALARY | decimal(6,0) | YES  |     | NULL    |       |
+------------+--------------+------+-----+---------+-------+

locations

+----------------+--------------+------+-----+---------+-------+
| Field          | Type         | Null | Key | Default | Extra |
+----------------+--------------+------+-----+---------+-------+
| LOCATION_ID    | decimal(4,0) | NO   | PRI | 0       |       |
| STREET_ADDRESS | varchar(40)  | YES  |     | NULL    |       |
| POSTAL_CODE    | varchar(12)  | YES  |     | NULL    |       |
| CITY           | varchar(30)  | NO   | MUL | NULL    |       |
| STATE_PROVINCE | varchar(25)  | YES  | MUL | NULL    |       |
| COUNTRY_ID     | varchar(2)   | YES  | MUL | NULL    |       |
+----------------+--------------+------+-----+---------+-------+

The relationships are

Countries: The countries table likely has a primary key column named COUNTRY_ID 
(which is a character data type of length 2) that relates to other tables through foreign keys. 
For example, the locations table likely has a foreign key column named COUNTRY_ID that references the countries table's primary key. 
This relationship allows associating locations with their corresponding countries.

Departments: The departments table likely has a primary key column named DEPARTMENT_ID 
(which is a number data type) that relates to other tables through foreign keys. 
For example, the employees table likely has a foreign key column named DEPARTMENT_ID that references the departments table's primary key. 
This relationship allows associating employees with their corresponding departments.

Employees: The employees table likely has a primary key column named EMPLOYEE_ID 
(which is a number data type) that relates to other tables through foreign keys. 
The employees table also likely has foreign key columns that reference other tables' primary keys. 
For example, it likely has a foreign key column named DEPARTMENT_ID that references the 
departments table's primary key and a foreign key column named JOB_ID that references the jobs table's primary key. 
These relationships allow associating employees with their corresponding departments and jobs.

Jobs: The jobs table likely has a primary key column named JOB_ID (which is a character data type of length 10) 
that relates to other tables through foreign keys. The employees table likely has a foreign key column named JOB_ID 
that references the jobs table's primary key. This relationship allows associating employees with their corresponding jobs.

Locations: The locations table likely has a primary key column named LOCATION_ID
(which is a number data type) that relates to other tables through foreign keys. 
It also likely has a foreign key column named COUNTRY_ID that references the countries table's primary key.
This relationship allows associating locations with their corresponding countries.

assume corrseponding table name which matches maximum number of column names from the given prompt


DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

IF a delete statement is asked then return you do not have the authorization for this

if there are no DO NOT DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database 
retry queries upto 3 times with diffrent queries.

If the question does not seem related to the database, just return "I don't know" as the answer."""

full_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content=(
                system_prefix
            )
        ),
        HumanMessagePromptTemplate.from_template("{input}"),
        MessagesPlaceholder('agent_scratchpad')
    ]
)


prompt_val = full_prompt.invoke(
    {
        "input": "How many arists are there",
        "top_k": 5,
        "dialect": "mySQL",
        "agent_scratchpad": [],
    }
)

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
agent = create_sql_agent(
    llm=llm,
    db=db,
    prompt=full_prompt,
    verbose=True,
    agent_type="openai-tools",
)

agent.invoke({"input": "average salary of programmer."})
