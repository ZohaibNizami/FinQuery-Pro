# Finquery_Pro
This project automates gathering diverse financial data into a SQL database, making complex analysis accessible. It solves the challenge of easily querying and interpreting multifaceted financial information by providing natural language interaction and a unified analytics dashboard.

```
finquery_pro/
├── .env                 # Local environment variables (GITIGNORED!)
├── .env.example         # Example environment variables
├── .gitignore           # Git ignore file
├── docker-compose.yml   # Docker Compose configuration
├── requirements.txt     # Python package dependencies
├── README.md            # Project documentation
│
├── database/            # Database related files
│   └── schema_core.sql  
│   └── schema_full.sql  
│
├── etl/                 # ETL pipeline code
│   ├── etl_pipeline.py  # Main ETL script
│   └── utils.py         
│
├── backend/             # FastAPI backend application
│   ├── Dockerfile       # Dockerfile for the backend service
│   ├── app/             # Main application source code
│   │   ├── __init__.py
│   │   ├── main.py      # FastAPI app definition, routers inclusion
│   │   ├── database.py  # SQLAlchemy setup (engine, session, Base)
│   │   ├── models.py    # SQLAlchemy ORM models
│   │   ├── schemas.py   # Pydantic schemas (data validation/serialization)
│   │   ├── crud.py      # Database interaction functions (CRUD operations)
│   │   ├── core/        # Core utilities like configuration
│   │   │   ├── __init__.py
│   │   │   └── config.py  # Pydantic settings for environment variables
│   │   ├── routers/     # API route definitions
│   │   │   ├── __init__.py
│   │   │   └── stocks.py  
│   │   │   └── analytics.py 
│   │   │   └── nlq.py     
│   │   └── services/    
│   │       ├── __init__.py
│   │       └── nlq_service.py 
│   └── tests/             
│
├── frontend/            
│   ├── app.py           
│   └── pages/           
│       └── 1_Dashboard.py 
│   └── utils.py         
│   └── requirements.txt 
│
└── venv/                # Python virtual environment (GITIGNORED!)
```

to run api : uvicorn backend.app.main:app --reload
to run steamlit : streamlit run /home/hanzala/Finquery_Pro/frontend/app.py



Instructions to run project : Finquery_Pro

1. Pull the updated code from the project repository (Finquery_Pro).
2. Navigate to the project directory.
3. Install the same Python version : Python 3.10.12
4. Activate the virtual environment (venv) using the command `source venv/bin/activate`.
5. Install the required packages using pip.
6. (requirements.txt) Install the project using `pip install -r requirements.txt`

7. Manually create the .env file in the root directory and add the following line:
    `DATABASE_URL = postgresql://postgres:1234@localhost:5432/postgres`

8. Use python-dotenv to load .env 
    `pip install python-dotenv`

9.  using PostgreSQL, recreate the DB and update credentials in .env.
    The DB Credentials are :
            DB_USER=postgres
            DB_PASSWORD=1234
            DB_HOST=localhost
            DB_PORT=5432
            DB_NAME=postgres


10. Run the backend API using `uvicorn backend.app.main:app --reload`

11. Run the frontend using `streamlit run Finquery_Pro/frontend/app.py`

12. The dashboard should display the stock prices and other relevant information.







