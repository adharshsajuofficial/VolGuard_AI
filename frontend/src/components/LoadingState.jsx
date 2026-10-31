import React from 'react';
import { Loader2 } from 'lucide-react';

export default function LoadingState({ symbol }) {
  return (
    <div className="loading-container" role="status" aria-live="polite">
      <div className="loading-card card">
        <Loader2 size={28} className="spin-icon text-amber" aria-hidden="true" />
        <h2 className="loading-title">Executing Quantitative Estimation for {symbol}…</h2>
        <p className="loading-subtitle">
          Retrieving market prices, computing daily logarithmic returns (<em>r_t</em>), and fitting GARCH(1,1) maximum likelihood conditional variance.
        </p>

        <div className="skeleton-grid" aria-hidden="true">
          <div className="skeleton-bar" style={{ width: '60%', height: '18px' }} />
          <div className="skeleton-bar" style={{ width: '100%', height: '90px' }} />
          <div className="skeleton-bar" style={{ width: '85%', height: '160px' }} />
        </div>
      </div>
    </div>
  );
}
