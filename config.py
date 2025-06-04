# ichimoku_bot/config.py
# Environmental Variables / Broker Settings
# Instrument & Market Settings
# Standard Defaults & Behaviours
# Files Paths & Storage

# --- dependencies ---
import os
from dotenv import load_dotenv

# --- environment loading ---
load_dotenv()  # loads .env into os.environ

# --- broker settings ---
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
OANDA_ACCESS_TOKEN = os.getenv("OANDA_ACCESS_TOKEN")
OANDA_ENVIRONMENT = os.getenv("OANDA_ENVIRONMENT", "practice")

# --- instrument & market settings ---
INSTRUMENT_PAIRS = ["EUR_USD", "USD_CAD", "USD_JPY"]
GRANULARITY = "M15"
CANDLE_COUNT = 100

# --- strategy defaults ---
DEFAULT_TAKE_PROFIT_PIPS = 10
DEFAULT_STOP_LOSS_PIPS = 5
MAX_CONCURRENT_TRADES = 2

# --- bot behavior ---
SHADOW_MODE = False
LOG_LEVEL = "INFO"

# --- file paths ---
DATA_DIR = "datasets/"
SHADOW_TRADE_LOG = "logs/shadow_trades.csv"
TRADE_LOG_FILE = "logs/trade_log.csv"

# --- misc ---
TIMEZONE = "UTC"


