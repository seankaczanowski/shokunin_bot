# ichimoku_bot/risk.py
# Risk Management Module
# Anchored in Zen principles: flow freely, but never fall off the cliff

def calculate_position_size(account_balance, stop_loss_pips, pip_value=0.10, risk_pct=0.01):
    """
    Calculate position size (units) based on account balance and defined stop loss.

    Parameters:
    - account_balance (float): Total account balance in base currency.
    - stop_loss_pips (float): Distance to stop loss in pips.
    - pip_value (float): Approximate value per pip per unit (default $0.10 per micro lot).
    - risk_pct (float): Fraction of account to risk on trade (default 1%).

    Returns:
    - int: Trade size in units.
    """
    risk_amount = account_balance * risk_pct
    units = risk_amount / (stop_loss_pips * pip_value)
    return int(units)


def apply_emergency_stop(account_balance, equity, max_drawdown_pct=0.10):
    """
    Determine whether an emergency stop should be triggered.

    Parameters:
    - account_balance (float): Starting balance.
    - equity (float): Current equity.
    - max_drawdown_pct (float): Maximum allowable drawdown before halting trading.

    Returns:
    - bool: True if emergency stop triggered, False otherwise.
    """
    drawdown = (account_balance - equity) / account_balance
    return drawdown >= max_drawdown_pct


# --- Placeholder for future expansion --- #

def adjust_risk_based_on_performance(win_rate, current_risk_pct):
    """
    (Coming Soon) Adjust risk level dynamically based on win rate performance.
    """
    pass


def limit_trade_exposure(open_positions, max_trades=2):
    """
    (Optional) Block further trades if too many positions are open.
    
    Returns:
    - bool: True if allowed to trade, False if max reached.
    """
    return len(open_positions) < max_trades
