from fastapi import APIRouter
from fastapi import Depends, HTTPException

from sqlalchemy.orm import Session
from ..database import get_db

import backend.app.crud as crud
import backend.app.schemas as schemas
import etl.etl_pipeline as etl

router = APIRouter()

#load analysts data to analyst recommendations table
@router.post("/load-analysts-data", status_code=200)
def load_analyst_data_endpoint(db: Session = Depends(get_db)):
    try:
        # Call the load_analyst_data function from your etl.py file
        etl.load_analyst_data(db)
        return {"message": "Analyst data loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading analyst data: {e}")
    

#get analyst recommendations data
@router.get("/analysts/{ticker}", response_model=list[schemas.AnalystRecommendation])
def get_analyst_recommendations(ticker: str, db: Session = Depends(get_db)):
    # Get the analyst recommendations for a given ticker
    recommendations = crud.get_analyst_recommendations(db, ticker)
    if not recommendations:
        raise HTTPException(status_code=404, detail="No analyst recommendations found for this ticker")
    return recommendations
    


