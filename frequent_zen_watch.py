# frequent_zen_watch.py
# Observes multiple pairs every 30 minutes in shadow mode with Ichimoku entry and trailing exit logic

import os
from dotenv import load_dotenv
import oandapyV20
from datetime import datetime
from zen_garden import fetch_candles, compute_ichimoku, plot_ichimoku
from weather_report import assess_weather
from intent_engine import interpret_weather
from trade_executor import execute_trade, evaluate_open_trades

import matplotlib
matplotlib.use("Agg")  # Headless plotting for cloud instances
import matplotlib.pyplot as plt
import time

# === Load environment variables ===
load_dotenv()
ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
ACCESS_TOKEN = os.getenv("OANDA_ACCESS_TOKEN")

# === Configuration ===
INSTRUMENTS = ["USD_JPY", "EUR_USD"]
GRANULARITY = "M30"
CANDLE_COUNT = 60  # Reduced to minimize memory footprint on micro instances

# === Connect to OANDA ===
client = oandapyV20.API(access_token=ACCESS_TOKEN, environment="live")  # Set correct OANDA environment
client.accountID = ACCOUNT_ID  # Attach for trade execution

# === Create output folders ===
os.makedirs("logs", exist_ok=True)
os.makedirs("charts", exist_ok=True)

def print_trade_ticker(instrument, intent, current_price):
    """
    Nicely formatted one-line terminal ticker for trade status.
    """
    status_icon = {
        "bullish": "📈",
        "bearish": "📉",
        "neutral": "🌫️",
        "avoid": "🛘"
    }.get(intent["bias"], "❓")

    conf_icon = {
        "strong": "🔥",
        "moderate": "💡",
        "low": "🌱"
    }.get(intent["confidence"], "❔")

    print(f"[TICKER] {instrument} | {status_icon} {intent['bias'].upper():8} | {conf_icon} {intent['confidence'].capitalize():9} | Price: {current_price:.5f}")

def run_zen_cycle():
    for instrument in INSTRUMENTS:
        print(f"\n=== Observing {instrument} ===")

        # === Fetch and process data ===
        candles = fetch_candles(client, instrument, granularity=GRANULARITY, count=CANDLE_COUNT)
        ichimoku = compute_ichimoku(candles)

        # === Save sketch only, do not open ===
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        sketch_file = f"charts/sketch_{instrument}_{GRANULARITY}_{timestamp}.png"
        plt.ioff()
        plot_ichimoku(candles, ichimoku, title=f"{instrument} | Ichimoku Sketch ({GRANULARITY})")
        plt.savefig(sketch_file, bbox_inches="tight")
        plt.close()
        print(f"Sketch saved to: {sketch_file}")

        # === Weather + Intent ===
        weather = assess_weather(candles, ichimoku)
        intent = interpret_weather(weather)

        print("\n--- Weather Report ---")
        for k, v in weather.items():
            print(f"{k.title()}: {v}")

        print("\n--- Intent ---")
        print(f"Bias: {intent['bias'].capitalize()} | Confidence: {intent['confidence'].capitalize()}")
        print(f"Comment: {intent['comment']}")

        # === Execute shadow trade with context ===
        print("\n--- Shadow Trade ---")
        execute_trade(intent, instrument, client, units=100, shadow=True, current_candle=candles[-1], candle_index=len(candles) - 1)

        # === Print terminal ticker ===
        print_trade_ticker(instrument, intent, current_price=candles[-1]['close'])

        # === Check for exits on open shadow trades ===
        evaluate_open_trades(candles, ichimoku, instrument)

        # === Save to log ===
        log_file = f"logs/log_{instrument}_{GRANULARITY}_{timestamp}.txt"
        with open(log_file, "w") as f:
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Instrument: {instrument}\nGranularity: {GRANULARITY}\n\n")
            f.write("--- Weather Report ---\n")
            for k, v in weather.items():
                f.write(f"{k.title()}: {v}\n")
            f.write("\n--- Intent ---\n")
            f.write(f"Bias: {intent['bias'].capitalize()}\n")
            f.write(f"Confidence: {intent['confidence'].capitalize()}\n")
            f.write(f"Comment: {intent['comment']}\n")
            f.write("\n--- Shadow Trade ---\n")
            f.write(f"Simulated Trade: {intent['bias']} ({intent['confidence']}) - {instrument} - 100 units\n")

        print(f"Log saved to: {log_file}")

# === Loop every 30 minutes ===
if __name__ == "__main__":
    while True:
        run_zen_cycle()
        print("\n[ALL DONE] Zen scan complete for all instruments. Sleeping 30 minutes...\n")
        time.sleep(1800)  # 30 minutes
