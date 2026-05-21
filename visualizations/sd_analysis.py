import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
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

# ── Fetch data
df = pd.read_sql("""
    SELECT date, timestamp, symbol, strike_low, strike_high,
           profit_per_share, total_paper_profit, irr_tier
    FROM arbitrage_records
    ORDER BY symbol, date, timestamp
""", conn)
conn.close()

# ── Process each symbol separately
for symbol in ["IDEA", "PNB"]:
    print(f"\n📊 Analyzing {symbol}...")

    sdf = df[df["symbol"] == symbol].copy().reset_index(drop=True)

    # ── Calculate rolling SD (window of 10 trades)
    sdf["rolling_sd"] = sdf["profit_per_share"].rolling(window=10).std()

    # ── SD direction — is it going up or down?
    sdf["sd_direction"] = sdf["rolling_sd"].diff()

    # ── Generate signals
    sdf["signal"] = "HOLD"
    sdf.loc[sdf["sd_direction"] < 0, "signal"] = "BUY"   # SD decreasing
    sdf.loc[sdf["sd_direction"] > 0, "signal"] = "SELL"  # SD increasing

    # ── Print summary
    signal_counts = sdf["signal"].value_counts()
    print(f"Signal Summary for {symbol}:")
    print(signal_counts)

    # ── Print BUY signal patterns
    buy_signals = sdf[sdf["signal"] == "BUY"]
    print(f"\nTop BUY signal patterns for {symbol}:")
    print(buy_signals.groupby(["irr_tier"])["profit_per_share"].mean().sort_values(ascending=False))

    # ── Chart — Rolling SD with Buy/Sell signals
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    # Plot profit per share
    ax1.plot(sdf.index, sdf["profit_per_share"], color="steelblue", linewidth=1, label="Profit per Share")
    ax1.scatter(sdf[sdf["signal"] == "BUY"].index,
                sdf[sdf["signal"] == "BUY"]["profit_per_share"],
                color="green", marker="^", s=50, label="BUY", zorder=5)
    ax1.scatter(sdf[sdf["signal"] == "SELL"].index,
                sdf[sdf["signal"] == "SELL"]["profit_per_share"],
                color="red", marker="v", s=50, label="SELL", zorder=5)
    ax1.set_title(f"{symbol} — Profit per Share with BUY/SELL Signals", fontweight="bold")
    ax1.set_ylabel("Profit per Share (₹)")
    ax1.legend()

    # Plot Rolling SD
    ax2.plot(sdf.index, sdf["rolling_sd"], color="orange", linewidth=1.5, label="Rolling SD (window=10)")
    ax2.axhline(y=sdf["rolling_sd"].mean(), color="red", linestyle="--", alpha=0.7, label="Mean SD")
    ax2.set_title(f"{symbol} — Rolling Standard Deviation", fontweight="bold")
    ax2.set_ylabel("Standard Deviation")
    ax2.set_xlabel("Trade Index")
    ax2.legend()

    plt.tight_layout()
    plt.savefig(f"outputs/sd_analysis_{symbol}.png", dpi=150)
    plt.close()
    print(f"✅ Chart saved for {symbol}")

# ── Combine both symbols for table and Excel export
all_signals = []

for symbol in ["IDEA", "PNB"]:
    sdf = df[df["symbol"] == symbol].copy().reset_index(drop=True)
    sdf["rolling_sd"] = sdf["profit_per_share"].rolling(window=10).std()
    sdf["sd_direction"] = sdf["rolling_sd"].diff()
    sdf["signal"] = "HOLD"
    sdf.loc[sdf["sd_direction"] < 0, "signal"] = "BUY"
    sdf.loc[sdf["sd_direction"] > 0, "signal"] = "SELL"
    all_signals.append(sdf)

final_df = pd.concat(all_signals, ignore_index=True)

# ── Clean up table for display
table_df = final_df[["date", "timestamp", "symbol", "strike_low", "strike_high",
                      "profit_per_share", "rolling_sd", "signal"]].copy()
table_df["rolling_sd"] = table_df["rolling_sd"].round(6)
table_df["profit_per_share"] = table_df["profit_per_share"].round(4)

# ── Print sample table in terminal
print("\n📋 Sample Signal Table (first 20 rows):")
print(table_df.head(20).to_string(index=False))

print("\n📋 BUY Signals Sample:")
print(table_df[table_df["signal"] == "BUY"].head(10).to_string(index=False))

print("\n📋 SELL Signals Sample:")
print(table_df[table_df["signal"] == "SELL"].head(10).to_string(index=False))

# ── Export separate Excel files for IDEA and PNB
for symbol in ["IDEA", "PNB"]:
    symbol_df = table_df[table_df["symbol"] == symbol]
    excel_path = f"outputs/signal_analysis_{symbol}.xlsx"
    
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        symbol_df.to_excel(writer, sheet_name="All Signals", index=False)
        symbol_df[symbol_df["signal"] == "BUY"].to_excel(writer, sheet_name="BUY Signals", index=False)
        symbol_df[symbol_df["signal"] == "SELL"].to_excel(writer, sheet_name="SELL Signals", index=False)
        symbol_df[symbol_df["signal"] == "HOLD"].to_excel(writer, sheet_name="HOLD Signals", index=False)
    
    print(f"✅ Excel exported for {symbol} → {excel_path}")
print("\n🎉 SD Analysis complete! Check outputs/ folder!")