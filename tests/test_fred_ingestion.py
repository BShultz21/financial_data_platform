import requests
import pyarrow.parquet as pq
import pytest
import ingestion.fred_data_handler as fred

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
