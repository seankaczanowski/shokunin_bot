# daily_zen_scan.py
# One glance: Candles, Clouds, and the Call of the Wind

import os
from dotenv import load_dotenv
import oandapyV20
from datetime import datetime
from zen_garden import fetch_candles, compute_ichimoku, plot_ichimoku
from weather_report import assess_weather
from intent_engine import interpret_weather
from trade_executor import execute_trade

import matplotlib.pyplot as plt
import webbrowser

# === Load environment variables from .env ===
load_dotenv()
ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
ACCESS_TOKEN = os.getenv("OANDA_ACCESS_TOKEN")

# === Config ===
INSTRUMENT = "USD_JPY"
GRANULARITY = "M30"
CANDLE_COUNT = 100

# === Connect to OANDA ===
client = oandapyV20.API(access_token=ACCESS_TOKEN)
client.accountID = ACCOUNT_ID  # Needed for trading

# === Fetch and compute Ichimoku ===
candles = fetch_candles(client, INSTRUMENT, granularity=GRANULARITY, count=CANDLE_COUNT)
ichimoku = compute_ichimoku(candles)

# === Plot and save Ichimoku sketch ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
filename = f"ichimoku_sketch_{INSTRUMENT}_{GRANULARITY}_{timestamp}.png"

plt.ioff()
plot_ichimoku(candles, ichimoku, title=f"{INSTRUMENT} | Ichimoku Sketch ({GRANULARITY})")
plt.savefig(filename, bbox_inches="tight")
plt.close()

print(f"\nIchimoku sketch saved to: {filename}")

# === Weather Scroll ===
weather = assess_weather(candles, ichimoku)

print("\n=== ZEN WEATHER SCROLL ===")
for k, v in weather.items():
    print(f"{k.title()}: {v}")

# === Intent Scroll ===
intent = interpret_weather(weather)

print("\n=== ZEN INTENT SCROLL ===")
print(f"Bias: {intent['bias'].capitalize()}")
print(f"Confidence: {intent['confidence'].capitalize()}")
print(f"Comment: {intent['comment']}")

# === Trade Execution (Shadow Mode) ===
print("\n=== ZEN TRADE SHADOW ===")
execute_trade(intent, INSTRUMENT, client, units=100, shadow=True)

# === Log Output to File ===
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_filename = f"{log_dir}/zen_log_{INSTRUMENT}_{GRANULARITY}_{timestamp}.txt"

with open(log_filename, "w") as f:
    f.write(f"Timestamp: {timestamp}\n")
    f.write(f"Instrument: {INSTRUMENT}\nGranularity: {GRANULARITY}\n\n")
    f.write("=== ZEN WEATHER SCROLL ===\n")
    for k, v in weather.items():
        f.write(f"{k.title()}: {v}\n")
    f.write("\n=== ZEN INTENT SCROLL ===\n")
    f.write(f"Bias: {intent['bias'].capitalize()}\n")
    f.write(f"Confidence: {intent['confidence'].capitalize()}\n")
    f.write(f"Comment: {intent['comment']}\n")
    f.write("\n=== ZEN TRADE SHADOW ===\n")
    f.write(f"Simulated Trade: {intent['bias']} ({intent['confidence']}) - {INSTRUMENT} - 100 units\n")

print(f"\n[LOG] Shadow report saved to: {log_filename}")

# === Auto-open Chart ===
webbrowser.open(filename)
