"""Helpers: symbol validation, risk classification, JSON-safe conversion."""
import math
import re

import config

_SYMBOL_RE = re.compile(r"^[A-Za-z0-9\^\.\-=]{1,15}$")


def normalize_symbol(symbol: str) -> str:
    """Upper-case and validate a ticker. Raises ValueError if malformed."""
    s = (symbol or "").strip().upper()
    if not _SYMBOL_RE.match(s):
        raise ValueError(f"Invalid symbol: {symbol!r}")
    return s


def risk_level(vol_pct: float) -> str:
    """Map annualized 5-day vol (%) to Low / Medium / High."""
    if vol_pct < config.RISK_LOW_MAX:
        return "Low"
    if vol_pct >= config.RISK_HIGH_MIN:
        return "High"
    return "Medium"


def clean_float(x, ndigits: int = 4):
    """float -> rounded float, NaN/inf -> None (valid JSON)."""
    if x is None:
        return None
    x = float(x)
    if math.isnan(x) or math.isinf(x):
        return None
    return round(x, ndigits)
