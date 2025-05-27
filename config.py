# ichimoku_bot/config.py
# Environmental Variables / Broker Settings
# Instrument & Market Settings
# Standard Defaults & Behaviours
# Files Paths & Storage

# Dependencies
# Standard Imports
import os
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()  # Automatically loads .env into os.environ

# Broker Settings
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
OANDA_ACCESS_TOKEN = os.getenv("OANDA_ACCESS_TOKEN")
OANDA_ENVIRONMENT = os.getenv("OANDA_ENVIRONMENT", "practice")  # default to "practice"

# Instrument & Market Settings
INSTRUMENT_PAIRS = ["EUR_USD", "USD_CAD", "USD_JPY"]
GRANULARITY = "M15"           # Options: S5, S10, M1, M15, H1, D, etc.
CANDLE_COUNT = 100            # How many candles to fetch per request

# Strategy Defaults
DEFAULT_TAKE_PROFIT_PIPS = 10
DEFAULT_STOP_LOSS_PIPS = 5
MAX_CONCURRENT_TRADES = 2     # How many open trades the bot is allowed to manage at once

# Bot Behavior Settings
SHADOW_MODE = False           # If True, log trades but don't execute
LOG_LEVEL = "INFO"            # Can be: DEBUG, INFO, WARNING, ERROR, CRITICAL

# File Paths & Storage
DATA_DIR = "datasets/"
LOG_FILE = "logs/zen_log.csv"
SHADOW_TRADE_LOG = "logs/shadow_trades.csv"

# Miscellaneous
TIMEZONE = "UTC"              # Can be changed to local timezone for timestamp alignment
