from system_queries.mySQL import get_relationship_query,get_schema_query
from services.sql_service import get_sql_database,db_name
def get_system_prefix():
    db = get_sql_database()
    dialect = input("Enter the dialect you want the database to be in: ")
    schema = db._execute(get_schema_query(db_name))
    relationships = db._execute(get_relationship_query())
    system_prefix = f"""You are an agent designed to interact with a SQL database.
    Given an input question, create a syntactically correct {dialect} query. just create
    the query dont execute it

    the schema of the database is

    {schema}

    and the relationships are 

    {relationships}

    always use the context and chat_history before making any queries

    """
    
    return system_prefix

