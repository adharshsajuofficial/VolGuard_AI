# VolGuard AI: Financial Risk Intelligence & Short-Term Volatility Forecasting

**Project Abstract — Hackathon 72-Hour Sprint**  
**Target Domain:** Financial Market Volatility & Quantitative Risk Forecasting  
**Benchmark Assets:** S&P 500 (`SPY`), NIFTY 50 (`^NSEI`), Nasdaq 100 (`QQQ`)  

---

### System Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MARKET DATA INGESTION PIPELINE                        │
│          Yahoo Finance API (`yfinance`) + Offline Cached CSV Fallback       │
│               Historical Daily OHLCV Prices (2014 – 2026)                  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FEATURE TRANSFORMATION LAYER                        │
│               Daily Log Returns: r_t = ln(Price_t / Price_t-1)              │
│               Target: 5-Day Forward Annualized Realized Volatility          │
└──────────────────────┬───────────────────────────────┬──────────────────────┘
                       │                               │
                       ▼                               ▼
       ┌──────────────────────────────┐ ┌──────────────────────────────┐
       │   20-Day Baseline Model      │ │     GARCH(1,1) Engine        │
       │ Rolling Realized Volatility  │ │ Conditional Variance Equation│
       │ Trailing 20-Day Sample Mean  │ │ Volatility Clustering & Shock│
       └──────────────┬───────────────┘ └──────────────┬───────────────┘
                      │                                │
                      └────────────────┬───────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 CHRONOLOGICAL WALK-FORWARD AUDIT ENGINE                     │
│    Zero-Lookahead Validation • Out-of-Sample Backtesting (100 Windows)      │
│         Evaluation Metrics: MAE • RMSE • Asymmetric QLIKE Loss              │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   INTERACTIVE RISK INTELLIGENCE DASHBOARD                    │
│      React 19 + Vite • Recharts Visualization • Dynamic 4-Tier Badges       │
│         🟢 Low (<15%)  🟡 Moderate (15-25%)  🟠 High (25-35%)  🔴 Extreme   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 1. The Problem Chosen and Why

Think of investing like sailing a boat. Beginners focus only on which way the wind blows—whether stock prices go up or down. Experienced sailors care far more about the height of the waves. In finance, those waves are called **volatility**—how fast and violently prices swing. During market storms like the 2020 pandemic crash, sudden turbulence can wipe out everyday savings overnight. We built **VolGuard AI** as an early-warning weather radar for financial markets. By predicting market volatility 5 days in advance across major equity indices, VolGuard AI empowers investors to protect their portfolios before the storm arrives.

### 2. Understanding of the Core Technical Difficulty

Forecasting volatility presents three technical challenges:
1. **Volatility Is Invisible:** You cannot look up volatility on a price tag; you only observe closing prices. It must be calculated from how widely price swings spread over time.
2. **Volatility Clustering ("Bad News Comes in Bunches"):** Financial markets do not act like coin tosses. Calm days cluster together, but sudden shocks spark chains of turbulent swings. Linear models fail because tomorrow's risk depends on yesterday's shock size.
3. **The "Lookahead Bias" Trap:** A common pitfall in financial AI is data leakage—accidentally using tomorrow's data to predict yesterday's events. If a formula calculates today's risk using future prices, it looks brilliant in testing but crashes in real life. Maintaining strict chronological discipline is mandatory.

### 3. Concrete Proposed Approach: Techniques, Tools, and Datasets

VolGuard AI combines econometrics with full-stack engineering:
- **Datasets:** 12+ years of daily data for the U.S. S&P 500 (`SPY`), India's NIFTY 50 (`^NSEI`), and Nasdaq 100 (`QQQ`), fetched via `yfinance` with an offline CSV cache.
- **Mathematical Formulation:** Closing prices convert into daily log returns $r_t = \ln(P_t / P_{t-1})$. Our prediction target is 5-day forward realized volatility ($\sigma_{5d}$), annualized ($\times \sqrt{252/5} \times 100\%$) to match market standards like the VIX.
- **Modeling Techniques:** We deploy two engines:
  1. *20-Day Baseline:* A rolling realized volatility model reflecting recent market variance.
  2. *GARCH(1,1) Engine:* An econometric model (using Python's `arch` library) capturing volatility clustering and risk memory.
- **Tech Stack:** A **Python FastAPI** backend handles modeling and REST endpoints, while a **React 19 + Vite** frontend uses **Recharts** to render interactive risk gauges and forecast cones.

### 4. Hitting the Minimum Viable Bar (MVP)

Our 72-hour MVP achieved four essential deliverables:
1. Automated ingestion of daily price histories with zero missing dates or corrupted values.
2. Verified mathematical pipelines computing returns and forward volatility without lookahead leakage.
3. An out-of-sample benchmark comparing GARCH(1,1) against the baseline, producing verifiable MAE and RMSE metrics.
4. An interactive web dashboard allowing users to select an index, view price and volatility trends, and read an instant color-coded risk badge (Low, Moderate, High, Extreme).

### 5. Stretch Goals Attempted

Beyond the MVP, our team achieved four stretch goals:
- **Cross-Market Generalization:** Validated models across mature U.S. equities (`SPY`, `QQQ`) and emerging Indian markets (`^NSEI`).
- **Crisis Stress-Testing:** Tested model survival during black-swan events, notably the 2020 COVID crash.
- **Asymmetric Risk Loss (QLIKE):** Implemented QLIKE loss to heavily penalize models that dangerously underestimate market risk.
- **Offline High-Fidelity Simulation:** Built an offline demo mode ensuring smooth presentations even if external APIs hit rate limits.

### 6. Novelty and Differentiation

Most projects treat volatility like standard regression with Mean Squared Error (MSE). But in finance, **underestimating risk is disastrous** (causing bankruptcy), whereas slight overestimation is merely cautious. VolGuard AI stands out through:
- **Asymmetric QLIKE Loss:** Following Patton (2011), we penalize risk under-predictions far more severely than over-predictions.
- **Model Divergence Indicator ($\Delta$):** We track the spread between GARCH(1,1) and the baseline. When GARCH spikes above trailing averages, it warns of an imminent volatility breakout before simple moving averages notice.
- **Zero-Lookahead Discipline:** Every training slice strictly follows calendar time, preventing artificial data snooping.

### 7. Evaluation Plan

We evaluated VolGuard AI over 100 non-overlapping walk-forward out-of-sample test windows (2024–2026):
- **Predictive Accuracy:** On the S&P 500, GARCH achieved an MAE of 5.71% (3.19% better than baseline) and an RMSE of 9.02% (7.22% better).
- **Asymmetric Risk Reduction:** GARCH reduced QLIKE loss by **22.21%** ($0.4390$ vs. $0.5643$).
- **Statistical Significance:** The **Diebold-Mariano test** confirmed this outperformance is statistically significant ($p = 0.0394 < 0.05$).
- **Crisis Resilience:** During the peak 2020 COVID crash, GARCH reduced forecast error from 20.25% down to 13.14%—a **35.1% error reduction**.
- **Risk Tier Accuracy:** Achieved **94% to 95% classification accuracy** for directional risk alerts.

### 8. Team Fit and Operational Risks

Our three-member team divided work by strengths:
- **Person 1 (Backend & Modeling):** Built data ingestion, return transforms, GARCH modeling with `arch`, and FastAPI endpoints.
- **Person 2 (Frontend & UI/UX):** Built the React 19 dashboard, Recharts visualizations, and interactive risk badges.
- **Person 3 (QA & Testing):** Conducted chronological walk-forward audits, Diebold-Mariano testing, stress-testing, and documentation.

**Risks & Mitigations:**
- *API Rate Limits:* Mitigated through offline CSV caching and client-side simulation fallbacks.
- *Solver Non-Convergence:* Mitigated by automatic fallback to rolling realized variance when GARCH optimization fails.
- *Lookahead Leakage:* Prevented via automated unit tests verifying strict chronological boundary separation.
