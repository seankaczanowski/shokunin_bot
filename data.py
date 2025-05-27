# data.py
# Market Data Handling for Ichimoku Bot

import os
import logging
from datetime import datetime

import pandas as pd
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.pricing as pricing
from ta.trend import IchimokuIndicator
from ta.trend import EMAIndicator
from ta.volatility import AverageTrueRange
from ta.utils import dropna

from indicators import compute_ichimoku, compute_heikin_ashi
from config import OANDA_ACCESS_TOKEN, OANDA_ENVIRONMENT, GRANULARITY, CANDLE_COUNT


class MarketDataClient:
    def __init__(self, access_token, account_id, is_live=False):
        environment = "live" if is_live else "practice"
        self.client = oandapyV20.API(access_token=access_token, environment=environment)
        self.account_id = account_id
        logging.info(f"Initialized MarketDataClient in {environment} mode")

    def fetch_candles(self, instrument, granularity="M15", count=100, price_type="M"):
        params = {
            "count": count,
            "granularity": granularity,
            "price": price_type
        }
        r = instruments.InstrumentsCandles(instrument=instrument, params=params)
        self.client.request(r)
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

        logging.info(f"Fetched {len(parsed_candles)} candles for {instrument}")
        return parsed_candles

    def candles_to_dataframe(self, parsed_candles):
        df = pd.DataFrame(parsed_candles)
        df["time"] = pd.to_datetime(df["time"])
        df.set_index("time", inplace=True)
        return df

    def get_latest_price(self, instrument):
        params = {"instruments": instrument}
        r = pricing.PricingInfo(accountID=self.account_id, params=params)
        self.client.request(r)
        prices = r.response["prices"][0]

        bid = float(prices["bids"][0]["price"])
        ask = float(prices["asks"][0]["price"])
        mid = round((bid + ask) / 2, 5)

        return {
            "instrument": instrument,
            "bid": bid,
            "ask": ask,
            "mid": mid,
            "time": prices["time"]
        }

    def get_batch_prices(self, instruments):
        instrument_str = ",".join(instruments)
        params = {"instruments": instrument_str}
        r = pricing.PricingInfo(accountID=self.account_id, params=params)
        self.client.request(r)

        price_dict = {}
        for p in r.response["prices"]:
            bid = float(p["bids"][0]["price"])
            ask = float(p["asks"][0]["price"])
            mid = round((bid + ask) / 2, 5)
            price_dict[p["instrument"]] = {
                "bid": bid,
                "ask": ask,
                "mid": mid,
                "time": p["time"]
            }
        return price_dict

    def convert_iso_to_datetime(self, iso_string):
        return datetime.fromisoformat(iso_string.replace("Z", "+00:00"))


# === Static Helpers ===
def load_data_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    df = df.rename(columns={
        "Open": "open", "High": "high", "Low": "low", "Close": "close"
    })
    df = df[['open', 'high', 'low', 'close']].astype(float)
    return df


