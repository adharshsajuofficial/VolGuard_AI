import React from 'react';
import { AlertCircle, RefreshCw, Radio } from 'lucide-react';

export default function ErrorState({ error, onRetry, onSwitchToDemo }) {
  return (
    <div className="error-container">
      <div className="card error-card">
        <div className="error-icon-box">
          <AlertCircle size={32} />
        </div>
        <h3 className="error-title">Unable to Retrieve Volatility Forecast</h3>
        <p className="error-message">
          {error || 'An unexpected network error occurred while querying the volatility calculation engine.'}
        </p>

        <div className="error-actions-row">
          <button type="button" onClick={onRetry} className="btn-primary">
            <RefreshCw size={15} />
            <span>Retry Query</span>
          </button>
          {onSwitchToDemo && (
            <button type="button" onClick={onSwitchToDemo} className="btn-secondary">
              <Radio size={15} />
              <span>Switch to Demo Simulation Mode</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
