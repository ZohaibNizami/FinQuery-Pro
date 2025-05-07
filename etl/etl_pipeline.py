import time
import yfinance as yf
from backend.app.database import SessionLocal
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from backend.app.schemas import Company, StockPriceDaily, InsiderTransaction, AnalystRecommendation
import pandas as pd
from datetime import datetime, timezone
from typing import List
from sqlalchemy.dialects.postgresql import insert



# --- Create a new ETL job record ---
def create_etl_job(db_conn):
    current_time = datetime.now(timezone.utc)
    insert_query = text("""
        INSERT INTO etl_jobs (start_time, status)
        VALUES (:start_time, :status)
        RETURNING job_id
    """)

    try:
        result = db_conn.execute(insert_query, {
            'start_time': current_time,
            'status': 'Running'
        })
        job_id = result.fetchone()[0]
        db_conn.commit()
        print(f"[✓] ETL job started with job_id: {job_id}")
        return job_id
    except SQLAlchemyError as e:
        db_conn.rollback()
        print(f"[!] Error creating ETL job: {e}")
        return None


# --- Update ETL job status ---
def update_etl_job_status(db_conn, job_id, status, details=None):
    current_time = datetime.now(timezone.utc)
    update_query = text("""
        UPDATE etl_jobs
        SET end_time = :end_time, status = :status, details = :details
        WHERE job_id = :job_id
    """)

    try:
        db_conn.execute(update_query, {
            'end_time': current_time,
            'status': status,
            'details': details or 'Completed successfully',
            'job_id': job_id
        })
        db_conn.commit()
        print(f"[✓] ETL job {job_id} status updated to {status}")
    except SQLAlchemyError as e:
        db_conn.rollback()
        print(f"[!] Error updating ETL job {job_id} status: {e}")


# --- Fetch Company Info ---
def fetch_company_info(ticker):
    try:
        company = yf.Ticker(ticker)
        info = company.info

        return {
            'ticker': ticker,
            'company_name': info.get('shortName'),
            'sector': info.get('sector'),
            'industry': info.get('industry'),
            'summary': info.get('longBusinessSummary')
        }
    except Exception as e:
        print(f"Error fetching company data for {ticker}: {e}")
        return None


# --- Fetch Price History ---

def fetch_price_history(ticker, period="1y"):
    try:
        ticker_obj = yf.Ticker(ticker)
        history_data = ticker_obj.history(period=period)

        if history_data.empty:
            print(f"No data returned for ticker: {ticker}")
            return []
        

        if 'Adj Close' not in history_data.columns:
            history_data['Adj Close'] = history_data['Close']

        price_data = []
        for index, row in history_data.iterrows():
            price_data.append({
                'ticker': ticker,
                'date': index.date(),
                'open_price': float(row['Open']),
                'high_price': float(row['High']),
                'low_price': float(row['Low']),
                'close_price': float(row['Close']),
                'volume': float(row['Volume'])
            })
        return price_data

    except Exception as e:
        print(f"Error fetching price data for {ticker}: {e}")
        return []

# --- Load Company Data ---
def load_company_data(db_conn, company_data):
    insert_query = text("""
        INSERT INTO companies (ticker, company_name, sector, industry)
        VALUES (:ticker, :company_name, :sector, :industry)
        ON CONFLICT (ticker) DO UPDATE
        SET company_name = EXCLUDED.company_name,
            sector = EXCLUDED.sector,
            industry = EXCLUDED.industry
    """)

    try:
        for company in company_data:
                db_conn.execute(insert_query, {
                    'ticker': company['ticker'],
                    'company_name': company['company_name'],
                    'sector': company['sector'],
                    'industry': company['industry'],
                    #'summary': company['summary']
                })
    except SQLAlchemyError as e:
        print(f"Error loading company data: {e}")

# --- Load Price Data ---

def load_price_data(db_conn, price_data):
    insert_query = text("""
        INSERT INTO stock_prices_daily (ticker, date, open_price, high_price, low_price, close_price, volume)
        VALUES (:ticker, :date, :open_price, :high_price, :low_price, :close_price, :volume)
        ON CONFLICT (ticker, date) DO UPDATE
        SET open_price = EXCLUDED.open_price,
            high_price = EXCLUDED.high_price,
            low_price = EXCLUDED.low_price,
            close_price = EXCLUDED.close_price,
            volume = EXCLUDED.volume
    """)

    try:
        for row in price_data:
            db_conn.execute(insert_query, row)
            db_conn.commit()
    except SQLAlchemyError as e:
        db_conn.rollback()
        print(f"Error loading price data: {e}")


# ---Fetch COmpany Fundamentals and store in database tablename : company_fundamentals---
def fetch_fundamentals(ticker):
    try:
        company = yf.Ticker(ticker)
        data_sources = {
            'financials': company.financials,
            'balance_sheet': company.balance_sheet,
            'cashflow': company.cashflow
        }

        fundamentals = []
        fiscal_period = 'ANNUAL'  # default assumption

        for source_name, df in data_sources.items():
            if df is None or df.empty:
                continue

            for date in df.columns:
                for metric_name in df.index:
                    value = df.at[metric_name, date]
                    if pd.isna(value):
                        continue
                    fundamentals.append({
                        'ticker': ticker,
                        'report_date': pd.to_datetime(date).date(),
                        'metric_name': metric_name,
                        'metric_value': float(value),
                        'fiscal_period': fiscal_period
                    })

        return fundamentals

    except Exception as e:
        print(f"Error fetching fundamentals for {ticker}: {e}")
        return []


# Load company fundamentals into database

def load_fundamentals_data(db_conn, fundamentals_data):
    if not fundamentals_data:
        return

    insert_query = text("""
        INSERT INTO company_fundamentals (ticker, report_date, metric_name, metric_value, fiscal_period)
        VALUES (:ticker, :report_date, :metric_name, :metric_value, :fiscal_period)
        ON CONFLICT (ticker, report_date, metric_name) DO UPDATE
        SET metric_value = EXCLUDED.metric_value,
            fiscal_period = EXCLUDED.fiscal_period
    """)

    try:
        db_conn.execute(insert_query, fundamentals_data)  # executemany() style in SQLAlchemy
        db_conn.commit()
        print(f"[✓] Inserted/Updated {len(fundamentals_data)} fundamentals rows.")
    except SQLAlchemyError as e:
        db_conn.rollback()
        print(f"[!] Error loading fundamentals data: {e}")




def load_filings_data(db_conn, filings_data=None):
    # Fallback sample data (if none provided)
    
    filings_data = [
            {
                'ticker': 'AAPL',
                'form_type': '10-K',
                'filing_date': '2023-10-27',
                'reporting_date': '2023-09-30',
                'document_url': 'http://example.com/aapl-10k'
            },
            {
                'ticker': 'MSFT',
                'form_type': '10-Q',
                'filing_date': '2023-07-25',
                'reporting_date': '2023-06-30',
                'document_url': 'http://example.com/msft-10q'
            },
            {
                'ticker': 'AAPL',
                'form_type': '10-Q',
                'filing_date': '2023-07-28',
                'reporting_date': '2023-06-30',
                'document_url': 'http://example.com/aapl-10q'
            }
        ]

    # ✅ SQL using named params (text wrapper is required)
    insert_query = text("""
        INSERT INTO sec_filings (ticker, form_type, filing_date, reporting_date, document_url)
        VALUES (:ticker, :form_type, :filing_date, :reporting_date, :document_url)
        ON CONFLICT (ticker, form_type, filing_date) DO NOTHING;
    """)

    try:
        with db_conn.begin():
            # ✅ Must be a list of dictionaries
            # if not isinstance(filings_data, list):
            #     raise ValueError("❌ filings_data must be a list of dictionaries.")

            db_conn.execute(insert_query, filings_data)

        print(f"✅ Loaded {len(filings_data)} filings into sec_filings table.")
    except SQLAlchemyError as e:
        print(f"❌ Failed to load filings: {e}")


# Sample entry point function
def sample_filings_data(db_conn, filings_data):
    load_filings_data(db_conn, filings_data)


#load insider data
def load_insider_data(db_conn, insider_data=None):
    # Fallback sample data
    insider_data = [
    {
        'ticker': 'AAPL',
        'insider_name': 'John Doe',
        'relation': 'CEO',
        'tx_type': 'Buy',
        'shares': 1000,
        'value': 50000.0,
        'tx_date': datetime(2023, 1, 1).date(),
        'filing_date': datetime(2023, 1, 2).date()
    },
    {
        'ticker': 'AAPL',
        'insider_name': 'Jane Smith',
        'relation': 'CFO',
        'tx_type': 'Sell',
        'shares': 500,
        'value': 25000.0,
        'tx_date': datetime(2023, 2, 1).date(),
        'filing_date': datetime(2023, 2, 2).date()
    }
]

    insert_query = text("""
    INSERT INTO insider_transactions (
        ticker, insider_name, relation, tx_type,
        shares, value, tx_date, filing_date
    ) VALUES (
        :ticker, :insider_name, :relation, :tx_type,
        :shares, :value, :tx_date, :filing_date
    )
    ON CONFLICT (ticker, insider_name, tx_date, tx_type) DO NOTHING
""")

    try:
        db_conn.execute(insert_query, insider_data)
        db_conn.commit()
        print(f"[✓] Inserted {len(insider_data)} insider transaction rows.")
    except SQLAlchemyError as e:
        db_conn.rollback()
        print(f"[!] Error loading insider data: {e}")


#-Load analyst recommendation data 
def load_analyst_data(db_conn, analyst_data=None):
    # Fallback sample data
    analyst_data = [
    {
        'ticker': 'AAPL',
        'firm': 'Goldman Sachs',
        'analyst_name': 'Alice Johnson',
        'rating': 'Buy',
        'target_price': 150.0,
        'report_date': datetime(2023, 3, 1).date()
    },
    {
        'ticker': 'AAPL',
        'firm': 'Morgan Stanley',
        'analyst_name': 'Bob Brown',
        'rating': 'Hold',
        'target_price': 135.0,
        'report_date': datetime(2023, 4, 1).date()
    }
]

    insert_query = text("""
    INSERT INTO analyst_recommendations (
        ticker, firm, analyst_name, rating, target_price, report_date
    ) VALUES (
        :ticker, :firm, :analyst_name, :rating, :target_price, :report_date
    )
    ON CONFLICT (ticker, firm, report_date)
    DO UPDATE SET
        rating = EXCLUDED.rating,
        target_price = EXCLUDED.target_price
""")


    try:
        db_conn.execute(insert_query, analyst_data)
        db_conn.commit()
        print(f"[✓] Inserted/Updated {len(analyst_data)} analyst recommendation rows.")
    except SQLAlchemyError as e:
        db_conn.rollback()
        print(f"[!] Error loading analyst data: {e}")

# ---------------------------

# --- Main ETL Logic ---

def run_etl(tickers, filings_data):
    db_conn = SessionLocal()
    job_id = None

    try:
        # Step 1: Start ETL job
        job_id = create_etl_job(db_conn)
        if not job_id:
            raise Exception("Failed to create ETL job. Exiting...")

        all_companies = []
        all_prices = []
        all_fundamentals = []

        # Step 2: Fetch data
        for ticker in tickers:
            company_info = fetch_company_info(ticker)
            if company_info:
                all_companies.append(company_info)

            price_history = fetch_price_history(ticker)
            if price_history:
                all_prices.extend(price_history)

            fundamentals = fetch_fundamentals(ticker)
            if fundamentals:
                all_fundamentals.extend(fundamentals)

            time.sleep(2)  # To avoid hitting API rate limits

        # Step 3: Load data
        if all_companies:
            load_company_data(db_conn, all_companies)
        
        if all_prices:
            load_price_data(db_conn, all_prices)

        if all_fundamentals:
            load_fundamentals_data(db_conn, all_fundamentals)

        if filings_data:
            load_filings_data(db_conn, filings_data)

        # Step 4: Load insider and analyst data
        load_insider_data(db_conn, tickers)  # Test insider data loading
        load_analyst_data(db_conn, tickers)  # Test analyst data loading

    except Exception as e:
        print(f"[!] ETL failed with error: {str(e)}")
        if job_id:
            update_etl_job_status(db_conn, job_id, status='Failed', details=str(e))
    finally:
        if job_id:
            # Check current status
            status_query = text("SELECT status FROM etl_jobs WHERE job_id = :job_id")
            status = db_conn.execute(status_query, {'job_id': job_id}).scalar()

            if status == 'Running':
                update_etl_job_status(db_conn, job_id, status='Success')

        db_conn.close()


if __name__ == "__main__":
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    
    filings_data = [
        {
            'ticker': 'AAPL',
            'form_type': '10-K',
            'filing_date': '2023-10-27',
            'reporting_date': '2023-09-30',
            'document_url': 'http://example.com/aapl-10k'
        }
        # (User can add real filings data here)
    ]

    run_etl(tickers, filings_data)


# # --- Main ETL function ---
# def run_etl(tickers, filings_data):
#     db_conn = SessionLocal()
#     job_id = None

#     try:
#         # Step 1: Start ETL job
#         job_id = create_etl_job(db_conn)
#         if not job_id:
#             raise Exception("Failed to create ETL job. Exiting...")

#         all_companies = []
#         all_prices = []
#         all_fundamentals = []

#         # Step 2: Fetch data
#         for ticker in tickers:
#             company_info = fetch_company_info(ticker)
#             if company_info:
#                 all_companies.append(company_info)

#             price_history = fetch_price_history(ticker)
#             if price_history:
#                 all_prices.extend(price_history)

#             fundamentals = fetch_fundamentals(ticker)
#             if fundamentals:
#                 all_fundamentals.extend(fundamentals)

#             time.sleep(1)  # To avoid hitting API rate limits

#         # Step 3: Load data
#         if all_companies:
#             load_company_data(db_conn, all_companies)
        
#         if all_prices:
#             load_price_data(db_conn, all_prices)

#         if all_fundamentals:
#             load_fundamentals_data(db_conn, all_fundamentals)

#         if filings_data:
#             load_filings_data(db_conn, filings_data)

#         # Fetch and load insider and analyst data
#         fetch_load_insider_data(db_conn, tickers)
#         fetch_load_analyst_data(db_conn, tickers)

#     except Exception as e:
#         print(f"[!] ETL failed with error: {str(e)}")
#         if job_id:
#             update_etl_job_status(db_conn, job_id, status='Failed', details=str(e))
#     finally:
#         if job_id:
#             # Check current status
#             status_query = text("SELECT status FROM etl_jobs WHERE job_id = :job_id")
#             status = db_conn.execute(status_query, {'job_id': job_id}).scalar()

#             if status == 'Running':
#                 update_etl_job_status(db_conn, job_id, status='Success')

#         db_conn.close()


# if __name__ == "__main__":
#     tickers = ['AAPL', 'MSFT', 'GOOGL']
    
#     filings_data = [
#         {
#             'ticker': 'MSFT',
#             'form_type': '20-K',
#             'filing_date': '2024-10-27',
#             'reporting_date': '2024-09-30',
#             'document_url': 'http://msft.com/msft-20k'
#         }
#         # (User can add real filings data here)
#     ]

#     run_etl(tickers, filings_data)



# # --- Main ETL Logic ---
# def run_etl():
#     tickers = ['AAPL', 'MSFT', 'GOOGL', 'ETH']
#     company_data = []
#     price_data = []

#     for ticker in tickers:
#         info = fetch_company_info(ticker)
#         if info:
#             company_data.append(info)

#         prices = fetch_price_history(ticker)
#         if prices:
#             price_data.extend(prices)

        
#         fundamentals_data = fetch_fundamentals(ticker)
#         if fundamentals_data:
#             fundamentals_data.append(fundamentals_data)

       
#         fundamentals_data = fetch_fundamentals(ticker)
#         load_fundamentals_data(db_conn, fundamentals_data)
            
                                                                                     
#     db = SessionLocal()
#     try:
#         db_conn = db.connection()
#         load_company_data(db_conn, company_data)
#         load_price_data(db_conn, price_data)
#         print("ETL completed successfully.")
#     except SQLAlchemyError as e:
#         db.rollback()
#         print("ETL failed:", e)
#     finally:
#         db.close()

#     try:
#         db.add(company_data)
#         db.add(price_data)
#         db.commit()
#     except Exception as e:
#         db.rollback()
#         print("Error inserting company:", e)


# if __name__ == '__main__':
#     run_etl()

