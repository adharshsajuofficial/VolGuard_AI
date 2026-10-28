import React from 'react';
import { ShieldAlert, Activity, RefreshCw, BookOpen, Wifi, WifiOff } from 'lucide-react';

export default function Header({ 
  symbol, 
  isSimulated, 
  onRefresh, 
  loading, 
  onOpenMethodology,
  lastUpdated 
}) {
  return (
    <header className="header-container">
      <div className="header-left">
        <div className="logo-badge">
          <ShieldAlert className="logo-icon" size={26} />
        </div>
        <div>
          <div className="brand-title-wrap">
            <h1 className="brand-title">VolGuard AI</h1>
            <span className="version-pill">v1.0 • Hackathon PS6</span>
          </div>
          <p className="brand-subtitle">
            Financial Risk Intelligence &amp; 5-Day Realized Volatility Forecasting Engine
          </p>
        </div>
      </div>

      <div className="header-right">
        {/* Backend Connectivity Status */}
        <div className={`status-chip ${isSimulated ? 'status-simulated' : 'status-live'}`} title={isSimulated ? "Backend offline - running realistic econometric simulation" : "Connected directly to FastAPI backend"}>
          {isSimulated ? (
            <>
              <WifiOff size={15} />
              <span>Demo / Sim Mode</span>
            </>
          ) : (
            <>
              <Wifi size={15} />
              <span>FastAPI Connected</span>
            </>
          )}
        </div>

        {/* Methodology Button */}
        <button 
          onClick={onOpenMethodology} 
          className="btn-secondary"
          title="Inspect Mathematical Formulations &amp; Methodologies"
        >
          <BookOpen size={16} />
          <span>Formulas &amp; Math</span>
        </button>

        {/* Refresh Button */}
        <button 
          onClick={onRefresh} 
          disabled={loading} 
          className="btn-primary"
          title="Refresh Data &amp; Re-run Volatility Forecasts"
        >
          <RefreshCw size={16} className={loading ? 'spin-icon' : ''} />
          <span>{loading ? 'Calculating...' : 'Refresh'}</span>
        </button>
      </div>
    </header>
  );
}
