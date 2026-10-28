import React from 'react';
import { SearchX, ArrowLeft } from 'lucide-react';

export default function EmptyState({ symbol, onReset }) {
  return (
    <div className="empty-container">
      <div className="card empty-card">
        <div className="empty-icon-box">
          <SearchX size={36} />
        </div>
        <h3 className="empty-title">No Market Data Found for "{symbol}"</h3>
        <p className="empty-message">
          Please verify the ticker symbol (e.g., SPY, ^NSEI, QQQ, AAPL). Ensure your internet connection or local historical backup CSV is available.
        </p>

        <button type="button" onClick={() => onReset('SPY')} className="btn-primary">
          <ArrowLeft size={16} />
          <span>Reset to S&amp;P 500 (SPY)</span>
        </button>
      </div>
    </div>
  );
}
