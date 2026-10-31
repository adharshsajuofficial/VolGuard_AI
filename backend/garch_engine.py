"""GARCH(1,1) fit + 5-day annualized volatility forecast via `arch`."""
import warnings

import numpy as np
from arch import arch_model

import config


class GarchError(Exception):
    """Model failed to fit or produced a non-finite forecast."""


def fit_garch(returns):
    """Fit constant-mean GARCH(1,1), normal errors. `returns` are decimal log returns.

    Returns are scaled x100 (percent) for optimizer stability.
    """
    r = np.asarray(returns, dtype=float) * 100.0
    if len(r) < 100:
        raise GarchError("need >= 100 observations")
    try:
        am = arch_model(r, mean="Constant", vol="GARCH", p=1, o=0, q=1, dist="normal", rescale=False)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return am.fit(disp="off", show_warning=False)
    except Exception as exc:
        raise GarchError(str(exc)) from exc


def forecast_garch_5day(res, horizon: int = config.HORIZON) -> float:
    """Annualized vol (%) over the next `horizon` days (5 by default; 10/20 supported).

    Sums the h=1..horizon conditional variances (cumulative window variance),
    then annualizes by 252/horizon. Variances are already in %^2 because the
    fit used percent returns, so no extra x100.
    """
    if horizon < 1:
        raise GarchError("horizon must be >= 1")
    f = res.forecast(horizon=horizon, reindex=False)
    var = np.asarray(f.variance.values[-1], dtype=float)
    out = float(np.sqrt(config.TRADING_DAYS / horizon * var.sum()))
    if not np.isfinite(out):
        raise GarchError("non-finite forecast")
    return out


# Horizon-neutral alias.
forecast_garch = forecast_garch_5day


def garch_forecast_from_returns(returns, horizon: int = config.HORIZON) -> float:
    """Convenience: fit on `returns` and forecast."""
    return forecast_garch_5day(fit_garch(returns), horizon)
