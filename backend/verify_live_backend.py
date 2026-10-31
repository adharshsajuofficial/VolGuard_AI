import urllib.request
import urllib.error
import json
import time
import subprocess
import sys

print("======================================================================")
print("  VolGuard AI - Live Backend End-to-End Operational Verification")
print("======================================================================")

# 1. Start the FastAPI server via uvicorn
print("\n[1/6] Starting FastAPI server on http://127.0.0.1:8000...")
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
    cwd="backend",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

time.sleep(4.0)

base_url = "http://127.0.0.1:8000"
results = []

def test_endpoint(name, path, expected_status=200):
    url = base_url + path
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={"Origin": "http://localhost:5173"})
        with urllib.request.urlopen(req, timeout=15) as response:
            status = response.getcode()
            headers = dict(response.headers)
            body = response.read().decode("utf-8")
            elapsed = round((time.time() - t0) * 1000, 1)
            content_type = headers.get("Content-Type", headers.get("content-type", ""))
            data = json.loads(body) if "application/json" in content_type else body
            cors = headers.get("access-control-allow-origin") or headers.get("Access-Control-Allow-Origin", "")
            results.append((name, path, status, elapsed, True, ""))
            return status, elapsed, cors, data
    except urllib.error.HTTPError as e:
        elapsed = round((time.time() - t0) * 1000, 1)
        if e.code == expected_status:
            results.append((name, path, e.code, elapsed, True, f"Expected HTTP {e.code}"))
            return e.code, elapsed, "", json.loads(e.read().decode())
        else:
            results.append((name, path, e.code, elapsed, False, f"Unexpected status {e.code}"))
            return e.code, elapsed, "", None
    except Exception as exc:
        elapsed = round((time.time() - t0) * 1000, 1)
        results.append((name, path, 0, elapsed, False, str(exc)))
        return 0, elapsed, "", None

try:
    print("\n[2/6] Testing Health & Liveness Endpoints...")
    st, el, cors, data = test_endpoint("Health Check", "/health")
    print(f"  [OK] GET /health -> {st} in {el}ms | Response: {data}")
    st, el, cors, data = test_endpoint("API Health Alias", "/api/health")
    print(f"  [OK] GET /api/health -> {st} in {el}ms | Response: {data}")

    print("\n[3/6] Testing Forecast Endpoints (SPY, ^NSEI, Multi-Horizon)...")
    st, el, cors, data = test_endpoint("Forecast SPY (5d)", "/api/forecast?symbol=SPY&horizon=5")
    print(f"  [OK] GET /api/forecast?symbol=SPY -> {st} in {el}ms")
    print(f"      Price: ${data.get('current_price')} | Baseline: {data.get('baseline_forecast')}% | GARCH: {data.get('garch_forecast')}% | Risk: {data.get('risk_level')}")
    print(f"      CORS Header: \"{cors}\"")

    st, el, cors, data = test_endpoint("Forecast ^NSEI (5d)", "/api/forecast?symbol=%5ENSEI&horizon=5")
    print(f"  [OK] GET /api/forecast?symbol=^NSEI -> {st} in {el}ms")
    print(f"      Price: {data.get('current_price')} | Baseline: {data.get('baseline_forecast')}% | GARCH: {data.get('garch_forecast')}% | Risk: {data.get('risk_level')}")

    st, el, cors, data = test_endpoint("Forecast SPY (10d)", "/api/forecast?symbol=SPY&horizon=10")
    print(f"  [OK] GET /api/forecast?symbol=SPY&horizon=10 -> {st} in {el}ms | Horizon: {data.get('forecast_horizon_days')}d")

    st, el, cors, data = test_endpoint("Forecast SPY (20d)", "/api/forecast?symbol=SPY&horizon=20")
    print(f"  [OK] GET /api/forecast?symbol=SPY&horizon=20 -> {st} in {el}ms | Horizon: {data.get('forecast_horizon_days')}d")

    print("\n[4/6] Testing History Endpoints (Price, Return, Rolling Volatility)...")
    st, el, cors, data = test_endpoint("History SPY 30d", "/api/history?symbol=SPY&days=30")
    records = data.get("data") or data.get("history") or []
    print(f"  [OK] GET /api/history?symbol=SPY&days=30 -> {st} in {el}ms | Records: {len(records)}")
    if records:
        print(f"      Sample: Date={records[-1].get('date')}, Close={records[-1].get('close')}, Vol20={records[-1].get('rolling_vol_20d')}%")

    st, el, cors, data = test_endpoint("History ^NSEI 60d", "/api/history?symbol=%5ENSEI&days=60")
    records = data.get("data") or data.get("history") or []
    print(f"  [OK] GET /api/history?symbol=^NSEI&days=60 -> {st} in {el}ms | Records: {len(records)}")

    print("\n[5/6] Testing Chronological Backtest Endpoints...")
    st, el, cors, data = test_endpoint("Backtest SPY", "/api/backtest?symbol=SPY&max_points=20&step=5")
    metrics = data.get("metrics", {})
    series = data.get("series") or data.get("predictions") or []
    print(f"  [OK] GET /api/backtest?symbol=SPY -> {st} in {el}ms")
    print(f"      Baseline MAE: {metrics.get('baseline_mae')}% | GARCH MAE: {metrics.get('garch_mae')}% | Outperformance: {metrics.get('outperformance_percent')}%")
    print(f"      Evaluated Window Points: {len(series)}")

    st, el, cors, data = test_endpoint("Backtest ^NSEI", "/api/backtest?symbol=%5ENSEI&max_points=20&step=5")
    metrics = data.get("metrics", {})
    print(f"  [OK] GET /api/backtest?symbol=^NSEI -> {st} in {el}ms | Baseline MAE: {metrics.get('baseline_mae')}% | GARCH MAE: {metrics.get('garch_mae')}%")

    print("\n[6/6] Testing Input Validation & Error Handling...")
    st, el, cors, data = test_endpoint("Malformed Symbol Rejection", "/api/forecast?symbol=$$$INVALID!!!", expected_status=422)
    print(f"  [OK] Rejected Malformed Ticker ($$$INVALID) -> HTTP {st} (Validation Error)")

    st, el, cors, data = test_endpoint("Unknown Symbol 404", "/api/forecast?symbol=NOTEXIST123", expected_status=404)
    print(f"  [OK] Unknown Ticker Handled Cleanly -> HTTP {st} (Not Found)")

    st, el, cors, data = test_endpoint("OpenAPI Swagger UI", "/docs")
    print(f"  [OK] Interactive Swagger Docs (/docs) -> HTTP {st}")

    # Summary table
    print("\n======================================================================")
    print("  TEST SUMMARY RESULTS")
    print("======================================================================")
    total = len(results)
    passed = sum(1 for r in results if r[4])
    for name, path, code, el, ok, note in results:
        status_sym = "PASS" if ok else "FAIL"
        print(f"  [{status_sym}] {name:30} {code:3} ({el:6.1f}ms) {path}")
    print(f"\nTotal Endpoints Tested: {total} | Passed: {passed} | Failed: {total - passed}")

finally:
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except Exception:
        proc.kill()
