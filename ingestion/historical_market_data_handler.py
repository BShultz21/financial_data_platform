import os
import requests
from dotenv import load_dotenv
import pyarrow as pa
import pyarrow.parquet as pq
import datetime as dt
from pathlib import Path

class HistoricalMarketDataHandler():
    def __init__(self):
        self.api_key = None
        self.url = None

    def load_api_key(self):
        load_dotenv()
        self.api_key = os.getenv("TIINGO_KEY")


    def call_api(self, ticker):
        headers = {
            'Content-Type': 'application/json'
        }
        self.url = f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?startDate=2000-01-02&token={self.api_key}"
        response = requests.get(self.url,headers=headers)
        if response.status_code != 200:
            raise requests.HTTPError
        return response

    def write_to_parquet(self, data, file_path):
        table = pa.Table.from_pylist(data)
        pq.write_table(table,file_path)

if __name__ == "__main__":
    handler = HistoricalMarketDataHandler()
    handler.load_api_key()
    tickers = ['msft']
    bronze_data = []
    for ticker in tickers:
        response = handler.call_api(ticker)
        retrieved_data = {'load_date': dt.date.today(), 'symbol': ticker, 'api_data': response.json()}
        bronze_data.append(retrieved_data)
    file_path = Path(str(Path(__file__).parent.parent) + '/storage/bronze/historical_market_data.parquet')
    handler.write_to_parquet(bronze_data, file_path)