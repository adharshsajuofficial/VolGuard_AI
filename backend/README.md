# VolGuard AI Backend

FastAPI volatility intelligence service: 5-day annualized volatility forecast, 20-day realized-vol baseline vs GARCH(1,1), walk-forward backtest.

## Run
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# or: uvicorn api:app --port 8000 --reload
# Interactive OpenAPI Docs: http://localhost:8000/docs
```
Docker (from repo root): `docker build -t volguard . && docker run -p 8000:8000 volguard`

## Test
```bash
pytest          # offline tests; forces CSV fallback and tests GARCH + models + API
```

## Endpoints
| Route | Method | Notes |
|---|---|---|
| `/health` or `/api/health` | GET | `{"status":"OK"}` |
| `/api/forecast?symbol=SPY&horizon=5` | GET | Baseline + GARCH forecast (annualized %), `risk_level`, `risk_score`, `current_price` |
| `/api/history?symbol=SPY&days=60` | GET | Historical dates, `close`, `price`, `log_return`, `return`, `rolling_vol_20d`, `vol20` |
| `/api/backtest?symbol=SPY&step=5&max_points=150` | GET | MAE/RMSE for both models, zero-lookahead walk-forward test series |

Default symbol is `SPY`; use `?symbol=^NSEI` for NIFTY 50.
```bash
curl "http://localhost:8000/api/forecast?symbol=SPY"
```
```js
fetch("http://localhost:8000/api/forecast?symbol=%5ENSEI").then(r => r.json()).then(console.log);
```

## Econometric Methodology
- **Log Return**: $r_t = \ln(P_t / P_{t-1})$ on Adjusted Close.
- **20-Day Baseline**: $\sigma_{\text{baseline}} = \sqrt{\frac{252}{20} \sum_{i=0}^{19} r_{t-i}^2} \times 100\%$.
- **Target ($\sigma_{5d}$)**: $\sqrt{\frac{252}{5} \sum_{i=1}^5 r_{t+i}^2} \times 100\%$.
- **GARCH(1,1)**: Fit on percent returns with `arch`, summing $h=1..5$ conditional variances, annualized via $\sqrt{\frac{252}{5} \sum \sigma_h^2}$.
- **Chronological Backtest**: Expanding sample, GARCH refitted on capped rolling window (1000 observations), forecast step every $5$ days, strictly evaluating data up to day $t$ without lookahead bias.
- **Risk Tiers**: Low ($<15\%$), Moderate ($15-25\%$), High ($25-35\%$), Extreme ($>35\%$).

## Data Pipeline
Attempts live download via `yfinance`. On network timeout, rate-limiting, or offline status, seamlessly falls back to `data/prices.csv`. The response field `source` indicates whether data was served from `yfinance` or `csv`.
