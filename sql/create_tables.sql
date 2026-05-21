DROP TABLE IF EXISTS arbitrage_records;

CREATE TABLE arbitrage_records (
    id SERIAL PRIMARY KEY,
    date DATE,
    timestamp TIME,
    symbol VARCHAR(20),
    expiry DATE,
    strike_low NUMERIC,
    strike_high NUMERIC,
    buy_low_ce NUMERIC,
    sell_high_ce NUMERIC,
    buy_high_pe NUMERIC,
    sell_low_pe NUMERIC,
    net_exec_cost NUMERIC,
    theoretical_value VARCHAR(10),
    irr_tier VARCHAR(20),
    target_mismatch VARCHAR(10),
    profit_per_share NUMERIC,
    total_paper_profit NUMERIC,
    file_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_symbol ON arbitrage_records(symbol);
CREATE INDEX IF NOT EXISTS idx_date ON arbitrage_records(date);
CREATE INDEX IF NOT EXISTS idx_expiry ON arbitrage_records(expiry);
CREATE INDEX IF NOT EXISTS idx_irr_tier ON arbitrage_records(irr_tier);