import time

import pytest

import api
import config
import data as data_mod


def test_warm_fills_caches_and_makes_requests_fast(client):
    api.clear_caches()
    api._warm(["SPY"], (5,))
    assert any(k[0] == "SPY" and k[2] == 5 for k in api._fc_cache)
    assert any(k[0] == "SPY" and k[2] == 5 for k in api._bt_cache)
    t = time.perf_counter()
    assert client.get("/api/forecast", params={"symbol": "SPY"}).status_code == 200
    assert client.get("/api/backtest", params={"symbol": "SPY"}).status_code == 200
    assert time.perf_counter() - t < 0.5


def test_warm_skips_bad_symbol(client):
    api._warm(["ZZZZ"], (5,))   # must not raise


def test_lifespan_warmup_runs(monkeypatch):
    from fastapi.testclient import TestClient
    monkeypatch.setattr(config, "WARMUP_ENABLED", True)
    monkeypatch.setattr(config, "WARMUP_SYMBOLS", ["SPY"])
    monkeypatch.setattr(config, "WARMUP_BACKGROUND_SYMBOLS", [])
    monkeypatch.setattr(config, "SUPPORTED_HORIZONS", (5,))
    api.clear_caches()
    with TestClient(api.app) as c:
        assert api._warm_state["core"] is True
        assert c.get("/health").json()["cache_warm"]["core"] is True
        assert any(k[0] == "SPY" for k in api._fc_cache)


def test_openapi_tags_and_params(client):
    spec = client.get("/openapi.json").json()
    tag_names = {t["name"] for t in spec["tags"]}
    assert tag_names == {"Health", "Risk Intelligence", "Market Data", "Quantitative Backtesting"}
    paths = spec["paths"]
    assert paths["/health"]["get"]["tags"] == ["Health"] == paths["/api/health"]["get"]["tags"]
    assert paths["/api/forecast"]["get"]["tags"] == ["Risk Intelligence"]
    assert paths["/api/history"]["get"]["tags"] == ["Market Data"]
    assert paths["/api/backtest"]["get"]["tags"] == ["Quantitative Backtesting"]
    for p in ("/api/forecast", "/api/history", "/api/backtest"):
        for prm in paths[p]["get"]["parameters"]:
            assert prm.get("description"), (p, prm["name"])
        assert "404" in paths[p]["get"]["responses"]
    assert client.get("/docs").status_code == 200
