# zen_simulator.py
# Full trade simulation engine now mirrors live bot logic, including dynamic trailing, Ichimoku, and mood-based exits

import pandas as pd
from zen_intent_engine import get_intent
from zen_ichimoku_weather import compute_ichimoku
from zen_heiken_assist import compute_heiken_ashi, ha_trend_strength
from zen_mood_reader import market_mood


def load_data_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    df = df.rename(columns={
        "Open": "open", "High": "high", "Low": "low", "Close": "close"
    })
    df = df[['open', 'high', 'low', 'close']].astype(float)
    return df


def fallback_ichimoku_exit(trade, idx, candles, ichimoku):
    if idx >= len(ichimoku["tenkan_sen"]) or ichimoku["tenkan_sen"][idx] is None:
        return False

    price = candles[idx]['close']
    tenkan = ichimoku['tenkan_sen'][idx]
    kijun = ichimoku['kijun_sen'][idx]
    chikou_data = ichimoku['chikou_span']

    tenkan_cross = tenkan < kijun if trade['direction'] == "bullish" else tenkan > kijun

    span_a = {i: v for (i, v) in ichimoku['senkou_span_a']}.get(idx)
    span_b = {i: v for (i, v) in ichimoku['senkou_span_b']}.get(idx)
    in_kumo = False
    if span_a is not None and span_b is not None:
        upper = max(span_a, span_b)
        lower = min(span_a, span_b)
        in_kumo = lower <= price <= upper

    if idx >= 26 and isinstance(chikou_data[idx - 26], tuple):
        chikou_price = chikou_data[idx - 26][1]
        back_candle = candles[idx - 26]
        high = back_candle['high']
        low = back_candle['low']
        if trade['direction'] == "bullish" and chikou_price < low:
            return True
        if trade['direction'] == "bearish" and chikou_price > high:
            return True

    return tenkan_cross or in_kumo


def mood_conflict(entry_mood, entry_confidence, current_mood, trade_direction):
    strong_conflict = ((trade_direction == "bullish" and current_mood in ["plunging", "strong pessimism"])
                       or (trade_direction == "bearish" and current_mood in ["soaring", "strong optimism"]))
    return strong_conflict and current_mood != entry_mood


def simulate_trade_lifecycle(df, start_index, entry_price, direction, intent, ichimoku):
    trade = {
        "direction": direction,
        "entry_price": entry_price,
        "max_favorable_price": entry_price,
        "trail_armed": False,
        "trail_distance": 0.0020,
        "entry_mood": intent['mood'],
        "entry_confidence": intent['confidence'],
        "mood_strikes": 0
    }

    for i in range(start_index + 1, min(start_index + 50, len(df))):
        price = df.iloc[i]['close']
        candle_dicts = [
            {"open": row.open, "high": row.high, "low": row.low, "close": row.close}
            for row in df.iloc[:i+1].itertuples()
        ]

        try:
            intent_now = get_intent(candle_dicts, ichimoku['senkou_span_a'][i][1], ichimoku['senkou_span_b'][i][1])
            if mood_conflict(trade['entry_mood'], trade['entry_confidence'], intent_now['mood'], trade['direction']):
                trade['mood_strikes'] += 1
                if trade['mood_strikes'] >= 2:
                    pnl = price - trade['entry_price'] if direction == "bullish" else trade['entry_price'] - price
                    return i, price, "Mood Shift", round(pnl * 10000, 1)
            else:
                trade['mood_strikes'] = 0
        except:
            pass

        if trade['direction'] == "bullish":
            trade['max_favorable_price'] = max(price, trade['max_favorable_price'])
        else:
            trade['max_favorable_price'] = min(price, trade['max_favorable_price'])

        moved = abs(trade['max_favorable_price'] - trade['entry_price'])
        if not trade['trail_armed'] and moved >= trade['trail_distance']:
            trade['trail_armed'] = True

        if trade['trail_armed']:
            if trade['direction'] == "bullish" and price <= (trade['max_favorable_price'] - trade['trail_distance']):
                return i, price, "Trailing Stop", round((price - trade['entry_price']) * 10000, 1)
            if trade['direction'] == "bearish" and price >= (trade['max_favorable_price'] + trade['trail_distance']):
                return i, price, "Trailing Stop", round((trade['entry_price'] - price) * 10000, 1)

        if fallback_ichimoku_exit(trade, i, candle_dicts, ichimoku):
            pnl = price - trade['entry_price'] if direction == "bullish" else trade['entry_price'] - price
            return i, price, "Ichimoku Exit", round(pnl * 10000, 1)

    final_price = df.iloc[min(start_index + 50, len(df) - 1)]['close']
    pnl = final_price - trade['entry_price'] if direction == "bullish" else trade['entry_price'] - final_price
    return min(start_index + 50, len(df) - 1), final_price, "Timeout Exit", round(pnl * 10000, 1)


def run_simulation(df, instrument="EUR_USD", lookback_window=100, show_logs=True):
    trades = []
    i = lookback_window + 52  # Ensure sufficient Ichimoku data
    while i < len(df):
        candles_for_ichimoku = df.iloc[i - lookback_window - 52 : i]
        candle_dicts_full = [
            {"open": row.open, "high": row.high, "low": row.low, "close": row.close}
            for row in candles_for_ichimoku.itertuples()
        ]
        ichimoku = compute_ichimoku(candle_dicts_full)

        candles_recent = candle_dicts_full[-lookback_window:]
        cloud_top = ichimoku["senkou_span_a"][-1][1]
        cloud_bottom = ichimoku["senkou_span_b"][-1][1]
        intent = get_intent(candles_recent, cloud_top, cloud_bottom)

        ha_df = compute_heiken_ashi(df.iloc[i - lookback_window:i])
        ha_trend = ha_trend_strength(ha_df)

        if intent["should_trade"]:
            ha_confirms = (
                (intent["type"] == "bullish_bias" and ha_trend == 1) or
                (intent["type"] == "bearish_bias" and ha_trend == -1)
            )
            if ha_confirms:
                entry_price = candles_recent[-1]["close"]
                direction = "bullish" if intent["type"] == "bullish_bias" else "bearish"

                exit_idx, exit_price, reason, pnl = simulate_trade_lifecycle(df, i, entry_price, direction, intent, ichimoku)
                trades.append({
                    "entry_index": i,
                    "exit_index": exit_idx,
                    "instrument": instrument,
                    "direction": direction,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "exit_reason": reason,
                    "pnl_pips": pnl,
                    "confidence": intent["confidence"],
                    "mood": intent["mood"]
                })

                if show_logs:
                    print(f"{i} → {exit_idx} | {direction.upper()} | {entry_price:.5f} → {exit_price:.5f} | {pnl:+.1f} pips | {reason}")

                i = exit_idx + 1
                continue
        i += 1
    return trades


if __name__ == "__main__":
    df = load_data_from_csv("EURUSD.csv")
    results = run_simulation(df)

    results_df = pd.DataFrame(results)
    results_df.to_csv("full_trade_simulation_results.csv", index=False)

    print(f"\nTotal Trades Simulated: {len(results)}")
    print("Results saved to: full_trade_simulation_results.csv")
