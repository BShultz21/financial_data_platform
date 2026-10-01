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

    def write_to_parquet(self, data):
        table = pa.Table.from_pylist(data)
        pq.write_table(table,'C:/Users/Braden/Documents/Python/financial_data_platform/storage/bronze/sec_data.parquet')

if __name__ == '__main__':
    data_handler = SECDataHandler()
    data_handler.load_user_agent_credentials()
    CIKs = ['0000320193', '0000019617','0000789019','0000070858','0001018724']
    bronze_data = []
    for CIK in CIKs:
        api_response = data_handler.call_api(CIK)
        retrieved_data = {'load_date': dt.date.today(), 'cik': CIK, 'api_data': api_response}
        bronze_data.append(retrieved_data)
    data_handler.write_to_parquet(bronze_data)