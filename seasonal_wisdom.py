# seasonal_wisdom.py
# Time-of-day market session awareness with weekend and holiday awareness

from datetime import datetime, time

# === Define known holidays (can expand this later) ===
FIXED_HOLIDAYS = {
    (1, 1): "New Year's Day",
    (12, 25): "Christmas Day",
    (7, 4): "US Independence Day",
    (12, 31): "New Year's Eve",
}

def is_weekend(dt):
    return dt.weekday() in [5, 6]  # Saturday or Sunday

def is_friday_closing(dt):
    return dt.weekday() == 4 and dt.time() >= time(20, 0)  # After 8PM UTC on Friday

def is_holiday(dt):
    return (dt.month, dt.day) in FIXED_HOLIDAYS

def get_market_session(now_utc=None):
    if now_utc is None:
        now_utc = datetime.utcnow()

    # === Early exit for known closures ===
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
