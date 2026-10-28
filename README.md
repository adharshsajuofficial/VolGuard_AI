# VolGuard AI 🛡️📈
### Financial Risk Intelligence & Short-Term Volatility Forecasting Platform

> **Hackathon 72-Hour Sprint — Problem Statement: Market Volatility & Risk Forecasting**  
> VolGuard AI predicts short-term market volatility (5-day annualized realized volatility) for major equity indices (such as S&P 500 / `SPY` and NIFTY 50 / `^NSEI`) using an econometric multi-model approach, chronological walk-forward validation, and an interactive risk intelligence dashboard.

---

## 🏛️ System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                 React Dashboard (Person 2)                  │
│       Vite • Recharts • Financial Risk Badge • Dark UI       │
└──────────────────────────────▲──────────────────────────────┘
                               │ JSON via REST (CORS)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Backend (Person 1)                  │
│        Data Ingestion • Return Transforms • Modeling        │
└───────────────▲─────────────────────────────▲───────────────┘
                │                             │
    ┌───────────┴──────────┐       ┌──────────┴──────────┐
    │ 20-Day Baseline Model│       │  GARCH(1,1) Engine  │
    │ Rolling Realized Vol │       │Conditional Variance │
    └──────────────────────┘       └─────────────────────┘
                │                             │
    ┌───────────┴─────────────────────────────┴──────────┐
    │     Held-Out Chronological Backtest (Person 3)      │
    │      Strict Zero-Lookahead Evaluation (MAE/RMSE)    │
    └─────────────────────────────────────────────────────┘
```

---

## 📐 Mathematical Formulation

All three team roles adhere to a unified mathematical target to prevent inconsistencies across codebases:

### 1. Daily Log Returns
$$r_t = \ln\left(\frac{P_t}{P_{t-1}}\right)$$
Where $P_t$ is the adjusted daily closing price on trading day $t$.

### 2. 5-Day Forward Annualized Realized Volatility ($\sigma_{5d}$)
$$\sigma_{5d} = \sqrt{\sum_{i=1}^{5} r_{t+i}^2}$$
To express this in standard annualized percentage units (comparable to the VIX), it is scaled by $\sqrt{252 / 5}$:
$$\sigma_{\text{annualized}} = \sqrt{\frac{252}{5} \sum_{i=1}^{5} r_{t+i}^2} \times 100\%$$

### 3. Baseline Model (20-Day Rolling Realized Volatility)
$$\sigma_{\text{baseline}} = \sqrt{\frac{252}{20} \sum_{k=0}^{19} r_{t-k}^2} \times 100\%$$

### 4. GARCH(1,1) Econometric Model
Captures volatility clustering (periods of turbulence following large shocks):
$$\sigma_t^2 = \omega + \alpha \cdot \epsilon_{t-1}^2 + \beta \cdot \sigma_{t-1}^2 \quad \text{subject to } \alpha + \beta < 1$$

---

## 🚦 Volatility Risk Tiers

| Risk Level | Annualized Volatility ($\sigma$) | Market Regime Characterization |
| :--- | :--- | :--- |
| 🟢 **Low Risk** | $< 15.0\%$ | Stable pricing, normal liquidity, standard risk limits. |
| 🟡 **Moderate Risk** | $15.0\% - 25.0\%$ | Typical market variance, routine portfolio monitoring. |
| 🟠 **High Risk** | $25.0\% - 35.0\%$ | Elevated volatility, volatility clustering, hedging advised. |
| 🔴 **Extreme Risk** | $> 35.0\%$ | Crisis / shock regime, capital preservation mode triggered. |

---

## 👥 Team Work Division & Deliverables

See [`workdivision.md`](./workdivision.md) for the complete 72-hour execution roadmap.

| Member | Domain | Key Responsibilities | Deliverables |
| :--- | :--- | :--- | :--- |
| **Person 1** | Backend & Modeling | Python, FastAPI, Pandas, `yfinance`, Baseline & GARCH(1,1) | `backend/main.py`, working API endpoints |
| **Person 2** | **Frontend (Active Scope)** | React + Vite, Recharts, Interactive Dashboard, API client | `frontend/`, production-grade risk dashboard |
| **Person 3** | Validation & Pitch | Chronological train/test splitting, MAE/RMSE benchmark, pitch deck | Out-of-sample audit, slides, demo video |

---

## ✨ Person 2 Frontend Features (Implemented)

The `frontend/` directory contains a full production-ready React 19 application built with Vite:

1. **Asset & Parameter Selector (`AssetSelector.jsx`)**:
   - Quick selector pills for broad market indices (`SPY`, `^NSEI` NIFTY 50, `QQQ`, `DIA`) and equities (`AAPL`, `TSLA`).
   - Custom ticker input field with instant search.
   - Forecast horizon selector: 5-Day (standard $\sigma_{5d}$), 10-Day, and 20-Day windows.
2. **Dynamic Risk Warning Badge (`RiskBadge.jsx`)**:
   - Live color-coded risk badge with pulsating indicator.
   - Volatility index score meter (0 to 100).
   - Actionable narrative advice for quantitative risk managers.
3. **Forecast Metric Cards (`ForecastPanel.jsx`)**:
   - 20-Day Baseline forecast display.
   - GARCH(1,1) parametric forecast display.
   - Model divergence ($\Delta$) metric showing volatility expansion vs mean reversion.
4. **Interactive Volatility & Price Charts (`VolatilityChart.jsx`)**:
   - Recharts multi-line and gradient area charts for 20-day rolling historical volatility.
   - Projected 5-day forward volatility cone.
   - Toggle between Volatility (%) and Price ($) trajectories.
   - Timeframe filters: 1M, 3M, 6M, and All.
   - Visual risk tier reference lines (15%, 25%, 35%).
5. **Model Comparison & Backtest Chart (`ModelComparisonChart.jsx`)**:
   - Walk-forward chronological comparison: Baseline Predictions vs GARCH Predictions vs Actual Ground Truth ($\sigma_{5d}$).
   - Toggleable residual absolute error bar chart ($|y - \hat{y}|$).
6. **Quantitative Backtest Benchmark Summary (`BacktestSummary.jsx`)**:
   - MAE and RMSE metrics for Baseline and GARCH models.
   - Percentage error reduction indicator.
   - Volatility clustering takeaways and zero-lookahead verification notes.
7. **Educational Methodology Modal (`MethodologyModal.jsx`)**:
   - Complete mathematical formulary accessible at any time via the "Formulas & Math" header button.
8. **Fault-Tolerant API Client with Offline Simulation (`api.js`)**:
   - Connects to `http://localhost:8000` automatically.
   - Seamlessly falls back to an econometric simulation engine if the backend is offline, allowing flawless demonstrations without server lag.
   - Loading skeletons (`LoadingState.jsx`), error boundaries (`ErrorState.jsx`), and empty states (`EmptyState.jsx`).

---

## 🚀 Getting Started

### 1. Run the Frontend (Person 2)
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

To verify production build:
```bash
npm run build
npm run preview
```

### 2. Run the Backend (Person 1)
```bash
cd backend
python -m venv .venv

# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
API Documentation will be live at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 📡 API Contract Specification

### `GET /api/forecast?symbol={symbol}&horizon={horizon_days}`
```json
{
  "symbol": "SPY",
  "as_of_date": "2026-10-28",
  "current_price": 586.50,
  "forecast_horizon_days": 5,
  "volatility_unit": "annualized_percent",
  "baseline_forecast": 16.8,
  "garch_forecast": 18.2,
  "risk_level": "moderate",
  "risk_score": 48,
  "summary": "Moderate volatility expected over the next 5 trading days.",
  "backtest": {
    "test_period": "2024-01-01 to Present",
    "samples_count": 690,
    "baseline_mae": 2.82,
    "garch_mae": 2.45,
    "baseline_rmse": 3.71,
    "garch_rmse": 3.22,
    "outperformance_percent": 13.1
  }
}
```

### `GET /api/history?symbol={symbol}&days={days}`
```json
{
  "symbol": "SPY",
  "data": [
    {
      "date": "2026-10-20",
      "close": 582.10,
      "log_return": 0.0032,
      "rolling_vol_20d": 16.8
    }
  ]
}
```

### `GET /api/backtest?symbol={symbol}`
```json
{
  "symbol": "SPY",
  "horizon_days": 5,
  "metrics": {
    "baseline_mae": 2.82,
    "garch_mae": 2.45,
    "baseline_rmse": 3.71,
    "garch_rmse": 3.22,
    "outperformance_percent": 13.1
  },
  "series": [
    {
      "date": "2026-09-01",
      "actual_realized": 19.2,
      "baseline_pred": 17.5,
      "garch_pred": 18.8
    }
  ]
}
```

---

## ✅ 5-Item Hackathon Readiness Verification
- [x] **Live & Interactive:** Displays forecasts generated by econometric models with real-time feedback.
- [x] **Zero Lookahead Bias:** Chronological out-of-sample testing using unseen future trading days.
- [x] **Reproducible Metrics:** All errors and volatilities calculated in consistent units (annualized %).
- [x] **Unbreakable Demo:** High-fidelity offline simulation fallback ensures demo succeeds in any environment.
- [x] **Clear Explanation:** In-app mathematical formulation modal allows every team member to defend the models.
