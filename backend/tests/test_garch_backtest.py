import numpy as np
import pandas as pd
import pytest

import data as data_mod
from backtest import run_backtest
from garch_engine import GarchError, fit_garch, forecast_garch_5day, garch_forecast_from_returns


@pytest.fixture(scope="module")
def rets():
    return data_mod.load_data("SPY")["Return"]


@pytest.mark.parametrize("h", [5, 10, 20])
def test_garch_forecast_finite_positive(rets, h):
    v = garch_forecast_from_returns(rets.to_numpy()[-1000:], horizon=h)
    assert np.isfinite(v) and 0 < v < 200


def test_garch_rejects_short_and_bad_horizon(rets):
    with pytest.raises(GarchError):
        fit_garch(np.zeros(50))
    with pytest.raises(GarchError):
        forecast_garch_5day(fit_garch(rets.to_numpy()[-500:]), horizon=0)


def test_backtest_shape_and_no_lookahead(rets):
    res = run_backtest(rets, max_points=15)
    assert res["n_points"] == 15 and res["horizon"] == 5 and res["step"] == 5
    for k in ("MAE", "RMSE", "bias", "QLIKE"):
        assert np.isfinite(res["baseline"][k]) and np.isfinite(res["garch"][k])
    dates = [p["date"] for p in res["predictions"]]
    assert dates == sorted(dates)
    # recompute one row by hand with data up to that date only
    p = res["predictions"][-1]
    i = rets.index.get_loc(pd.Timestamp(p["date"]))
    r = rets.to_numpy()
    assert p["baseline"] == pytest.approx(np.sqrt(252 / 20 * np.sum(r[i - 19:i + 1] ** 2)) * 100)
    assert p["actual"] == pytest.approx(np.sqrt(252 / 5 * np.sum(r[i + 1:i + 6] ** 2)) * 100)


@pytest.mark.parametrize("h", [10, 20])
def test_backtest_horizon(rets, h):
    res = run_backtest(rets, max_points=10, step=h, horizon=h)
    assert res["horizon"] == h
    i = rets.index.get_loc(pd.Timestamp(res["predictions"][-1]["date"]))
    assert i + h <= len(rets) - 1          # full h-day target exists
    r = rets.to_numpy()
    assert res["predictions"][-1]["actual"] == pytest.approx(
        np.sqrt(252 / h * np.sum(r[i + 1:i + 1 + h] ** 2)) * 100)


def test_backtest_too_little_data(rets):
    with pytest.raises(ValueError):
        run_backtest(rets.iloc[:300])
