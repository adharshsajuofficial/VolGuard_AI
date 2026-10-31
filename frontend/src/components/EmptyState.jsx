import React from 'react';
import { SearchX, ArrowLeft } from 'lucide-react';

export default function EmptyState({ symbol, onReset }) {
  return (
    <div className="empty-container" role="status">
      <div className="card empty-card">
        <div className="empty-icon-box" aria-hidden="true">
          <SearchX size={28} />
        </div>
        <h2 className="empty-title">Zero Market Observations Recorded for "{symbol}"</h2>
        <p className="empty-message">
          Verify the target ticker identifier (e.g. SPY, ^NSEI, QQQ, DIA, AAPL). Ensure market connectivity or local historical cache partition is mounted.
        </p>

        <button type="button" onClick={() => onReset('SPY')} className="btn-primary">
          <ArrowLeft size={14} aria-hidden="true" />
          <span>RESET TO S&amp;P 500 BENCHMARK (SPY)</span>
        </button>
      </div>
    </div>
  );
}
