import datetime
import requests
import duckdb
import pyarrow.parquet as pq
import pytest
from ingestion.historical_market_data_handler import HistoricalMarketDataHandler
from transformation import sec_bronze_to_silver as sec
from transformation import market_bronze_to_silver as mkt_transformation
from transformation import fred_bronze_to_silver as fred_transformation
import ingestion.fred_data_handler as fred


def test_sec_flatten_element(sec_data):
    compiled_data = []
    for row in sec_data:
        data,row_count = sec.flatten_element(row)
        compiled_data.extend(data)

    assert len(compiled_data) == 10

def test__sec_every_row_has_identity_columns(sec_data):
    compiled_data = []
    for row in sec_data:
        data,row_count = sec.flatten_element(row)
        compiled_data.extend(data)

    for element in compiled_data:
        assert element['load_date'] == datetime.datetime(2026, 10, 19, 0, 0)
        assert element['cik']
        assert element['taxonomy'] == 'us-gaap'
        assert element['unit']
        assert element['conceptfact']

def test_sec_known_value(sec_data):
    compiled_data = []
    for row in sec_data:
        data,row_count = sec.flatten_element(row)
        compiled_data.extend(data)

    assert compiled_data[1]['conceptfact'] == 'AffordableHousingTaxCreditsAndOtherTaxBenefitsAmount'
    assert compiled_data[1]['value'] == 1200000000
    assert compiled_data[1]['accountnum'] == '0000019617-15-000464'

def test_sec_data_types(sec_data):
    compiled_data = []
    for row in sec_data:
        data,row_count = sec.flatten_element(row)
        compiled_data.extend(data)

    for element in compiled_data:
        assert type(element['load_date']) == datetime.datetime
        assert type(element['cik'] == int)
        assert type(element['taxonomy']) == str
        assert type(element['conceptfact']) == str
        assert type(element['unit']) == str
        if element['start_date']:
            assert type(element['start_date']) == datetime.datetime
        assert type(element['end_date']) == datetime.datetime
        assert type(element['value']) == float
        assert type(element['accountnum']) == str
        assert type(element['fy']) == int
        assert type(element['fp']) == str
        assert type(element['form']) == str
        assert type(element['filed']) == datetime.datetime
        if element['frame']:
            assert type(element['frame']) == str

def test_sec_data_quality(sec_data):
    compiled_data = []
    for row in sec_data:
        data,row_count = sec.flatten_element(row)
        compiled_data.extend(data)

    for element in compiled_data:
        if element['start_date']:
            assert element['end_date'] >= element['start_date']

        assert element['filed'] >= element['end_date']
        assert element['form'] in ['10-K', '10-Q', '8-K', '10-Q/A', '10-K/A']
        assert element['fp'] in ['FY', 'Q1', 'Q2', 'Q3', 'Q4']

def test_good_market_data_call_api():
    handler = HistoricalMarketDataHandler()
    handler.load_api_key()
    response = handler.call_api('MSFT')
    assert response.status_code == 200

def test_bad_market_data_call_api():
    handler = HistoricalMarketDataHandler()
    handler.load_api_key()
    with pytest.raises(requests.HTTPError):
        handler.call_api('adfsd')

def test_create_bronze_market_parquet_file(tmp_path,market_data):
    path = tmp_path / "storage" / "bronze" / "historical_market_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    handler = HistoricalMarketDataHandler()
    handler.write_to_parquet(market_data,path)

    assert path.is_file()
    table = pq.read_table(path)
    assert table.num_rows == len(market_data)

def test_create_bronze_market_sql_table(tmp_path, bronze_market_data_parquet):
    path = tmp_path / "storage" / "bronze" / "historical_market_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)

    mkt_transformation.create_bronze_level_market_table(path)
    bronze_sql_rows = duckdb.sql("SELECT count(*) FROM bronze_historical_market_table").fetchone()[0]
    bronze_parquet_table = pq.read_table(path)
    assert bronze_sql_rows == bronze_parquet_table.num_rows

def test_create_silver_market_parquet(tmp_path, bronze_market_data_sql_table):
    path = tmp_path / "storage" / "silver" / "historical_market_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)

    mkt_transformation.create_silver_market_parquet(path)
    assert path.is_file()
    silver_parquet_table = pq.read_table(path)
    assert silver_parquet_table.num_rows == 4


def test_silver_market_datatypes(tmp_path, silver_market_parquet):
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

def test_silver_market_duplicates(tmp_path, duplicate_silver_market_parquet):
    path = tmp_path / "storage" / "silver" / "historical_market_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)

    dupes = duckdb.sql(f"""
        SELECT count(*) FROM (
            SELECT symbol, trade_date FROM '{path}'
            GROUP BY 1, 2 HAVING count(*) > 1)
    """).fetchone()[0]
    assert dupes == 0

def test_good_fred_api_call():
    handler = fred.FredDataHandler()
    handler.load_api_key()
    response = handler.call_api('MORTGAGE30US')
    assert response.status_code == 200

def test_bad_fred_api_call():
    handler = fred.FredDataHandler()
    handler.load_api_key()
    with pytest.raises(requests.HTTPError):
        handler.call_api('adfsd')

def test_fred_write_to_bronze_parquet(tmp_path,fred_data):
    path = tmp_path / "storage" / "bronze" / "fred_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    handler = fred.FredDataHandler()
    handler.write_to_parquet(fred_data, path)

    assert path.is_file()
    table = pq.read_table(path)
    assert table.num_rows == len(fred_data)

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
