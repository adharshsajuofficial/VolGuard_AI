"""Central configuration. Override via environment variables where noted."""
import os

DEFAULT_SYMBOL = "SPY"
ALT_SYMBOL = "^NSEI"  # NIFTY 50

TRADING_DAYS = 252
BASELINE_WINDOW = 20
HORIZON = 5
SUPPORTED_HORIZONS = (5, 10, 20)   # frontend selector values
MIN_HORIZON = 1
MAX_HORIZON = 60

DEFAULT_HISTORY_DAYS = 252 * 3
MAX_HISTORY_DAYS = 252 * 30
FETCH_PERIOD_YEARS = 12            # history pulled from Yahoo
FETCH_TIMEOUT_SECONDS = float(os.getenv("VOLGUARD_FETCH_TIMEOUT", "3.0"))
OFFLINE_MODE = os.getenv("VOLGUARD_OFFLINE", "0").lower() in ("1", "true", "yes")
MIN_OBSERVATIONS = 300             # min returns needed to fit GARCH sensibly

# Annualized-vol (%) cutoffs for risk classification (4-tier standard).
RISK_LOW_MAX = 15.0
RISK_MODERATE_MAX = 25.0
RISK_HIGH_MIN = 25.0
RISK_HIGH_MAX = 35.0

# Backtest defaults (GARCH refit is the slow part).
BT_MIN_TRAIN = 504                 # ~2 years before first forecast
BT_STEP = 5                        # forecast every 5 days -> non-overlapping targets
BT_MAX_POINTS = 150                # most recent N forecast points
BT_FIT_WINDOW = 1000               # rolling cap on GARCH training sample

CACHE_TTL_SECONDS = 15 * 60

# Startup cache pre-warming (set VOLGUARD_WARMUP=0 to disable, e.g. in tests).
WARMUP_ENABLED = os.getenv("VOLGUARD_WARMUP", "1").lower() not in ("0", "false", "no")
WARMUP_SYMBOLS = [DEFAULT_SYMBOL, ALT_SYMBOL]           # blocking: ready before first request
WARMUP_BACKGROUND_SYMBOLS = ["QQQ", "DIA", "AAPL", "TSLA"]  # filled in background thread
OFFLINE_DEMO_SYMBOLS = ["SPY", "^NSEI", "QQQ", "DIA", "AAPL", "TSLA"]

def _find_csv():
    env_path = os.getenv("VOLGUARD_CSV")
    if env_path and os.path.exists(env_path):
        return env_path
    data_csv = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "prices.csv")
    if os.path.exists(data_csv):
        return data_csv
    backend_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prices.csv")
    if os.path.exists(backend_csv):
        return backend_csv
    return data_csv

CSV_PATH = _find_csv()
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173").split(",")
    if o.strip()
]
