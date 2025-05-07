# Define GET /filings/{ticker} endpoint using get_db, calling crud.get_filings. Set response_model=List[schemas.SECFiling].

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from typing import List

from ..schemas import SECFilingBase
from ..crud import  get_filings
from ..database import get_db

from etl.etl_pipeline import load_filings_data

router = APIRouter()


@router.post("/load-sample-filings")
def sample_filings_data(ti, db_conn: Session = Depends(get_db)):
    try:
        load_filings_data(db_conn )
        return {"message": "✅ Sample SEC filings loaded successfully."}
    except Exception as e:
        # import traceback
        # traceback.print_exc()  # Optional: shows the error in logs
        # raise HTTPException(status_code=500, detail=f"❌ Failed to load filings: {str(e)}")

        return {"detail": f"❌ Failed to load filings: {str(e)}"}

    

@router.get("/filings/{ticker}/from_db", response_model=List[SECFilingBase])
def get_sec_filings(ticker: str, db:Session = Depends(get_db)):
    filings = get_filings(db, ticker)
    if not filings:
        return JSONResponse(status_code=404, content={"message": "Company not found"})
    return filings


