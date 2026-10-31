"""VolGuard AI - Quantitative Model Evaluation & Benchmarking Runner
Person 3 Deliverable: Computes MAE, RMSE, QLIKE, Diebold-Mariano test,
stress regime benchmarks, and risk alarm classification metrics.
"""
import sys
import os
import json
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import config
import data as data_mod
from models import baseline_volatility, realized_vol_5day
from garch_engine import garch_forecast_from_returns, fit_garch


def qlike_loss(actual_vol: np.ndarray, pred_vol: np.ndarray) -> np.ndarray:
    """Element-wise Quasi-Likelihood (QLIKE) loss."""
    actual_var = np.maximum(1e-6, actual_vol ** 2)
    pred_var = np.maximum(1e-6, pred_vol ** 2)
    ratio = actual_var / pred_var
    return ratio - np.log(ratio) - 1.0


def diebold_mariano_test(loss_base: np.ndarray, loss_garch: np.ndarray) -> dict:
    """Diebold-Mariano test for predictive accuracy equality."""
    d = loss_base - loss_garch  # positive means GARCH has smaller loss (better)
    n = len(d)
    mean_d = float(np.mean(d))
    std_d = float(np.std(d, ddof=1))
    se_d = std_d / np.sqrt(n)
    dm_stat = mean_d / se_d if se_d > 0 else 0.0
    # One-sided p-value testing H1: GARCH loss < Baseline loss
    p_value = float(1.0 - stats.norm.cdf(dm_stat))
    return {
        "mean_loss_differential": round(mean_d, 4),
        "dm_statistic": round(dm_stat, 3),
        "p_value": round(p_value, 4),
        "statistically_significant": p_value < 0.05
    }


def evaluate_asset(symbol: str, max_points: int = 120, step: int = 5) -> dict:
    """Run chronological walk-forward out-of-sample evaluation."""
    print(f"\n[VolGuard Eval] Evaluating {symbol} (walk-forward, step={step})...")
    df = data_mod.load_data(symbol)
    returns = df["Return"].to_numpy(dtype=float)
    dates = df.index
    n = len(returns)
    h = config.HORIZON
    min_train = config.BT_MIN_TRAIN
    fit_window = config.BT_FIT_WINDOW

    last_i = n - 1 - h
    first_i = min_train - 1
    idx = list(range(last_i, first_i - 1, -step))[:max_points][::-1]

    records = []
    for i in idx:
        train = returns[max(0, i + 1 - fit_window): i + 1]
        try:
            g = garch_forecast_from_returns(train, horizon=h)
        except Exception:
            continue
        base = baseline_volatility(returns[: i + 1])
        act = realized_vol_5day(returns, t=i, horizon=h)
        records.append({
            "date": dates[i].date().isoformat(),
            "baseline": base,
            "garch": g,
            "actual": act
        })

    eval_df = pd.DataFrame(records)
    act = eval_df["actual"].to_numpy()
    b_pred = eval_df["baseline"].to_numpy()
    g_pred = eval_df["garch"].to_numpy()

    # Errors
    b_err = b_pred - act
    g_err = g_pred - act

    b_mae = float(np.mean(np.abs(b_err)))
    g_mae = float(np.mean(np.abs(g_err)))
    b_rmse = float(np.sqrt(np.mean(b_err ** 2)))
    g_rmse = float(np.sqrt(np.mean(g_err ** 2)))

    # QLIKE Loss
    b_qlike_arr = qlike_loss(act, b_pred)
    g_qlike_arr = qlike_loss(act, g_pred)
    b_qlike = float(np.mean(b_qlike_arr))
    g_qlike = float(np.mean(g_qlike_arr))

    # Diebold-Mariano test on absolute error & QLIKE
    dm_mae = diebold_mariano_test(np.abs(b_err), np.abs(g_err))
    dm_qlike = diebold_mariano_test(b_qlike_arr, g_qlike_arr)

    # Risk Alarm Confusion Matrix (High risk >= 25.0%)
    high_threshold = 25.0
    b_alarm = b_pred >= high_threshold
    g_alarm = g_pred >= high_threshold
    act_high = act >= high_threshold

    def alarm_stats(pred_flags, act_flags):
        tp = int(np.sum(pred_flags & act_flags))
        fp = int(np.sum(pred_flags & ~act_flags))
        tn = int(np.sum(~pred_flags & ~act_flags))
        fn = int(np.sum(~pred_flags & act_flags))
        total = tp + fp + tn + fn
        prec = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        acc = (tp + tn) / total if total > 0 else 1.0
        return {
            "TP": tp, "FP": fp, "TN": tn, "FN": fn,
            "accuracy": round(acc * 100, 1),
            "precision": round(prec * 100, 1),
            "recall": round(rec * 100, 1),
            "f1_score": round(f1, 3)
        }

    return {
        "symbol": symbol,
        "n_samples": len(eval_df),
        "start_date": records[0]["date"],
        "end_date": records[-1]["date"],
        "baseline_mae": round(b_mae, 3),
        "garch_mae": round(g_mae, 3),
        "mae_reduction_pct": round((b_mae - g_mae) / b_mae * 100, 2),
        "baseline_rmse": round(b_rmse, 3),
        "garch_rmse": round(g_rmse, 3),
        "rmse_reduction_pct": round((b_rmse - g_rmse) / b_rmse * 100, 2),
        "baseline_qlike": round(b_qlike, 4),
        "garch_qlike": round(g_qlike, 4),
        "qlike_reduction_pct": round((b_qlike - g_qlike) / b_qlike * 100, 2),
        "diebold_mariano_mae": dm_mae,
        "diebold_mariano_qlike": dm_qlike,
        "alarm_baseline": alarm_stats(b_alarm, act_high),
        "alarm_garch": alarm_stats(g_alarm, act_high)
    }


def evaluate_stress_regimes(symbol: str = "SPY") -> dict:
    """Benchmark model behavior across distinct market regimes."""
    df = data_mod.load_data(symbol)
    returns = df["Return"].to_numpy(dtype=float)
    dates = df.index
    h = config.HORIZON
    fit_window = config.BT_FIT_WINDOW

    regimes = {
        "COVID-19 Shock (Feb - Jun 2020)": ("2020-02-01", "2020-06-30"),
        "2022 Inflation & Rate Bear Market": ("2022-01-01", "2022-12-31"),
        "2017 Low-Volatility Regime": ("2017-01-01", "2017-12-31"),
        "2024-2026 Recent Market Dynamics": ("2024-01-01", "2026-10-30")
    }

    results = {}
    for name, (start_dt, end_dt) in regimes.items():
        mask = (dates >= pd.to_datetime(start_dt)) & (dates <= pd.to_datetime(end_dt))
        matching_indices = np.where(mask)[0]
        # Filter for indices with valid forward horizon
        valid_indices = [i for i in matching_indices if i >= config.BT_MIN_TRAIN and i <= len(returns) - 1 - h]

        if not valid_indices:
            continue

        b_errs, g_errs, actuals = [], [], []
        for i in valid_indices[::3]:  # sample every 3 days in regime
            train = returns[max(0, i + 1 - fit_window): i + 1]
            try:
                g = garch_forecast_from_returns(train, horizon=h)
            except Exception:
                continue
            base = baseline_volatility(returns[: i + 1])
            act = realized_vol_5day(returns, t=i, horizon=h)

            b_errs.append(abs(base - act))
            g_errs.append(abs(g - act))
            actuals.append(act)

        if b_errs:
            b_mae = float(np.mean(b_errs))
            g_mae = float(np.mean(g_errs))
            results[name] = {
                "period": f"{start_dt} to {end_dt}",
                "avg_realized_vol": round(float(np.mean(actuals)), 2),
                "max_realized_vol": round(float(np.max(actuals)), 2),
                "baseline_mae": round(b_mae, 2),
                "garch_mae": round(g_mae, 2),
                "garch_improvement_pct": round((b_mae - g_mae) / b_mae * 100, 1),
                "samples": len(b_errs)
            }

    return results


def analyze_volatility_clustering(symbol: str = "SPY") -> dict:
    """Analyze econometric properties: GARCH parameters and volatility clustering persistence."""
    df = data_mod.load_data(symbol)
    r = df["Return"].to_numpy()
    
    # Fit GARCH on full dataset
    res = fit_garch(r)
    p = res.params
    omega = float(p["omega"])
    alpha = float(p["alpha[1]"])
    beta = float(p["beta[1]"])
    persistence = alpha + beta
    
    # Half life of a volatility shock: t_half = ln(0.5) / ln(persistence)
    half_life_days = float(np.log(0.5) / np.log(persistence)) if persistence < 1.0 else 999.0

    # Return autocorrelation of squared returns (Ljung-Box / clustering indicator)
    r_sq = r ** 2
    lags = [1, 2, 5, 10, 20]
    acf_sq = {f"lag_{lag}": round(float(pd.Series(r_sq).autocorr(lag=lag)), 4) for lag in lags}

    return {
        "omega": round(omega, 6),
        "alpha": round(alpha, 4),
        "beta": round(beta, 4),
        "persistence": round(persistence, 4),
        "half_life_trading_days": round(half_life_days, 1),
        "squared_return_autocorrelations": acf_sq
    }


def main():
    print("=" * 70)
    print("  VolGuard AI - Quantitative Validation & Econometric Audit")
    print("  Lead: Person 3 (Testing, Validation & Pitch Lead)")
    print("=" * 70)

    # 1. Evaluate S&P 500 (SPY) and NIFTY 50 (^NSEI)
    eval_spy = evaluate_asset("SPY", max_points=100, step=5)
    eval_nifty = evaluate_asset("^NSEI", max_points=100, step=5)

    # 2. Stress testing across historical regimes
    stress = evaluate_stress_regimes("SPY")

    # 3. Econometric Volatility Clustering Parameters
    clustering = analyze_volatility_clustering("SPY")

    full_results = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "assets": {
            "SPY": eval_spy,
            "^NSEI": eval_nifty
        },
        "stress_regimes": stress,
        "volatility_clustering": clustering
    }

    # Save to docs/evaluation_results.json
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    os.makedirs(docs_dir, exist_ok=True)
    out_json = os.path.join(docs_dir, "evaluation_results.json")
    with open(out_json, "w") as f:
        json.dump(full_results, f, indent=2)

    print("\n" + "=" * 70)
    print("  BENCHMARK SUMMARY RESULTS")
    print("=" * 70)
    print(f"S&P 500 (SPY) 5-Day Out-of-Sample Results ({eval_spy['n_samples']} walk-forward windows):")
    print(f"  * Baseline MAE: {eval_spy['baseline_mae']}%  |  GARCH(1,1) MAE: {eval_spy['garch_mae']}% (-{eval_spy['mae_reduction_pct']}%)")
    print(f"  * Baseline RMSE: {eval_spy['baseline_rmse']}% |  GARCH(1,1) RMSE: {eval_spy['garch_rmse']}% (-{eval_spy['rmse_reduction_pct']}%)")
    print(f"  * Baseline QLIKE: {eval_spy['baseline_qlike']} |  GARCH(1,1) QLIKE: {eval_spy['garch_qlike']} (-{eval_spy['qlike_reduction_pct']}%)")
    print(f"  * Diebold-Mariano Stat: {eval_spy['diebold_mariano_mae']['dm_statistic']} (p-value: {eval_spy['diebold_mariano_mae']['p_value']}, Sig: {eval_spy['diebold_mariano_mae']['statistically_significant']})")
    
    print("\nStress Regimes (SPY):")
    for reg, data in stress.items():
        print(f"  * {reg}: Avg Vol: {data['avg_realized_vol']}%, Baseline MAE: {data['baseline_mae']}%, GARCH MAE: {data['garch_mae']}% (Improvement: {data['garch_improvement_pct']}%)")

    print("\nEconometric Clustering & Persistence:")
    print(f"  * Alpha (Shock Impact): {clustering['alpha']}")
    print(f"  * Beta (Persistence): {clustering['beta']}")
    print(f"  * Total Persistence (alpha + beta): {clustering['persistence']}")
    print(f"  * Half-life of Volatility Shock: {clustering['half_life_trading_days']} trading days")

    print(f"\n[OK] Results saved to {out_json}")


if __name__ == "__main__":
    main()
