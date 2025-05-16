# intent_engine.py

from mood_reader import market_mood
from seasonal_wisdom import get_market_session

def get_intent(candles, cloud_top, cloud_bottom, now_utc=None):
    """
    Determines market intent based on Ichimoku placement, mood, and seasonal session context.

    candles: List of recent candle dicts (open, high, low, close)
    cloud_top: float - top of the Ichimoku cloud
    cloud_bottom: float - bottom of the Ichimoku cloud
    now_utc: optional datetime for session detection (default: current UTC time)

    Returns a dictionary with enriched intent and session metadata.
    """

    # === Market Session Awareness ===
    session_data = get_market_session(now_utc)
    session_name = session_data.get("session", "Unknown")
    session_mood = session_data.get("mood", "")
    session_notes = session_data.get("notes", "")

    # === Mood Analysis ===
    mood_report = market_mood(candles, cloud_top, cloud_bottom)

    mood = mood_report["mood"]
    recent_tk_cross = mood_report["recent_tk_cross"]
    cloud_breakout = mood_report["cloud_breakout"]
    entered_cloud = mood_report["entered_cloud"]
    prior_mood = mood_report["prior_mood"]

    latest_close = candles[-1]["close"]

    # === Basic Position-Based Intent ===
    if latest_close > cloud_top:
        raw_intent = "bullish_bias"
    elif latest_close < cloud_bottom:
        raw_intent = "bearish_bias"
    else:
        raw_intent = "neutral"

    # === Confidence Logic ===
    confidence = 0.5  # base confidence

    if mood in ["soaring", "plunging"]:
        confidence += 0.25
    elif mood in ["climbing from valley", "slipping from heights"]:
        confidence += 0.1
    elif mood == "foggy":
        confidence = 0.0
    elif mood == "wandering":
        confidence -= 0.05

    # Session adjustments
    if session_name == "Weekend":
        confidence = 0.0
    elif session_name == "Holiday":
        confidence *= 0.5
    elif session_name == "Friday Close":
        confidence *= 0.7

    # Signal boosts
    if recent_tk_cross:
        confidence += 0.05
    if cloud_breakout:
        confidence += 0.05

    confidence = min(1.0, max(0.0, confidence))  # clamp to [0, 1]
    should_trade = confidence >= 0.6

    return {
        "type": raw_intent,
        "confidence": confidence,
        "should_trade": should_trade,
        "mood": mood,
        "session": session_name,
        "session_mood": session_mood,
        "session_notes": session_notes,
        "mood_context": {
            "recent_tk_cross": recent_tk_cross,
            "cloud_breakout": cloud_breakout,
            "entered_cloud": entered_cloud,
            "prior_mood": prior_mood
        }
    }
