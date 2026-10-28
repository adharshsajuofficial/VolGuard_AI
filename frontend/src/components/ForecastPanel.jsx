import React from 'react';
import { Gauge, Cpu, ArrowUpRight, ArrowDownRight, Layers, HelpCircle } from 'lucide-react';

export default function ForecastPanel({ forecastData, onOpenMethodology }) {
  if (!forecastData) return null;

  const baseline = forecastData.baseline_forecast;
  const garch = forecastData.garch_forecast;
  const spread = (baseline != null && garch != null) ? +(garch - baseline).toFixed(2) : null;
  const horizon = forecastData.forecast_horizon_days || 5;

  return (
    <div className="forecast-panel-grid">
      {/* 20-Day Baseline Model Card */}
      <div className="card metric-card">
        <div className="metric-header">
          <div className="metric-icon-wrap icon-baseline">
            <Gauge size={20} />
          </div>
          <div className="metric-title-group">
            <h3 className="metric-title">20-Day Baseline Model</h3>
            <span className="metric-subtitle">Historical Realized Rolling Volatility</span>
          </div>
        </div>

        <div className="metric-body">
          <div className="metric-primary-value">
            {baseline != null ? `${baseline.toFixed(1)}%` : 'N/A'}
          </div>
          <div className="metric-unit-badge">Annualized Volatility (σ Baseline)</div>
        </div>

        <div className="metric-footer">
          <span className="metric-footer-note">
            Target: <strong>{horizon}-Day Horizon</strong>
          </span>
          <button 
            type="button" 
            onClick={onOpenMethodology} 
            className="metric-help-btn"
            title="Formula: sqrt(252/20 * sum(r_t^2))"
          >
            <HelpCircle size={14} />
          </button>
        </div>
      </div>

      {/* GARCH(1,1) Econometric Model Card */}
      <div className="card metric-card">
        <div className="metric-header">
          <div className="metric-icon-wrap icon-garch">
            <Cpu size={20} />
          </div>
          <div className="metric-title-group">
            <h3 className="metric-title">GARCH(1,1) Model</h3>
            <span className="metric-subtitle">Conditional Variance &amp; Clustering</span>
          </div>
        </div>

        <div className="metric-body">
          <div className="metric-primary-value" style={{ color: '#38BDF8' }}>
            {garch != null ? `${garch.toFixed(1)}%` : 'Null (Fit Pending)'}
          </div>
          <div className="metric-unit-badge">Parametric Conditional Volatility</div>
        </div>

        <div className="metric-footer">
          <span className="metric-footer-note">
            {garch != null ? 'Fitted on Zero-Lookahead Returns' : 'Awaiting Arch Estimation'}
          </span>
          <button 
            type="button" 
            onClick={onOpenMethodology} 
            className="metric-help-btn"
            title="Formula: sigma_t^2 = omega + alpha*eps^2 + beta*sigma_{t-1}^2"
          >
            <HelpCircle size={14} />
          </button>
        </div>
      </div>

      {/* Model Spread & Divergence Card */}
      <div className="card metric-card">
        <div className="metric-header">
          <div className="metric-icon-wrap icon-spread">
            <Layers size={20} />
          </div>
          <div className="metric-title-group">
            <h3 className="metric-title">Model Divergence ($\Delta$)</h3>
            <span className="metric-subtitle">GARCH vs. 20-Day Baseline</span>
          </div>
        </div>

        <div className="metric-body">
          <div className="metric-primary-value">
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
              <span className="spread-badge-text">
                <ArrowUpRight size={13} /> Volatility expansion expected
              </span>
            ) : spread != null && spread < 0 ? (
              <span className="spread-badge-text">
                <ArrowDownRight size={13} /> Mean reversion / calming trend
              </span>
            ) : (
              'Neutral divergence'
            )}
          </div>
        </div>

        <div className="metric-footer">
          <span className="metric-footer-note">
            {spread != null ? `Δ = ${Math.abs(spread).toFixed(1)} pts spread` : 'Single model active'}
          </span>
        </div>
      </div>
    </div>
  );
}
