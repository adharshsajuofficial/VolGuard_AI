import pytest

import api

SYMS = ["SPY", "^NSEI", "QQQ", "DIA", "AAPL", "TSLA"]


def test_health_both_routes(client):
    for p in ("/health", "/api/health"):
        j = client.get(p).json()
        assert j["status"] == "OK" and "cache_warm" in j


@pytest.mark.parametrize("sym", SYMS)
def test_forecast_all_demo_tickers(client, sym):
    r = client.get("/api/forecast", params={"symbol": sym})
    assert r.status_code == 200, r.text
    j = r.json()
    for k in ("symbol", "date", "as_of_date", "current_price", "last_price", "last_return", "forecast_5d_vol",
              "baseline_forecast", "garch_forecast", "forecast_horizon_days", "volatility_unit",
              "risk_level", "risk_score", "summary", "source", "backtest"):
        assert k in j, k
    assert j["symbol"] == sym and j["forecast_horizon_days"] == 5
    assert j["risk_level"] in ("low", "moderate", "high", "extreme")
    assert 0 <= j["risk_score"] <= 100


@pytest.mark.parametrize("h", [5, 10, 20])
def test_forecast_horizon_consistent(client, h):
    j = client.get("/api/forecast", params={"symbol": "SPY", "horizon": h}).json()
    assert j["forecast_horizon_days"] == h
    assert j["summary"].startswith(f"{h}-day")
    assert j["forecast_5d_vol"] == j["forecast_vol"]
    assert j["garch_forecast"] == pytest.approx(j["forecast_5d_vol"]["garch"], abs=0.01)
    assert j["baseline_forecast"] == pytest.approx(j["forecast_5d_vol"]["baseline"], abs=0.01)
    # backtest preview is the real one for the same horizon, not a hardcoded stub
    bt = client.get("/api/backtest", params={"symbol": "SPY", "horizon": h}).json()
    assert j["backtest"]["samples_count"] == bt["n_points"]
    assert j["backtest"]["garch_mae"] == pytest.approx(bt["MAE_garch"], abs=0.01)
    assert bt["horizon_days"] == h


def test_horizons_differ_for_garch(client):
    g = {h: client.get("/api/forecast", params={"symbol": "SPY", "horizon": h}).json()["garch_forecast"]
         for h in (5, 10, 20)}
    assert len(set(g.values())) == 3


@pytest.mark.parametrize("params", [{"horizon": 0}, {"horizon": 61}, {"horizon": "x"}, {"symbol": "$$$"}])
def test_forecast_validation(client, params):
    assert client.get("/api/forecast", params=params).status_code == 422


def test_forecast_unknown_symbol_404(client):
    assert client.get("/api/forecast", params={"symbol": "ZZZZ"}).status_code == 404


def test_history(client):
    j = client.get("/api/history", params={"symbol": "QQQ", "days": 30}).json()
    assert len(j["history"]) == 30 == len(j["data"])
    assert {"date", "price", "return", "vol20"} <= set(j["history"][0])
    assert {"date", "close", "log_return", "rolling_vol_20d"} <= set(j["data"][0])
    assert j["history"][-1]["vol20"] is not None
    assert client.get("/api/history", params={"days": 0}).status_code == 422


def test_backtest_contract(client):
    j = client.get("/api/backtest", params={"symbol": "SPY"}).json()
    for k in ("symbol", "horizon_days", "n_points", "MAE_baseline", "MAE_garch", "RMSE_baseline", "RMSE_garch",
              "better_model", "baseline", "garch", "metrics", "predictions", "series"):
        assert k in j, k
    assert j["n_points"] == 150 and j["step"] == 5
    assert {"MAE", "RMSE", "bias", "QLIKE"} <= set(j["baseline"])
    assert {"baseline", "baseline_pred", "garch", "garch_pred", "actual", "actual_realized", "date"} <= set(j["series"][0])
    assert "series" not in client.get("/api/backtest", params={"include_series": "false"}).json()


def test_backtest_default_step_scales_with_horizon(client):
    assert client.get("/api/backtest", params={"horizon": 20, "max_points": 20}).json()["step"] == 20


def test_cors_header(client):
    r = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"
