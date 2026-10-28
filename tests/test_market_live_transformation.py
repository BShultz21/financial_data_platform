import duckdb
import pyarrow.parquet as pq
from transformation import market_bronze_to_silver as mkt_transformation

def test_create_bronze_live_market_sql_table(tmp_path, bronze_live_market_data_parquet):
    path = tmp_path / "storage" / "bronze" / "live_market_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)

    mkt_transformation.create_bronze_live_market_table(path)
    bronze_sql_rows = duckdb.sql("SELECT count(*) FROM bronze_live_market").fetchone()[0]
    bronze_parquet_table = pq.read_table(path)
    assert bronze_sql_rows == bronze_parquet_table.num_rows

def test_create_silver_live_market_parquet(tmp_path, bronze_live_market_data_sql_table):
    path = tmp_path / "storage" / "silver" / "live_market_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)

    mkt_transformation.create_silver_live_market_parquet(path)
    assert path.is_file()
    silver_parquet_table = pq.read_table(path)
    assert silver_parquet_table.num_rows == 3

def test_silver_live_market_datatypes(tmp_path, silver_live_market_parquet):
    path = tmp_path / "storage" / "silver" / "live_market_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)

    silver_table = duckdb.sql(f"SELECT * FROM '{path}'")
    schema = dict(zip(silver_table.columns, [str(item) for item in silver_table.dtypes]))

    assert schema == {
            "load_date": "TIMESTAMP",
            "ticker": "VARCHAR",
            "timestamp": "TIMESTAMP",
            "open_price": "DOUBLE",
            "high_price": "DOUBLE",
            "low_price" : "DOUBLE",
            "tngoLast": "DOUBLE",
            "prevClose": "DOUBLE",
            "prevDate": "DATE",
            "volume": "DOUBLE",
            "lqSpread": "DOUBLE",
            "lqBidPrice": "DOUBLE",
            "lqBidSize": "INTEGER",
            "lqRefPrice": "DOUBLE",
            "lqAskPrice": "DOUBLE",
            "lqAskSize": "DOUBLE"
        }

def test_silver_live_market_duplicates(tmp_path, silver_live_market_parquet):
    path = tmp_path / "storage" / "silver" / "live_market_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)

    dupes = duckdb.sql(f"""
        SELECT count(*) FROM (
            SELECT ticker, timestamp FROM '{path}'
            GROUP BY 1, 2 HAVING count(*) > 1)
    """).fetchone()[0]
    assert dupes == 0