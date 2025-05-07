from sqlalchemy.orm import Session
from .models import Company, StockPriceDaily, CompanyFundamentals, SECFiling, InsiderTransaction, AnalystRecommendation, SignificantDevelopment, NLQHistory
from .schemas import Company as CompanySchema, SignificantDevelopmentBase
from datetime import datetime

# CRUD for Company
def get_company(db: Session, ticker: str):
    """
    Fetch a company by its ticker symbol from the database.
    """
    return db.query(Company).filter(Company.ticker == ticker).first()




def create_company(db: Session, company: CompanySchema):
    """
    Create a new company in the database.
    """
    db_company = Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


# CRUD for StockPriceDaily
def get_stock_prices(db: Session, ticker: str, skip: int = 0, limit: int = 100):
    """
    Fetch stock price data for a given company by its ticker symbol.
    """
    return db.query(StockPriceDaily).filter(StockPriceDaily.ticker == ticker).offset(skip).limit(limit).all()

def create_stock_price(db: Session, stock_price: StockPriceDaily):
    """
    Create a new stock price record in the database.
    """
    db.add(stock_price)
    db.commit()
    db.refresh(stock_price)
    return stock_price

# Optional: CRUD for updating or deleting a company or stock price record can also be added
def update_company(db: Session, ticker: str, updated_data: dict):
    """
    Update a company's details by its ticker symbol.
    """
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if company:
        for key, value in updated_data.items():
            setattr(company, key, value)
        db.commit()
        db.refresh(company)
        return company
    return None


# Delete Company from Table: companies
def delete_company(db: Session, ticker: str):
    """
    Delete a company record from the database by its ticker symbol.
    """
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if company:
        db.delete(company)
        db.commit()
        return company
    return None



def get_company_by_sector(db: Session, sector: str):
    """
    Fetch a company by its ticker symbol from the database.
    """
    return db.query(Company).filter(Company.sector == sector).first(); 


# ------------------ company_fundamentals ------------------
# Get data from DB table: company_fundamentals

def get_fundamentals(db: Session, ticker: str, limit: int = 100):
    """
    Fetch a company's fundamental data by its ticker symbol from the database.
    """
    return db.query(CompanyFundamentals).filter(CompanyFundamentals.ticker == ticker).limit(limit).all()


# ------------------ Get_SEC_Filings ------------------

def get_filings(db: Session, ticker: str, limit: int = 20):
    """
    Fetch a company's SEC filings by its ticker symbol from the database.
    """
    return db.query(SECFiling).filter(SECFiling.ticker == ticker).limit(limit).all()



# ------------------ InsiderTransaction ------------------
def get_insider_transactions_by_ticker(db: Session, ticker: str):
    return db.query(InsiderTransaction).filter(InsiderTransaction.ticker == ticker).all()


# ------------------ AnalystRecommendation ------------------
def get_analyst_recommendations(db: Session, ticker: str):
    return db.query(AnalystRecommendation).filter(AnalystRecommendation.ticker == ticker).all()


# ------------------ SignificantDevelopment ------------------
def get_significant_developments_by_ticker(db: Session, ticker: str):
    return db.query(SignificantDevelopment).filter(SignificantDevelopment.ticker == ticker).all()


def create_development(db: Session, dev: SignificantDevelopmentBase):
    db_dev = SignificantDevelopment(**dev.dict())
    db.add(db_dev)
    db.commit()
    db.refresh(db_dev)
    return db_dev

# ------------------ NLQHistory ---------------------

def create_nlq_history_entry(
    db: Session,
    user_input: str,
    generated_sql: str,
    execution_status: str,
    result_summary: str = None
):
    entry = NLQHistory(
        user_input=user_input,
        generated_sql=generated_sql,
        execution_status=execution_status,
        result_summary=result_summary,
        timestamp=datetime.utcnow()
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

# def create_nlq_history_entry(db: Session, entry: NLQHistoryBase):
#     db_entry = NLQHistory(**entry.dict())
#     db.add(db_entry)
#     db.commit()
#     db.refresh(db_entry)
#     return db_entry

# def get_nlq_history(db: Session, limit: int = 20):
#     return db.query(NLQHistory).order_by(NLQHistory.timestamp.desc()).limit(limit).all()







from sqlalchemy import text

def get_stocks_data(db, ticker):
    query = """
        SELECT 
            stock_prices_daily.open_price,
            stock_prices_daily.close_price,
            stock_prices_daily.high_price,
            stock_prices_daily.low_price,
            company_fundamentals.ticker,
            company_fundamentals.metric_value,
            company_fundamentals.fiscal_period
        FROM stock_prices_daily
        JOIN company_fundamentals 
            ON company_fundamentals.ticker = stock_prices_daily.ticker
        WHERE 
            company_fundamentals.metric_value > 1000000 
            AND company_fundamentals.fiscal_period = 'ANNUAL'
            AND company_fundamentals.ticker = :ticker
        LIMIT 100;
    """
    result = db.execute(text(query), {"ticker": ticker})  
    rows = result.fetchall()
    
    stocks_list = []
    for row in rows:
        stocks_list.append(dict(row._mapping))
    
    return stocks_list


import seaborn as sns

# Load the 'tips' dataset
tips = sns.load_dataset('tips')

# Display the first few rows
print(tips.head())



def get_data(day, time):

    Person_visited = []
    List_Male = []
    List_Female = []
    
    for index, row in tips.iterrows():
        if row['day'] == day and row['time'] == time:
            Person_visited.append(row['sex'])
            print("---------------------------------")
            print(len(Person_visited))
            print("---------------------------------")

            

    for i in Person_visited:
        if i == 'Male':
            List_Male.append(i)
            print(len(List_Male))

        elif i == 'Female':
            List_Female.append(i)            
            print(len(List_Female))

        else: 
            print("111111")

            # return List_Male, List_Female

    print(tips.shape)
    data = {
        "male": len(List_Male),
        "female": len(List_Female)
    }
    
    return data



    #return len(List_Male), len(List_Female)
    






    










    
    
    
