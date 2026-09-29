import os
import requests
from dotenv import load_dotenv
import pyarrow as pa
import pyarrow.parquet as pq

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
        response= requests.get(self.url,headers=headers)
        return response.json()

    def write_to_parquet(self, data):
        table = pa.Table.from_pylist(data)
        pq.write_table(table,'C:/Users/Braden/Documents/Python/financial_data_platform/result.parquet')

if __name__ == "__main__":
    handler = HistoricalMarketDataHandler()
    handler.load_api_key()
    response = handler.call_api('aapl')
    handler.write_to_parquet(response)