"""Baseline volatility + realized-vol target. Returns are decimal log returns."""
import numpy as np
import pandas as pd

import config


def baseline_volatility(returns, window: int = config.BASELINE_WINDOW) -> float:
    """Annualized realized vol (%) from the last `window` returns.

    sigma = sqrt(252/window * sum(r^2)) * 100. Used as the 5-day forecast.
    """
    r = np.asarray(returns, dtype=float)
    if len(r) < window:
        raise ValueError("Not enough data to compute baseline volatility")
    return float(np.sqrt(config.TRADING_DAYS / window * np.sum(r[-window:] ** 2)) * 100)


def realized_vol_5day(returns, t: int, horizon: int = config.HORIZON) -> float:
    """Actual annualized vol (%) over days t+1..t+horizon (the target)."""
    r = np.asarray(returns, dtype=float)
    period = r[t + 1: t + 1 + horizon]
    if len(period) < horizon:
        raise ValueError("Not enough forward data for realized target")
    return float(np.sqrt(config.TRADING_DAYS / horizon * np.sum(period ** 2)) * 100)


def rolling_vol(returns: pd.Series, window: int = config.BASELINE_WINDOW) -> pd.Series:
    """Rolling annualized realized vol (%), same formula as baseline."""
    return np.sqrt(config.TRADING_DAYS / window * (returns ** 2).rolling(window).sum()) * 100
