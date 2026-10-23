import datetime

import requests
from requests import HTTPError
import duckdb
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from pandas.io.sql import table_exists
from pyarrow import table, DataType

from ingestion.historical_market_data_handler import HistoricalMarketDataHandler
from transformation import sec_bronze_to_silver as sec
from transformation import market_bronze_to_silver as mkt_transformation
from ingestion import historical_market_data_handler as mkt_handler


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

    mkt_transformation.create_bronze_level_table(path)
    bronze_sql_rows = duckdb.sql("SELECT count(*) FROM bronze_historical_market_table").fetchone()[0]
    bronze_parquet_table = pq.read_table(path)
    assert bronze_sql_rows == bronze_parquet_table.num_rows

def test_create_silver_market_parquet(tmp_path, bronze_market_data_sql_table):
    path = tmp_path / "storage" / "silver" / "historical_market_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)

    mkt_transformation.create_silver_parquet_file(path)
    assert path.is_file()
    silver_parquet_table = pq.read_table(path)
    assert silver_parquet_table.num_rows == 4

"""
def test_silver_market_datatypes(tmp_path, silver_market_parquet):
    path = tmp_path / "storage" / "silver" / "historical_market_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)

    silver_table = duckdb.sql(f"SELECT * FROM '{path}'")
    print(silver_table.columns)
    print(silver_table.
"""