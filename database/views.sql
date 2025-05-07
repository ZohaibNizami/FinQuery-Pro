-- vw_stock_performance_summary

CREATE OR REPLACE VIEW vw_stock_performance_summary AS
WITH price_with_returns AS (
    SELECT
        spd.id,
        spd.ticker,
        c.company_name,
        spd.date,
        spd.close_price,
        LAG(spd.close_price) OVER (PARTITION BY spd.ticker ORDER BY spd.date) AS prev_close_price,
        AVG(spd.close_price) OVER (PARTITION BY spd.ticker ORDER BY spd.date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS moving_avg_7d
    FROM stock_prices_daily spd
    JOIN companies c ON spd.ticker = c.ticker
)
SELECT
    id,
    ticker,
    company_name,
    date,
    close_price,
    prev_close_price,
    CASE 
        WHEN prev_close_price IS NOT NULL THEN ROUND(((close_price - prev_close_price) / prev_close_price * 100)::NUMERIC, 2)
        ELSE NULL
    END AS daily_return_pct,
    ROUND(moving_avg_7d::NUMERIC, 2) AS moving_avg_7d
FROM price_with_returns;


-- for testing 
SELECT * FROM vw_stock_performance_summary WHERE ticker = 'AAPL' ORDER BY date DESC LIMIT 10;

---------------------------------

--vw_insider_activity_trends

CREATE OR REPLACE VIEW vw_insider_activity_trends AS
WITH insider_monthly AS (
    SELECT
        it.ticker,
        DATE_TRUNC('month', it.tx_date) AS month,
        SUM(CASE WHEN it.tx_type = 'Buy' THEN it.shares ELSE 0 END) AS total_shares_bought,
        SUM(CASE WHEN it.tx_type = 'Sell' THEN it.shares ELSE 0 END) AS total_shares_sold,
        COUNT(DISTINCT it.insider_name) AS unique_insiders
    FROM insider_transactions it
    GROUP BY it.ticker, DATE_TRUNC('month', it.tx_date)
)
SELECT
    im.ticker,
    c.company_name,
    im.month,
    im.total_shares_bought,
    im.total_shares_sold,
    im.unique_insiders
FROM insider_monthly im
JOIN companies c ON im.ticker = c.ticker
ORDER BY im.ticker, im.month;


-- for testing 
SELECT * FROM vw_insider_activity_trends WHERE ticker = 'AAPL';

---------------------------------

-- vw_sec_filing_frequency



