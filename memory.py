# ichimoku_bot/memory.py
# Unified Trade Memory Log — clean, quiet, and extensible

import csv
import os
from datetime import datetime, time
from config import TRADE_LOG_FILE as LOG_FILE


# === Session & Market Mood Awareness ===

FIXED_HOLIDAYS = {
    (1, 1): "New Year's Day",
    (12, 25): "Christmas Day",
    (7, 4): "US Independence Day",
    (12, 31): "New Year's Eve",
}

def is_weekend(dt):
    return dt.weekday() in [5, 6]

def is_friday_closing(dt):
    return dt.weekday() == 4 and dt.time() >= time(20, 0)

def is_holiday(dt):
    return (dt.month, dt.day) in FIXED_HOLIDAYS

def get_market_session(now_utc=None):
    if now_utc is None:
        now_utc = datetime.utcnow()

    if is_weekend(now_utc):
        return {
            "session": "Weekend",
            "mood": "Silent and closed",
            "volatility": "None",
            "notes": "Markets are closed over the weekend. Reflection time."
        }

    if is_friday_closing(now_utc):
        return {
            "session": "Friday Close",
            "mood": "Winding down",
            "volatility": "Decreasing",
            "notes": "Liquidity fades. Spreads widen. Avoid new positions."
        }

    if is_holiday(now_utc):
        return {
            "session": "Holiday",
            "mood": "Muted and irregular",
            "volatility": "Low",
            "notes": f"Observed holiday: {FIXED_HOLIDAYS[(now_utc.month, now_utc.day)]}. Expect limited activity."
        }

    current = now_utc.time()

    def within(start, end):
        return start <= current < end

    sessions = {
        "Tokyo": within(time(0, 0), time(8, 0)),
        "London": within(time(7, 0), time(16, 0)),
        "New York": within(time(13, 0), time(22, 0)),
    }

    active = [name for name, is_active in sessions.items() if is_active]

    if "Tokyo" in active and len(active) == 1:
        return {
            "session": "Tokyo",
            "mood": "Cautious and contemplative",
            "volatility": "Low to moderate",
            "notes": "Yen activity tends to dominate. Thinner liquidity."
        }
    elif "London" in active and len(active) == 1:
        return {
            "session": "London",
            "mood": "Decisive and trending",
            "volatility": "High",
            "notes": "European majors dominate. Strong directional moves possible."
        }
    elif "New York" in active and len(active) == 1:
        return {
            "session": "New York",
            "mood": "Reactive and volatile",
            "volatility": "High",
            "notes": "Often driven by US news. Reversals are common."
        }
    elif len(active) > 1:
        return {
            "session": "Overlap",
            "mood": "Energetic and turbulent",
            "volatility": "Very high",
            "notes": f"{' & '.join(active)} sessions overlap. Peak trading hours."
        }

    return {
        "session": "Off-hours",
        "mood": "Quiet and still",
        "volatility": "Low",
        "notes": "Markets are open but subdued. Await clearer signals."
    }


# === Logging ===

def log_trade(order_details: dict, context: dict):
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
    latest = df.iloc[-1]
    chikou_span = df.iloc[-27]['close'] if len(df) >= 27 else None

    if latest['close'] > max(latest['senkou_span_a'], latest['senkou_span_b']):
        price_vs_cloud = "above"
    elif latest['close'] < min(latest['senkou_span_a'], latest['senkou_span_b']):
        price_vs_cloud = "below"
    else:
        price_vs_cloud = "inside"

    session_info = get_market_session()

    context = {
        "timestamp": str(latest.name),
        "confidence": signal.get("confidence"),
        "confirmations": signal.get("confirmations"),
        "chikou_span": chikou_span,
        "price_vs_cloud": price_vs_cloud,
        "strategy_name": signal.get("strategy_name", "KijunTenkanCross"),
        "session": session_info["session"],
        "weather": session_info["mood"]
    }

    return context
