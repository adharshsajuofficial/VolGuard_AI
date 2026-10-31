"""Chronological walk-forward backtest. Zero lookahead.

At index i the models see returns[:i+1] only; the target is returns[i+1:i+6].
GARCH refits on a capped rolling window and every `step` days for speed.
"""
import logging

import numpy as np
import pandas as pd

import config
from garch_engine import GarchError, garch_forecast_from_returns
from models import baseline_volatility, realized_vol_5day

log = logging.getLogger("volguard.backtest")


def _metrics(pred: np.ndarray, actual: np.ndarray) -> dict:
    err = pred - actual
    return {
        "MAE": float(np.mean(np.abs(err))),
        "RMSE": float(np.sqrt(np.mean(err ** 2))),
        "bias": float(np.mean(err)),
    }


def run_backtest(returns: pd.Series,
                 min_train: int = config.BT_MIN_TRAIN,
                 step: int = config.BT_STEP,
                 max_points: int = config.BT_MAX_POINTS,
                 fit_window: int = config.BT_FIT_WINDOW) -> dict:
    """Walk-forward evaluation on a Series of decimal log returns (DatetimeIndex)."""
    r = returns.to_numpy(dtype=float)
    dates = returns.index
    n = len(r)
    h = config.HORIZON
    last_i = n - 1 - h                      # last i with a full 5-day target
    first_i = min_train - 1
    if last_i < first_i:
        raise ValueError(f"need at least {min_train + h} returns, got {n}")

    idx = list(range(last_i, first_i - 1, -step))[:max_points][::-1]  # newest-aligned

    rows, skipped = [], 0
    for i in idx:
        train = r[max(0, i + 1 - fit_window): i + 1]   # data up to and incl. day i
        try:
            g = garch_forecast_from_returns(train)
        except GarchError as exc:
            skipped += 1
            log.warning("GARCH skip at %s: %s", dates[i].date(), exc)
            continue
        rows.append({
            "date": dates[i].date().isoformat(),
            "baseline": baseline_volatility(r[: i + 1]),
            "garch": g,
            "actual": realized_vol_5day(r, i),
        })
    if not rows:
        raise ValueError("backtest produced no points")

    df = pd.DataFrame(rows)
    actual = df["actual"].to_numpy()
    mb = _metrics(df["baseline"].to_numpy(), actual)
    mg = _metrics(df["garch"].to_numpy(), actual)
    return {
        "n_points": len(df),
        "skipped": skipped,
        "step": step,
        "baseline": mb,
        "garch": mg,
        "better_model": "garch" if mg["RMSE"] < mb["RMSE"] else "baseline",
        "predictions": rows,
    }
