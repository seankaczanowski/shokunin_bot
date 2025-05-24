
# zen_heiken_assist.py

import pandas as pd

def compute_heiken_ashi(df):
    ha_df = pd.DataFrame(index=df.index)
    ha_df['HA_Close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    ha_open = [(df['open'].iloc[0] + df['close'].iloc[0]) / 2]  # seed
    for i in range(1, len(df)):
        ha_open.append((ha_open[i-1] + ha_df['HA_Close'].iloc[i-1]) / 2)
    ha_df['HA_Open'] = ha_open
    ha_df['HA_High'] = df[['high', 'low']].join(ha_df[['HA_Open', 'HA_Close']]).max(axis=1)
    ha_df['HA_Low'] = df[['high', 'low']].join(ha_df[['HA_Open', 'HA_Close']]).min(axis=1)
    return ha_df

def ha_trend_strength(ha_df, lookback=3):
    """
    Returns +1 for bullish, -1 for bearish, 0 for neutral based on HA color consistency.
    """
    recent = ha_df.tail(lookback)
    bullish = (recent['HA_Close'] > recent['HA_Open']).sum()
    bearish = (recent['HA_Close'] < recent['HA_Open']).sum()
    if bullish == lookback:
        return 1
    elif bearish == lookback:
        return -1
    return 0
