# weather_report.py
# Soft glance weather report for Ichimoku vision

def assess_weather(candles, ichimoku_lines):
    """
    Return a poetic and intuitive weather report based on Ichimoku components.
    """

    latest_idx = len(candles) - 1
    latest_close = candles[latest_idx]['close']

    # === CLOUD POSITION (Span A/B) ===
    span_a_points = {i: v for (i,v) in ichimoku_lines['senkou_span_a']}
    span_b_points = {i: v for (i,v) in ichimoku_lines['senkou_span_b']}

    span_a = span_a_points.get(latest_idx, None)
    span_b = span_b_points.get(latest_idx, None)

    # SKY: Clear, Cloudy, Stormy
    if span_a is not None and span_b is not None:
        upper = max(span_a, span_b)
        lower = min(span_a, span_b)
        if latest_close > upper:
            sky = "Clear skies"
        elif latest_close < lower:
            sky = "Stormy"
        else:
            sky = "Cloudy"
    else:
        sky = "Unknown (insufficient cloud)"

    # CLOUD: Thickness
    if span_a is not None and span_b is not None:
        thickness = abs(span_a - span_b)
        if thickness > 0.001:
            cloud = "Thick and stable cloud"
        else:
            cloud = "Thin and fragile cloud"
    else:
        cloud = "Unknown thickness"

    # WIND: Direction (slope of Span A)
    wind = "Unknown wind"
    if latest_idx >= 1:
        prev_span_a = span_a_points.get(latest_idx - 1, None)
        if prev_span_a is not None and span_a is not None:
            if span_a > prev_span_a:
                wind = "Favorable tailwinds"
            else:
                wind = "Unfavorable headwinds"

    # FREEDOM: Chikou Span vs past candle
    freedom = "Unknown path"
    if latest_idx >= 26:
        chikou = ichimoku_lines['chikou_span'][latest_idx - 26]
        if chikou and isinstance(chikou, tuple):
            chikou_price = chikou[1]
            back_candle = candles[latest_idx - 26]
            high = back_candle['high']
            low = back_candle['low']
            if chikou_price > high:
                freedom = "Path is clear above"
            elif chikou_price < low:
                freedom = "Path is clear below"
            else:
                freedom = "Path is tangled in the forest"

    # MOMENTUM: Tenkan vs Kijun
    tenkan = ichimoku_lines['tenkan_sen'][latest_idx]
    kijun = ichimoku_lines['kijun_sen'][latest_idx]
    if tenkan is not None and kijun is not None:
        if tenkan > kijun:
            momentum = "Quick favorable winds"
        else:
            momentum = "Slack and sluggish sails"
    else:
        momentum = "Unknown momentum"

    return {
        "sky": sky,
        "cloud": cloud,
        "wind": wind,
        "freedom": freedom,
        "momentum": momentum
    }
