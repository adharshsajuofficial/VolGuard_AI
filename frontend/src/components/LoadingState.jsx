import React from 'react';
import { Loader2 } from 'lucide-react';

export default function LoadingState({ symbol }) {
  return (
    <div className="loading-container">
      <div className="loading-card card">
        <Loader2 size={36} className="spin-icon text-cyan" />
        <h3 className="loading-title">Calculating Volatility Models for {symbol}...</h3>
        <p className="loading-subtitle">
          Retrieving market prices, computing daily log returns ($r_t$), and fitting GARCH(1,1) conditional variance.
        </p>

        <div className="skeleton-grid">
          <div className="skeleton-bar" style={{ width: '80%', height: '24px' }} />
          <div className="skeleton-bar" style={{ width: '100%', height: '140px' }} />
          <div className="skeleton-bar" style={{ width: '92%', height: '220px' }} />
        </div>
      </div>
    </div>
  );
}
