# VolGuard AI — 2-Minute Live Demo Checklist & Judge Defense Runbook

**Audience:** Hackathon Judges & Evaluation Panel  
**Primary Demonstrators:** Person 2 (Frontend) & Person 3 (Validation Lead)  
**Total Target Run Time:** 2 Minutes 00 Seconds (strict hackathon cue)

---

## 📋 Pre-Demo Verification Checklist (T-minus 5 Minutes)

- [ ] **Backend Server Running:**
  ```bash
  cd backend
  uvicorn main:app --port 8000 --reload
  ```
  Verify `http://localhost:8000/health` returns `{"status":"OK"}`.
- [ ] **Frontend Dev Server Running:**
  ```bash
  cd frontend
  npm run dev
  ```
  Verify `http://localhost:5173` renders with zero console errors.
- [ ] **Offline Fallback Ready:** If internet or Wi-Fi cuts out at the venue, the frontend automatically switches to the built-in econometric simulation engine with high-fidelity calculations.
- [ ] **Test Report Available:** Keep `docs/model_evaluation_report.md` and `docs/zero_lookahead_audit.md` open in browser tabs to instantly answer technical questions.
- [ ] **Test Suite Verified:** `pytest tests -v` shows 30/30 passing.

---

## ⏱️ Second-by-Second 2-Minute Live Demo Script

### [00:00 - 00:20] Hook & Problem Statement
- **Action:** Open `http://localhost:5173`. Point to the header status badge showing `Connected (Live API)`.
- **Speech (Person 3):**
  > "Judges, equity market risk changes in hours, not weeks. Most hedge funds and traders rely on backward-looking 20-day rolling averages that lag real-world crashes. VolGuard AI is an early-warning volatility intelligence platform forecasting 5-day forward annualized volatility with certified zero lookahead bias."

### [00:20 - 00:45] Asset Selection & 4-Tier Risk Warning
- **Action:**
  1. Click **`SPY`**, then click **`TSLA`** to show contrast.
  2. Watch the **Risk Badge** dynamically shift color from Green/Amber (Moderate Risk ~18%) on SPY to pulsating Red (**Extreme Risk ~48%**) on TSLA.
  3. Highlight the **Risk Index Score** (0 to 100) and actionable narrative guidance.
- **Speech (Person 2):**
  > "Here on our dashboard, risk managers instantly see the projected volatility regime. For the S&P 500, we're at moderate risk. But switching to high-beta assets like Tesla, VolGuard's risk shield immediately flashes Extreme Risk, recommending portfolio hedging before market close."

### [00:45 - 01:15] Forecast Cones & Model Divergence
- **Action:**
  1. Scroll to the **Volatility & Price Chart**.
  2. Hover over the forward **5-Day Forecast Cone** (dotted lines extending into the future).
  3. Toggle timeframe filters: **1M**, **3M**, **All**.
  4. Point to the **Model Divergence metric ($\Delta$)** in the Forecast Panel.
- **Speech (Person 2):**
  > "Notice our dual-model architecture: we display both the 20-day rolling baseline and the GARCH(1,1) conditional variance model. When GARCH exceeds the baseline, it indicates active volatility expansion—shocks are compounding. The forecast cone gives quantitative desks upper and lower bounds for their options and Value-at-Risk calculations."

### [01:15 - 01:45] Chronological Backtest & Outperformance Proof
- **Action:**
  1. Scroll down to the **Model Comparison & Walk-Forward Backtest** view.
  2. Point out the three lines: Actual Ground Truth ($\sigma_{5d}$), Baseline, and GARCH.
  3. Toggle the **Residual Absolute Error Bar Chart**.
  4. Highlight the **Benchmark Summary Card**: MAE, RMSE, and QLIKE loss reduction.
- **Speech (Person 3):**
  > "Every metric on this screen is backed by strict chronological out-of-sample backtesting. On our held-out test windows, GARCH achieves a 22.2% reduction in asymmetric QLIKE loss with p < 0.05. And during market crashes like the March 2020 COVID shock, GARCH reduces prediction error by 35.1% because it immediately adapts to shock clustering."

### [01:45 - 02:00] Mathematical Rigor & Closing
- **Action:**
  1. Click the **"Formulas & Math"** button in the header to open the `MethodologyModal`.
  2. Briefly show the clean LaTeX equations ($r_t$, $\sigma_{5d}$, GARCH variance equation).
- **Speech (Person 3):**
  > "Every equation is fully documented in-app, backed by 30 automated validation tests. VolGuard AI gives institutions actionable foresight instead of retrospective regret. Thank you!"

---

## 🎯 Anticipated Judge Questions & Bulletproof Defenses

### Q1: "How do you guarantee there is zero lookahead bias in your backtest?"
> **Defense:**  
> "We enforced strict temporal causality at both the data and algorithmic layers:
> 1. At every walk-forward step $t$, the models only receive historical returns up to index $t$ (`returns[:t+1]`).
> 2. The target $\sigma_{5d}$ is computed strictly on forward returns (`returns[t+1 : t+6]`).
> 3. We wrote a dedicated test (`tests/test_zero_lookahead.py`) where we perturbed future returns by injecting a simulated -26% market crash into days $t+1..t+5$. The historical prediction at day $t$ remained identical to 12 decimal places of machine precision, proving zero future leakage."

### Q2: "Why use GARCH(1,1) instead of an LSTM or Deep Learning model?"
> **Defense:**  
> "Three reasons:
> 1. **Overfitting & Noise:** Daily financial returns have an extremely low signal-to-noise ratio. Complex deep learning models frequently overfit to historical regimes and fail out-of-sample.
> 2. **Econometric Interpretability:** Financial regulators and risk committees require transparent, defensible models. GARCH's parameters $\alpha$ (shock magnitude) and $\beta$ (persistence) have direct physical interpretations in terms of volatility memory and half-life.
> 3. **Latency & Microseconds:** Fitting GARCH takes milliseconds, allowing instantaneous real-time recalculation across hundreds of portfolio tickers without expensive GPU clusters."

### Q3: "What is QLIKE loss and why does it matter more than MAE or RMSE?"
> **Defense:**  
> "In quantitative finance, volatility errors are inherently asymmetric. If you forecast 15% volatility and actual volatility is 25%, your portfolio is under-capitalized, triggering margin calls or insolvency. If you forecast 25% and actual is 15%, you're slightly conservative. Patton (2011) proved that QLIKE is the optimal robust loss function because it heavily penalizes underestimating volatility. Our model achieved a statistically significant 22.2% QLIKE reduction ($p = 0.0394$)."

### Q4: "What happens if Yahoo Finance is rate-limited or the network fails?"
> **Defense:**  
> "We engineered a 3-tier fault tolerance pipeline:
> 1. First, live fetch from Yahoo Finance via `yfinance`.
> 2. If rate-limited or offline, the FastAPI backend automatically falls back to clean, curated historical CSV data (`prices.csv`).
> 3. If the backend itself is unavailable or booting, our React frontend features an autonomous client-side econometric simulation engine that calculates realistic drift, shocks, and GARCH variances with zero lag."
