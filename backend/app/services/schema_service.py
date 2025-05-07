
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.database import get_db
from fastapi import Depends



def get_database_schema(db: Session = Depends(get_db)) -> str:
    # Step 1: Fetch table names
    table_query = text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    result = db.execute(table_query)
    tables = [row[0] for row in result]

    schema_output = []

    # Step 2: Fetch columns for each table
    for table in tables:
        column_query = text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = :table_name
            ORDER BY ordinal_position;
        """)
        columns_result = db.execute(column_query, {"table_name": table})
        columns = [f"{col[0]} ({col[1].upper()})" for col in columns_result]           
        schema_output.append(f"Table: {table}, Columns: {', '.join(columns)}")

    return "\n".join(schema_output)








    


