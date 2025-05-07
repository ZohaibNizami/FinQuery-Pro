from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List


# Company schemas
class CompanyBase(BaseModel):
    company_name: str
    industry: str
    sector: str

    class Config:
        orm_mode = True  # Allows Pydantic to work with SQLAlchemy models

class Company(CompanyBase):
    ticker : str

    class Config:
        orm_mode = True
        

# StockPriceDaily schemas
class StockPriceDailyBase(BaseModel):
    date: date
    open_price: float
    close_price: float
    high_price: float
    low_price: float
    volume: int

    class Config:
        orm_mode = True

class StockPriceDaily(StockPriceDailyBase):
    ticker: str  # Can be used for linking to the Company model

    class Config:
        orm_mode = True



# CompanyFundamentals Schemas
class CompanyFundamentalsRecord(BaseModel):

    report_date: date
    metric_name: str
    metric_value: float
    fiscal_period: str

class CompanyFundamentalsResponse(BaseModel):
    ticker: str
    records: List[CompanyFundamentalsRecord]
    status: str = "OK"

    class Config:
        orm_mode = True


# SEC Filings Schemas
class SECFilingBase(BaseModel):
    ticker: str
    form_type: Optional[str]
    filing_date: date
    reporting_date: Optional[date]
    document_url: Optional[str]


class SECFiling(SECFilingBase):
    ticker: str
    metrics: List[SECFilingBase]
    

    class Config:
        orm_mode = True




class NLQueryRequest(BaseModel):
    query: str

    class Config:
        orm_mode = True


# --- Insider Transactions ---
class InsiderTransactionBase(BaseModel):
    ticker: str
    insider_name: str
    relation: Optional[str] = None
    tx_type: str
    shares: int
    value: float
    tx_date: date
    filing_date: date

    class Config:
        orm_mode = True

class InsiderTransaction(InsiderTransactionBase):
    tx_id: int

    class Config:
        orm_mode = True


# --- Analyst Recommendations ---
class AnalystRecommendationBase(BaseModel):
    ticker: str
    firm: str
    analyst_name: Optional[str] = None
    rating: str
    target_price: Optional[float] = None
    report_date: date

    class Config:
        orm_mode = True

class AnalystRecommendation(AnalystRecommendationBase):
    rec_id: int

    class Config:
        orm_mode = True


# --- Significant Developments ---
class SignificantDevelopmentBase(BaseModel):
    ticker: str
    headline: str
    source: Optional[str] = None
    published_date: date

    class Config:
        orm_mode = True

class SignificantDevelopment(SignificantDevelopmentBase):
    dev_id: int

    class Config:
        orm_mode = True


# --- ETL Jobs ---
class ETLJobBase(BaseModel):
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str
    details: Optional[str] = None

    class Config:
        orm_mode = True

class ETLJob(ETLJobBase):
    job_id: int

    class Config:
        orm_mode = True


# --- NLQ History ---
class NLQHistoryBase(BaseModel):
    user_input: str
    generated_sql: str
    execution_status: str
    result_summary: Optional[str] = None
    timestamp: datetime

    class Config:
        orm_mode = True

class NLQHistory(NLQHistoryBase):
    query_id: int

    class Config:
        orm_mode = True



