# ichimoku_bot/strategy.py

# --- Base Strategy Class ---
class BaseStrategy:
    def evaluate(self, df):
        # every strategy must define its own evaluate method
        raise NotImplementedError("Strategy must implement an evaluate method.")

    def should_exit(self, df, entry_signal):
        # every strategy must define its own exit logic
        raise NotImplementedError("Strategy must implement a should_exit method.")


# --- Kijun-Tenkan Cross Strategy ---
class KijunTenkanCross(BaseStrategy):
    def evaluate(self, df):
        # skip if insufficient data (ichimoku needs at least 52 periods)
        if len(df) < 52:
            return None

        latest = df.iloc[-1]      # current candle
        previous = df.iloc[-2]    # previous candle

        # check for tenkan-kijun crossover
        signal = None
        if previous['tenkan_sen'] < previous['kijun_sen'] and latest['tenkan_sen'] > latest['kijun_sen']:
            signal = 'buy'
        elif previous['tenkan_sen'] > previous['kijun_sen'] and latest['tenkan_sen'] < latest['kijun_sen']:
            signal = 'sell'

        if not signal:
            return None

        # confirmation 1: price position relative to the cloud
        price_above_cloud = latest['close'] > latest['senkou_span_a'] and latest['close'] > latest['senkou_span_b']
        price_below_cloud = latest['close'] < latest['senkou_span_a'] and latest['close'] < latest['senkou_span_b']

        cloud_confirmation = (
            signal == 'buy' and price_above_cloud
        ) or (
            signal == 'sell' and price_below_cloud
        )

        # confirmation 2: chikou span location vs. current price
        chikou_span = df.iloc[-27]['close']  # close price from 26 periods ago
        chikou_confirmation = (
            signal == 'buy' and chikou_span < latest['close']
        ) or (
            signal == 'sell' and chikou_span > latest['close']
        )

        # count confirmations and assign confidence score
        confirmations = int(cloud_confirmation) + int(chikou_confirmation)
        if confirmations == 0:
            return None

        confidence = 0.6 if confirmations == 1 else 0.9

        return {
            "signal": signal,
            "confidence": confidence,
            "confirmations": confirmations,
            "time": latest.name
        }

    def should_exit(self, df, entry_signal):
        # exit when price re-enters the cloud — a return to uncertainty
        if len(df) < 1:
            return False

        latest = df.iloc[-1]
        span_a = latest['senkou_span_a']
        span_b = latest['senkou_span_b']

        upper_cloud = max(span_a, span_b)
        lower_cloud = min(span_a, span_b)

        if entry_signal == 'buy':
            return latest['close'] <= upper_cloud
        elif entry_signal == 'sell':
            return latest['close'] >= lower_cloud

        return False


# --- Optional: time-based session labeling (stub) ---
def get_session_insight(timestamp):
    # optional: return 'Tokyo', 'London', or 'New York' session label
    pass
