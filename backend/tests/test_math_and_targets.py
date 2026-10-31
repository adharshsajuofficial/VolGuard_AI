import numpy as np
import pandas as pd
import pytest

import config
import data as data_mod
from models import baseline_volatility, realized_vol, realized_vol_5day, rolling_vol


def test_log_returns_match_definition():
    df = data_mod.load_data("SPY")
    expected = np.log(df["Price"] / df["Price"].shift(1)).dropna()
    # first row's return uses the (dropped) prior price, so compare from the 2nd row on
    np.testing.assert_allclose(df["Return"].to_numpy()[1:], expected.to_numpy())
    assert df["Return"].notna().all() and df.index.is_monotonic_increasing


def test_baseline_formula():
    r = np.random.default_rng(1).normal(0, 0.01, 100)
    exp = np.sqrt(252 / 20 * np.sum(r[-20:] ** 2)) * 100
    assert baseline_volatility(r) == pytest.approx(exp)


def test_baseline_needs_enough_data():
    with pytest.raises(ValueError):
        baseline_volatility(np.zeros(10))


@pytest.mark.parametrize("h", [5, 10, 20])
def test_target_uses_only_future_days(h):
    r = np.random.default_rng(2).normal(0, 0.01, 200)
    t = 100
    exp = np.sqrt(252 / h * np.sum(r[t + 1:t + 1 + h] ** 2)) * 100
    assert realized_vol(r, t, h) == pytest.approx(exp)
    r2 = r.copy()
    r2[: t + 1] = 5.0   # changing the past/present must not move the target
    assert realized_vol(r2, t, h) == pytest.approx(exp)
    r3 = r.copy()
    r3[t + 1] += 0.05   # changing day t+1 must move it
    assert realized_vol(r3, t, h) != pytest.approx(exp)


def test_target_alias_and_short_data():
    r = np.ones(10) * 0.01
    assert realized_vol_5day(r, 2) == realized_vol(r, 2, 5)
    with pytest.raises(ValueError):
        realized_vol(r, 8, 5)


def test_rolling_vol_matches_baseline():
    r = pd.Series(np.random.default_rng(3).normal(0, 0.01, 60))
    assert rolling_vol(r).iloc[-1] == pytest.approx(baseline_volatility(r.to_numpy()))
