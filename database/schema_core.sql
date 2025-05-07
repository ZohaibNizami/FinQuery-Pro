-- Core schema for storing company and daily stock price data

-- Table to store basic company information
CREATE TABLE companies (
    ticker TEXT PRIMARY KEY,        -- Unique stock ticker symbol (e.g., AAPL)
    name TEXT NOT NULL,             -- Full company name
    sector TEXT,                    -- Business sector (e.g., Technology)
    industry TEXT                   -- Specific industry (e.g., Consumer Electronics)
);

-- Table to store daily stock prices
CREATE TABLE stock_prices_daily (
    price_id SERIAL PRIMARY KEY,    -- Auto-incremented ID for each price record
    ticker TEXT REFERENCES companies(ticker),  -- Foreign key to companies table
    date DATE NOT NULL,             -- Date of the stock price
    open NUMERIC,                   -- Opening price
    high NUMERIC,                   -- Highest price of the day
    low NUMERIC,                    -- Lowest price of the day
    close NUMERIC,                  -- Closing price
    adjusted_close NUMERIC,         -- Adjusted close (after splits/dividends)
    volume BIGINT,                  -- Number of shares traded

    -- Ensure no duplicate records for same ticker on the same date
    UNIQUE(ticker, date)
)

--Create Table for stock splits (company_fundamentals)
CREATE TABLE IF NOT EXISTS company_fundamentals (
    fundamental_id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value NUMERIC,
    fiscal_period TEXT,

    CONSTRAINT fk_fundamentals_ticker FOREIGN KEY (ticker)
        REFERENCES companies(ticker) ON DELETE CASCADE,

    CONSTRAINT unique_fundamental UNIQUE (ticker, report_date, metric_name)
);


--Create Table (sec_filings)
CREATE TABLE IF NOT EXISTS sec_filings (
    filing_id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    form_type VARCHAR(20),
    filing_date DATE NOT NULL,
    reporting_date DATE,
    document_url TEXT,

    CONSTRAINT fk_filings_ticker FOREIGN KEY (ticker)
        REFERENCES companies(ticker) ON DELETE CASCADE
);


-- Insider Transactions Table
CREATE TABLE insider_transactions (
    tx_id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    insider_name TEXT NOT NULL,
    relation TEXT,
    tx_type TEXT NOT NULL,
    shares INTEGER NOT NULL,
    value NUMERIC(20, 2) NOT NULL,
    tx_date DATE NOT NULL,
    filing_date DATE NOT NULL,
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);


-- Analyst Recommendations Table
CREATE TABLE analyst_recommendations (
    rec_id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    firm TEXT NOT NULL,
    analyst_name TEXT,
    rating TEXT NOT NULL,
    target_price NUMERIC(20, 2),
    report_date DATE NOT NULL,
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);


-- Significant Developments Table
CREATE TABLE significant_developments (
    dev_id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    headline TEXT NOT NULL,
    source TEXT,
    published_date DATE NOT NULL,
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);


-- ETL Jobs Table
CREATE TABLE etl_jobs (
    job_id SERIAL PRIMARY KEY,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    status TEXT NOT NULL,
    details TEXT
);


-- NLQ History Table
CREATE TABLE nlq_history (
    query_id SERIAL PRIMARY KEY,
    user_input TEXT NOT NULL,
    generated_sql TEXT NOT NULL,
    execution_status TEXT NOT NULL,
    result_summary TEXT,
    timestamp TIMESTAMPTZ NOT NULL
);
