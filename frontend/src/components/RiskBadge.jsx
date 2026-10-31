import React from 'react';
import { AlertTriangle, ShieldCheck, AlertOctagon, Flame } from 'lucide-react';

const RISK_CONFIG = {
  low: {
    label: 'STABLE BASELINE REGIME',
    color: '#10B981',
    borderColor: '#10B981',
    icon: ShieldCheck,
    description: 'Sub-15% annualized volatility. Macro conditions exhibit compressed variance, robust liquidity depth, and orderly capital formation.'
  },
  moderate: {
    label: 'MODERATE VOLATILITY REGIME',
    color: '#F59E0B',
    borderColor: '#F59E0B',
    icon: AlertTriangle,
    description: '15% – 25% annualized volatility. Standard equity variance envelope. Normal portfolio risk limits and hedging parameters active.'
  },
  high: {
    label: 'ELEVATED TAIL REGIME',
    color: '#F97316',
    borderColor: '#F97316',
    icon: AlertOctagon,
    description: '25% – 35% annualized volatility. Heightened turbulence; volatility clustering detected across rolling high-frequency intervals.'
  },
  extreme: {
    label: 'EXTREME TAIL RISK / CRISIS',
    color: '#EF4444',
    borderColor: '#EF4444',
    icon: Flame,
    description: 'Exceeding 35% annualized volatility. Severe liquidity dislocation or sovereign shock conditions; defensive hedging and capital preservation enforced.'
  }
};

export default function RiskBadge({ forecastData }) {
  if (!forecastData) return null;

  const riskKey = (forecastData.risk_level || 'moderate').toLowerCase();
  const config = RISK_CONFIG[riskKey] || RISK_CONFIG.moderate;
  const vol = forecastData.garch_forecast ?? forecastData.baseline_forecast ?? 18.0;
  const riskScore = forecastData.risk_score ?? Math.min(100, Math.round(vol * 2.2));

  return (
    <section 
      className="card risk-badge-card"
      style={{ 
        borderLeft: `2px solid ${config.color}`
      }}
      aria-label="Sovereign Risk Assessment Summary"
    >
      <div className="risk-badge-header">
        <div className="risk-badge-title-wrap">
          <div 
            className="risk-status-chip"
            style={{ 
              borderColor: config.borderColor,
              color: config.color
            }}
          >
            <span className="chip-square-block" style={{ backgroundColor: config.color }} aria-hidden="true" />
            <span className="chip-label-text">{config.label}</span>
          </div>
          <span className="risk-horizon-tag label-uppercase">
            {forecastData.forecast_horizon_days || 5}-DAY FORWARD MATRIX
          </span>
        </div>

        <div className="risk-vol-value-wrap">
          <span className="risk-vol-sub label-uppercase">PROJECTED ANNUALIZED VOLATILITY (σ)</span>
          <span className="risk-vol-main tabular-nums" style={{ color: config.color }}>
            {vol.toFixed(1)}%
          </span>
        </div>
      </div>

      {/* Risk Index Progress Bar */}
      <div className="risk-meter-container">
        <div className="risk-meter-labels">
          <span className="risk-meter-title label-uppercase">QUANTITATIVE RISK FACTOR</span>
          <span className="risk-meter-val tabular-nums" style={{ color: config.color }}>
            {riskScore} <span className="risk-meter-denom">/ 100</span>
          </span>
        </div>
        <div className="risk-meter-track" role="progressbar" aria-valuenow={riskScore} aria-valuemin={0} aria-valuemax={100}>
          <div 
            className="risk-meter-fill"
            style={{ 
              width: `${Math.min(100, Math.max(5, riskScore))}%`,
              backgroundColor: config.color
            }}
          />
        </div>
        <div className="risk-meter-ticks label-uppercase" aria-hidden="true">
          <span>0 (CALM)</span>
          <span>25 (BASELINE)</span>
          <span>50 (ELEVATED)</span>
          <span>75 (TURBULENT)</span>
          <span>100 (CRISIS)</span>
        </div>
      </div>

      {/* Editorial Risk Memorandum */}
      <div className="risk-narrative-box">
        <p className="risk-narrative-editorial">
          {forecastData.summary || config.description}
        </p>
      </div>
    </section>
  );
}
