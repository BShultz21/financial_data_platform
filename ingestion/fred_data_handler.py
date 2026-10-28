import os
from idlelib.rpc import request_queue

import requests
from dotenv import load_dotenv
import pyarrow as pa
import pyarrow.parquet as pq
import datetime as dt
from pathlib import Path


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
        if response.status_code != 200:
            raise requests.HTTPError
        return response

    def write_to_parquet(self, data, file_path):
        if type(data) is list:
            table = pa.Table.from_pylist(data)
            pq.write_to_dataset(table, file_path, partition_cols=['load_date'],
                                existing_data_behavior="delete_matching")
        else:
            raise TypeError

if __name__ == '__main__':
    handler = FredDataHandler()
    handler.load_api_key()
    metrics = ['DRCCLACBS', 'CPIAUCSL', 'UNRATE', 'MORTGAGE30US']
    bronze_data = []
    for metric in metrics:
        api_response = handler.call_api(metric)
        retrieved_data = {'load_date': dt.date.today(), 'metric': metric, 'api_data': api_response.json()}
        bronze_data.append(retrieved_data)
    file_path = Path(str(Path(__file__).parent.parent) + '/storage/bronze/fred/')
    handler.write_to_parquet(bronze_data, file_path)



