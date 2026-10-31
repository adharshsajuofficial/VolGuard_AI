"""Baseline volatility + realized-vol target. Returns are decimal log returns."""
import numpy as np
import pandas as pd

import config


def baseline_volatility(returns, window: int = config.BASELINE_WINDOW) -> float:
    """Annualized realized vol (%) from the last `window` returns.

    sigma = sqrt(252/window * sum(r^2)) * 100. Used as the flat baseline forecast for
    ANY horizon: annualized vol is horizon-invariant under the no-change assumption,
    so the same 20-day number is compared against the 5/10/20-day realized target.
    """
    r = np.asarray(returns, dtype=float)
    if len(r) < window:
        raise ValueError("Not enough data to compute baseline volatility")
    return float(np.sqrt(config.TRADING_DAYS / window * np.sum(r[-window:] ** 2)) * 100)


def realized_vol(returns, t: int, horizon: int = config.HORIZON) -> float:
    """Actual annualized vol (%) over days t+1..t+horizon (the target).

    sigma_h = sqrt(252/h * sum_{i=1..h} r_{t+i}^2) * 100. Indices are strictly
    after t, so nothing seen at time t leaks into the target.
    """
    r = np.asarray(returns, dtype=float)
    period = r[t + 1: t + 1 + horizon]
    if len(period) < horizon:
        raise ValueError("Not enough forward data for realized target")
    return float(np.sqrt(config.TRADING_DAYS / horizon * np.sum(period ** 2)) * 100)


# Backwards-compatible name (horizon defaults to 5).
realized_vol_5day = realized_vol


def rolling_vol(returns: pd.Series, window: int = config.BASELINE_WINDOW) -> pd.Series:
    """Rolling annualized realized vol (%), same formula as baseline."""
    return np.sqrt(config.TRADING_DAYS / window * (returns ** 2).rolling(window).sum()) * 100
