from pathlib import Path
import duckdb

path = str(Path(__file__).parent.parent) + '/storage/bronze/fred_data.parquet'

def bronze_to_silver_transformation():
    duckdb.sql(F"CREATE TABLE bronze_table AS SELECT * FROM '{path}'")
    print(duckdb.sql("SELECT * EXCLUDE(api_data), unnest(api_data, recursive := true) FROM bronze_table"))

if __name__ == '__main__':
    bronze_to_silver_transformation()