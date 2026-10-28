import datetime
import os
import requests
from dotenv import load_dotenv
import pyarrow as pa
import pyarrow.parquet as pq
import datetime as dt
from pathlib import Path

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

    def add_metadata_to_live_data(self, data):
        compiled_data = []
        for item in data:
            row = [{'load_date': datetime.datetime.now(datetime.timezone.utc), 'api_data': item}]
            compiled_data.extend(row)
        print(compiled_data)

    def write_to_parquet(self, data, file_path):
        if type(data) is list:
            table = pa.Table.from_pylist(data)
            pq.write_table(table,file_path)
        elif type(data) is dict:
            table = pa.Table.from_pydict(data)
            pq.write_table(table, file_path)
        else:
            raise TypeError

if __name__ == "__main__":
    handler = MarketDataHandler()
    handler.load_api_key()
    tickers = ['aapl', 'msft', 'jpm']
    bronze_data = []
    response = handler.get_data(tickers)
    handler.add_metadata_to_live_data(response.json())
    """
    for ticker in tickers:
        response = handler.call_api(ticker)
        retrieved_data = {'load_date': dt.date.today(), 'symbol': ticker, 'api_data': response.json()}
        bronze_data.append(retrieved_data)
    file_path = Path(str(Path(__file__).parent.parent) + '/storage/bronze/historical_market_data.parquet')
    handler.write_to_parquet(bronze_data, file_path)
    """