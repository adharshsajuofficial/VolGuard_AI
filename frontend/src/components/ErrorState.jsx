import React from 'react';
import { AlertCircle, RefreshCw, Radio } from 'lucide-react';

export default function ErrorState({ error, onRetry, onSwitchToDemo }) {
  return (
    <div className="error-container" role="alert">
      <div className="card error-card">
        <div className="error-icon-box" aria-hidden="true">
          <AlertCircle size={28} />
        </div>
        <h2 className="error-title">Quantitative Engine Execution Aborted</h2>
        <p className="error-message">
          {error || 'An unexpected socket timeout or mathematical error interrupted the econometric estimation engine.'}
        </p>

        <div className="error-actions-row">
          <button type="button" onClick={onRetry} className="btn-primary">
            <RefreshCw size={13} aria-hidden="true" />
            <span>RE-EXECUTE ESTIMATION</span>
          </button>
          {onSwitchToDemo && (
            <button type="button" onClick={onSwitchToDemo} className="btn-secondary">
              <Radio size={13} aria-hidden="true" />
              <span>ENGAGE OFFLINE SIMULATION</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
