from fastapi import APIRouter
from fastapi import Depends, HTTPException

from sqlalchemy.orm import Session
from ..database import get_db

import backend.app.crud as crud
import backend.app.schemas as schemas
import etl.etl_pipeline as etl

router = APIRouter()

#load
@router.post("/load-insider-data", status_code=200)
def load_insider_data_endpoint(db: Session = Depends(get_db)):
    try:
        # Call the load_insider_data function from your etl.py file
        etl.load_insider_data(db)
        return {"message": "Insider data loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading insider data: {e}")
    
    
#get data
@router.get("/insider/{ticker}", response_model=list[schemas.InsiderTransaction])
def read_insider_transactions(ticker: str, db: Session = Depends(get_db)):
    data = crud.get_insider_transactions_by_ticker(db, ticker)
    if not data:
        raise HTTPException(status_code=404, detail="No insider transactions found")
    return data







