"""Central configuration. Override via environment variables where noted."""
import os

DEFAULT_SYMBOL = "SPY"
ALT_SYMBOL = "^NSEI"  # NIFTY 50

TRADING_DAYS = 252
BASELINE_WINDOW = 20
HORIZON = 5

DEFAULT_HISTORY_DAYS = 252 * 3
MAX_HISTORY_DAYS = 252 * 30
FETCH_PERIOD_YEARS = 12            # history pulled from Yahoo
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

def _find_csv():
    env_path = os.getenv("VOLGUARD_CSV")
    if env_path and os.path.exists(env_path):
        return env_path
    backend_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prices.csv")
    if os.path.exists(backend_csv):
        return backend_csv
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "prices.csv")

CSV_PATH = _find_csv()
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173").split(",")
    if o.strip()
]
