

from sqlalchemy.orm import Session
from sqlalchemy import text
import re

def execute_validated_sql(db: Session, sql_query: str):

    stripped_query = sql_query.strip()
    upper_query = stripped_query.upper()

    # if not upper_query.startswith("SELECT"):
    #     raise ValueError("Only SELECT statements are allowed.")

    # Ensure there are columns after SELECT DISTINCT
    # if "DISTINCT" in upper_query and "SELECT" in upper_query:
    #     if "FROM" not in upper_query or len(upper_query.split("FROM")[0].strip().split()) == 1:
    #         raise ValueError("SELECT DISTINCT must have at least one column specified.")
    # Find everything between ```SQL and ```
    match = re.search(r"```SQL(.*?)```", upper_query, re.DOTALL | re.IGNORECASE)
    
    if match:
        sql_block = match.group(1)
        
        # Remove lines that start with '--' (comments)
        sql_lines = sql_block.splitlines()
        query_lines = [line.strip() for line in sql_lines if not line.strip().startswith('--')]
        
        # Join back into a single query
        clean_query = " ".join(query_lines)
        upper_query = clean_query.strip()
    else:
        return ""
    print("============================upper query==================================")
    print(upper_query)
    print("==========================================================================")


    # Ensure only one SELECT statement (no multiple semicolons)
    if upper_query.count(";") > 1:
        raise ValueError("Only a single SELECT statement is allowed.")

    # Check for forbidden keywords
    forbidden_keywords = ["DELETE", "UPDATE", "INSERT", "DROP", "TRUNCATE", "GRANT", "REVOKE"]
    pattern = r'\b(' + '|'.join(forbidden_keywords) + r')\b'
    if re.search(pattern, upper_query):
        raise ValueError("Query contains forbidden keywords.")

    # Ensure query has FROM clause
    if "FROM" not in upper_query:
        raise ValueError("Query must include a FROM clause.")

    try:
        result = db.execute(text(upper_query))
        rows = result.fetchall()
        columns = result.keys()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        raise RuntimeError(f"Query execution failed: {str(e)}")
    
    