"""FastAPI Endpoint Integration & Contract Verification Tests
Person 3 Deliverable: Ensures API contract compliance with Person 2's React dashboard.
"""
import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from api import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoints(client):
    """Verify health check endpoints return status OK."""
    res1 = client.get("/health")
    assert res1.status_code == 200
    assert res1.json() == {"status": "OK"}

    res2 = client.get("/api/health")
    assert res2.status_code == 200
    assert res2.json() == {"status": "OK"}


def test_forecast_contract(client):
    """Verify /api/forecast returns all required fields for the React dashboard."""
    response = client.get("/api/forecast?symbol=SPY&horizon=5")
    assert response.status_code == 200
    data = response.json()
    
    # Contract assertions
    assert data["symbol"] == "SPY"
    assert "as_of_date" in data and data["as_of_date"]
    assert "current_price" in data and data["current_price"] > 0
    assert data["forecast_horizon_days"] == 5
    assert data["volatility_unit"] == "annualized_percent"
    assert "baseline_forecast" in data and data["baseline_forecast"] > 0
    assert "garch_forecast" in data and data["garch_forecast"] > 0
    assert data["risk_level"] in ["low", "moderate", "high", "extreme"]
    assert 0 <= data["risk_score"] <= 100
    assert isinstance(data["summary"], str) and len(data["summary"]) > 10
    
    # Nested backtest preview assertions
    assert "backtest" in data
    assert "baseline_mae" in data["backtest"]
    assert "garch_mae" in data["backtest"]


def test_forecast_horizon_parameter(client):
    """Verify forecast responds to custom horizon parameter (e.g., 10 days)."""
    response = client.get("/api/forecast?symbol=SPY&horizon=10")
    assert response.status_code == 200
    data = response.json()
    assert data["forecast_horizon_days"] == 10


def test_history_contract(client):
    """Verify /api/history returns valid time-series for Recharts component."""
    response = client.get("/api/history?symbol=SPY&days=30")
    assert response.status_code == 200
    payload = response.json()
    
    assert payload["symbol"] == "SPY"
    assert "data" in payload or "history" in payload
    records = payload.get("data") or payload.get("history")
    assert len(records) <= 30
    assert len(records) > 0
    
    first = records[0]
    assert "date" in first
    assert "close" in first or "price" in first
    assert "rolling_vol_20d" in first or "vol20" in first


def test_backtest_contract(client):
    """Verify /api/backtest returns model metrics and walk-forward series."""
    response = client.get("/api/backtest?symbol=SPY&max_points=15&step=5")
    assert response.status_code == 200
    payload = response.json()
    
    assert payload["symbol"] == "SPY"
    assert payload["horizon_days"] == 5
    assert "metrics" in payload
    metrics = payload["metrics"]
    assert "baseline_mae" in metrics
    assert "garch_mae" in metrics
    assert "baseline_rmse" in metrics
    assert "garch_rmse" in metrics
    
    # Series verification
    series = payload.get("series") or payload.get("predictions")
    assert len(series) > 0
    item = series[0]
    assert "date" in item
    assert "actual" in item or "actual_realized" in item
    assert "baseline" in item or "baseline_pred" in item
    assert "garch" in item or "garch_pred" in item


def test_invalid_symbol_rejection(client):
    """Verify that illegal tickers return 422 HTTP status."""
    res = client.get("/api/forecast?symbol=$$$MALFORMED!!!")
    assert res.status_code == 422


def test_unknown_symbol_404(client):
    """Verify that unknown tickers return 404 HTTP status."""
    res = client.get("/api/forecast?symbol=NOTEXIST123")
    assert res.status_code == 404
