import requests
import pyarrow.parquet as pq
import pytest
from ingestion.market_data_handler import MarketDataHandler

def test_good_live_market_call():
    handler = MarketDataHandler()
    handler.load_api_key()
    response = handler.get_data(['AAPL', 'TSLA','MSFT'])
    assert response.status_code == 200

def test_bad_live_market_call():
    handler = MarketDataHandler()
    handler.load_api_key()
    with pytest.raises(requests.HTTPError):
        handler.get_data(['adfsd'])

def test_bronze_live_market_data_parquet(tmp_path, live_market_data):
    path = tmp_path / "storage" / "bronze" / "live_market_data.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    handler = MarketDataHandler()
    handler.write_to_parquet(live_market_data, path)

    assert path.is_file()
    table = pq.read_table(path)
    assert table.num_rows == len(live_market_data)