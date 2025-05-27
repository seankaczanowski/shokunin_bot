# ichimoku_bot/indicators.py
# Modular Indicator Calculator Using `ta` Library

import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, SMAIndicator, MACD
from ta.volatility import BollingerBands, AverageTrueRange

# Ichimoku and Heikin Ashi Calculations
def add_ichimoku_to_df(df):
    ichimoku = IchimokuIndicator(
        high=df['high'],
        low=df['low'],
        window1=9,
        window2=26,
        window3=52,
        visual=True,
        fillna=False
    )
    df['tenkan_sen'] = ichimoku.ichimoku_conversion_line()
    df['kijun_sen'] = ichimoku.ichimoku_base_line()
    df['senkou_span_a'] = ichimoku.ichimoku_a()
    df['senkou_span_b'] = ichimoku.ichimoku_b()
    df['chikou_span'] = df['close'].shift(-26)
    return df

def add_heikin_ashi_to_df(df):
    df = df.copy()
    df['ha_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    df['ha_open'] = df['open']
    for i in range(1, len(df)):
        df.iloc[i, df.columns.get_loc('ha_open')] = (
            df.iloc[i - 1]['ha_open'] + df.iloc[i - 1]['ha_close']
        ) / 2
    df['ha_high'] = df[['ha_open', 'ha_close', 'high']].max(axis=1)
    df['ha_low'] = df[['ha_open', 'ha_close', 'low']].min(axis=1)
    return df

def add_atr_to_df(df, window=14):
    df = df.copy()
    atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=window)
    df['atr'] = atr.average_true_range()
    return df

# Momentum Indicators
def add_rsi(df, window=14):
    rsi = RSIIndicator(close=df['close'], window=window)
    df['rsi'] = rsi.rsi()
    return df

# Trend Indicators
def add_ema(df, window=20):
    ema = EMAIndicator(close=df['close'], window=window)
    df[f'ema_{window}'] = ema.ema_indicator()
    return df

def add_sma(df, window=20):
    sma = SMAIndicator(close=df['close'], window=window)
    df[f'sma_{window}'] = sma.sma_indicator()
    return df

def add_macd(df):
    macd = MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_diff'] = macd.macd_diff()
    return df

# Volatility Indicators
def add_bollinger_bands(df, window=20, std_dev=2):
    bb = BollingerBands(close=df['close'], window=window, window_dev=std_dev)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_middle'] = bb.bollinger_mavg()
    df['bb_lower'] = bb.bollinger_lband()
    df['bb_width'] = bb.bollinger_wband()
    return df

def add_atr(df, window=14):
    atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=window)
    df['atr'] = atr.average_true_range()
    return df
