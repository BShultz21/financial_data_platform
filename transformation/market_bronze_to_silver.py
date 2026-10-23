from pathlib import Path
import duckdb

directory_root = str(Path(__file__).parent.parent)

def create_bronze_level_table(data_path):
    duckdb.sql(F"CREATE OR REPLACE TABLE bronze_historical_market_table AS SELECT * FROM '{data_path}'")
    return None


def create_silver_parquet_file(output_path):
    duckdb.sql("COPY("
               "WITH UNNEST_DATA AS ((SELECT * EXCLUDE(api_data), unnest(api_data, recursive := true) FROM bronze_historical_market_table))"
                       "SELECT CAST(load_date AS TIMESTAMP) as load_date, "
                             "CAST(symbol AS VARCHAR) as symbol, "
                             "CAST(date AS TIMESTAMP) as trade_date,"
                             "CAST(close AS DOUBLE) as close_price,"
                             "CAST(high as DOUBLE) as high_price,"
                             "CAST(low AS DOUBLE) as low_price,"
                             "CAST(open AS DOUBLE) as open_price, "
                             "CAST(volume AS UHUGEINT) as Volume ,"
                             "CAST(adjClose AS DOUBLE) as adjClose, "
                             "CAST(adjHigh AS DOUBLE) as adjHigh, "
                             "CAST(adjLow AS DOUBLE) as adjLow, "
                             "CAST(adjOpen AS DOUBLE) as adjOpen, "
                             "CAST(adjVolume AS UHUGEINT) as adjVolume, "
                             "CAST(divCash AS DOUBLE) as divCash,"
                             "CAST(splitFactor AS DOUBLE) as splitFactor"
                             " FROM UNNEST_DATA)"
                     f" TO '{output_path}'")
    return None

if __name__ == '__main__':
    create_bronze_level_table(directory_root + '/storage/bronze/historical_market_data.parquet')
    path = directory_root + "/storage/silver/historical_market_data.parquet"
    create_silver_parquet_file(path)