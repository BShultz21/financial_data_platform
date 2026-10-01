from pathlib import Path
import duckdb

directory_root = str(Path(__file__).parent.parent)

def fred_bronze_to_silver_transformation():
    path = directory_root + '/storage/bronze/fred_data.parquet'
    duckdb.sql(F"CREATE TABLE bronze_table AS SELECT * FROM '{path}'")
    duckdb.sql("COPY (WITH CTE AS (SELECT * EXCLUDE(api_data), unnest(api_data, recursive := true) FROM bronze_table)"
                "SELECT * EXCLUDE(observations), unnest(observations, recursive := true) FROM CTE)"
               f" TO '{directory_root}/storage/silver/fred_data.parquet'" )

def historical_market_bronze_to_silver_transformation():
    path = directory_root + '/storage/bronze/historical_stock_data.parquet'
    duckdb.sql(F"CREATE TABLE bronze_table AS SELECT * FROM '{path}'")
    print(duckdb.sql("SELECT * EXCLUDE(api_data), unnest(api_data, recursive := true) FROM bronze_table"))

if __name__ == '__main__':
    fred_bronze_to_silver_transformation()