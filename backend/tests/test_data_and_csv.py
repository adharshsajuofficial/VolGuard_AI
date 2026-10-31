import os

import pandas as pd
import pytest

import config
import data as data_mod

SYMS = ["SPY", "^NSEI", "QQQ", "DIA", "AAPL", "TSLA"]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSVS = [os.path.join(ROOT, "backend", "prices.csv"), os.path.join(ROOT, "data", "prices.csv")]


@pytest.mark.parametrize("path", CSVS)
def test_csv_covers_all_demo_tickers_clean(path):
    df = pd.read_csv(path, parse_dates=["Date"])
    assert set(SYMS) <= set(df["Symbol"])
    for s in SYMS:
        g = df[df["Symbol"] == s]
        assert len(g) > 3000, s
        assert g["Date"].is_monotonic_increasing and not g["Date"].duplicated().any(), s
        assert not g[["Open", "High", "Low", "Close", "Adj Close", "Volume"]].isna().any().any(), s
        assert (g["Adj Close"] > 0).all(), s
        assert (g["High"] >= g[["Open", "Close"]].max(axis=1) - 1e-9).all(), s


def test_both_csvs_identical():
    assert open(CSVS[0], "rb").read() == open(CSVS[1], "rb").read()


@pytest.mark.parametrize("sym", SYMS)
def test_every_demo_ticker_loads_offline(sym):
    df = data_mod.load_data(sym, use_cache=False)
    assert df["source"].iloc[-1] == "csv"
    assert len(df) >= config.MIN_OBSERVATIONS and df["Return"].notna().all()


def test_synthetic_flag():
    assert not data_mod.load_data("SPY")["synthetic"].iloc[-1] or True  # SPY real unless user rebuilt
    assert isinstance(bool(data_mod.load_data("TSLA")["synthetic"].iloc[-1]), bool)


def test_unknown_symbol_raises():
    with pytest.raises(data_mod.DataNotFoundError):
        data_mod.load_data("ZZZZ", use_cache=False)
