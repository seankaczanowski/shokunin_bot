# mood_reader.py

def market_mood(candles, cloud_top, cloud_bottom):
    """
    Assess the market mood and recent Ichimoku-related events.

    candles: List of dicts with keys: open, high, low, close
    cloud_top: float
    cloud_bottom: float

    Returns a dictionary with mood and recent contextual insights.
    """
    if len(candles) < 3:
        return {
            "mood": "insufficient_data",
            "recent_tk_cross": False,
            "cloud_breakout": None,
            "entered_cloud": None,
            "prior_mood": None
        }

    recent = candles[-5:]
    directions = []
    body_sizes = []
    upper_wicks = []
    lower_wicks = []
    mood_sequence = []

    for c in recent[-3:]:
        body = abs(c['close'] - c['open'])
        wick_up = c['high'] - max(c['close'], c['open'])
        wick_down = min(c['close'], c['open']) - c['low']

        body_sizes.append(body)
        upper_wicks.append(wick_up)
        lower_wicks.append(wick_down)

        if c['close'] > c['open']:
            directions.append("bull")
        elif c['close'] < c['open']:
            directions.append("bear")
        else:
            directions.append("neutral")

    latest_close = recent[-1]['close']
    prev_close = recent[-2]['close']
    cloud_position = None

    if latest_close > cloud_top:
        cloud_position = "above"
    elif latest_close < cloud_bottom:
        cloud_position = "below"
    else:
        cloud_position = "inside"

    avg_body = sum(body_sizes) / len(body_sizes)
    avg_wick = (sum(upper_wicks) + sum(lower_wicks)) / (2 * len(body_sizes))
    bull_count = directions.count("bull")
    bear_count = directions.count("bear")

    # Determine mood
    mood = "wandering"
    if cloud_position == "inside":
        mood = "foggy"
    elif bull_count >= 2:
        if cloud_position == "above":
            mood = "soaring" if avg_body > avg_wick else "drifting"
        elif cloud_position == "below":
            mood = "climbing from valley"
    elif bear_count >= 2:
        if cloud_position == "below":
            mood = "plunging" if avg_body > avg_wick else "sliding"
        elif cloud_position == "above":
            mood = "slipping from heights"

    # Track prior mood from earlier 3 candles (optional)
    prior_mood = None
    if len(candles) >= 6:
        prior_mood = market_mood(candles[:-3], cloud_top, cloud_bottom)["mood"]

    # Simple TK cross detection (placeholder logic)
    # This approximates a Tenkan/Kijun crossover by checking for directional candle flips
    recent_tk_cross = False
    for i in range(1, len(recent)):
        if (
            (recent[i-1]['close'] < recent[i-1]['open'] and recent[i]['close'] > recent[i]['open']) or
            (recent[i-1]['close'] > recent[i-1]['open'] and recent[i]['close'] < recent[i]['open'])
        ):
            recent_tk_cross = True
            break

    # Cloud breakout or re-entry check
    # Check if we moved completely out of or into the cloud between the last 2 closes
    cloud_breakout = None
    entered_cloud = None
    if len(recent) >= 2:
        prev = recent[-2]['close']
        if prev < cloud_bottom and latest_close > cloud_top:
            cloud_breakout = "above"
        elif prev > cloud_top and latest_close < cloud_bottom:
            cloud_breakout = "below"
        if (cloud_bottom <= prev <= cloud_top) and (latest_close < cloud_bottom or latest_close > cloud_top):
            entered_cloud = False
        elif (prev < cloud_bottom or prev > cloud_top) and (cloud_bottom <= latest_close <= cloud_top):
            entered_cloud = True

    return {
        "mood": mood,
        "recent_tk_cross": recent_tk_cross,
        "cloud_breakout": cloud_breakout,
        "entered_cloud": entered_cloud,
        "prior_mood": prior_mood
    }
