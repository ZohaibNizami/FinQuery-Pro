from fastapi import APIRouter
from fastapi import Depends, HTTPException

from sqlalchemy.orm import Session
from ..database import get_db

import backend.app.crud as crud
import backend.app.schemas as schemas
import etl.etl_pipeline as etl


router = APIRouter()

#To get data from db 
@router.get("/developments/{ticker}", response_model=list[schemas.SignificantDevelopment])
def get_significant_developments(ticker: str, db: Session = Depends(get_db)):
    # Get the significant developments for a given ticker
    developments = crud.get_significant_developments_by_ticker(db, ticker)
    if not developments:
        raise HTTPException(status_code=404, detail="No significant developments found for this ticker")
    return developments