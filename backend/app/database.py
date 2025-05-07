from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .core.config import settings  # Import from new config module


# Use the DATABASE_URL property
DATABASE_URL = settings.DATABASE_URL
print(DATABASE_URL)

engine = create_engine(DATABASE_URL, echo = True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

print("Using DATABASE_URL:", DATABASE_URL)

try:
    if get_db():
        print("Database connection success")
except:
    print("Connection Failed")

