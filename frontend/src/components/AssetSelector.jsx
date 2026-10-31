import React, { useState } from 'react';
import { Search, TrendingUp, Calendar, ArrowRight } from 'lucide-react';

const POPULAR_ASSETS = [
  { symbol: 'SPY', name: 'S&P 500 ETF', category: 'Broad US' },
  { symbol: '^NSEI', name: 'NIFTY 50', category: 'NSE India' },
  { symbol: 'QQQ', name: 'Nasdaq 100', category: 'Tech Sector' },
  { symbol: 'DIA', name: 'Dow Jones', category: 'Mega Cap' },
  { symbol: 'AAPL', name: 'Apple Inc.', category: 'Equities' },
  { symbol: 'TSLA', name: 'Tesla Inc.', category: 'High Beta' }
];

const HORIZONS = [
  { days: 5, label: '5-Day Horizon', badge: 'Primary Benchmark' },
  { days: 10, label: '10-Day Horizon', badge: 'Bi-Weekly Matrix' },
  { days: 20, label: '20-Day Horizon', badge: 'Monthly Window' }
];

export default function AssetSelector({ 
  currentSymbol, 
  currentHorizon, 
  onSelectAsset, 
  onSelectHorizon, 
  loading 
}) {
  const [customInput, setCustomInput] = useState('');

  const handleCustomSubmit = (e) => {
    e.preventDefault();
    const clean = customInput.trim().toUpperCase();
    if (clean) {
      onSelectAsset(clean);
      setCustomInput('');
    }
  };

  return (
    <section className="card selector-container" aria-label="Asset & Horizon Matrix">
      <div className="selector-section">
        <div className="section-label">
          <TrendingUp size={14} aria-hidden="true" />
          <span>PORTFOLIO SECTOR &amp; UNDERLYING INSTRUMENT</span>
        </div>

        <div className="asset-pills-wrap" role="group" aria-label="Quick asset selection">
          {POPULAR_ASSETS.map((asset) => {
            const isSelected = currentSymbol.toUpperCase() === asset.symbol.toUpperCase();
            return (
              <button
                key={asset.symbol}
                type="button"
                onClick={() => onSelectAsset(asset.symbol)}
                className={`asset-btn ${isSelected ? 'asset-btn-active' : ''}`}
                disabled={loading}
                aria-pressed={isSelected}
              >
                <span className="asset-symbol tabular-nums">{asset.symbol}</span>
                <span className="asset-name">{asset.name}</span>
              </button>
            );
          })}
        </div>

        {/* Custom ticker search */}
        <form onSubmit={handleCustomSubmit} className="custom-ticker-form" role="search">
          <div className="input-with-icon">
            <Search size={14} className="search-icon" aria-hidden="true" />
            <input
              type="text"
              id="custom-symbol-input"
              placeholder="QUERY CUSTOM TICKER (e.g. MSFT, NVDA, GOOG, ^GSPC)..."
              value={customInput}
              onChange={(e) => setCustomInput(e.target.value)}
              className="custom-ticker-input"
              disabled={loading}
              aria-label="Enter Custom Ticker Symbol"
            />
          </div>
          <button 
            type="submit" 
            className="btn-submit-ticker"
            disabled={loading || !customInput.trim()}
            title="Load Market Data for Custom Symbol"
          >
            <span>INGEST</span>
            <ArrowRight size={13} aria-hidden="true" />
          </button>
        </form>
      </div>

      <div className="selector-divider" aria-hidden="true" />

      {/* Forecast Horizon Matrix */}
      <div className="horizon-section">
        <div className="section-label">
          <Calendar size={14} aria-hidden="true" />
          <span>ESTIMATION WINDOW (σ HORIZON)</span>
        </div>
        <div className="horizon-buttons-wrap" role="group" aria-label="Forecast horizon selection">
          {HORIZONS.map((h) => {
            const isSelected = currentHorizon === h.days;
            return (
              <button
                key={h.days}
                type="button"
                onClick={() => onSelectHorizon(h.days)}
                className={`horizon-btn ${isSelected ? 'horizon-btn-active' : ''}`}
                disabled={loading}
                aria-pressed={isSelected}
              >
                <span className="horizon-label tabular-nums">{h.label}</span>
                <span className="horizon-sub">{h.badge}</span>
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}
