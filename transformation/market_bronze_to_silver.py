from pathlib import Path
import duckdb

directory_root = str(Path(__file__).parent.parent)

def historical_market_bronze_to_silver_transformation():
    path = directory_root + '/storage/bronze/historical_stock_data.parquet'
    duckdb.sql(F"CREATE TABLE bronze_historical_market_table AS SELECT * FROM '{path}'")
    duckdb.sql("COPY (SELECT * EXCLUDE(api_data), unnest(api_data, recursive := true) FROM bronze_historical_market_table)"
                     f" TO '{directory_root}/storage/silver/historical_stock_data.parquet'")