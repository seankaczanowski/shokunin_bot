# shokunin_bot

A disciplined and modular Forex trading bot inspired by the philosophy of *shokunin*—the Japanese artisan who devotes their life to the craft with humility, care, and precision.

---

## 🌿 Philosophy

This bot walks the middle path: rooted in the intuitive wisdom of Ichimoku Kinko Hyo, but built with modern tools, clean architecture, and quiet consistency.

We don’t chase. We observe.  
We don’t force. We respond.  
No shortcuts to satori—just well-drawn candlesticks and clear decisions.

---

## ⚙️ Project Structure

```bash
shokunin_bot/
├── main.py                # Bot runner
├── config.py              # Settings and API credentials
├── broker.py              # OANDA integration, order execution
├── data.py                # Candle fetching, formatting
├── indicators.py          # Ichimoku + Heikin Ashi logic
├── strategy.py            # Signal interpretation and entry logic
├── risk.py                # Position sizing, stoploss, safety rules
├── memory.py              # Logging, shadow trades, diagnostics
│
├── archive/               # Legacy files (old zen_trader_bot)
├── logs/                  # CSV logs (ignored by Git)
├── charts/, sketches/     # Visual outputs (ignored by Git)
├── datasets/, utils/      # Helpers & data (optional tools)
├── .venv/                 # Virtual environment (ignored)
│
├── requirements.txt       # Minimal production dependencies
├── requirements-dev.txt   # Extra tools for notebooks, plots
├── setup_env.bat          # Quick setup for production bot
├── setup_dev.bat          # Adds dev tools (Jupyter, seaborn, etc.)

---

## 🏷️ Legacy

This project was originally developed under the name `zen_trader_bot`, a freeform exploration into intuition-led trading with poetic ambition. That spirit lives on—but `shokunin_bot` represents a refined evolution: clean, disciplined, and purpose-built.

Every line of code now reflects the craft.

> “Perfection is not when there is nothing more to add,  
> but when there is nothing left to take away.” — Antoine de Saint-Exupéry

---
