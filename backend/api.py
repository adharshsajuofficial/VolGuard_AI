"""VolGuard AI FastAPI app.  Run: uvicorn api:app --port 8000"""
import asyncio
import logging
import threading
import time
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import config
import data as data_mod
from backtest import run_backtest
from garch_engine import GarchError, garch_forecast_from_returns
from models import baseline_volatility, rolling_vol
from utils import clean_float, normalize_symbol, risk_level

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("volguard.api")

# ---------- caches ----------
_bt_cache: dict = {}          # (sym, last_date, horizon, step, max_points) -> backtest dict
_fc_cache: dict = {}          # (sym, last_date, horizon) -> ForecastResponse
_locks: dict = {}
_locks_guard = threading.Lock()
_warm_state = {"core": False, "background": False, "seconds": None}
_MAX_CACHE_ENTRIES = 256


def _key_lock(key) -> threading.Lock:
    with _locks_guard:
        return _locks.setdefault(key, threading.Lock())


def _cache_put(cache: dict, key, value) -> None:
    if len(cache) >= _MAX_CACHE_ENTRIES:
        cache.clear()
    cache[key] = value


def clear_caches() -> None:
    _bt_cache.clear()
    _fc_cache.clear()
    _warm_state.update(core=False, background=False, seconds=None)


# ---------- app + docs metadata ----------
DESCRIPTION = """
Volatility intelligence API: **20-day realized-volatility baseline vs GARCH(1,1)** forecasts of
annualized volatility over a 5, 10 or 20 trading-day horizon, with a zero-lookahead walk-forward backtest.

**Math (all volatilities are annualized percent)**

* log return: `r_t = ln(P_t / P_{t-1})`
* baseline: `sqrt(252/20 * sum(r_{t-i}^2, i=0..19)) * 100` held flat over the horizon
* realized target: `sqrt(252/h * sum(r_{t+i}^2, i=1..h)) * 100` (strictly future days)
* GARCH(1,1): fitted on percent returns with `arch`; sums the h conditional variances, annualized by `252/h`

**Data**: live Yahoo Finance first, bundled `prices.csv` fallback. The `source` field says which one served the
request. `is_synthetic=true` flags placeholder offline rows (see `fetch_offline_data.py`).

**Demo tickers available offline**: `SPY`, `^NSEI`, `QQQ`, `DIA`, `AAPL`, `TSLA`.
"""

TAGS = [
    {"name": "Health", "description": "Liveness and cache-warm status."},
    {"name": "Risk Intelligence", "description": "Forward volatility forecast, risk tier and score."},
    {"name": "Market Data", "description": "Price, log-return and rolling 20-day volatility history."},
    {"name": "Quantitative Backtesting",
     "description": "Chronological walk-forward evaluation of baseline vs GARCH (MAE, RMSE, QLIKE)."},
]

SYMBOL_DESC = "Ticker symbol. Offline-ready: SPY, ^NSEI, QQQ, DIA, AAPL, TSLA. Case-insensitive."
HORIZON_DESC = f"Forecast horizon in trading days. UI values: 5 (default), 10, 20. Accepted range {config.MIN_HORIZON}-{config.MAX_HORIZON}."
_ERR = {
    404: {"description": "No data for the symbol (live fetch and CSV fallback both failed)."},
    422: {"description": "Invalid symbol or out-of-range parameter."},
}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Pre-warm caches so the first dashboard click is instant."""
    if config.WARMUP_ENABLED:
        t0 = time.time()
        await asyncio.to_thread(_warm, config.WARMUP_SYMBOLS, (config.HORIZON,))
        _warm_state.update(core=True, seconds=round(time.time() - t0, 2))
        log.info("cache warm (core) in %.2fs: %s", time.time() - t0, config.WARMUP_SYMBOLS)
        threading.Thread(target=_warm_background, name="volguard-warmup", daemon=True).start()
    yield


app = FastAPI(title="VolGuard AI Backend", version="1.1.0", description=DESCRIPTION,
              openapi_tags=TAGS, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- schemas ----------
class VolPair(BaseModel):
    baseline: float = Field(..., description="20-day realized vol held flat (annualized %).")
    garch: Optional[float] = Field(None, description="GARCH(1,1) forecast (annualized %); null if the fit failed.")


class ForecastResponse(BaseModel):
    symbol: str
    date: str = Field(..., description="Last trading day in the data (YYYY-MM-DD).")
    as_of_date: Optional[str] = None
    current_price: Optional[float] = None
    last_price: float
    last_return: float = Field(..., description="Last daily log return (decimal).")
    forecast_5d_vol: VolPair = Field(..., description="Legacy key name; holds the forecast for the REQUESTED horizon.")
    forecast_vol: Optional[VolPair] = Field(None, description="Same as forecast_5d_vol, horizon-neutral name.")
    baseline_forecast: float
    garch_forecast: Optional[float] = None
    forecast_horizon_days: int = Field(5, description="Requested horizon in trading days.")
    baseline_window_days: int = Field(config.BASELINE_WINDOW, description="Look-back window of the baseline.")
    volatility_unit: str = "annualized_percent"
    risk_level: str = Field(..., description="low (<15) | moderate (15-25) | high (25-35) | extreme (>35)")
    risk_score: int = Field(..., description="0-100 score derived from the headline forecast.")
    summary: str
    source: str = Field(..., description="yfinance | csv")
    is_synthetic: bool = Field(False, description="True when served from placeholder (non-market) CSV rows.")
    backtest: Optional[dict] = Field(None, description="Walk-forward summary for the SAME horizon.")

    model_config = {"json_schema_extra": {"example": {
        "symbol": "SPY", "date": "2026-10-30", "as_of_date": "2026-10-30", "current_price": 755.72,
        "last_price": 755.72, "last_return": -0.017, "forecast_5d_vol": {"baseline": 12.3, "garch": 14.8},
        "forecast_vol": {"baseline": 12.3, "garch": 14.8}, "baseline_forecast": 12.3, "garch_forecast": 14.8,
        "forecast_horizon_days": 5, "baseline_window_days": 20, "volatility_unit": "annualized_percent",
        "risk_level": "low", "risk_score": 33,
        "summary": "5-day annualized volatility forecast is 14.8% (low Risk).", "source": "csv",
        "is_synthetic": False,
        "backtest": {"test_period": "Walk-Forward Held-out", "samples_count": 150, "baseline_mae": 4.1,
                     "garch_mae": 3.7, "baseline_rmse": 5.6, "garch_rmse": 5.0, "outperformance_percent": 9.8}}}}


class HistoryResponse(BaseModel):
    symbol: str
    source: str
    is_synthetic: bool = False
    history: List[dict] = Field(..., description="Rows: date, price, return, vol20.")
    data: Optional[List[dict]] = Field(None, description="Same rows, alt keys: close, log_return, rolling_vol_20d.")


class ModelMetrics(BaseModel):
    MAE: float
    RMSE: float
    bias: float
    QLIKE: Optional[float] = Field(None, description="QLIKE loss on variances; lower is better.")


class BacktestResponse(BaseModel):
    symbol: str
    horizon_days: int = 5
    n_points: int
    skipped: int
    step: int
    MAE_baseline: float
    MAE_garch: float
    RMSE_baseline: float
    RMSE_garch: float
    better_model: str
    baseline: ModelMetrics
    garch: ModelMetrics
    metrics: Optional[dict] = None
    is_synthetic: bool = False
    predictions: Optional[List[dict]] = None
    series: Optional[List[dict]] = None


# ---------- helpers ----------
def _load(symbol: str):
    try:
        sym = normalize_symbol(symbol)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    try:
        return sym, data_mod.load_data(sym)
    except data_mod.DataNotFoundError as exc:
        log.error("no data for %s: %s", sym, exc)
        raise HTTPException(status_code=404, detail=f"No data found for symbol {sym}")


def _get_backtest(sym: str, df, horizon: int, step: Optional[int] = None,
                  max_points: int = config.BT_MAX_POINTS) -> dict:
    """Cached walk-forward backtest. Default step = max(5, horizon) keeps targets non-overlapping."""
    step = step or max(config.BT_STEP, horizon)
    key = (sym, df.index[-1], horizon, step, max_points)
    res = _bt_cache.get(key)
    if res is not None:
        return res
    with _key_lock(("bt",) + key):
        res = _bt_cache.get(key)
        if res is None:
            t0 = time.time()
            res = run_backtest(df["Return"], step=step, max_points=max_points, horizon=horizon)
            log.info("backtest %s h=%d: %d pts in %.1fs", sym, horizon, res["n_points"], time.time() - t0)
            _cache_put(_bt_cache, key, res)
    return res


def _backtest_preview(res: dict) -> dict:
    b_mae, g_mae = res["baseline"]["MAE"], res["garch"]["MAE"]
    return {
        "test_period": "Walk-Forward Held-out",
        "samples_count": res["n_points"],
        "baseline_mae": round(b_mae, 2),
        "garch_mae": round(g_mae, 2),
        "baseline_rmse": round(res["baseline"]["RMSE"], 2),
        "garch_rmse": round(res["garch"]["RMSE"], 2),
        "outperformance_percent": round(max(0.0, (b_mae - g_mae) / max(1e-5, b_mae) * 100), 1),
    }


def _compute_forecast(sym: str, df, horizon: int) -> ForecastResponse:
    key = (sym, df.index[-1], horizon)
    hit = _fc_cache.get(key)
    if hit is not None:
        return hit
    with _key_lock(("fc",) + key):
        hit = _fc_cache.get(key)
        if hit is not None:
            return hit
        r = df["Return"]
        base = baseline_volatility(r.to_numpy())
        try:
            garch = garch_forecast_from_returns(r.to_numpy()[-config.BT_FIT_WINDOW:], horizon=horizon)
        except GarchError as exc:
            log.warning("GARCH failed for %s: %s", sym, exc)
            garch = None
        headline = garch if garch is not None else base
        last_p = round(float(df["Price"].iloc[-1]), 4)
        last_d = df.index[-1].date().isoformat()
        r_level = risk_level(headline)
        r_score = min(100, max(5, int(headline * 2.2)))
        synthetic = bool(df["synthetic"].iloc[-1]) if "synthetic" in df.columns else False

        summary = f"{horizon}-day annualized volatility forecast is {round(headline, 1)}% ({r_level} Risk). "
        summary += ("GARCH captures volatility clustering; baseline is 20-day realized vol held flat."
                    if garch is not None else "GARCH unavailable; showing the 20-day realized baseline.")
        if synthetic:
            summary += " Offline placeholder data, not market prices."

        try:
            preview = _backtest_preview(_get_backtest(sym, df, horizon))
        except ValueError as exc:  # too little history for a backtest
            log.warning("no backtest preview for %s: %s", sym, exc)
            preview = None

        pair = VolPair(baseline=round(base, 4), garch=clean_float(garch))
        out = ForecastResponse(
            symbol=sym, date=last_d, as_of_date=last_d, current_price=last_p, last_price=last_p,
            last_return=round(float(r.iloc[-1]), 6),
            forecast_5d_vol=pair, forecast_vol=pair,
            baseline_forecast=round(base, 2),
            garch_forecast=round(garch, 2) if garch is not None else round(base, 2),
            forecast_horizon_days=horizon, baseline_window_days=config.BASELINE_WINDOW,
            volatility_unit="annualized_percent", risk_level=r_level, risk_score=r_score,
            summary=summary, source=df["source"].iloc[-1], is_synthetic=synthetic, backtest=preview,
        )
        _cache_put(_fc_cache, key, out)
        return out


def _warm(symbols, horizons) -> None:
    for sym in symbols:
        try:
            df = data_mod.load_data(sym)
        except Exception as exc:
            log.warning("warm-up skipped %s: %s", sym, exc)
            continue
        for h in horizons:
            try:
                _compute_forecast(sym, df, h)
            except Exception as exc:
                log.warning("warm-up failed %s h=%d: %s", sym, h, exc)


def _warm_background() -> None:
    t0 = time.time()
    _warm(config.WARMUP_SYMBOLS, [h for h in config.SUPPORTED_HORIZONS if h != config.HORIZON])
    _warm(config.WARMUP_BACKGROUND_SYMBOLS, config.SUPPORTED_HORIZONS)
    _warm_state["background"] = True
    log.info("cache warm (background) in %.1fs", time.time() - t0)


# ---------- endpoints ----------
@app.get("/health", tags=["Health"], summary="Liveness check")
@app.get("/api/health", tags=["Health"], summary="Liveness check (API-prefixed alias)")
def health():
    """Returns `{"status": "OK"}`."""
    return {"status": "OK"}


@app.get("/api/forecast", response_model=ForecastResponse, tags=["Risk Intelligence"],
         summary="Volatility forecast: baseline vs GARCH(1,1)", responses=_ERR)
def forecast(
    symbol: str = Query(config.DEFAULT_SYMBOL, description=SYMBOL_DESC, examples=["SPY"]),
    horizon: int = Query(5, ge=config.MIN_HORIZON, le=config.MAX_HORIZON, description=HORIZON_DESC,
                         examples=[5]),
):
    """Annualized volatility forecast for the next `horizon` trading days, with risk tier,
    0-100 risk score and a walk-forward backtest summary computed for the same horizon."""
    sym, df = _load(symbol)
    return _compute_forecast(sym, df, horizon)


@app.get("/api/history", response_model=HistoryResponse, tags=["Market Data"],
         summary="Price, log-return and rolling 20-day volatility history", responses=_ERR)
def history(symbol: str = Query(config.DEFAULT_SYMBOL, description=SYMBOL_DESC, examples=["SPY"]),
            days: int = Query(config.DEFAULT_HISTORY_DAYS, ge=1, le=config.MAX_HISTORY_DAYS,
                              description="Most recent N trading days to return (default 756 = ~3y).",
                              examples=[60])):
    """Last `days` trading days: price, daily log return and rolling 20-day annualized vol."""
    sym, df = _load(symbol)
    vol = rolling_vol(df["Return"])
    tail = df.tail(days)
    history_list = [{
        "date": ts.date().isoformat(),
        "price": round(float(row.Price), 4),
        "return": clean_float(row.Return, 6),
        "vol20": clean_float(vol.loc[ts]),
    } for ts, row in tail.iterrows()]
    data_list = [{
        "date": ts.date().isoformat(),
        "close": round(float(row.Price), 4),
        "log_return": clean_float(row.Return, 6),
        "rolling_vol_20d": clean_float(vol.loc[ts]),
    } for ts, row in tail.iterrows()]
    return HistoryResponse(symbol=sym, source=df["source"].iloc[-1],
                           is_synthetic=bool(df["synthetic"].iloc[-1]) if "synthetic" in df.columns else False,
                           history=history_list, data=data_list)


@app.get("/api/backtest", response_model=BacktestResponse, response_model_exclude_none=True,
         tags=["Quantitative Backtesting"], summary="Walk-forward backtest: baseline vs GARCH(1,1)",
         responses=_ERR)
def backtest(symbol: str = Query(config.DEFAULT_SYMBOL, description=SYMBOL_DESC, examples=["SPY"]),
             horizon: int = Query(5, ge=config.MIN_HORIZON, le=config.MAX_HORIZON,
                                  description=HORIZON_DESC, examples=[5]),
             include_series: bool = Query(True, description="Include per-date predictions."),
             step: Optional[int] = Query(None, ge=1, le=60,
                                         description="Days between forecasts. Default max(5, horizon) "
                                                     "so realized targets never overlap."),
             max_points: int = Query(config.BT_MAX_POINTS, ge=10, le=600,
                                     description="Most recent N forecast points to evaluate.")):
    """Chronological expanding-window evaluation. At each date only data up to that date is used;
    the target is the realized vol of the following `horizon` days. Results are cached."""
    sym, df = _load(symbol)
    try:
        res = _get_backtest(sym, df, horizon, step, max_points)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    series_formatted = [{
        "date": p["date"],
        "baseline": p["baseline"],
        "baseline_pred": round(p["baseline"], 2),
        "garch": p["garch"],
        "garch_pred": round(p["garch"], 2),
        "actual": p["actual"],
        "actual_realized": round(p["actual"], 2),
    } for p in res.get("predictions", [])]

    preview = _backtest_preview(res)
    metrics_obj = {k: v for k, v in preview.items() if k != "test_period"}
    metrics_obj["baseline_qlike"] = round(res["baseline"]["QLIKE"], 4)
    metrics_obj["garch_qlike"] = round(res["garch"]["QLIKE"], 4)

    return BacktestResponse(
        symbol=sym,
        horizon_days=horizon,
        n_points=res["n_points"],
        skipped=res["skipped"],
        step=res["step"],
        MAE_baseline=res["baseline"]["MAE"],
        MAE_garch=res["garch"]["MAE"],
        RMSE_baseline=res["baseline"]["RMSE"],
        RMSE_garch=res["garch"]["RMSE"],
        better_model=res["better_model"],
        baseline=res["baseline"],
        garch=res["garch"],
        metrics=metrics_obj,
        is_synthetic=bool(df["synthetic"].iloc[-1]) if "synthetic" in df.columns else False,
        predictions=series_formatted if include_series else None,
        series=series_formatted if include_series else None,
    )
