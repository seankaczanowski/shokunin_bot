# ichimoku_bot/broker.py
# Oanda Connection / Account Info 
# Order Actions / Trade Management
# Price / Market Data
# Utility / Safety 

# Dependencies
# Standard Library
import os
import logging

# Third-Party Libraries
import oandapyV20
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.positions as positions

# Local Modules
from dotenv import load_dotenv
from config import ACCOUNT_ID, OANDA_API_KEY

# Load environment variables if needed
load_dotenv()

class BrokerClient:
    def __init__(self, account_id=ACCOUNT_ID, access_token=OANDA_API_KEY, is_live=False):
        environment = "live" if is_live else "practice"
        self.client = oandapyV20.API(access_token=access_token, environment=environment)
        self.account_id = account_id
        logging.info(f"BrokerClient initialized in {environment} mode.")

    # === Account Info ===
    def get_account_summary(self):
        r = accounts.AccountSummary(accountID=self.account_id)
        self.client.request(r)
        return r.response

    def get_open_trades(self):
        r = trades.OpenTrades(accountID=self.account_id)
        self.client.request(r)
        return r.response.get("trades", [])

    def get_open_positions(self):
        r = positions.OpenPositions(accountID=self.account_id)
        self.client.request(r)
        return r.response.get("positions", [])

    def get_pending_orders(self):
        r = orders.OrdersPending(accountID=self.account_id)
        self.client.request(r)
        return r.response.get("orders", [])

    # Order Actions
    def place_market_order(self, instrument, units, stop_loss=None, take_profit=None):
        order = {
            "order": {
                "instrument": instrument,
                "units": str(units),
                "type": "MARKET",
                "positionFill": "DEFAULT"
            }
        }

        if stop_loss:
            order["order"]["stopLossOnFill"] = {"price": str(stop_loss)}
        if take_profit:
            order["order"]["takeProfitOnFill"] = {"price": str(take_profit)}

        r = orders.OrderCreate(accountID=self.account_id, data=order)
        self.client.request(r)
        return r.response

    def close_trade(self, trade_id):
        r = trades.TradeClose(accountID=self.account_id, tradeID=trade_id)
        self.client.request(r)
        return r.response

    def close_all_trades(self, instrument=None):
        open_trades = self.get_open_trades()
        closed = []
        for trade in open_trades:
            if instrument and trade["instrument"] != instrument:
                continue
            result = self.close_trade(trade["id"])
            closed.append(result)
        return closed

    # Price / Market Data
    def get_price(self, instrument):
        params = {"instruments": instrument}
        r = pricing.PricingInfo(accountID=self.account_id, params=params)
        self.client.request(r)
        price_data = r.response["prices"][0]
        bid = float(price_data["bids"][0]["price"])
        ask = float(price_data["asks"][0]["price"])
        mid = round((bid + ask) / 2, 5)
        return {"bid": bid, "ask": ask, "mid": mid, "time": price_data["time"]}

    def get_candle_data(self, instrument, granularity="M15", count=100):
        import oandapyV20.endpoints.instruments as instruments_api
        params = {
            "count": count,
            "granularity": granularity,
            "price": "M"
        }
        r = instruments_api.InstrumentsCandles(instrument=instrument, params=params)
        self.client.request(r)
        candles = r.response.get("candles", [])

        return [
            {
                "time": c["time"],
                "open": float(c["mid"]["o"]),
                "high": float(c["mid"]["h"]),
                "low": float(c["mid"]["l"]),
                "close": float(c["mid"]["c"])
            }
            for c in candles if c["complete"]
        ]

    # Utility / Safety
    def is_trade_allowed(self, instrument):
        open_trades = self.get_open_trades()
        for trade in open_trades:
            if trade["instrument"] == instrument:
                logging.info(f"Trade blocked: already an open trade on {instrument}")
                return False
        return True
