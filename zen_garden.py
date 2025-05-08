# zen_garden.py
# Building the garden for our Zen trader

import matplotlib
matplotlib.use("Agg")

import oandapyV20.endpoints.instruments as instruments
import matplotlib.pyplot as plt

def fetch_candles(client, instrument, granularity="M5", count=100):
    """
    Fetch historical candles from Oanda.
    """
    params = {
        "count": count,
        "granularity": granularity,
        "price": "M"  # Mid prices
    }
    r = instruments.InstrumentsCandles(instrument=instrument, params=params)
    client.request(r)
    candles = r.response.get('candles', [])
    
    parsed_candles = []
    for candle in candles:
        if candle['complete']:
            parsed_candles.append({
                "time": candle["time"],
                "open": float(candle["mid"]["o"]),
                "high": float(candle["mid"]["h"]),
                "low": float(candle["mid"]["l"]),
                "close": float(candle["mid"]["c"])
            })
    return parsed_candles

def compute_ichimoku(candles):
    """
    Compute Ichimoku components from candles.
    """
    highs = [c['high'] for c in candles]
    lows = [c['low'] for c in candles]
    closes = [c['close'] for c in candles]

    tenkan_sen = []
    kijun_sen = []
    senkou_span_a = []
    senkou_span_b = []
    chikou_span = []

    for i in range(len(candles)):
        if i >= 9 - 1:
            high = max(highs[i-8:i+1])
            low = min(lows[i-8:i+1])
            tenkan_sen.append((high + low) / 2)
        else:
            tenkan_sen.append(None)

        if i >= 26 - 1:
            high = max(highs[i-25:i+1])
            low = min(lows[i-25:i+1])
            kijun_sen.append((high + low) / 2)
        else:
            kijun_sen.append(None)

        if i >= 26:
            chikou_span.append((i-26, closes[i]))
        else:
            chikou_span.append(None)

    for i in range(len(candles)):
        if i >= 26 - 1 and tenkan_sen[i] is not None and kijun_sen[i] is not None:
            span_a = (tenkan_sen[i] + kijun_sen[i]) / 2
            if i + 26 < len(candles):
                senkou_span_a.append((i + 26, span_a))

        if i >= 52 - 1:
            high = max(highs[i-51:i+1])
            low = min(lows[i-51:i+1])
            span_b = (high + low) / 2
            if i + 26 < len(candles):
                senkou_span_b.append((i + 26, span_b))

    return {
        "tenkan_sen": tenkan_sen,
        "kijun_sen": kijun_sen,
        "senkou_span_a": senkou_span_a,
        "senkou_span_b": senkou_span_b,
        "chikou_span": chikou_span
    }

def plot_ichimoku(candles, ichimoku_lines, title="Ichimoku Sketch"):
    """
    Plot Ichimoku components and price.
    """
    closes = [c['close'] for c in candles]
    x = list(range(len(closes)))

    plt.figure(figsize=(14,8))
    plt.plot(x, closes, label="Price", color="black", linewidth=1)

    plt.plot(x, ichimoku_lines['tenkan_sen'], label="Tenkan-sen (9)", color="blue", linestyle='--')
    plt.plot(x, ichimoku_lines['kijun_sen'], label="Kijun-sen (26)", color="red", linestyle='-.')

    if ichimoku_lines['senkou_span_a']:
        x_span_a = [i for (i,v) in ichimoku_lines['senkou_span_a']]
        y_span_a = [v for (i,v) in ichimoku_lines['senkou_span_a']]
        plt.plot(x_span_a, y_span_a, label="Senkou Span A", color="green")

    if ichimoku_lines['senkou_span_b']:
        x_span_b = [i for (i,v) in ichimoku_lines['senkou_span_b']]
        y_span_b = [v for (i,v) in ichimoku_lines['senkou_span_b']]
        plt.plot(x_span_b, y_span_b, label="Senkou Span B", color="orange")

    chikou_x = []
    chikou_y = []
    for v in ichimoku_lines['chikou_span']:
        if v is not None:
            chikou_x.append(v[0])
            chikou_y.append(v[1])
    if chikou_x:
        plt.plot(chikou_x, chikou_y, label="Chikou Span", color="purple")

    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.gca().invert_xaxis()
    plt.show()
