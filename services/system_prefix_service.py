from system_queries.mySQL import get_relationship_query,get_schema_query
from services.sql_service import get_sql_database,db_name
def get_system_prefix():# pass inputs here
    db = get_sql_database()
    dialect = input("Enter the dialect you want the database to be in: ") #no inputs in service
    schema = db._execute(get_schema_query(db_name))
    relationships = db._execute(get_relationship_query())
    
    system_prefix = f"""you are an expert {dialect} db developer. Below is the schema and 
    relationship for the same. I will ask you to write more sql queries on top of that.
    Make sure that you will not write any DDL or delete, update queries.
    All the queries has to be of type select. Dont execute these queries 
    just provide us the query .

    the schema of the database is

    {schema}

    and the relationships are 

    {relationships}


    """
    
    return system_prefix

