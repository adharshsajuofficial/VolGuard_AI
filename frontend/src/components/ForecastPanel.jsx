import React from 'react';
import { Gauge, Cpu, ArrowUpRight, ArrowDownRight, Layers, HelpCircle } from 'lucide-react';

export default function ForecastPanel({ forecastData, onOpenMethodology }) {
  if (!forecastData) return null;

  const baseline = forecastData.baseline_forecast;
  const garch = forecastData.garch_forecast;
  const spread = (baseline != null && garch != null) ? +(garch - baseline).toFixed(2) : null;
  const horizon = forecastData.forecast_horizon_days || 5;

  return (
    <section className="forecast-panel-grid" aria-label="Econometric Forecast Matrix">
      {/* 20-Day Baseline Model Card */}
      <div className="card metric-card">
        <div className="metric-header">
          <div className="metric-icon-wrap" aria-hidden="true">
            <Gauge size={16} />
          </div>
          <div className="metric-title-group">
            <h2 className="metric-title">20-Day Historical Benchmark</h2>
            <span className="metric-subtitle label-uppercase">NON-PARAMETRIC REALIZED VARIANCE</span>
          </div>
        </div>

        <div className="metric-body">
          <div className="metric-primary-value tabular-nums">
            {baseline != null ? `${baseline.toFixed(1)}%` : 'N/A'}
          </div>
          <div className="metric-unit-badge label-uppercase">ANNUALIZED SIGMA (σ BASELINE)</div>
        </div>

        <div className="metric-footer">
          <span className="metric-footer-note label-uppercase">
            TARGET HORIZON: <strong>{horizon} TRADING DAYS</strong>
          </span>
          <button 
            type="button" 
            onClick={onOpenMethodology} 
            className="metric-help-btn"
            title="Inspect Baseline Mathematical Formulation"
            aria-label="Inspect 20-day baseline formula"
          >
            <HelpCircle size={13} aria-hidden="true" />
          </button>
        </div>
      </div>

      {/* GARCH(1,1) Econometric Model Card - Signature Amber Focus */}
      <div className="card metric-card metric-card-amber-focus">
        <div className="metric-header">
          <div className="metric-icon-wrap metric-icon-amber" aria-hidden="true">
            <Cpu size={16} />
          </div>
          <div className="metric-title-group">
            <h2 className="metric-title">GARCH(1,1) Core Engine</h2>
            <span className="metric-subtitle label-uppercase">PARAMETRIC CONDITIONAL VARIANCE</span>
          </div>
        </div>

        <div className="metric-body">
          <div className="metric-primary-value metric-value-amber tabular-nums">
            {garch != null ? `${garch.toFixed(1)}%` : 'FIT PENDING'}
          </div>
          <div className="metric-unit-badge label-uppercase">VOLATILITY CLUSTERING VECTOR</div>
        </div>

        <div className="metric-footer">
          <span className="metric-footer-note label-uppercase">
            {garch != null ? 'FITTED WITH ZERO LOOKAHEAD' : 'AWAITING MLE CONVERGENCE'}
          </span>
          <button 
            type="button" 
            onClick={onOpenMethodology} 
            className="metric-help-btn"
            title="Inspect GARCH(1,1) Maximum Likelihood Equations"
            aria-label="Inspect GARCH formula"
          >
            <HelpCircle size={13} aria-hidden="true" />
          </button>
        </div>
      </div>

      {/* Model Spread & Divergence Card */}
      <div className="card metric-card">
        <div className="metric-header">
          <div className="metric-icon-wrap" aria-hidden="true">
            <Layers size={16} />
          </div>
          <div className="metric-title-group">
            <h2 className="metric-title">Model Divergence (Δ Spread)</h2>
            <span className="metric-subtitle label-uppercase">GARCH MINUS 20-DAY BASELINE</span>
          </div>
        </div>

        <div className="metric-body">
          <div className="metric-primary-value tabular-nums">
            {spread != null ? (
              <span className={`spread-val ${spread >= 0 ? 'spread-pos' : 'spread-neg'}`}>
                {spread >= 0 ? `+${spread.toFixed(2)}%` : `${spread.toFixed(2)}%`}
              </span>
            ) : (
              '--'
            )}
          </div>
          <div className="metric-unit-badge">
            {spread != null && spread > 0 ? (
              <span className="spread-badge-text text-expansion label-uppercase">
                <ArrowUpRight size={13} aria-hidden="true" /> VARIANCE EXPANSION ANTICIPATED
              </span>
            ) : spread != null && spread < 0 ? (
              <span className="spread-badge-text text-contraction label-uppercase">
                <ArrowDownRight size={13} aria-hidden="true" /> MEAN-REVERSION CONTRACTION
              </span>
            ) : (
              <span className="label-uppercase">PARITY SPREAD</span>
            )}
          </div>
        </div>

        <div className="metric-footer">
          <span className="metric-footer-note label-uppercase tabular-nums">
            {spread != null ? `Δ = ${Math.abs(spread).toFixed(2)} PTS DIFFERENTIAL` : 'SINGLE MODEL ACTIVE'}
          </span>
        </div>
      </div>
    </section>
  );
}
