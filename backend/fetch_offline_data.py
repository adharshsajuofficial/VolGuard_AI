"""Build the offline price CSV used when Yahoo Finance is unreachable.

Usage (from backend/):
    python fetch_offline_data.py                    # real Yahoo data for all 6 demo tickers
    python fetch_offline_data.py --allow-synthetic  # real where possible, placeholder otherwise
    python fetch_offline_data.py --synthetic-missing  # no network: placeholders for missing tickers only

Output is written to BOTH backend/prices.csv and ../data/prices.csv.
Column `Origin` is `real` or `synthetic`. Synthetic rows are labelled placeholders
(factor model on top of SPY returns) and are surfaced as `is_synthetic=true` by the API.
Run the default mode once with internet to replace placeholders with real history.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATHS = [os.path.join(HERE, "prices.csv"),
             os.path.join(os.path.dirname(HERE), "data", "prices.csv")]
DEMO_SYMBOLS = ["SPY", "^NSEI", "QQQ", "DIA", "AAPL", "TSLA"]
COLUMNS = ["Date", "Symbol", "Open", "High", "Low", "Close", "Adj Close", "Volume", "Origin"]

# symbol: (start price, beta to SPY, idiosyncratic annual vol, daily alpha, base volume)
SYNTH = {
    "QQQ":  (87.6, 1.15, 0.10, 0.00005, 30_000_000),
    "DIA":  (163.0, 0.90, 0.05, -0.00012, 3_000_000),
    "AAPL": (19.8, 1.05, 0.22, 0.00012, 250_000_000),
    "TSLA": (10.0, 1.30, 0.45, 0.00030, 120_000_000),
}


def fetch_real(symbol: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.download(symbol, start="2014-01-01", interval="1d", auto_adjust=False,
                     progress=False, threads=False, timeout=15)
    if df is None or df.empty:
        raise RuntimeError(f"no data for {symbol}")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[["Open", "High", "Low", "Close", "Adj Close", "Volume"]].dropna()
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df.index.name = "Date"
    df = df[~df.index.duplicated(keep="last")].sort_index().reset_index()
    df.insert(1, "Symbol", symbol)
    df["Origin"] = "real"
    return df[COLUMNS]


def make_synthetic(symbol: str, spy: pd.DataFrame) -> pd.DataFrame:
    """Deterministic placeholder: beta * SPY log return + GARCH(1,1) idiosyncratic noise."""
    p0, beta, idio_vol, alpha, vol0 = SYNTH[symbol]
    rng = np.random.default_rng(sum(map(ord, symbol)) * 7919)  # deterministic
    spy = spy.sort_values("Date").reset_index(drop=True)
    px = spy["Adj Close"].to_numpy(float)
    r_spy = np.diff(np.log(px), prepend=np.nan)
    n = len(spy)
    long_var = (idio_vol ** 2) / 252
    a, b = 0.08, 0.90
    omega = long_var * (1 - a - b)
    var, eps = long_var, 0.0
    r = np.zeros(n)
    for i in range(1, n):
        var = omega + a * eps ** 2 + b * var
        eps = np.sqrt(var) * rng.standard_normal()
        r[i] = np.clip(alpha + beta * r_spy[i] + eps, -0.25, 0.25)
    close = p0 * np.exp(np.cumsum(r))
    prev = np.concatenate([[p0], close[:-1]])
    gap = rng.normal(0, 0.002, n)
    open_ = prev * np.exp(gap)
    span = np.abs(r) + np.abs(rng.normal(0, 0.004, n))
    high = np.maximum(open_, close) * np.exp(span / 2)
    low = np.minimum(open_, close) * np.exp(-span / 2)
    vol = (vol0 * np.exp(rng.normal(0, 0.25, n)) * (1 + 8 * np.abs(r))).astype(np.int64)
    out = pd.DataFrame({"Date": spy["Date"], "Symbol": symbol, "Open": open_, "High": high,
                        "Low": low, "Close": close, "Adj Close": close, "Volume": vol,
                        "Origin": "synthetic"})
    return out.iloc[1:].reset_index(drop=True)  # first return undefined


def load_existing() -> pd.DataFrame:
    for p in OUT_PATHS:
        if os.path.exists(p):
            df = pd.read_csv(p, parse_dates=["Date"])
            if "Origin" not in df.columns:
                df["Origin"] = "real"
            return df
    return pd.DataFrame(columns=COLUMNS)


def validate(df: pd.DataFrame) -> None:
    for sym, g in df.groupby("Symbol"):
        assert g["Date"].is_monotonic_increasing, f"{sym}: dates not sorted"
        assert not g["Date"].duplicated().any(), f"{sym}: duplicate dates"
        assert not g[["Open", "High", "Low", "Close", "Adj Close", "Volume"]].isna().any().any(), f"{sym}: NaN"
        assert (g["Adj Close"] > 0).all(), f"{sym}: non-positive price"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--symbols", nargs="*", default=DEMO_SYMBOLS)
    ap.add_argument("--allow-synthetic", action="store_true",
                    help="fall back to labelled placeholder data when download fails")
    ap.add_argument("--synthetic-missing", action="store_true",
                    help="skip network; add placeholders only for symbols absent from the CSV")
    args = ap.parse_args(argv)

    existing = load_existing()
    frames = {s: g for s, g in existing.groupby("Symbol")}
    for sym in args.symbols:
        sym = sym.upper()
        if args.synthetic_missing:
            if sym in frames or sym not in SYNTH:
                continue
            frames[sym] = make_synthetic(sym, frames["SPY"])
            print(f"{sym}: synthetic placeholder ({len(frames[sym])} rows)")
            continue
        try:
            frames[sym] = fetch_real(sym)
            print(f"{sym}: real data ({len(frames[sym])} rows)")
        except Exception as exc:
            if sym in frames:
                print(f"{sym}: download failed ({exc}); keeping existing rows")
            elif args.allow_synthetic and sym in SYNTH and "SPY" in frames:
                frames[sym] = make_synthetic(sym, frames["SPY"])
                print(f"{sym}: download failed ({exc}); synthetic placeholder")
            else:
                print(f"{sym}: download failed ({exc}); skipped", file=sys.stderr)
    order = {s: i for i, s in enumerate(DEMO_SYMBOLS)}
    out = pd.concat([frames[s] for s in sorted(frames, key=lambda s: order.get(s, 99))], ignore_index=True)
    out = out[COLUMNS]
    validate(out)
    for p in OUT_PATHS:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        out.to_csv(p, index=False, date_format="%Y-%m-%d")
        print("wrote", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
