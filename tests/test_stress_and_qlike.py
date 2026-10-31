"""Evaluation Metrics, QLIKE Loss, Stress Testing & Risk Alarm Fidelity
Person 3 Deliverable: Benchmarks formal volatility loss functions (MAE, RMSE, QLIKE)
and stress-tests models during historical market crisis regimes.
"""
import sys
import os
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import config
import data as data_mod
from models import baseline_volatility, realized_vol_5day
from garch_engine import garch_forecast_from_returns
from utils import risk_level


def qlike_loss(actual_vol: np.ndarray, pred_vol: np.ndarray) -> float:
    """Quasi-Likelihood (QLIKE) loss function (Patton, 2011).
    Standard robust loss function in econometric volatility literature.
    QLIKE = mean( actual^2 / pred^2 - ln(actual^2 / pred^2) - 1 )
    Penalizes under-predictions of volatility heavily (asymmetry for risk management).
    """
    actual_var = np.maximum(1e-6, actual_vol ** 2)
    pred_var = np.maximum(1e-6, pred_vol ** 2)
    ratio = actual_var / pred_var
    loss = ratio - np.log(ratio) - 1.0
    return float(np.mean(loss))


def test_qlike_loss_properties():
    """Verify QLIKE loss is zero when prediction is perfect and strictly positive otherwise."""
    actual = np.array([15.0, 20.0, 25.0])
    perfect_pred = np.array([15.0, 20.0, 25.0])
    under_pred = np.array([10.0, 15.0, 20.0])  # Underestimated risk
    over_pred = np.array([20.0, 25.0, 30.0])   # Overestimated risk
    
    assert np.isclose(qlike_loss(actual, perfect_pred), 0.0, atol=1e-7)
    assert qlike_loss(actual, under_pred) > 0.0
    assert qlike_loss(actual, over_pred) > 0.0
    
    # QLIKE penalizes underestimation of volatility more than overestimation
    # (crucial for financial solvency / VaR compliance)
    loss_under = qlike_loss(np.array([20.0]), np.array([10.0]))
    loss_over = qlike_loss(np.array([20.0]), np.array([30.0]))
    assert loss_under > loss_over, "QLIKE must penalize underestimating risk more severely"


def test_covid_2020_stress_regime():
    """Stress-test: Evaluate model performance and volatility clustering during the March 2020 COVID shock."""
    df = data_mod.load_data("SPY")
    
    # Isolate COVID crash period: Feb 2020 to April 2020
    covid_df = df.loc["2020-02-01":"2020-04-30"]
    assert len(covid_df) >= 40, "COVID-19 period records missing"
    
    # Check max realized volatility in this shock
    covid_returns = df.loc[:"2020-04-30", "Return"].to_numpy()
    peak_idx = np.argmin(df.loc["2020-03-01":"2020-03-31", "Return"])
    
    # Verify volatility spiked into 'extreme' tier (> 35%)
    # In March 2020, annualized volatility reached > 60%
    peak_loc = df.index.get_loc(df.loc["2020-03-01":"2020-03-31"].index[peak_idx])
    base_spike = baseline_volatility(df["Return"].iloc[:peak_loc + 1])
    assert base_spike > 35.0, f"Baseline should detect extreme volatility shock, got {base_spike}%"
    assert risk_level(base_spike) == "extreme"


def test_risk_alarm_evaluation_fidelity():
    """Evaluate confusion matrix and alarm metrics for elevated risk detection (vol >= 20%)."""
    df = data_mod.load_data("SPY")
    returns = df["Return"].to_numpy()
    n = len(returns)
    h = 5
    
    # Walk forward across 50 sample dates
    sample_indices = range(n - 250, n - h - 1, 5)
    
    tp, fp, tn, fn = 0, 0, 0, 0
    threshold = 20.0  # Moderate/High volatility threshold
    
    for i in sample_indices:
        pred = baseline_volatility(returns[:i + 1])
        actual = realized_vol_5day(returns, t=i, horizon=h)
        
        predicted_alarm = pred >= threshold
        actual_alarm = actual >= threshold
        
        if predicted_alarm and actual_alarm:
            tp += 1
        elif predicted_alarm and not actual_alarm:
            fp += 1
        elif not predicted_alarm and not actual_alarm:
            tn += 1
        else:
            fn += 1
            
    total_alarms = tp + fp
    total_actual_events = tp + fn
    
    # System should produce valid classification metrics
    assert (tp + tn + fp + fn) > 0
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    assert accuracy >= 0.65, f"Expected risk alarm accuracy >= 65%, got {accuracy:.2f}"
