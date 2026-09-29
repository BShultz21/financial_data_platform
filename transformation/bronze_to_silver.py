from pathlib import Path
import duckdb

path = str(Path(__file__).parent.parent) + '/storage/bronze/result.parquet'

def bronze_to_silver_transformation():
    duckdb.sql(F"CREATE TABLE bronze_table AS SELECT * FROM '{path}'")
    print(duckdb.sql("SELECT load_date, symbol, unnest(stock_data, recursive := true) FROM bronze_table"))

if __name__ == '__main__':
    bronze_to_silver_transformation()