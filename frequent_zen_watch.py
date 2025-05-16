# frequent_zen_watch.py
# Observes multiple pairs every 15 minutes with Ichimoku mood-driven logic

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
from intent_engine import get_intent
from trade_executor import execute_trade, evaluate_open_trades

# === Load environment variables ===
load_dotenv()
ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
ACCESS_TOKEN = os.getenv("OANDA_ACCESS_TOKEN")

# === Configuration ===
INSTRUMENTS = ["USD_JPY", "EUR_USD", "USD_CAD"]
GRANULARITY = "M15"
CANDLE_COUNT = 100  # Ensure enough for Ichimoku projections

# === Initialize API client ===
client = oandapyV20.API(access_token=ACCESS_TOKEN, environment="live")
client.accountID = ACCOUNT_ID

# === Create output folders ===
os.makedirs("logs", exist_ok=True)
os.makedirs("charts", exist_ok=True)

ZEN_LOG_PATH = "logs/zen_log.csv"

def log_unified_entry(instrument, granularity, price, intent):
    header = [
        "timestamp", "instrument", "granularity", "price",
        "intent_type", "confidence", "mood", "should_trade",
        "recent_tk_cross", "cloud_breakout", "entered_cloud", "prior_mood"
    ]

    data = [
        datetime.now().isoformat(),
        instrument,
        granularity,
        price,
        intent.get("type", ""),
        intent.get("confidence", ""),
        intent.get("mood", ""),
        intent.get("should_trade", ""),
        intent["mood_context"].get("recent_tk_cross", ""),
        intent["mood_context"].get("cloud_breakout", ""),
        intent["mood_context"].get("entered_cloud", ""),
        intent["mood_context"].get("prior_mood", "")
    ]

    file_exists = os.path.isfile(ZEN_LOG_PATH)
    with open(ZEN_LOG_PATH, mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(data)

def print_trade_ticker(instrument, intent, current_price):
    status_icon = {
        "bullish_bias": "📈",
        "bearish_bias": "📉",
        "neutral": "🌫️"
    }.get(intent["type"], "❓")

    mood_icon = {
        "soaring": "🕊️", "plunging": "🌪️",
        "drifting": "🍃", "sliding": "🥀",
        "foggy": "🌫️", "climbing from valley": "⛰️",
        "slipping from heights": "🪂", "wandering": "🚶‍♂️"
    }.get(intent["mood"], "❔")

    print(f"[TICKER] {instrument} | {status_icon} {intent['type'].upper():15} | {mood_icon} Mood: {intent['mood']} | Confidence: {intent['confidence']:.2f} | Price: {current_price:.5f}")

def run_zen_cycle():
    for instrument in INSTRUMENTS:
        try:
            print(f"\n=== Observing {instrument} ===")

            # === Fetch + Compute ===
            candles = fetch_candles(client, instrument, granularity=GRANULARITY, count=CANDLE_COUNT)
            ichimoku = compute_ichimoku(candles)

            if not ichimoku["senkou_span_a"] or not ichimoku["senkou_span_b"]:
                print(f"[SKIP] Not enough Ichimoku span data for {instrument}. Waiting for more candles.")
                continue

            cloud_top = ichimoku["senkou_span_a"][-1][1]
            cloud_bottom = ichimoku["senkou_span_b"][-1][1]

            # === Save sketch ===
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            sketch_file = f"charts/sketch_{instrument}_{GRANULARITY}_{timestamp}.png"
            plt.ioff()
            plot_ichimoku(candles, ichimoku, title=f"{instrument} | Ichimoku Sketch ({GRANULARITY})")
            plt.savefig(sketch_file, bbox_inches="tight")
            plt.close()
            print(f"Sketch saved to: {sketch_file}")

            # === Intent using mood-based engine ===
            intent = get_intent(candles, cloud_top, cloud_bottom)

            print("\n--- Intent ---")
            print(f"Type: {intent['type'].capitalize()} | Confidence: {intent['confidence']:.2f}")
            print(f"Mood: {intent['mood']} | Session: {intent['session']}")
            for k, v in intent["mood_context"].items():
                print(f"{k.replace('_', ' ').title()}: {v}")

            # === Shadow Trade + Exit Check ===
            print("\n--- Shadow Trade ---")
            execute_trade(intent, instrument, client, shadow=True, current_candle=candles[-1], candle_index=len(candles) - 1)
            print_trade_ticker(instrument, intent, candles[-1]['close'])
            evaluate_open_trades(candles, ichimoku, instrument)

            # === Unified CSV Log ===
            log_unified_entry(instrument, GRANULARITY, candles[-1]['close'], intent)

        except Exception as e:
            print(f"[ERROR] Failed to complete cycle for {instrument}: {e}")

# === Loop every 15 minutes ===
if __name__ == "__main__":
    while True:
        run_zen_cycle()
        print("\n[ALL DONE] Zen scan complete for all instruments. Sleeping 15 minutes...\n")
        time.sleep(900)
