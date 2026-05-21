import os
import sys

os.environ["HADOOP_HOME"] = "C:\\hadoop"
os.environ["PATH"] = os.environ["PATH"] + ";C:\\hadoop\\bin"
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, split, trim, regexp_replace, to_date
import pandas as pd
import glob

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("ArbitragePipeline") \
    .config("spark.jars.packages", "org.postgresql:postgresql:42.6.0") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

all_files = glob.glob("/opt/data/*.csv")
print(f"Found {len(all_files)} files: {all_files}")

dfs = []
for file in all_files:
    df = pd.read_csv(file)
    df["file_name"] = os.path.basename(file)
    dfs.append(df)

combined_df = pd.concat(dfs, ignore_index=True)
print(f"Total rows loaded: {len(combined_df)}")

# ── Convert to Spark DataFrame
sdf = spark.createDataFrame(combined_df)
sdf.printSchema()
print(f"Total rows in Spark: {sdf.count()}")

# ── Rename columns
sdf = sdf.withColumnRenamed("Date", "date") \
         .withColumnRenamed("Timestamp", "timestamp") \
         .withColumnRenamed("Symbol", "symbol") \
         .withColumnRenamed("Expiry", "expiry") \
         .withColumnRenamed("Strikes (Low/High)", "strikes") \
         .withColumnRenamed("Buy Low CE (Ask)", "buy_low_ce") \
         .withColumnRenamed("Sell High CE (Bid)", "sell_high_ce") \
         .withColumnRenamed("Buy High PE (Ask)", "buy_high_pe") \
         .withColumnRenamed("Sell Low PE (Bid)", "sell_low_pe") \
         .withColumnRenamed("Net Exec Cost", "net_exec_cost") \
         .withColumnRenamed("Theoretical Value", "theoretical_value") \
         .withColumnRenamed("IRR Tier Achieved", "irr_tier") \
         .withColumnRenamed("Target Mismatch (For Tier)", "target_mismatch") \
         .withColumnRenamed("Profit Per Share", "profit_per_share") \
         .withColumnRenamed("Total Paper Profit", "total_paper_profit")

# ── Split Strikes
sdf = sdf.withColumn("strike_low", split(col("strikes"), "/").getItem(0).cast("double")) \
         .withColumn("strike_high", split(col("strikes"), "/").getItem(1).cast("double")) \
         .drop("strikes")

# ── Clean symbol column
sdf = sdf.withColumn("symbol", trim(col("symbol")))

# ── Cast date and expiry to proper date format
sdf = sdf.withColumn("date", to_date(col("date"), "dd-MM-yyyy"))
sdf = sdf.withColumn("expiry", to_date(col("expiry"), "dd-MM-yyyy"))

# ── Clean total_paper_profit
sdf = sdf.withColumn("total_paper_profit",
    regexp_replace(col("total_paper_profit").cast("string"), ",", "").cast("double"))

# ── Drop rows where symbol is null
sdf = sdf.filter(col("symbol").isNotNull())

print("Sample cleaned data:")
sdf.show(5)

# ── Write to PostgreSQL
print("Writing to PostgreSQL...")
sdf.write \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://arbitrage_postgres:5432/arbitrage_db") \
    .option("dbtable", "arbitrage_records") \
    .option("user", "admin") \
    .option("password", "admin123") \
    .option("driver", "org.postgresql.Driver") \
    .mode("append") \
    .save()

print("✅ Data successfully written to PostgreSQL!")
spark.stop()