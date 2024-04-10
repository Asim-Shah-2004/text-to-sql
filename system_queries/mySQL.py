def get_schema_query(db_name):
    return f"""SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = '{db_name}'  
    ORDER BY TABLE_NAME, ORDINAL_POSITION;"""

def get_relationship_query():
    return """SELECT 
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