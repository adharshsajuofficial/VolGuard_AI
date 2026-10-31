"""Data Pipeline & Numerical Integrity Tests
Person 3 Deliverable: Audits dataset cleanliness, absence of NaNs, date ordering,
and graceful fallback mechanisms between Yahoo Finance and CSV sources.
"""
import sys
import os
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import config
import data as data_mod


def test_prepare_dataframe_cleans_and_sorts():
    """Verify data.prepare cleans index, sorts dates, calculates returns, and drops NaNs."""
    raw_dates = ["2023-01-05", "2023-01-03", "2023-01-04"]  # unordered
    raw_df = pd.DataFrame({
        "Close": [102.0, 100.0, 101.0]
    }, index=pd.to_datetime(raw_dates))
    
    clean_df = data_mod.prepare(raw_df)
    
    # Must be sorted ascending; first date (2023-01-03) dropped because return requires lag(1)
    assert list(clean_df.index.strftime("%Y-%m-%d")) == ["2023-01-04", "2023-01-05"]
    assert "Price" in clean_df.columns
    assert "Return" in clean_df.columns
    assert clean_df["Return"].isna().sum() == 0
    assert not np.isinf(clean_df["Return"]).any()


def test_prepare_drops_non_positive_prices():
    """Verify that zero or negative prices (e.g. data corruptions) are filtered out."""
    dates = pd.date_range("2023-01-01", periods=5, freq="D")
    raw_df = pd.DataFrame({
        "Close": [100.0, 0.0, -5.0, 102.0, 103.0]
    }, index=dates)
    
    clean_df = data_mod.prepare(raw_df)
    assert (clean_df["Price"] > 0).all()


def test_fallback_csv_dataset_health():
    """Verify backend/prices.csv contains valid SPY and ^NSEI records without NaNs."""
    for sym in ["SPY", "^NSEI"]:
        df = data_mod.load_csv(sym)
        assert len(df) > 500, f"Fallback CSV has insufficient records for {sym}"
        assert "Close" in df.columns or "Adj Close" in df.columns
        
        prepared = data_mod.prepare(df)
        assert prepared.index.is_monotonic_increasing
        assert prepared["Price"].isna().sum() == 0
        assert prepared["Return"].isna().sum() == 0
        assert not np.isinf(prepared["Return"]).any()
        assert (prepared["Price"] > 0).all()


def test_cache_functionality():
    """Verify data caching reduces redundant calls and clear_cache clears it."""
    data_mod.clear_cache()
    df1 = data_mod.load_data("SPY", use_cache=True)
    df2 = data_mod.load_data("SPY", use_cache=True)
    assert df1 is df2, "Cache hit did not return cached DataFrame object"
    
    data_mod.clear_cache()
    assert len(data_mod._cache) == 0


def test_invalid_symbol_not_found():
    """Verify that querying a non-existent symbol cleanly raises DataNotFoundError."""
    with pytest.raises(data_mod.DataNotFoundError):
        data_mod.load_data("DEFINITELY_NOT_A_VALID_STOCK_TICKER_12345")


def test_trading_calendar_continuity():
    """Verify that returned data doesn't contain weekend dates."""
    df = data_mod.load_data("SPY")
    day_of_week = df.index.dayofweek
    # In standard US trading, weekdays are 0 (Monday) to 4 (Friday)
    # yfinance and prices.csv should not contain weekend trades (5=Sat, 6=Sun)
    weekend_count = (day_of_week >= 5).sum()
    assert weekend_count == 0, f"Found {weekend_count} weekend trading dates in dataset!"
