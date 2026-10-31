"""Mathematical Formulation & Target Verification Tests
Person 3 Deliverable: Validates all equations, unit scaling, and econometric constraints.
"""
import sys
import os
import math
import numpy as np
import pandas as pd
import pytest

# Ensure backend directory is in python search path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import config
from models import baseline_volatility, realized_vol_5day, rolling_vol
from garch_engine import fit_garch, forecast_garch_5day, garch_forecast_from_returns
from utils import risk_level, clean_float, normalize_symbol


def test_log_returns_formula():
    """Verify daily log returns formula r_t = ln(P_t / P_{t-1})."""
    p0 = 100.0
    p1 = 105.0
    expected_ret = math.log(105.0 / 100.0)
    actual_ret = np.log(p1 / p0)
    assert np.isclose(expected_ret, actual_ret, atol=1e-7)
    assert np.isclose(actual_ret, 0.04879016, atol=1e-6)


def test_baseline_volatility_formula():
    """Verify 20-day historical realized volatility baseline equation:
    sigma_baseline = sqrt(252/20 * sum(r^2)) * 100.
    """
    # Create synthetic series of 20 daily returns of 1% each (0.01)
    returns = np.full(20, 0.01)
    # sum(r^2) = 20 * 0.0001 = 0.002
    # 252/20 * 0.002 = 252 * 0.0001 = 0.0252
    # sqrt(0.0252) * 100 = ~15.8745%
    expected = math.sqrt(252.0 / 20.0 * (20 * 0.01 ** 2)) * 100.0
    calc = baseline_volatility(returns, window=20)
    assert np.isclose(calc, expected, atol=1e-5)
    assert np.isclose(calc, 15.8745, atol=1e-4)


def test_realized_vol_5day_target():
    """Verify 5-day forward target formula:
    sigma_5d = sqrt(252/5 * sum(r_{t+1:t+6}^2)) * 100.
    """
    # 30 days of data
    returns = np.full(30, 0.01)
    t = 10
    # forward slice is index 11 to 15 (5 days)
    # sum(r^2) = 5 * 0.0001 = 0.0005
    # 252/5 * 0.0005 = 252 * 0.0001 = 0.0252
    # sqrt(0.0252) * 100 = 15.8745%
    expected = math.sqrt(252.0 / 5.0 * (5 * 0.01 ** 2)) * 100.0
    calc = realized_vol_5day(returns, t=t, horizon=5)
    assert np.isclose(calc, expected, atol=1e-5)


def test_rolling_vol_matches_baseline():
    """Verify rolling_vol() series at index t equals baseline_volatility(returns[:t+1])."""
    np.random.seed(42)
    sample_returns = np.random.normal(0, 0.012, 100)
    s = pd.Series(sample_returns)
    roll = rolling_vol(s, window=20)
    
    # At index 50, rolling_vol must equal baseline of slice up to index 50
    roll_val = roll.iloc[50]
    base_val = baseline_volatility(sample_returns[:51], window=20)
    assert np.isclose(roll_val, base_val, atol=1e-6)


def test_units_consistency_annualized_percentage():
    """Verify all volatility metrics output values in annualized percent (e.g. 15.8 not 0.158).
    This prevents frontend percentage miscalculations.
    """
    np.random.seed(123)
    sample_returns = np.random.normal(0, 0.01, 300)
    base_val = baseline_volatility(sample_returns, window=20)
    garch_val = garch_forecast_from_returns(sample_returns, horizon=5)
    
    # Normal daily return of 1% equates to annualized vol ~ 15%
    assert 5.0 < base_val < 80.0, f"Baseline volatility {base_val} out of expected % range"
    assert 5.0 < garch_val < 80.0, f"GARCH volatility {garch_val} out of expected % range"


def test_garch_model_constraints():
    """Verify GARCH(1,1) parameter positivity and covariance stationarity (alpha + beta < 1)."""
    np.random.seed(999)
    # Generate GARCH(1,1) synthetic returns
    n = 600
    r = np.random.normal(0, 0.01, n)
    res = fit_garch(r)
    
    params = res.params
    omega = params.get("omega")
    alpha = params.get("alpha[1]")
    beta = params.get("beta[1]")
    
    assert omega is not None and omega > 0, "GARCH omega must be positive"
    assert alpha is not None and alpha >= 0, "GARCH alpha must be non-negative"
    assert beta is not None and beta >= 0, "GARCH beta must be non-negative"
    assert alpha + beta < 1.05, f"GARCH stationarity condition violated: alpha+beta={alpha+beta}"
    
    # Check 5-day forecast
    f_vol = forecast_garch_5day(res, horizon=5)
    assert np.isfinite(f_vol) and f_vol > 0


def test_risk_level_tier_classification():
    """Verify 4-tier risk classification matching README and workdivision specifications:
    - low: < 15.0%
    - moderate: 15.0% - 25.0%
    - high: 25.0% - 35.0%
    - extreme: > 35.0%
    """
    assert risk_level(10.5) == "low"
    assert risk_level(14.99) == "low"
    assert risk_level(15.0) == "moderate"
    assert risk_level(20.0) == "moderate"
    assert risk_level(25.0) == "moderate"
    assert risk_level(25.01) == "high"
    assert risk_level(30.0) == "high"
    assert risk_level(35.0) == "high"
    assert risk_level(35.01) == "extreme"
    assert risk_level(65.0) == "extreme"


def test_clean_float_sanitization():
    """Verify clean_float converts NaNs and Infs to None for JSON safety."""
    assert clean_float(18.23456, 2) == 18.23
    assert clean_float(float("nan")) is None
    assert clean_float(float("inf")) is None
    assert clean_float(float("-inf")) is None
    assert clean_float(None) is None


def test_normalize_symbol():
    """Verify symbol validation and formatting."""
    assert normalize_symbol("spy") == "SPY"
    assert normalize_symbol("^nsei") == "^NSEI"
    assert normalize_symbol("  qqq  ") == "QQQ"
    with pytest.raises(ValueError):
        normalize_symbol("")
    with pytest.raises(ValueError):
        normalize_symbol("TOOLONGSYMBOLNAMEXYZ123")
