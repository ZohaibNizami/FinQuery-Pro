# from fastapi import Depends, HTTPException
# import google.generativeai as genai
# from backend.app.database import get_db 
# from sqlalchemy.orm import Session
# from backend.app.services.schema_service import get_database_schema
# from backend.app.core.config import GEMINI_API_KEY

# genai.configure(api_key=GEMINI_API_KEY)



    

# def generate_sql_from_nl(natural_language_query: str, db: Session = Depends(get_db)) -> str:
#     try:
#         schema = get_database_schema(db)



#         prompt = f"""
# You are an advanced PostgreSQL Query Generator AI assistant.

# ---

# **Your Goal:**  
# Generate a **single, valid, secure, and optimized PostgreSQL `SELECT` query** based **strictly on the provided database schema** and the user's question.

# ---

# **Context:**
# You have access only to the schema described below.  
# Do NOT assume extra columns, tables, relationships, or data.  
# This is a READ-ONLY environment — only SELECT queries are allowed.

# ---

# **Database Schema:**
# {schema}

# ---

# **User Question:**
# {natural_language_query}

# ---

# **Instructions:**

# 1. **SELECT-Only:**  
#    Only generate a PostgreSQL `SELECT` query.  
#    Do NOT generate `INSERT`, `UPDATE`, `DELETE`, `DROP`, `CREATE`, or `DO` blocks.

# 2. **Schema-Strict:**  
#    Use only the provided tables, columns, and data types.

# 3. **Clarity & Performance:**  
#    - Use specific column names instead of `SELECT *`.  
#    - Use aliases (`AS`) where helpful.  
#    - Apply filters (`WHERE`), sorting (`ORDER BY`), or aggregation (`GROUP BY`) as needed.

# 4. **No Side Effects:**  
#    Do not include comments that suggest side-effects (e.g., dropping tables or calling functions).  
#    Keep it clean, safe, and executable.

# 5. **Ambiguity Handling:**  
#    - If a reasonable assumption must be made, include it as a single-line SQL comment before the query.  
#    - If the question cannot be answered with the schema, respond only with:  
#      `Cannot answer based on the provided schema.`

# 6. **Output Format:**  
#    - Output a single `SELECT` query.  
#    - No markdown (` ```sql `), no explanations, no extra text.  
#    - Optional SQL comments for assumptions are allowed.

# 7. **Imp Points:**
#    - 1. Ensure the `SELECT DISTINCT` clause is followed by valid columns.
#    - 2. If you use `DISTINCT`, list the columns you want to select after it, like `SELECT DISTINCT column1, column2

# ---

# **Start your output with the query or an optional SQL comment.**
# Do not prefix or suffix the result with anything else.

# **Now generate the SQL:**
# """

#         model = genai.GenerativeModel('gemini-2.0-flash')
#         response = model.generate_content(prompt)


#         try:
#             raw_text = response.candidates[0].content.parts[0].text.strip()
#             print("Gemini raw output:\n", raw_text)

#             if "Cannot answer based on the provided schema." in raw_text:
#                 return "Cannot answer based on the provided schema."

#             # Extract lines that could be SQL or assumptions
#             sql_lines = raw_text.splitlines()
#             filtered_lines = [
#                 line for line in sql_lines
#                 if line.strip().startswith("--") or
#                 line.strip().upper().startswith("SELECT") or
#                 "FROM" in line.upper()
#             ]
#             sql_only = "\n".join(filtered_lines).strip()

#             # Validate SQL structure
#             if not sql_only or "SELECT" not in sql_only.upper() or "FROM" not in sql_only.upper():
#                 print("No valid SQL found in Gemini response.")
#                 raise HTTPException(status_code=400, detail="SQL is empty or invalid.")
            
#             print("Final SQL to execute:\n", sql_only)
#             return sql_only
        
#         except Exception as parse_error:
#             print("Error parse_error")
#             raise HTTPException(status_code=500, detail="Failed to parse Gemini response")

#     except Exception as e:
#         print("Unhandled Exception in generate_sql_from_nl:", e)
#         raise HTTPException(status_code=500, detail=str(e))



from fastapi import Depends, HTTPException
import google.generativeai as genai
from backend.app.database import get_db
from sqlalchemy.orm import Session
from backend.app.services.schema_service import get_database_schema
from backend.app.core.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

def generate_sql_from_nl(natural_language_query: str, db: Session = Depends(get_db)) -> str:
    """
    Generate a PostgreSQL SELECT query based on natural language input
    using Gemini AI and the provided database schema.
    """
    try:
      schema = get_database_schema(db)

      prompt = f"""
      You are an expert SQL generator assistant.

      DATABASE SCHEMA:
      {schema}

      USER QUESTION:
      {natural_language_query}

   RULES:
   - Only generate PostgreSQL SELECT queries.
   - Strictly use only the given schema tables and columns.
   - If assumptions are made, mention them as a SQL comment (starting with --).
   - If query cannot be generated from schema, respond only with: Cannot answer based on the provided schema.
   - No explanations, no markdown. Just clean SQL query.

   Start your output immediately with SQL or optional comment.
         """
      model = genai.GenerativeModel('gemini-2.0-flash')
      response = model.generate_content(
         prompt,
         generation_config={
            "temperature": 0.1,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 512,
            "stop_sequences": ["#"],
            },
         )
      print("================================================================================")
      print(response)
      print("===============================================================================")
        
      try:
         raw_text = response.candidates[0].content.parts[0].text.strip()
         print("Gemini raw output:\n", raw_text)

         if "Cannot answer based on the provided schema." in raw_text:
            return "Cannot answer based on the provided schema."

         # # 🔥 Exact Code1 response filter
         # lines = raw_text.splitlines()
         # sql_lines = []
         # for line in lines:
         #    if line.strip().startswith("--") or \
         #       line.strip().upper().startswith("SELECT") or \
         #       "FROM" in line.upper():
         #       sql_lines.append(line)

         #    final_sql = "\n".join(sql_lines).strip()
            # print("=============================================================")
            # print(f"final sql, {final_sql}")
            # print("=============================================================")

            # if not final_sql or "SELECT" not in final_sql.upper() or "FROM" not in final_sql.upper():
            #    print("Invalid or empty SQL generated.")
            #    raise HTTPException(status_code=400, detail="Generated SQL is invalid or empty.")

            # print("Final SQL to execute:\n", final_sql)
         return raw_text
        
      except Exception as parse_error:
         print("Parsing error:", parse_error)
         raise HTTPException(status_code=500, detail="Error parsing Gemini response.")

    except Exception as e:
        print("Unhandled exception in generate_sql_from_nl:", e)
        raise HTTPException(status_code=500, detail=str(e))






