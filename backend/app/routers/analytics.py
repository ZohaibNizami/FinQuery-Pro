from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from backend.app.database import get_db 

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# vw_stock_performance_summary
@router.get("/performance/{ticker}", response_model=List[Dict[str, Any]])
def get_stock_performance(ticker: str, db: Session = Depends(get_db)):
    sql = "SELECT * FROM vw_stock_performance_summary WHERE ticker = :ticker"
    result = db.execute(text(sql), {"ticker": ticker}).fetchall()
    return [dict(row._mapping) for row in result]


#vw_insider_activity_trends
@router.get("/insider-trends/{ticker}", response_model=List[Dict[str, Any]])
def get_insider_trends(ticker: str, db: Session = Depends(get_db)):
    sql = "SELECT * FROM vw_insider_activity_trends WHERE ticker = :ticker"
    result = db.execute(text(sql), {"ticker": ticker}).fetchall()
    return [dict(row._mapping) for row in result]


#vw_sec_filing_frequency
@router.get("/sec-filing-frequency/{ticker}", response_model=List[Dict[str, Any]])
def get_sec_filing_frequency(ticker: str, db: Session = Depends(get_db)):
    sql = "SELECT * FROM vw_sec_filing_frequency WHERE ticker = :ticker"
    result = db.execute(text(sql), {"ticker": ticker}).fetchall()
    return [dict(row._mapping) for row in result]


# Optional: Dynamic SQL Example
@router.get("/correlation")
def get_correlation(tickers: str, db: Session = Depends(get_db)):
    ticker_list = tickers.split(",")
    # Example: dynamic SQL based on multiple tickers
    sql = f"""
    SELECT ticker, date, close_price
    FROM stock_prices_daily
    WHERE ticker IN :tickers
    ORDER BY date
    """
    result = db.execute(text(sql), {"tickers": tuple(ticker_list)}).fetchall()
    return [dict(row._mapping) for row in result]
