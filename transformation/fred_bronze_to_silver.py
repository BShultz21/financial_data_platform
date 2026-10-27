from pathlib import Path
import duckdb

directory_root = str(Path(__file__).parent.parent)

def create_bronze_level_fred_table(data_path):
    duckdb.sql(F"CREATE OR REPLACE TABLE bronze_fred_table AS SELECT * FROM '{data_path}'")
    return None

def create_silver_layer_fred_parquet(output_path):
    duckdb.sql("COPY("
            "WITH UNNEST_CTE1 AS (SELECT * EXCLUDE(api_data), unnest(api_data, recursive := true) FROM bronze_fred_table)"
               ", UNNEST_CTE2 AS (SELECT * EXCLUDE(observations), unnest(observations, recursive := true) FROM UNNEST_CTE1)"
               " SELECT "
               "CAST (load_date AS TIMESTAMP) as load_date,"
               "CAST (metric as VARCHAR) AS metric,"
               "CAST (realtime_start as DATE) as realtime_start,"
               "CAST (realtime_end AS DATE) AS realtime_end,"
               "CAST (observation_start AS DATE) as observation_start,"
               "CAST (observation_end  AS DATE) AS observation_end,"
               "CAST (units as VARCHAR) AS units,"
               "CAST (output_type as int) as output_type,"
               "CAST (file_type as VARCHAR) AS file_type,"
               "CAST (order_by AS VARCHAR) AS order_by,"
               "CAST (sort_order as VARCHAR) AS sort_order,"
               "CAST (count as INT) as count,"
               "CAST (UNNEST_CTE2.offset as INT) as 'offset',"
               "CAST (UNNEST_CTE2.limit as BIGINT) as 'limit',"
               "CAST (date as DATE) as observation_date,"
               "CAST (value as DOUBLE) as value"
               " FROM UNNEST_CTE2"
               " QUALIFY ROW_NUMBER() OVER (PARTITION BY metric, date ORDER BY load_date DESC) = 1)"
               f" TO '{output_path}'")