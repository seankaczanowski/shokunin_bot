# trade_executor.py
# Executes and tracks trades — shadow or real — with Ichimoku-based and dynamic trailing exit logic

import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.accounts as accounts
import os
from datetime import datetime
import csv

open_trades = []  # Each trade: dict with instrument, direction, entry_price, trail info, etc.
TRADE_LOG_PATH = "logs/shadow_trades.csv"

def log_shadow_trade(trade):
    header = ["timestamp", "instrument", "direction", "entry_price", "entry_index", "units"]
    data = [
        datetime.now().isoformat(),
        trade["instrument"],
        trade["direction"],
        trade["entry_price"],
        trade["entry_index"],
        trade["units"]
    ]

    file_exists = os.path.isfile(TRADE_LOG_PATH)
    with open(TRADE_LOG_PATH, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(data)

def get_account_balance(client):
    r = accounts.AccountDetails(accountID=client.accountID)
    client.request(r)
    return float(r.response['account']['balance'])

def calculate_dynamic_units(balance, instrument, risk_pct=0.01, est_stop_loss_pips=20):
    risk_amount = balance * risk_pct
    pip_value_per_1000 = 0.10
    unit_blocks = risk_amount / (pip_value_per_1000 * est_stop_loss_pips)
    return int(unit_blocks * 1000)

def compute_trailing_distance(candles, lookback=14, multiplier=1.5):
    highs = [c['high'] for c in candles[-lookback:]]
    lows = [c['low'] for c in candles[-lookback:]]
    ranges = [h - l for h, l in zip(highs, lows)]
    avg_range = sum(ranges) / len(ranges)
    return avg_range * multiplier

def execute_trade(intent, instrument, client, shadow=True, current_candle=None, candle_index=None):
    intent_type = intent.get("type")
    confidence = intent.get("confidence")

    if intent_type not in ["bullish_bias", "bearish_bias"] or not intent.get("should_trade", False):
        print("[EXECUTOR] Intent unclear or confidence too low. Standing down.")
        return

    balance = get_account_balance(client)
    units = calculate_dynamic_units(balance, instrument)
    side = "buy" if intent_type == "bullish_bias" else "sell"
    units_signed = units if side == "buy" else -units

    if shadow:
        print(f"[SHADOW MODE] Would place {side.upper()} MARKET order for {instrument} ({units_signed} units).")
        print(f"[SHADOW MODE] Mood: {intent['mood']} | Confidence: {intent['confidence']}")
        if current_candle:
            trail_dist = compute_trailing_distance([current_candle])
            open_trades.append({
                "instrument": instrument,
                "direction": "bullish" if side == "buy" else "bearish",
                "entry_price": current_candle['close'],
                "entry_index": candle_index,
                "units": units,
                "trail_distance": trail_dist,
                "trail_armed": False,
                "max_favorable_price": current_candle['close']
            })
            log_shadow_trade(open_trades[-1])
        return

    order_data = {
        "order": {
            "instrument": instrument,
            "units": str(units_signed),
            "type": "MARKET",
            "positionFill": "DEFAULT"
        }
    }

    try:
        r = orders.OrderCreate(accountID=client.accountID, data=order_data)
        client.request(r)
        print("[EXECUTOR] Order successfully placed.")
        print(r.response)
    except Exception as e:
        print("[EXECUTOR] Order failed.")
        print(e)

def fallback_ichimoku_exit(trade, candles, ichimoku_lines):
    idx = len(candles) - 1
    price = candles[idx]['close']
    tenkan = ichimoku_lines['tenkan_sen'][idx]
    kijun = ichimoku_lines['kijun_sen'][idx]
    chikou_data = ichimoku_lines['chikou_span']

    tenkan_cross = tenkan < kijun if trade['direction'] == "bullish" else tenkan > kijun

    span_a = {i: v for (i, v) in ichimoku_lines['senkou_span_a']}.get(idx)
    span_b = {i: v for (i, v) in ichimoku_lines['senkou_span_b']}.get(idx)
    in_kumo = False
    if span_a is not None and span_b is not None:
        upper = max(span_a, span_b)
        lower = min(span_a, span_b)
        in_kumo = lower <= price <= upper

    if idx >= 26:
        chikou = chikou_data[idx - 26]
        if chikou and isinstance(chikou, tuple):
            chikou_price = chikou[1]
            back_candle = candles[idx - 26]
            high = back_candle['high']
            low = back_candle['low']
            if trade['direction'] == "bullish" and chikou_price < low:
                return True
            if trade['direction'] == "bearish" and chikou_price > high:
                return True

    return tenkan_cross or in_kumo

def should_exit_trade(trade, candles, ichimoku_lines):
    idx = len(candles) - 1
    price = candles[idx]['close']

    if 'trail_distance' in trade:
        if trade['direction'] == "bullish":
            trade['max_favorable_price'] = max(price, trade['max_favorable_price'])
        else:
            trade['max_favorable_price'] = min(price, trade['max_favorable_price'])

        if not trade['trail_armed']:
            moved = abs(trade['max_favorable_price'] - trade['entry_price'])
            if moved >= trade['trail_distance']:
                trade['trail_armed'] = True
                print(f"[TRAIL] Armed trailing stop for {trade['instrument']}")

        if trade['trail_armed']:
            if trade['direction'] == "bullish" and price <= (trade['max_favorable_price'] - trade['trail_distance']):
                print("[TRAIL EXIT] Bullish trade hit trailing stop.")
                return True
            if trade['direction'] == "bearish" and price >= (trade['max_favorable_price'] + trade['trail_distance']):
                print("[TRAIL EXIT] Bearish trade hit trailing stop.")
                return True

    return fallback_ichimoku_exit(trade, candles, ichimoku_lines)

def evaluate_open_trades(candles, ichimoku_lines, instrument):
    global open_trades
    idx = len(candles) - 1
    remaining_trades = []

    for trade in open_trades:
        if trade['instrument'] != instrument:
            remaining_trades.append(trade)
            continue

        if should_exit_trade(trade, candles, ichimoku_lines):
            exit_price = candles[idx]['close']
            pnl = exit_price - trade['entry_price'] if trade['direction'] == "bullish" else trade['entry_price'] - exit_price
            pnl_pips = round(pnl * 10000, 1)
            print(f"[SHADOW EXIT] {instrument} | {trade['direction'].upper()} exit | P/L: {pnl_pips} pips")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            log_path = f"logs/exit_{instrument}_{timestamp}.txt"
            with open(log_path, "w") as f:
                f.write(f"Instrument: {instrument}\n")
                f.write(f"Direction: {trade['direction']}\n")
                f.write(f"Entry Price: {trade['entry_price']}\n")
                f.write(f"Exit Price: {exit_price}\n")
                f.write(f"P/L: {pnl_pips} pips\n")
        else:
            remaining_trades.append(trade)

    open_trades = remaining_trades
