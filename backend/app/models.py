from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey, UniqueConstraint, NUMERIC, Text, Numeric
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from backend.app.database import engine

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True)
    company_name = Column(String)
    industry = Column(String)
    sector = Column(String)

    stock_prices = relationship("StockPriceDaily", back_populates="company")

    #stock_prices = relationship("StockPriceDaily", back_populates="company", cascade="all, delete-orphan"  , passive_deletes=True)

    fundamentals = relationship("CompanyFundamentals", back_populates="company", cascade="all, delete-orphan")
    sec_filings = relationship("SECFiling", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company(ticker={self.ticker}, company_name={self.company_name})>"

    
class StockPriceDaily(Base):
    __tablename__ = "stock_prices_daily"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(Date)
    open_price = Column(Float)
    close_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    volume = Column(Integer)
    ticker = Column(String, ForeignKey("companies.ticker"))
    #ticker = Column(String, ForeignKey("companies.ticker", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("ticker", "date", name="unique_ticker_date"),
    )

    company = relationship("Company", back_populates="stock_prices")
    


class CompanyFundamentals(Base):
    __tablename__ = "company_fundamentals"
    
    fundamental_id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), ForeignKey("companies.ticker", ondelete="CASCADE"), nullable=False)
    report_date = Column(Date, nullable=False)
    metric_name = Column(String, nullable=False)
    metric_value = Column(NUMERIC)
    fiscal_period = Column(String)

    __table_args__ = (UniqueConstraint("ticker", "report_date", "metric_name", name="uix_ticker_report_metric"),)
    company = relationship("Company", back_populates="fundamentals")



class SECFiling(Base):
    __tablename__ = "sec_filings"
    filing_id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), ForeignKey("companies.ticker", ondelete="CASCADE"), nullable=False)
    form_type = Column(String(20))
    filing_date = Column(Date, nullable=False)
    reporting_date = Column(Date)
    document_url = Column(String)

    company = relationship("Company", back_populates="sec_filings")


class InsiderTransaction(Base):
    __tablename__ = 'insider_transactions'

    tx_id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), ForeignKey('companies.ticker'), nullable=False)
    insider_name = Column(Text, nullable=False)
    relation = Column(Text, nullable=True)
    tx_type = Column(Text, nullable=False)
    shares = Column(Integer, nullable=False)
    value = Column(Numeric, nullable=False)
    tx_date = Column(Date, nullable=False)
    filing_date = Column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint('ticker', 'insider_name', 'tx_date', 'tx_type', name='uix_insider_tx'),
    )


class AnalystRecommendation(Base):
    __tablename__ = 'analyst_recommendations'

    rec_id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), ForeignKey('companies.ticker'), nullable=False)
    firm = Column(Text, nullable=False)
    analyst_name = Column(Text, nullable=True)
    rating = Column(Text, nullable=False)
    target_price = Column(Numeric, nullable=True)
    report_date = Column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint('ticker', 'firm', 'report_date', name='uix_analyst_rating'),
    )

class SignificantDevelopment(Base):
    __tablename__ = 'significant_developments'

    dev_id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), ForeignKey('companies.ticker'), nullable=False)
    headline = Column(Text, nullable=False)
    source = Column(Text, nullable=True)
    published_date = Column(Date, nullable=False)

class ETLJob(Base):
    __tablename__ = 'etl_jobs'

    job_id = Column(Integer, primary_key=True, index=True)
    start_time = Column(PG_TIMESTAMP(timezone=True), nullable=False)
    end_time = Column(PG_TIMESTAMP(timezone=True), nullable=True)
    status = Column(Text, nullable=False)
    details = Column(Text, nullable=True)

class NLQHistory(Base):
    __tablename__ = 'nlq_history'

    query_id = Column(Integer, primary_key=True, index=True)
    user_input = Column(Text, nullable=False)
    generated_sql = Column(Text, nullable=False)
    execution_status = Column(Text, nullable=False)
    result_summary = Column(Text, nullable=True)
    timestamp = Column(PG_TIMESTAMP(timezone=True), nullable=False)



Base.metadata.create_all(bind=engine)


    

