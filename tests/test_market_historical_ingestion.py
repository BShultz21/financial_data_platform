import requests
import pyarrow.parquet as pq
import pytest
from ingestion.market_data_handler import MarketDataHandler


def test_good_historical_market_call():
    handler = MarketDataHandler()
    handler.load_api_key()
    response = handler.get_historical_data('MSFT')
    assert response.status_code == 200

def test_bad_historical_market_call():
    handler = MarketDataHandler()
    handler.load_api_key()
    with pytest.raises(requests.HTTPError):
        handler.get_historical_data('adfsd')

def test_create_bronze_historical_market_parquet_file(tmp_path,historical_market_data):
    path = tmp_path / "storage" / "bronze" / "historical_market_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    handler = MarketDataHandler()
    handler.write_to_parquet(historical_market_data,path)

    assert path.is_file()
    table = pq.read_table(path)
    assert table.num_rows == len(historical_market_data)