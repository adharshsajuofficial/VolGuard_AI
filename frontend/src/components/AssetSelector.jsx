import React, { useState } from 'react';
import { Search, TrendingUp, Calendar, ArrowRight } from 'lucide-react';

const POPULAR_ASSETS = [
  { symbol: 'SPY', name: 'S&P 500 (US)', category: 'Broad Market' },
  { symbol: '^NSEI', name: 'NIFTY 50 (India)', category: 'Indian Equities' },
  { symbol: 'QQQ', name: 'Nasdaq 100', category: 'Tech Index' },
  { symbol: 'DIA', name: 'Dow Jones', category: 'Blue Chip' },
  { symbol: 'AAPL', name: 'Apple Inc.', category: 'Large Cap' },
  { symbol: 'TSLA', name: 'Tesla Inc.', category: 'High Beta' }
];

const HORIZONS = [
  { days: 5, label: '5-Day Horizon', badge: 'Standard Target' },
  { days: 10, label: '10-Day Horizon', badge: 'Extended' },
  { days: 20, label: '20-Day Horizon', badge: 'Monthly' }
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
    <div className="card selector-container">
      <div className="selector-section">
        <div className="section-label">
          <TrendingUp size={16} />
          <span>Select Target Asset / Market Index</span>
        </div>

        <div className="asset-pills-wrap">
          {POPULAR_ASSETS.map((asset) => {
            const isSelected = currentSymbol.toUpperCase() === asset.symbol.toUpperCase();
            return (
              <button
                key={asset.symbol}
                type="button"
                onClick={() => onSelectAsset(asset.symbol)}
                className={`asset-pill ${isSelected ? 'asset-pill-active' : ''}`}
                disabled={loading}
              >
                <span className="asset-pill-symbol">{asset.symbol}</span>
                <span className="asset-pill-name">{asset.name}</span>
              </button>
            );
          })}
        </div>

        {/* Custom ticker search */}
        <form onSubmit={handleCustomSubmit} className="custom-ticker-form">
          <div className="input-with-icon">
            <Search size={16} className="search-icon" />
            <input
              type="text"
              placeholder="Enter Custom Symbol (e.g. MSFT, NVDA, GOOG)..."
              value={customInput}
              onChange={(e) => setCustomInput(e.target.value)}
              className="custom-ticker-input"
              disabled={loading}
            />
          </div>
          <button 
            type="submit" 
            className="btn-submit-ticker"
            disabled={loading || !customInput.trim()}
          >
            <span>Analyze</span>
            <ArrowRight size={14} />
          </button>
        </form>
      </div>

      <div className="selector-divider" />

      {/* Forecast Horizon Selector */}
      <div className="horizon-section">
        <div className="section-label">
          <Calendar size={16} />
          <span>Forecast Horizon Window (σ Horizon)</span>
        </div>
        <div className="horizon-buttons-wrap">
          {HORIZONS.map((h) => {
            const isSelected = currentHorizon === h.days;
            return (
              <button
                key={h.days}
                type="button"
                onClick={() => onSelectHorizon(h.days)}
                className={`horizon-btn ${isSelected ? 'horizon-btn-active' : ''}`}
                disabled={loading}
              >
                <span className="horizon-label">{h.label}</span>
                <span className="horizon-sub">{h.badge}</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
