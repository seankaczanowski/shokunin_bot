# frequent_zen_watch.py
# Observes multiple pairs every 15 minutes in shadow mode with Ichimoku entry and trailing exit logic

import os
import time
import csv
from datetime import datetime
from dotenv import load_dotenv

import oandapyV20
import matplotlib
matplotlib.use("Agg")  # Headless plotting for cloud instances
import matplotlib.pyplot as plt

from zen_garden import fetch_candles, compute_ichimoku, plot_ichimoku
from weather_report import assess_weather
from intent_engine import interpret_weather
from trade_executor import execute_trade, evaluate_open_trades

# === Load environment variables ===
load_dotenv()
ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
ACCESS_TOKEN = os.getenv("OANDA_ACCESS_TOKEN")

# === Configuration ===
INSTRUMENTS = ["USD_JPY", "EUR_USD", "USD_CAD"]
GRANULARITY = "M15"
CANDLE_COUNT = 60

# === Initialize API client ===
client = oandapyV20.API(access_token=ACCESS_TOKEN, environment="live")
client.accountID = ACCOUNT_ID

# === Create output folders ===
os.makedirs("logs", exist_ok=True)
os.makedirs("charts", exist_ok=True)

ZEN_LOG_PATH = "logs/zen_log.csv"

def log_unified_entry(instrument, granularity, price, weather, intent):
    header = [
        "timestamp", "instrument", "granularity", "price",
        "sky", "cloud", "wind", "freedom", "momentum",
        "bias", "confidence", "intent_comment"
    ]

    data = [
        datetime.now().isoformat(),
        instrument,
        granularity,
        price,
        weather.get("sky", ""),
        weather.get("cloud", ""),
        weather.get("wind", ""),
        weather.get("freedom", ""),
        weather.get("momentum", ""),
        intent.get("bias", ""),
        intent.get("confidence", ""),
        intent.get("comment", "").replace("\n", " ")
    ]

    file_exists = os.path.isfile(ZEN_LOG_PATH)
    with open(ZEN_LOG_PATH, mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(data)

def print_trade_ticker(instrument, intent, current_price):
    status_icon = {
        "bullish": "📈",
        "bearish": "📉",
        "neutral": "🌫️",
        "avoid": "🚸"
    }.get(intent["bias"], "❓")

    conf_icon = {
        "strong": "🔥",
        "moderate": "💡",
        "low": "🌱"
    }.get(intent["confidence"], "❔")

    session_tag = f"[{intent.get('session', 'Unknown')}]"

    print(f"[TICKER] {instrument} | {status_icon} {intent['bias'].upper():8} | {conf_icon} {intent['confidence'].capitalize():9} | Price: {current_price:.5f} {session_tag}")

def run_zen_cycle():
    for instrument in INSTRUMENTS:
        print(f"\n=== Observing {instrument} ===")

        # === Fetch + Compute ===
        candles = fetch_candles(client, instrument, granularity=GRANULARITY, count=CANDLE_COUNT)
        ichimoku = compute_ichimoku(candles)

        # === Save sketch ===
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        sketch_file = f"charts/sketch_{instrument}_{GRANULARITY}_{timestamp}.png"
        plt.ioff()
        plot_ichimoku(candles, ichimoku, title=f"{instrument} | Ichimoku Sketch ({GRANULARITY})")
        plt.savefig(sketch_file, bbox_inches="tight")
        plt.close()
        print(f"Sketch saved to: {sketch_file}")

        # === Weather & Intent ===
        weather = assess_weather(candles, ichimoku)
        intent = interpret_weather(weather)

        print("\n--- Weather Report ---")
        for k, v in weather.items():
            print(f"{k.title()}: {v}")

        print("\n--- Intent ---")
        print(f"Bias: {intent['bias'].capitalize()} | Confidence: {intent['confidence'].capitalize()}")
        print(f"Comment: {intent['comment']}")

        # === Shadow Trade + Exit Check ===
        print("\n--- Shadow Trade ---")
        execute_trade(intent, instrument, client, shadow=True, current_candle=candles[-1], candle_index=len(candles) - 1)
        print_trade_ticker(instrument, intent, candles[-1]['close'])
        evaluate_open_trades(candles, ichimoku, instrument)

        # === Unified CSV Log ===
        log_unified_entry(instrument, GRANULARITY, candles[-1]['close'], weather, intent)

# === Loop every 15 minutes ===
if __name__ == "__main__":
    while True:
        run_zen_cycle()
        print("\n[ALL DONE] Zen scan complete for all instruments. Sleeping 15 minutes...\n")
        time.sleep(900)
