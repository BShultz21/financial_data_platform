import duckdb
import pyarrow.parquet as pq
from transformation import fred_bronze_to_silver as fred_transformation

def test_write_fred_to_bronze_sql_table(tmp_path, bronze_fred_parquet):
    path = tmp_path / "storage" / "bronze" / "fred_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)

    fred_transformation.create_bronze_level_fred_table(path)
    bronze_rows = duckdb.sql("SELECT COUNT(*) FROM bronze_fred_table").fetchone()[0]
    bronze_parquet = pq.read_table(path)

    assert bronze_rows == bronze_parquet.num_rows

def test_create_silver_fred_parquet(tmp_path, bronze_fred_sql_table):
    path = tmp_path / "storage" / "silver" / "fred_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)

    fred_transformation.create_silver_layer_fred_parquet(path)
    assert path.is_file()
    silver_parquet_file = pq.read_table(path)
    assert silver_parquet_file.num_rows == 8

def test_silver_fred_datatypes(tmp_path, silver_fred_parquet):
    path = tmp_path / "storage" / "silver" / "fred_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)

    silver_table = duckdb.sql(f"SELECT * FROM '{path}'")
    schema = dict(zip(silver_table.columns, [str(item) for item in silver_table.dtypes]))

    assert schema =={
        'load_date' : 'TIMESTAMP',
        'metric': 'VARCHAR',
        'realtime_start': 'DATE',
        'realtime_end': 'DATE',
        'observation_start': 'DATE',
        'observation_end': 'DATE',
        'units': 'VARCHAR',
        'output_type': 'INTEGER',
        'file_type': 'VARCHAR',
        'order_by': 'VARCHAR',
        'sort_order': 'VARCHAR',
        'count': 'INTEGER',
        'offset': 'INTEGER',
        'limit': 'BIGINT',
        'observation_date': 'DATE',
        'value': 'DOUBLE'
    }

def test_silver_fred_duplicates(tmp_path, silver_duplicate_fred_parquet):
    path = tmp_path / "storage" / "silver" / "fred_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)

    dupes = duckdb.sql(f"""
        SELECT count(*) FROM (
            SELECT metric, observation_date FROM '{path}'
            GROUP BY 1, 2 HAVING count(*) > 1)
    """).fetchone()[0]
    assert dupes == 0