import os
import requests
from dotenv import load_dotenv
import pyarrow as pa
import pyarrow.parquet as pq
import datetime as dt


class SECDataHandler:
    def __init__(self):
        self.CIKs = {'AAPL': '0000320193', 'JPM': '0000019617', 'MSFT': '0000789019', 'BAC': '0000070858', 'AMZN': '0001018724'}
        self.headers = None

    def load_user_agent_credentials(self):
        load_dotenv()
        self.headers = {'User-Agent': f'{os.getenv('NAME')} {os.getenv('EMAIL_ADDRESS')}'}

    def call_api(self, cik):
        self.url = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json'
        response = requests.get(self.url, headers=self.headers)
        return response.json()['facts']['us-gaap']

    def add_metadata(self, data):
        compiled_data = []
        timestamp = dt.datetime.now(dt.timezone.utc)
        for item in data:
            row = [{'load_date': timestamp.strftime('%Y-%m-%d %H'),
                    'api_data': item}]
            compiled_data.append(row)

        print(compiled_data)
        return compiled_data

    def write_to_parquet(self, data):
        table = pa.Table.from_pylist(data)
        pq.write_table(table,'C:/Users/Braden/Documents/Python/financial_data_platform/storage/bronze/sec_data.parquet')

    def row_counter(self, api_response):
        row_count = 0
        for ConceptFact,Data in api_response.items():
            units = Data.get('units') if isinstance(Data, dict) else None
            if units is None:
                continue
            for unit, item in units.items():
                row_count += len(item or [])
        return row_count

if __name__ == '__main__':
    data_handler = SECDataHandler()
    data_handler.load_user_agent_credentials()
    CIKs = ['0000320193','0000019617','0000789019', '0000070858','0001018724']
    bronze_data = []
    for CIK in CIKs:
        api_response = data_handler.call_api(CIK)
        row_count = data_handler.row_counter(api_response)
        bronze_data.append(api_response)
    compiled_data = data_handler.add_metadata(bronze_data)
    data_handler.write_to_parquet(compiled_data)