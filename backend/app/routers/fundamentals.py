
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from typing import List

from ..schemas import CompanyFundamentalsResponse, CompanyFundamentalsRecord
from ..crud import get_fundamentals
from ..database import get_db
from ..models import CompanyFundamentals
from collections import defaultdict



router = APIRouter()


@router.get("/fundamentals", response_model=List[CompanyFundamentalsResponse])
def get_company_fundamentals(ticker: str , db: Session = Depends(get_db)):
    # Fetch all rows from the DB
    fundamentals = db.query(CompanyFundamentals).all()

    grouped = defaultdict(list)

    # Group records by ticker
    for f in fundamentals:
        grouped[f.ticker].append(CompanyFundamentalsRecord(
            report_date=f.report_date,
            metric_name=f.metric_name,
            metric_value=f.metric_value,
            fiscal_period=f.fiscal_period
        ))

    # Prepare response in expected format
    response = []
    for ticker, records in grouped.items():
        response.append(CompanyFundamentalsResponse(
            ticker=ticker,
            records=records,
            status="ok"
        ))

    return response





 
    

    

