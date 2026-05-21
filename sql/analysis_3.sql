-- ============================================================
-- ANALYSIS 3 — Interview Ready Queries
-- ============================================================

-- ── WINDOW FUNCTIONS ──

-- 1. RANK — Top strike combinations by average profit
SELECT symbol,
       strike_low,
       strike_high,
       ROUND(AVG(total_paper_profit)::numeric, 2) as avg_profit,
       RANK() OVER (PARTITION BY symbol ORDER BY AVG(total_paper_profit) DESC) as rank
FROM arbitrage_records
GROUP BY symbol, strike_low, strike_high
ORDER BY symbol, rank
LIMIT 10;

-- 2. SUM OVER — Daily profit with cumulative running total
SELECT date,
       symbol,
       ROUND(SUM(total_paper_profit)::numeric, 2) as daily_profit,
       ROUND(SUM(SUM(total_paper_profit)) OVER (PARTITION BY symbol ORDER BY date)::numeric, 2) as cumulative_profit
FROM arbitrage_records
GROUP BY date, symbol
ORDER BY symbol, date;

-- 3. LAG — Compare each trade profit with previous trade
SELECT date,
       timestamp,
       symbol,
       profit_per_share,
       LAG(profit_per_share) OVER (PARTITION BY symbol ORDER BY date, timestamp) as prev_profit,
       ROUND((profit_per_share - LAG(profit_per_share) OVER (PARTITION BY symbol ORDER BY date, timestamp))::numeric, 4) as profit_change
FROM arbitrage_records
ORDER BY symbol, date, timestamp
LIMIT 10;

-- ── CTEs ──

-- 4. Best trading hours
WITH hourly_profit AS (
    SELECT SUBSTRING(timestamp, 1, 2) as hour,
           symbol,
           ROUND(SUM(total_paper_profit)::numeric, 2) as total_profit,
           COUNT(*) as total_trades
    FROM arbitrage_records
    GROUP BY hour, symbol
)
SELECT * FROM hourly_profit
ORDER BY total_profit DESC;

-- 5. Top 3 strike combinations per symbol
WITH strike_performance AS (
    SELECT symbol,
           strike_low,
           strike_high,
           ROUND(AVG(total_paper_profit)::numeric, 2) as avg_profit,
           COUNT(*) as occurrences
    FROM arbitrage_records
    GROUP BY symbol, strike_low, strike_high
),
ranked_strikes AS (
    SELECT *,
           RANK() OVER (PARTITION BY symbol ORDER BY avg_profit DESC) as rnk
    FROM strike_performance
)
SELECT * FROM ranked_strikes
WHERE rnk <= 3
ORDER BY symbol, rnk;

-- 6. Morning vs Afternoon session performance
WITH session_analysis AS (
    SELECT
        CASE
            WHEN SUBSTRING(timestamp, 1, 2) IN ('09', '10') THEN 'Morning Session'
            ELSE 'Afternoon Session'
        END as session,
        symbol,
        ROUND(SUM(total_paper_profit)::numeric, 2) as total_profit,
        COUNT(*) as total_trades,
        ROUND(AVG(profit_per_share)::numeric, 4) as avg_profit
    FROM arbitrage_records
    GROUP BY session, symbol
)
SELECT * FROM session_analysis
ORDER BY symbol, total_profit DESC;