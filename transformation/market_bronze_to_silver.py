from pathlib import Path
import duckdb

directory_root = str(Path(__file__).parent.parent)

def create_bronze_historical_market_table(data_path):
    duckdb.sql(F"CREATE OR REPLACE TABLE bronze_historical_market AS SELECT * FROM '{data_path}'")
    return None

def create_bronze_live_market_table(data_path):
    duckdb.sql(F"CREATE OR REPLACE TABLE bronze_live_market AS SELECT * FROM '{data_path}'")
    return None

def create_silver_live_market_parquet(output_path):
    duckdb.sql("COPY("
               "WITH UNNEST_DATA AS ((SELECT * EXCLUDE(api_data), unnest(api_data, recursive := true) FROM bronze_live_market))"
               ",DATA_TYPE_CONVERSION AS ("
                       "SELECT CAST(load_date AS TIMESTAMP) as load_date, "
                             "CAST(ticker AS VARCHAR) as ticker, "
                             "CAST(timestamp AS TIMESTAMP) as timestamp,"
                             "CAST(open AS DOUBLE) as open_price,"
                             "CAST(high as DOUBLE) as high_price,"
                             "CAST(low AS DOUBLE) as low_price,"
                             "CAST(tngoLast AS DOUBLE) as tngoLast, "
                             "CAST(prevClose AS DOUBLE) as prevClose ,"
                             "CAST(prevDate AS DATE) as prevDate, "
                             "CAST(volume AS DOUBLE) as volume, "
                             "CAST(lqSpread AS DOUBLE) as lqSpread, "
                             "CAST(lqBidPrice AS DOUBLE) as lqBidPrice, "
                             "CAST(lqBidSize AS INT) as lqBidSize, "
                             "CAST(lqRefPrice AS DOUBLE) as lqRefPrice,"
                             "CAST(lqAskPrice AS DOUBLE) as lqAskPrice, "
                             "CAST(lqAskSize AS DOUBLE) as lqAskSize"
                             " FROM UNNEST_DATA)"
                     f" SELECT * FROM DATA_TYPE_CONVERSION QUALIFY ROW_NUMBER() OVER (PARTITION BY ticker, timestamp ORDER BY load_date DESC) = 1) TO '{output_path}'")

def create_silver_historical_market_parquet(output_path):
    duckdb.sql("COPY("
               "WITH UNNEST_DATA AS ((SELECT * EXCLUDE(api_data), unnest(api_data, recursive := true) FROM bronze_historical_market))"
               ",DATA_TYPE_CONVERSION AS ("
                       "SELECT CAST(load_date AS TIMESTAMP) as load_date, "
                             "CAST(symbol AS VARCHAR) as symbol, "
                             "CAST(date AS TIMESTAMP) as trade_date,"
                             "CAST(close AS DOUBLE) as close_price,"
                             "CAST(high as DOUBLE) as high_price,"
                             "CAST(low AS DOUBLE) as low_price,"
                             "CAST(open AS DOUBLE) as open_price, "
                             "CAST(volume AS BIGINT) as volume ,"
                             "CAST(adjClose AS DOUBLE) as adjClose, "
                             "CAST(adjHigh AS DOUBLE) as adjHigh, "
                             "CAST(adjLow AS DOUBLE) as adjLow, "
                             "CAST(adjOpen AS DOUBLE) as adjOpen, "
                             "CAST(adjVolume AS BIGINT) as adjVolume, "
                             "CAST(divCash AS DOUBLE) as divCash,"
                             "CAST(splitFactor AS DOUBLE) as splitFactor"
                             " FROM UNNEST_DATA)"
                     f" SELECT * FROM DATA_TYPE_CONVERSION QUALIFY ROW_NUMBER() OVER (PARTITION BY symbol, trade_date ORDER BY load_date DESC) = 1) TO '{output_path}'")
    return None
