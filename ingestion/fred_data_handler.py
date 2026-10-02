import os
import requests
from dotenv import load_dotenv
import pyarrow as pa
import pyarrow.parquet as pq
import datetime as dt


class FredDataHandler:
    def __init__(self):
        self.api_key = None
        self.url = None

    def load_api_key(self):
        load_dotenv()
        self.api_key = os.getenv("FRED_API_KEY")

    def set_url(self, series):
        self.url = (f'https://api.stlouisfed.org/fred/series/observations?series_id={series}'
                    f'&observation_start=2000-01-01&api_key={self.api_key}&file_type=json')

    def call_api(self, series):
        self.set_url(series)
        response = requests.get(self.url)
        return response.json()

    def write_to_parquet(self, data):
        table = pa.Table.from_pylist(data)
        pq.write_table(table,'C:/Users/Braden/Documents/Python/financial_data_platform/storage/bronze/fred_data.parquet')

if __name__ == '__main__':
    handler = FredDataHandler()
    handler.load_api_key()
    metrics = ['DRCCLACBS', 'CPIAUCSL', 'UNRATE', 'MORTGAGE30US', 'TOTALSL', 'TDSP', 'DGS10', 'DGS30', 'DGS2', 'DGS5','DGS3MO',
               'DFII5', 'DFII7', 'DFII10', 'DFII20', 'DFII30']
    bronze_data = []
    for metric in metrics:
        api_response = handler.call_api(metric)
        retrieved_data = {'load_date': dt.date.today(), 'metric': metric, 'api_data': api_response}
        bronze_data.append(retrieved_data)
    handler.write_to_parquet(bronze_data)
