import os

import requests
from dotenv import load_dotenv

class historical_market_data_handler():
    def __init__(self):
        self.url = 'https://data.alpaca.markets/v2/stocks/bars'
        self.api_key = None
        self.secret_key = None

    def load_api_key(self):
        load_dotenv()
        self.api_key = os.getenv("ALPACA_PUBLIC_KEY")
        self.secret_key = os.getenv("ALPACA_SECRET_KEY")

if __name__ == "__main__":
    handler = historical_market_data_handler()
    handler.load_api_key()
    print(handler.api_key)