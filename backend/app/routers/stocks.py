from fastapi import APIRouter, Depends
from fastapi import HTTPException

from ..crud import get_company, get_stock_prices as get_prices_from_db
from ..crud import get_company_by_sector, delete_company, get_stocks_data, get_data

from ..database import get_db
from ..schemas import Company, StockPriceDaily, CompanyFundamentalsRecord, CompanyFundamentalsResponse
from etl.etl_pipeline import fetch_company_info, fetch_price_history, load_company_data, load_price_data, fetch_fundamentals, load_fundamentals_data, update_etl_job_status, create_etl_job
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import text

router = APIRouter()

#Load tickers to database
# @router.post("/etl/company", response_model=Company)
# def etl_company(ticker: str, db: Session = Depends(get_db)):
#     company_info = fetch_company_info(ticker)

#     if not company_info:
#         raise HTTPException(status_code=404, detail="Company info not found")

#     try:
#         #db_conn = db.connection()
#         load_company_data(db, [company_info])
#         db.commit()

#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

#     return Company(
#         ticker=company_info['ticker'],
#         company_name=company_info['company_name'],
#         sector=company_info['sector'],
#         industry=company_info['industry'],
#         summary=company_info['summary']
#     )

@router.post("/etl/company", response_model=Company)
def etl_company(ticker: str, db: Session = Depends(get_db)):
    job_id = None

    try:
        # Step 1: Start ETL Job
        job_id = create_etl_job(db)

        # Step 2: Fetch Company Info
        company_info = fetch_company_info(ticker)

        if not company_info:
            # If no info found, update ETL job as Failed
            if job_id:
                update_etl_job_status(db, job_id, status="Failed", details="Null Info: Company not found")
            raise HTTPException(status_code=404, detail="Company info not found")

        # Step 3: Load Company Data
        load_company_data(db, [company_info])
        db.commit()

    except SQLAlchemyError as e:
        db.rollback()
        if job_id:
            update_etl_job_status(db, job_id, status="Failed", details=str(e))
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        db.rollback()
        if job_id:
            update_etl_job_status(db, job_id, status="Failed", details=str(e))
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    finally:
        if job_id:
            # Check final status
            status_query = text("SELECT status FROM etl_jobs WHERE job_id = :job_id")
            current_status = db.execute(status_query, {"job_id": job_id}).scalar()

            if current_status == "Running":
                update_etl_job_status(db, job_id, status="Success")

    # Step 4: Return the Result
    return Company(
        ticker=company_info['ticker'],
        company_name=company_info['company_name'],
        sector=company_info['sector'],
        industry=company_info['industry'],
        summary=company_info.get('summary')  # Use .get() in case it's missing
    )

# Fetch & load stock price data ---
@router.post("/etl/price", response_model=list[StockPriceDaily])
def etl_price(ticker: str, db: Session = Depends(get_db)):
    job_id = None
    price_data = []

    try:
        job_id = create_etl_job(db)
        price_data = fetch_price_history(ticker)


        if not price_data:
            raise HTTPException(status_code=404, detail="Price history not found")
        update_etl_job_status(db, job_id, status="Failed", details="Price not found")

        load_price_data(db, [price_data])
        db.commit()

    except SQLAlchemyError as e:
        db.rollback()
        if job_id:
            update_etl_job_status(db, job_id, status="Failed", details=str(e))
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        db.rollback()
        if job_id:
            update_etl_job_status(db, job_id, status="Failed", details=str(e))
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


    finally:
        if job_id:
            # Check final status
            status_query = text("SELECT status FROM etl_jobs WHERE job_id = :job_id")
            current_status = db.execute(status_query, {"job_id": job_id}).scalar()

            if current_status == "Running":
                update_etl_job_status(db, job_id, status="Success")

    return [
        StockPriceDaily(
            ticker = row.get("ticker", None),
            date = row.get("date", None),
            open_price = row.get("open_price", None),
            high_price = row.get("high_price", None),
            low_price = row.get("low_price", None),
            close_price = row.get("close_price", None),
            volume = row.get("volume", None),
        )
        for row in price_data
    ]

# Fetch & load Company Fundamentals data ---

@router.post("/fundamentals", response_model=CompanyFundamentalsResponse)
def etl_company_fundamentals(ticker: str, db: Session = Depends(get_db)):
    job_id = None
    inserted_records = []

    try:
        job_id = create_etl_job(db)
        fundamentals_data = fetch_fundamentals(ticker)

        if not fundamentals_data:
            update_etl_job_status(db, job_id, status="Failed", details="No fundamentals data found")
            raise HTTPException(status_code=404, detail="No fundamentals data found")

        load_price_data(db, fundamentals_data)  

        for record in fundamentals_data:
            load_fundamentals_data(db, record)
            inserted_records.append(
                CompanyFundamentalsRecord(
                    ticker=record['ticker'],
                    report_date=record['report_date'],
                    metric_name=record['metric_name'],
                    metric_value=record['metric_value'],
                    fiscal_period=record['fiscal_period'],
                )
            )

        db.commit() 
        update_etl_job_status(db, job_id, status="Success") 

    except SQLAlchemyError as e:
        db.rollback()
        if job_id:
            update_etl_job_status(db, job_id, status="Failed", details=str(e))
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        db.rollback()
        if job_id:
            update_etl_job_status(db, job_id, status="Failed", details=str(e))
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    return CompanyFundamentalsResponse(
        ticker=ticker,
        records=inserted_records,
        status="Fundamentals data inserted/updated successfully"
    )


#-----------------------------------------------

#Fetch data from database
@router.get("/stocks/{ticker}/info_from_db", response_model=Company)
def get_company_info(ticker: str, db: Session = Depends(get_db)):
    job_id = None

    try:
        job_id = create_etl_job(db)  # Start ETL Job (status=Running by default)
        
        company = get_company(db, ticker)

        if not company:
            update_etl_job_status(db, job_id, status="Failed", details="Company not found")
            raise HTTPException(status_code=404, detail="Company not found")

        update_etl_job_status(db, job_id, status="Success")  # Success if company found
        return company

    except SQLAlchemyError as e:
        db.rollback()
        if job_id:
            update_etl_job_status(db, job_id, status="Failed", details=str(e))
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        if job_id:
            update_etl_job_status(db, job_id, status="Failed", details=str(e))
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



@router.get("/stocks/{ticker}/prices_from_db", response_model=list[StockPriceDaily])
def fetch_stock_prices(ticker: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    job_id = None

    try:

        job_id = create_etl_job(db)
        prices = get_prices_from_db(db, ticker, skip, limit)

        if not prices:
            update_etl_job_status(db, job_id, status="Failed", details="No stock prices found")
            raise HTTPException(status_code=404, detail="No stock prices found")
        update_etl_job_status(db, job_id, status="Success")
        return prices
    
    except SQLAlchemyError as e:
        db.rollback()
        if job_id:
            update_etl_job_status(db, job_id, status="Failed", details=str(e))
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        if job_id:
            update_etl_job_status(db, job_id, status="Failed", details=str(e))
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    

#Fetch data from database by sector
@router.get("/sector/{sector}/info_from_db", response_model=Company)
def get_sector_info(sector: str, db: Session = Depends(get_db)):
    job_id = None

    try:
        job_id = create_etl_job(db)
        company = get_company_by_sector(db, sector)

        if not company:
            update_etl_job_status(db, job_id, status="Failed", details="No Sector found")
            raise HTTPException(status_code=404, detail="Sector not found")
        update_etl_job_status(db, job_id, status="Success")
        return company
    
    except SQLAlchemyError as e:
        db.rollback()
        if job_id:
            update_etl_job_status(db, job_id, status="Failed", details=str(e))
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        if job_id:
            update_etl_job_status(db, job_id, status="Failed", details=str(e))
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


#Delete company on the basis of ticker
@router.delete("/companies/{ticker}", response_model=Company)
def delete_company_info(ticker: str, db: Session = Depends(get_db)):
    """
    Delete a company by its ticker symbol.
    """
    company = delete_company(db, ticker)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with ticker '{ticker}' not found")

    db.delete(company)
    db.commit()
    return {"message": f"Company with ticker '{ticker}' has been deleted"}

#get_router

@router.get("/stocks/{ticker}/stocks_from_db")
def get_stocks(ticker: str, db: Session = Depends(get_db)):
    stocks = get_stocks_data(db, ticker)
    if not stocks:
        raise HTTPException(status_code=404, detail="Stocks not found")
    return stocks


#input day and time
@router.get("/persons/{day}/{time}/persons_visited")
def get_person_data(day: str, time: str):
    person = get_data(day, time)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person



