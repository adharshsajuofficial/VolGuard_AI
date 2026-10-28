import React, { useEffect } from 'react';
import { X, BookOpen, AlertCircle, ShieldAlert, Cpu, Calculator } from 'lucide-react';

export default function MethodologyModal({ isOpen, onClose }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-header-title">
            <BookOpen size={22} className="text-cyan" />
            <h2>VolGuard AI — Mathematical Formulations &amp; Methodology</h2>
          </div>
          <button type="button" onClick={onClose} className="modal-close-btn" title="Close Modal">
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          {/* Section 1: Target Definition */}
          <div className="methodology-section">
            <div className="section-title-wrap">
              <Calculator size={18} className="text-emerald" />
              <h3>1. Exactly What the System Predicts</h3>
            </div>
            <p>
              To eliminate any ambiguity between engineering and quantitative modeling, all models in VolGuard AI adhere to a unified mathematical target:
            </p>
            <div className="formula-box">
              <div className="formula-title">Daily Log Returns (r_t):</div>
              <code>r_t = ln( P_t / P_{"{t-1}"} )</code>
              <p className="formula-desc">Where P_t is the adjusted daily closing price on trading day t.</p>
            </div>

            <div className="formula-box">
              <div className="formula-title">5-Day Forward Realized Volatility (σ 5-day):</div>
              <code>{"σ_5d = √[ Σ_{i=1..5} (r_{t+i})² ]"}</code>
              <p className="formula-desc">
                To express this in standard annualized percentage terms (compatible with VIX and annual volatility metrics), we multiply by √(252 / 5):
              </p>
              <code>{"σ_annualized = √[ (252 / 5) × Σ_{i=1..5} (r_{t+i})² ] × 100%"}</code>
            </div>
          </div>

          {/* Section 2: Model Specifications */}
          <div className="methodology-section">
            <div className="section-title-wrap">
              <Cpu size={18} className="text-cyan" />
              <h3>2. Model Architectures</h3>
            </div>

            <div className="model-explain-grid">
              <div className="model-explain-card">
                <h4>A. 20-Day Baseline Model</h4>
                <p>
                  Estimates forward volatility based strictly on the rolling sample variance of the prior 20 trading days:
                </p>
                <code>{"σ_baseline = √[ (252 / 20) × Σ_{k=0..19} (r_{t-k})² ] × 100%"}</code>
                <p className="text-sub">
                  Provides a robust, non-parametric anchor benchmark against which all predictive algorithms must be evaluated.
                </p>
              </div>

              <div className="model-explain-card">
                <h4>B. GARCH(1,1) Econometric Model</h4>
                <p>
                  Captures volatility clustering (large price moves cluster together) using conditional variance:
                </p>
                <code>{"σ_t² = ω + α · ε_{t-1}² + β · σ_{t-1}²"}</code>
                <p className="text-sub">
                  Fitted using Maximum Likelihood Estimation via the <code>arch</code> package with stationarity constraints (α + β &lt; 1).
                </p>
              </div>
            </div>
          </div>

          {/* Section 3: Risk Threshold Rules */}
          <div className="methodology-section">
            <div className="section-title-wrap">
              <ShieldAlert size={18} className="text-amber" />
              <h3>3. Volatility Risk Level Classification</h3>
            </div>
            <table className="methodology-table">
              <thead>
                <tr>
                  <th>Risk Tier</th>
                  <th>Annualized Volatility (σ)</th>
                  <th>Market Regime Characterization</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><span className="badge-chip chip-low">Low Risk</span></td>
                  <td>&lt; 15.0%</td>
                  <td>Calm conditions, normal asset liquidity, standard risk limits.</td>
                </tr>
                <tr>
                  <td><span className="badge-chip chip-mod">Moderate Risk</span></td>
                  <td>15.0% – 25.0%</td>
                  <td>Standard equity variance; typical earnings or macro cycle window.</td>
                </tr>
                <tr>
                  <td><span className="badge-chip chip-high">High Risk</span></td>
                  <td>25.0% – 35.0%</td>
                  <td>Elevated market turbulence; increased options implied vol, portfolio hedging advised.</td>
                </tr>
                <tr>
                  <td><span className="badge-chip chip-ext">Extreme Risk</span></td>
                  <td>&gt; 35.0%</td>
                  <td>Crisis or flash-crash regime; sharp drawdown risks, capital preservation triggers.</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Section 4: Strict Chronological Backtesting */}
          <div className="methodology-section">
            <div className="section-title-wrap">
              <AlertCircle size={18} className="text-rose" />
              <h3>4. Zero-Lookahead Backtest Rigor</h3>
            </div>
            <p>
              Time-series models frequently fail in production due to subtle lookahead leakage. VolGuard AI strictly enforces:
            </p>
            <ul className="methodology-list">
              <li><strong>No Data Shuffling:</strong> Splitting is chronological only (Train period → Test period).</li>
              <li><strong>Out-of-Sample Evaluation:</strong> The 5-day realized outcome is calculated strictly after prediction date t.</li>
              <li><strong>Metrics:</strong> Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE) computed in identical annualized percentage units.</li>
            </ul>
          </div>
        </div>

        <div className="modal-footer">
          <button type="button" onClick={onClose} className="btn-primary">
            Understood &amp; Close
          </button>
        </div>
      </div>
    </div>
  );
}
