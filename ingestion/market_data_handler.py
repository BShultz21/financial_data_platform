import datetime
import os
import requests
from dotenv import load_dotenv
import pyarrow as pa
import pyarrow.parquet as pq
import datetime as dt
from pathlib import Path

from transformation.fred_bronze_to_silver import directory_root


class MarketDataHandler:
    def __init__(self):
        self.api_key = None
        self.url = None

    def load_api_key(self):
        load_dotenv()
        self.api_key = os.getenv("TIINGO_KEY")


    def get_historical_data(self, ticker):
        headers = {
            'Content-Type': 'application/json'
        }
        self.url = f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?startDate=2000-01-02&token={self.api_key}"
        response = requests.get(self.url,headers=headers)
        if response.status_code != 200:
            raise requests.HTTPError
        return response

    def get_data(self, tickers):
        ticker_string = ','.join(tickers)
        headers = {
            'Content-Type': 'application/json'
        }
        self.url = f"https://api.tiingo.com/tiingo/equity/intraday/?tickers={ticker_string}&token={self.api_key}"
        response = requests.get(self.url,headers=headers)
        if response.status_code != 200 or response.json() == []:
            print(response.text)
            raise requests.HTTPError
        return response

    def add_metadata(self, data):
        compiled_data = []
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        for item in data:
            row = [{'load_date': timestamp.strftime('%Y-%m-%d %H:%M'),
                    'api_data': item}]
            compiled_data.extend(row)

        return compiled_data

    def write_to_parquet(self, data, file_path):
        if type(data) is list:
            table = pa.Table.from_pylist(data)
            pq.write_to_dataset(table, file_path, partition_cols=['load_date'],
                                existing_data_behavior="delete_matching")
        else:
            raise TypeError

if __name__ == "__main__":
    handler = MarketDataHandler()
    handler.load_api_key()
    tickers = ['aapl', 'msft', 'jpm']
    bronze_data = []
    response = handler.get_data(tickers)
    data = handler.add_metadata(response.json())
    output_path = directory_root + "/storage/bronze/live_market/"
    handler.write_to_parquet(data, output_path)

    for ticker in tickers:
        response = handler.get_historical_data(ticker)
        bronze_data.append(response.json())
    historical_data = handler.add_metadata(bronze_data)
    file_path = Path(str(Path(__file__).parent.parent) + '/storage/bronze/historical_market/')
    handler.write_to_parquet(historical_data, file_path)
