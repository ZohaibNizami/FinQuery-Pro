from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from sqlalchemy import text

db_router = APIRouter()

@db_router.get("/db-status")
def db_stat(db: Session = Depends(get_db)):
    try:
        # Run a simple query to verify the DB session works
        db.execute(text("SELECT 1"))
        return {"db_stat": "connected"}
    
    except Exception as e:
        print("DB connection error:", e)
        return {"db_stat": "disconnected"}
