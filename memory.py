# ichimoku_bot/memory.py
# Unified Trade Memory Log — clean, quiet, and extensible

import csv
import os
from datetime import datetime
from config import TRADE_LOG_FILE as LOG_FILE


def log_trade(order_details: dict, context: dict):
    """
    Logs trade execution and context into a unified CSV file.

    Parameters:
    - order_details: dict containing price, units, signal, etc.
    - context: dict containing indicators, confidence, weather, etc.
    """
    file_exists = os.path.isfile(LOG_FILE)

    log_entry = {
        "timestamp": context.get("timestamp", datetime.utcnow().isoformat()),
        "instrument": order_details.get("instrument"),
        "signal": order_details.get("signal"),
        "confidence": context.get("confidence"),
        "confirmations": context.get("confirmations"),
        "entry_price": order_details.get("entry_price"),
        "exit_price": order_details.get("exit_price", ""),
        "profit_loss": order_details.get("profit_loss", ""),
        "units": order_details.get("units"),
        "stop_loss": order_details.get("stop_loss"),
        "take_profit": order_details.get("take_profit"),
        "chikou_span": context.get("chikou_span", ""),
        "price_vs_cloud": context.get("price_vs_cloud", ""),
        "session": context.get("session", ""),
        "strategy_name": context.get("strategy_name", ""),
        "weather": context.get("weather", "")
    }

    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=log_entry.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(log_entry)


def update_memory(signal: dict, df):
    """
    Derives and returns a context dictionary from the signal and latest indicators.

    Parameters:
    - signal: dict returned by strategy.evaluate()
    - df: full indicator-enhanced DataFrame

    Returns:
    - dict of context to pass into log_trade()
    """
    latest = df.iloc[-1]
    chikou_span = df.iloc[-27]['close'] if len(df) >= 27 else None

    if latest['close'] > max(latest['senkou_span_a'], latest['senkou_span_b']):
        price_vs_cloud = "above"
    elif latest['close'] < min(latest['senkou_span_a'], latest['senkou_span_b']):
        price_vs_cloud = "below"
    else:
        price_vs_cloud = "inside"

    context = {
        "timestamp": str(latest.name),
        "confidence": signal.get("confidence"),
        "confirmations": signal.get("confirmations"),
        "chikou_span": chikou_span,
        "price_vs_cloud": price_vs_cloud,
        "strategy_name": signal.get("strategy_name", "KijunTenkanCross"),
        "weather": "",       # placeholder for future weather summary
        "session": ""        # placeholder for session label
    }

    return context
