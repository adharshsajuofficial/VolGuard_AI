"""Data ingestion: Yahoo Finance via yfinance, CSV fallback, log returns."""
import logging
import os
import time
from datetime import date, timedelta
from typing import Optional

import numpy as np
import pandas as pd

import config

log = logging.getLogger("volguard.data")


class DataNotFoundError(Exception):
    """No usable price data for the symbol (online or CSV)."""


_cache: dict = {}


def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """yfinance >=0.2.4x may return MultiIndex columns (field, ticker)."""
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = df.columns.get_level_values(0)
    return df


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    """Sort by date, pick price column, add `Price` and log `Return`, drop NaNs."""
    df = _flatten_columns(df)
    if df is None or df.empty:
        raise DataNotFoundError("empty frame")
    df = df.copy()
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df.index.name = "Date"
    df = df[~df.index.duplicated(keep="last")].sort_index()
    col = "Adj Close" if "Adj Close" in df.columns else "Close"
    if col not in df.columns:
        raise DataNotFoundError("no Close/Adj Close column")
    df["Price"] = pd.to_numeric(df[col], errors="coerce")
    df = df[df["Price"] > 0].dropna(subset=["Price"])
    df["Return"] = np.log(df["Price"] / df["Price"].shift(1))
    return df.dropna(subset=["Return"])


def fetch_online(symbol: str, start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
    """Download daily OHLCV from Yahoo. Raises on failure or empty result."""
    import yfinance as yf

    if start is None:
        start = (date.today() - timedelta(days=int(365.25 * config.FETCH_PERIOD_YEARS))).isoformat()
    df = yf.download(symbol, start=start, end=end, interval="1d",
                     auto_adjust=False, progress=False, threads=False)
    if df is None or df.empty:
        raise DataNotFoundError(f"yfinance returned no data for {symbol}")
    return df


def load_csv(symbol: str, path: Optional[str] = None) -> pd.DataFrame:
    """Read the fallback CSV. If it has a `Symbol` column, filter on it."""
    path = path or config.CSV_PATH
    if not os.path.exists(path):
        raise DataNotFoundError(f"fallback CSV missing: {path}")
    df = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
    if "Symbol" in df.columns:
        df = df[df["Symbol"].astype(str).str.upper() == symbol.upper()]
        if df.empty:
            raise DataNotFoundError(f"{symbol} not in fallback CSV")
    return df


def load_data(symbol: str, start: Optional[str] = None, end: Optional[str] = None,
              use_cache: bool = True) -> pd.DataFrame:
    """Return DataFrame indexed by date with `Price` and `Return` columns.

    Tries Yahoo first, falls back to CSV. Raises DataNotFoundError if both fail.
    Result has attribute-free `source` column ('yfinance' | 'csv').
    """
    key = (symbol, start, end)
    hit = _cache.get(key)
    if use_cache and hit and time.time() - hit[0] < config.CACHE_TTL_SECONDS:
        return hit[1]

    source = "yfinance"
    try:
        raw = fetch_online(symbol, start, end)
        df = prepare(raw)
    except Exception as exc:  # network, rate-limit, empty, schema change
        log.warning("online fetch failed for %s (%s); trying CSV", symbol, exc)
        source = "csv"
        try:
            df = prepare(load_csv(symbol))
        except DataNotFoundError:
            raise
        except Exception as exc2:
            raise DataNotFoundError(f"no data for {symbol}: {exc2}") from exc2
    if len(df) < config.BASELINE_WINDOW + config.HORIZON + 1:
        raise DataNotFoundError(f"not enough rows for {symbol}: {len(df)}")
    df["source"] = source
    _cache[key] = (time.time(), df)
    return df


def clear_cache() -> None:
    _cache.clear()
