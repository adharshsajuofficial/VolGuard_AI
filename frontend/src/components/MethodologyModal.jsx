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
    <div 
      className="modal-overlay" 
      onClick={onClose} 
      role="dialog" 
      aria-modal="true" 
      aria-labelledby="modal-methodology-title"
    >
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-header-title">
            <BookOpen size={18} className="text-amber" aria-hidden="true" />
            <h2 id="modal-methodology-title">VolGuard AI — Sovereign Econometric Memorandum &amp; Formulations</h2>
          </div>
          <button 
            type="button" 
            onClick={onClose} 
            className="modal-close-btn" 
            title="Conclude Memorandum (Esc)"
            aria-label="Close Modal"
          >
            <X size={16} aria-hidden="true" />
          </button>
        </div>

        <div className="modal-body">
          {/* Section 1: Target Definition */}
          <section className="methodology-section">
            <div className="section-title-wrap">
              <Calculator size={15} className="text-amber" aria-hidden="true" />
              <h3>1. Unified Quantitative Target Definition</h3>
            </div>
            <p className="methodology-text">
              To eliminate divergence between macroeconomic quantitative theory and production software execution, all forecasting models target annualized realized variance across an explicit 5-day horizon window:
            </p>
            <div className="formula-box">
              <div className="formula-title">DAILY LOGARITHMIC RETURNS (r_t):</div>
              <code>r_t = ln( P_t / P_{"{t-1}"} )</code>
              <p className="formula-desc">Where P_t is the adjusted daily closing price on trading day <em>t</em>.</p>
            </div>

            <div className="formula-box">
              <div className="formula-title">5-DAY FORWARD REALIZED VOLATILITY (σ 5-day):</div>
              <code>{"σ_5d = √[ Σ_{i=1..5} (r_{t+i})² ]"}</code>
              <p className="formula-desc">
                Standardized into annual percentage units (compatible with VIX and sovereign implied volatility benchmarks):
              </p>
              <code>{"σ_annualized = √[ (252 / 5) × Σ_{i=1..5} (r_{t+i})² ] × 100%"}</code>
            </div>
          </section>

          {/* Section 2: Model Specifications */}
          <section className="methodology-section">
            <div className="section-title-wrap">
              <Cpu size={15} className="text-amber" aria-hidden="true" />
              <h3>2. Econometric Architecture Specifications</h3>
            </div>

            <div className="model-explain-grid">
              <div className="model-explain-card">
                <h4>A. 20-Day Baseline Benchmark</h4>
                <p>
                  Estimates forward volatility based strictly on empirical sample variance of the prior 20 trading days:
                </p>
                <code>{"σ_baseline = √[ (252 / 20) × Σ_{k=0..19} (r_{t-k})² ] × 100%"}</code>
                <p className="text-sub label-uppercase">
                  NON-PARAMETRIC ANCHOR BENCHMARK
                </p>
              </div>

              <div className="model-explain-card model-explain-amber-focus">
                <h4>B. GARCH(1,1) Core Engine</h4>
                <p>
                  Captures conditional variance and shock clustering where variance innovations persist into subsequent trading periods:
                </p>
                <code>{"σ_t² = ω + α · ε_{t-1}² + β · σ_{t-1}²"}</code>
                <p className="text-sub label-uppercase">
                  MAXIMUM LIKELIHOOD ESTIMATION WITH STATIONARITY CONSTRAINTS (α + β &lt; 1)
                </p>
              </div>
            </div>
          </section>

          {/* Section 3: Risk Threshold Rules */}
          <section className="methodology-section">
            <div className="section-title-wrap">
              <ShieldAlert size={15} className="text-amber" aria-hidden="true" />
              <h3>3. Sovereign Volatility Regime Classification</h3>
            </div>
            <div className="table-responsive">
              <table className="methodology-table">
                <thead>
                  <tr>
                    <th scope="col" className="label-uppercase">RISK CLASSIFICATION</th>
                    <th scope="col" className="label-uppercase">ANNUALIZED SIGMA (σ)</th>
                    <th scope="col" className="label-uppercase">MACRO REGIME CHARACTERIZATION &amp; HEDGING LIMITS</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>
                      <div className="badge-chip chip-low">
                        <span className="chip-square-block" style={{ backgroundColor: '#10B981' }} aria-hidden="true" />
                        <span>STABLE BASELINE</span>
                      </div>
                    </td>
                    <td className="tabular-nums">&lt; 15.0%</td>
                    <td>Compressed variance, resilient order liquidity, standard risk limits active.</td>
                  </tr>
                  <tr>
                    <td>
                      <div className="badge-chip chip-mod">
                        <span className="chip-square-block" style={{ backgroundColor: '#F59E0B' }} aria-hidden="true" />
                        <span>MODERATE VOLATILITY</span>
                      </div>
                    </td>
                    <td className="tabular-nums">15.0% – 25.0%</td>
                    <td>Standard macro variance; normal capital limits, monitor sector exposure.</td>
                  </tr>
                  <tr>
                    <td>
                      <div className="badge-chip chip-high">
                        <span className="chip-square-block" style={{ backgroundColor: '#F97316' }} aria-hidden="true" />
                        <span>ELEVATED TAIL</span>
                      </div>
                    </td>
                    <td className="tabular-nums">25.0% – 35.0%</td>
                    <td>Heightened variance; elevated options implied volatility, defensive hedging advised.</td>
                  </tr>
                  <tr>
                    <td>
                      <div className="badge-chip chip-ext">
                        <span className="chip-square-block" style={{ backgroundColor: '#EF4444' }} aria-hidden="true" />
                        <span>CRISIS TAIL / DISLOCATION</span>
                      </div>
                    </td>
                    <td className="tabular-nums">&gt; 35.0%</td>
                    <td>Severe market dislocation or liquidity cascade; capital preservation triggers enforced.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          {/* Section 4: Strict Chronological Backtesting */}
          <section className="methodology-section">
            <div className="section-title-wrap">
              <AlertCircle size={15} className="text-amber" aria-hidden="true" />
              <h3>4. Zero-Lookahead Walk-Forward Rigor</h3>
            </div>
            <p className="methodology-text">
              To eliminate insidious lookahead leakage in financial time-series forecasting:
            </p>
            <ul className="methodology-list">
              <li><strong>Strict Chronological Traversal:</strong> Data splitting proceeds purely forward through calendar time (Train → Test).</li>
              <li><strong>Zero Future Contamination:</strong> The 5-day realized outcome is calculated strictly after prediction date <em>t</em>.</li>
              <li><strong>Standardized Scoring:</strong> MAE and RMSE are evaluated in identical annualized percentage points.</li>
            </ul>
          </section>
        </div>

        <div className="modal-footer">
          <button type="button" onClick={onClose} className="btn-primary">
            CONCLUDE MEMORANDUM
          </button>
        </div>
      </div>
    </div>
  );
}
