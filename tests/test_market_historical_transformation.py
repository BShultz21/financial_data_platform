import duckdb
import pyarrow.parquet as pq
from transformation import market_bronze_to_silver as mkt_transformation


def test_create_bronze_historical_market_sql_table(tmp_path, bronze_historical_market_data_parquet):
    path = tmp_path / "storage" / "bronze" / "historical_market_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)

    mkt_transformation.create_bronze_historical_market_table(path)
    bronze_sql_rows = duckdb.sql("SELECT count(*) FROM bronze_historical_market").fetchone()[0]
    bronze_parquet_table = pq.read_table(path)
    assert bronze_sql_rows == bronze_parquet_table.num_rows

def test_create_silver_historical_market_parquet(tmp_path, bronze_historical_market_data_sql_table):
    path = tmp_path / "storage" / "silver" / "historical_market_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)

    mkt_transformation.create_silver_historical_market_parquet(path)
    assert path.is_file()
    silver_parquet_table = pq.read_table(path)
    assert silver_parquet_table.num_rows == 4

def test_silver_historical_market_datatypes(tmp_path, silver_historical_market_parquet):
    path = tmp_path / "storage" / "silver" / "historical_market_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)

    silver_table = duckdb.sql(f"SELECT * FROM '{path}'")
    schema = dict(zip(silver_table.columns, [str(item) for item in silver_table.dtypes]))

    assert schema == {
            "load_date": "TIMESTAMP",
            "symbol": "VARCHAR",
            "trade_date": "TIMESTAMP",
            "close_price": "DOUBLE",
            "high_price": "DOUBLE",
            "low_price": "DOUBLE",
            "open_price": "DOUBLE",
            "volume": "BIGINT",
            "adjClose": "DOUBLE",
            "adjHigh": "DOUBLE",
            "adjLow": "DOUBLE",
            "adjOpen": "DOUBLE",
            "adjVolume": "BIGINT",
            "divCash": "DOUBLE",
            "splitFactor": "DOUBLE",
        }

def test_silver_historical_market_duplicates(tmp_path, duplicate_historical_silver_market_parquet):
    path = tmp_path / "storage" / "silver" / "historical_market_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)

    dupes = duckdb.sql(f"""
        SELECT count(*) FROM (
            SELECT symbol, trade_date FROM '{path}'
            GROUP BY 1, 2 HAVING count(*) > 1)
    """).fetchone()[0]
    assert dupes == 0