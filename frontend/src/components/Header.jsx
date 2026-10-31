import React from 'react';
import { Shield, RefreshCw, BookOpen, Clock } from 'lucide-react';

export default function Header({ 
  symbol, 
  isSimulated, 
  onRefresh, 
  loading, 
  onOpenMethodology,
  lastUpdated 
}) {
  const formattedTime = lastUpdated instanceof Date 
    ? lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }) 
    : '--:--:--';

  return (
    <header className="header-container" role="banner">
      <div className="header-left">
        <div className="logo-badge" aria-hidden="true">
          <Shield className="logo-icon" size={20} />
        </div>
        <div className="brand-text-block">
          <div className="brand-title-wrap">
            <h1 className="brand-title">VolGuard AI</h1>
            <span className="system-tag label-uppercase">SOVEREIGN RISK MATRIX</span>
          </div>
          <p className="brand-subtitle">
            Institutional Volatility Cartography &amp; 5-Day Realized Econometric Forecast Engine
          </p>
        </div>
      </div>

      <div className="header-center">
        <div className="terminal-meta-item">
          <span className="meta-label">TARGET ASSET</span>
          <span className="meta-value tabular-nums">{symbol}</span>
        </div>
        <div className="terminal-meta-divider" aria-hidden="true" />
        <div className="terminal-meta-item">
          <span className="meta-label">CHRONO STAMP</span>
          <span className="meta-value tabular-nums">
            <Clock size={12} className="meta-clock-icon" aria-hidden="true" />
            {formattedTime} UTC
          </span>
        </div>
        <div className="terminal-meta-divider" aria-hidden="true" />
        <div className="terminal-meta-item">
          <span className="meta-label">HORIZON</span>
          <span className="meta-value tabular-nums">5D (σ TARGET)</span>
        </div>
      </div>

      <div className="header-right">
        {/* Status Chip with 4px Square Status Block */}
        <div 
          className={`status-chip ${isSimulated ? 'status-simulated' : 'status-live'}`} 
          title={isSimulated ? "Backend offline — high-fidelity econometric fallback active" : "Connected directly to FastAPI quantitative engine"}
          role="status"
          aria-live="polite"
        >
          <span className="status-block" aria-hidden="true" />
          <span className="status-text">{isSimulated ? "OFFLINE SIMULATION" : "LIVE FASTAPI FEED"}</span>
        </div>

        {/* Methodology Action */}
        <button 
          type="button"
          onClick={onOpenMethodology} 
          className="btn-secondary"
          title="Inspect Mathematical Formulations &amp; Econometric Architecture"
        >
          <BookOpen size={14} aria-hidden="true" />
          <span>RESEARCH MEMORANDUM</span>
        </button>

        {/* Primary Execution Action */}
        <button 
          type="button"
          onClick={onRefresh} 
          disabled={loading} 
          className="btn-primary"
          title="Refresh Data &amp; Re-run Volatility Forecasts"
          aria-busy={loading}
        >
          <RefreshCw size={14} className={loading ? 'spin-icon' : ''} aria-hidden="true" />
          <span>{loading ? 'CALCULATING...' : 'EXECUTE ESTIMATION'}</span>
        </button>
      </div>
    </header>
  );
}
