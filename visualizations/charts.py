import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ── Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port="5433",
    database="arbitrage_db",
    user="admin",
    password="admin123"
)

os.makedirs("outputs", exist_ok=True)
sns.set_theme(style="whitegrid")

# ── Chart 1: Total Profit by Symbol
df1 = pd.read_sql("""
    SELECT symbol,
           ROUND(SUM(total_paper_profit)::numeric, 2) as total_profit
    FROM arbitrage_records
    GROUP BY symbol
    ORDER BY total_profit DESC
""", conn)

plt.figure(figsize=(8, 5))
sns.barplot(data=df1, x="symbol", y="total_profit", palette="Blues_d")
plt.title("Total Paper Profit by Symbol", fontsize=14, fontweight="bold")
plt.xlabel("Symbol")
plt.ylabel("Total Profit (₹)")
for i, row in df1.iterrows():
    plt.text(i, row["total_profit"] + 10000, f"₹{row['total_profit']:,.0f}", ha="center", fontsize=10)
plt.tight_layout()
plt.savefig("outputs/chart1_total_profit_by_symbol.png")
plt.close()
print("✅ Chart 1 saved")

# ── Chart 2: Daily Profit Trend
df2 = pd.read_sql("""
    SELECT date, symbol,
           ROUND(SUM(total_paper_profit)::numeric, 2) as daily_profit
    FROM arbitrage_records
    GROUP BY date, symbol
    ORDER BY date
""", conn)

plt.figure(figsize=(10, 5))
sns.lineplot(data=df2, x="date", y="daily_profit", hue="symbol", marker="o", linewidth=2.5)
plt.title("Daily Profit Trend — IDEA vs PNB", fontsize=14, fontweight="bold")
plt.xlabel("Date")
plt.ylabel("Daily Profit (₹)")
plt.tight_layout()
plt.savefig("outputs/chart2_daily_profit_trend.png")
plt.close()
print("✅ Chart 2 saved")

# ── Chart 3: Best Trading Hours
df3 = pd.read_sql("""
    SELECT SUBSTRING(timestamp, 1, 2) as hour, symbol,
           ROUND(SUM(total_paper_profit)::numeric, 2) as total_profit
    FROM arbitrage_records
    GROUP BY hour, symbol
    ORDER BY total_profit DESC
""", conn)

plt.figure(figsize=(10, 5))
sns.barplot(data=df3, x="hour", y="total_profit", hue="symbol", palette="Set2")
plt.title("Profit by Trading Hour", fontsize=14, fontweight="bold")
plt.xlabel("Hour of Day")
plt.ylabel("Total Profit (₹)")
plt.tight_layout()
plt.savefig("outputs/chart3_profit_by_hour.png")
plt.close()
print("✅ Chart 3 saved")

# ── Chart 4: IRR Tier Performance
df4 = pd.read_sql("""
    SELECT irr_tier, symbol,
           ROUND(AVG(profit_per_share)::numeric, 4) as avg_profit
    FROM arbitrage_records
    GROUP BY irr_tier, symbol
    ORDER BY symbol, avg_profit DESC
""", conn)

plt.figure(figsize=(10, 5))
sns.barplot(data=df4, x="irr_tier", y="avg_profit", hue="symbol", palette="coolwarm")
plt.title("Average Profit per Share by IRR Tier", fontsize=14, fontweight="bold")
plt.xlabel("IRR Tier")
plt.ylabel("Avg Profit Per Share (₹)")
plt.tight_layout()
plt.savefig("outputs/chart4_irr_tier_performance.png")
plt.close()
print("✅ Chart 4 saved")

# ── Chart 5: Top 10 Strike Combinations for PNB
df5 = pd.read_sql("""
    SELECT CONCAT(strike_low::int, '/', strike_high::int) as strikes,
           ROUND(AVG(total_paper_profit)::numeric, 2) as avg_profit
    FROM arbitrage_records
    WHERE symbol = 'PNB'
    GROUP BY strike_low, strike_high
    ORDER BY avg_profit DESC
    LIMIT 10
""", conn)

plt.figure(figsize=(12, 5))
sns.barplot(data=df5, x="strikes", y="avg_profit", palette="viridis")
plt.title("Top 10 Strike Combinations for PNB", fontsize=14, fontweight="bold")
plt.xlabel("Strike Combination (Low/High)")
plt.ylabel("Avg Profit (₹)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("outputs/chart5_top_strikes_pnb.png")
plt.close()
print("✅ Chart 5 saved")

conn.close()
print("\n🎉 All charts saved in outputs/ folder!")