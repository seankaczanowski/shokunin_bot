### ichimoku_bot/main.py

import os
import time
import csv
from datetime import datetime
from dotenv import load_dotenv

import oandapyV20
import matplotlib
matplotlib.use("Agg") # Headless plotting for cloud instances
import matplotlib.pyplot as plt

import config 
from data import fetch_candles, compute_ichimoku, plot_ichimoku

### Load Environment Variable
load_dotenv()

### --- Main Loop --- ###
def main():
    # Entry point for the bot
    pass

if __name__ == "__main__":
    main()