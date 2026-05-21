-- ── 1. Total profit per symbol
SELECT symbol,
       COUNT(*) as total_trades,
       ROUND(SUM(total_paper_profit)::numeric, 2) as total_profit,
       ROUND(AVG(profit_per_share)::numeric, 4) as avg_profit_per_share
FROM arbitrage_records
GROUP BY symbol
ORDER BY total_profit DESC;

-- ── 2. Window Function — Rank strike combinations by profit per symbol
SELECT symbol,
       strike_low,
       strike_high,
       ROUND(AVG(total_paper_profit)::numeric, 2) as avg_profit,
       RANK() OVER (PARTITION BY symbol ORDER BY AVG(total_paper_profit) DESC) as profit_rank
FROM arbitrage_records
GROUP BY symbol, strike_low, strike_high
ORDER BY symbol, profit_rank;

-- ── 3. CTE — Top 5 most profitable trading hours
WITH hourly_profit AS (
    SELECT SUBSTRING(timestamp, 1, 2) as hour,
           symbol,
           ROUND(SUM(total_paper_profit)::numeric, 2) as total_profit
    FROM arbitrage_records
    GROUP BY hour, symbol
)
SELECT * FROM hourly_profit
ORDER BY total_profit DESC
LIMIT 10;

-- ── 4. Daily profit trend using Window Function
SELECT date,
       symbol,
       ROUND(SUM(total_paper_profit)::numeric, 2) as daily_profit,
       ROUND(SUM(SUM(total_paper_profit)) OVER (PARTITION BY symbol ORDER BY date)::numeric, 2) as cumulative_profit
FROM arbitrage_records
GROUP BY date, symbol
ORDER BY symbol, date;

-- ── 5. IRR Tier performance analysis
SELECT irr_tier,
       symbol,
       COUNT(*) as occurrences,
       ROUND(AVG(profit_per_share)::numeric, 4) as avg_profit
FROM arbitrage_records
GROUP BY irr_tier, symbol
ORDER BY symbol, avg_profit DESC;