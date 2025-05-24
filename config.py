### ichimoku_bot/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Example config values
OANDA_API_KEY = os.getenv("OANDA_API_KEY")
ACCOUNT_ID = os.getenv("ACCOUNT_ID")
PAIR = "EUR_USD"
GRANULARITY = "M15"