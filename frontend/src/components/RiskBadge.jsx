import React from 'react';
import { AlertTriangle, ShieldCheck, AlertOctagon, Flame, Info } from 'lucide-react';

const RISK_CONFIG = {
  low: {
    label: 'LOW RISK',
    color: '#10B981',
    bgColor: 'rgba(16, 185, 129, 0.12)',
    borderColor: 'rgba(16, 185, 129, 0.4)',
    icon: ShieldCheck,
    description: 'Sub-15% annualized volatility. Market regime indicates stable pricing and normal liquidity.'
  },
  moderate: {
    label: 'MODERATE RISK',
    color: '#F59E0B',
    bgColor: 'rgba(245, 158, 11, 0.12)',
    borderColor: 'rgba(245, 158, 11, 0.4)',
    icon: AlertTriangle,
    description: '15% – 25% annualized volatility. Typical market variance; monitor ongoing positions.'
  },
  high: {
    label: 'HIGH RISK',
    color: '#F97316',
    bgColor: 'rgba(249, 115, 22, 0.14)',
    borderColor: 'rgba(249, 115, 22, 0.45)',
    icon: AlertOctagon,
    description: '25% – 35% annualized volatility. Heightened turbulence; volatility clustering detected.'
  },
  extreme: {
    label: 'EXTREME RISK',
    color: '#EF4444',
    bgColor: 'rgba(239, 68, 68, 0.16)',
    borderColor: 'rgba(239, 68, 68, 0.5)',
    icon: Flame,
    description: 'Surpassing 35% annualized volatility. Severe shock or crisis conditions; hedging recommended.'
  }
};

export default function RiskBadge({ forecastData }) {
  if (!forecastData) return null;

  const riskKey = (forecastData.risk_level || 'moderate').toLowerCase();
  const config = RISK_CONFIG[riskKey] || RISK_CONFIG.moderate;
  const IconComponent = config.icon;
  const vol = forecastData.garch_forecast ?? forecastData.baseline_forecast ?? 18.0;
  const riskScore = forecastData.risk_score ?? Math.min(100, Math.round(vol * 2.2));

  return (
    <div 
      className="card risk-badge-card"
      style={{ 
        borderColor: config.borderColor,
        background: `linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, ${config.bgColor} 100%)` 
      }}
    >
      <div className="risk-badge-header">
        <div className="risk-badge-title-wrap">
          <div 
            className="risk-indicator-pill" 
            style={{ 
              backgroundColor: config.bgColor, 
              color: config.color,
              borderColor: config.borderColor
            }}
          >
            <span className="pulse-dot" style={{ backgroundColor: config.color }} />
            <IconComponent size={18} />
            <span className="risk-label-text">{config.label}</span>
          </div>
          <span className="risk-horizon-tag">Next {forecastData.forecast_horizon_days || 5} Trading Days</span>
        </div>

        <div className="risk-vol-value-wrap">
          <span className="risk-vol-sub">Projected Annualized Volatility</span>
          <span className="risk-vol-main" style={{ color: config.color }}>
            {vol.toFixed(1)}%
          </span>
        </div>
      </div>

      {/* Risk Score Progress Bar */}
      <div className="risk-meter-container">
        <div className="risk-meter-labels">
          <span>Risk Index</span>
          <span className="risk-meter-val" style={{ color: config.color }}>{riskScore} / 100</span>
        </div>
        <div className="risk-meter-track">
          <div 
            className="risk-meter-fill"
            style={{ 
              width: `${Math.min(100, Math.max(5, riskScore))}%`,
              backgroundColor: config.color,
              boxShadow: `0 0 12px ${config.color}`
            }}
          />
        </div>
        <div className="risk-meter-ticks">
          <span>0 (Calm)</span>
          <span>25 (Normal)</span>
          <span>50 (Elevated)</span>
          <span>75 (Turbulent)</span>
          <span>100 (Crisis)</span>
        </div>
      </div>

      {/* Summary Narrative */}
      <div className="risk-narrative-box">
        <p className="risk-narrative-text">
          {forecastData.summary || config.description}
        </p>
      </div>
    </div>
  );
}
