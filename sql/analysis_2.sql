-- ============================================================
-- WINDOW FUNCTIONS
-- ============================================================

-- 1. Rank strike combinations by average profit within each symbol
SELECT symbol,
       strike_low,
       strike_high,
       ROUND(AVG(total_paper_profit)::numeric, 2) as avg_profit,
       RANK() OVER (PARTITION BY symbol ORDER BY AVG(total_paper_profit) DESC) as profit_rank
FROM arbitrage_records
GROUP BY symbol, strike_low, strike_high
ORDER BY symbol, profit_rank;

-- 2. Daily profit with cumulative running total per symbol
SELECT date,
       symbol,
       ROUND(SUM(total_paper_profit)::numeric, 2) as daily_profit,
       ROUND(SUM(SUM(total_paper_profit)) OVER (PARTITION BY symbol ORDER BY date)::numeric, 2) as cumulative_profit
FROM arbitrage_records
GROUP BY date, symbol
ORDER BY symbol, date;

-- 3. Lag analysis — compare each trade profit with previous trade
SELECT date,
       timestamp,
       symbol,
       profit_per_share,
       LAG(profit_per_share) OVER (PARTITION BY symbol ORDER BY date, timestamp) as prev_profit,
       ROUND((profit_per_share - LAG(profit_per_share) OVER (PARTITION BY symbol ORDER BY date, timestamp))::numeric, 4) as profit_change
FROM arbitrage_records
ORDER BY symbol, date, timestamp;

-- 4. Percentile rank — top performing trades
SELECT date,
       timestamp,
       symbol,
       profit_per_share,
       total_paper_profit,
       ROUND(PERCENT_RANK() OVER (PARTITION BY symbol ORDER BY total_paper_profit)::numeric, 4) as percentile_rank
FROM arbitrage_records
ORDER BY symbol, percentile_rank DESC;

-- ============================================================
-- CTEs (Common Table Expressions)
-- ============================================================

-- 5. Best trading hours per symbol
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

-- 6. Top 3 strike combinations per symbol using CTE
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

-- 7. IRR tier performance using CTE
WITH irr_analysis AS (
    SELECT irr_tier,
           symbol,
           COUNT(*) as occurrences,
           ROUND(AVG(profit_per_share)::numeric, 4) as avg_profit,
           ROUND(SUM(total_paper_profit)::numeric, 2) as total_profit
    FROM arbitrage_records
    GROUP BY irr_tier, symbol
)
SELECT * FROM irr_analysis
ORDER BY symbol, avg_profit DESC;

-- 8. Peak vs off-peak analysis using CTE
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