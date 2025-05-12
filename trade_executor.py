# trade_executor.py
# Executes and tracks trades — shadow or real — with Ichimoku-based exit logic

import oandapyV20.endpoints.orders as orders
import os
from datetime import datetime
import csv

# === Simple in-memory tracker ===
open_trades = []  # Each trade: dict with instrument, direction, entry_price, entry_index
TRADE_LOG_PATH = "logs/shadow_trades.csv"

def log_shadow_trade(trade):
    """
    Append a shadow trade to CSV log.
    """
    header = ["timestamp", "instrument", "direction", "entry_price", "entry_index"]
    data = [
        datetime.now().isoformat(),
        trade["instrument"],
        trade["direction"],
        trade["entry_price"],
        trade["entry_index"]
    ]

    file_exists = os.path.isfile(TRADE_LOG_PATH)

    with open(TRADE_LOG_PATH, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(data)

def execute_trade(intent, instrument, client, units=100, shadow=True, current_candle=None, candle_index=None):
    """
    Place or simulate a market order based on intent.
    Store shadow trades in memory.
    """
    bias = intent.get("bias")
    confidence = intent.get("confidence")

    if bias not in ["bullish", "bearish"]:
        print("[EXECUTOR] No clear directional bias. Standing down.")
        return

    # === Confidence-based risk scaling ===
    if confidence == "strong":
        scaled_units = 300
    elif confidence == "moderate":
        scaled_units = 150
    else:
        print("[EXECUTOR] Confidence too low to act. Standing down.")
        return

    side = "buy" if bias == "bullish" else "sell"
    units_signed = scaled_units if side == "buy" else -scaled_units

    if shadow:
        print(f"[SHADOW MODE] Would place {side.upper()} MARKET order for {instrument} ({units_signed} units).")
        print(f"[SHADOW MODE] Intent: {intent['comment']}")

        if current_candle is not None:
            open_trades.append({
                "instrument": instrument,
                "direction": bias,
                "entry_price": current_candle['close'],
                "entry_index": candle_index
            })
            log_shadow_trade(open_trades[-1])
        return

    # === REAL ORDER ===
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

def should_exit_trade(trade, candles, ichimoku_lines):
    """
    Decide if we should exit a trade based on Ichimoku exit signals.
    """
    idx = len(candles) - 1
    price = candles[idx]['close']

    tenkan = ichimoku_lines['tenkan_sen'][idx]
    kijun = ichimoku_lines['kijun_sen'][idx]
    chikou_data = ichimoku_lines['chikou_span']

    # Reversal signals
    tenkan_cross = tenkan < kijun if trade['direction'] == "bullish" else tenkan > kijun

    # Price inside cloud check
    span_a = {i: v for (i, v) in ichimoku_lines['senkou_span_a']}.get(idx)
    span_b = {i: v for (i, v) in ichimoku_lines['senkou_span_b']}.get(idx)
    in_kumo = False
    if span_a is not None and span_b is not None:
        upper = max(span_a, span_b)
        lower = min(span_a, span_b)
        in_kumo = lower <= price <= upper

    # Chikou failure
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

    if tenkan_cross or in_kumo:
        return True

    return False

def evaluate_open_trades(candles, ichimoku_lines, instrument):
    """
    Go through open shadow trades and check for exits.
    """
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
            pnl_pips = round(pnl * 10000, 1)  # Approximate to pips
            print(f"[SHADOW EXIT] {instrument} | {trade['direction'].upper()} exit | P/L: {pnl_pips} pips")

            # Optional: write to log file
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
