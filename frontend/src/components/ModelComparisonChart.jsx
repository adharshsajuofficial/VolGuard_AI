import React, { useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  BarChart,
  Bar
} from 'recharts';
import { GitCompare, SlidersHorizontal, CheckCircle2 } from 'lucide-react';

export default function ModelComparisonChart({ backtestData, symbol }) {
  const [chartType, setChartType] = useState('series'); // 'series' | 'errors'

  if (!backtestData || !backtestData.series || backtestData.series.length === 0) {
    return (
      <div className="card chart-card empty-chart">
        <GitCompare size={32} className="text-secondary" />
        <p>No backtest comparison data available for {symbol}.</p>
      </div>
    );
  }

  // Pre-calculate residual absolute errors
  const processedSeries = backtestData.series.map(pt => ({
    ...pt,
    baseline_err: +(Math.abs(pt.actual_realized - pt.baseline_pred)).toFixed(2),
    garch_err: +(Math.abs(pt.actual_realized - pt.garch_pred)).toFixed(2)
  }));

  return (
    <div className="card chart-card">
      <div className="chart-header">
        <div className="chart-title-wrap">
          <div className="chart-icon-box" style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38BDF8' }}>
            <GitCompare size={20} />
          </div>
          <div>
            <h3 className="chart-title">Model Comparison &amp; Out-of-Sample Backtest</h3>
            <span className="chart-subtitle">
              Chronological Test Period: Baseline vs. GARCH(1,1) vs. True Realized Volatility (σ 5-day Target)
            </span>
          </div>
        </div>

        <div className="chart-controls">
          <div className="segmented-control">
            <button
              type="button"
              onClick={() => setChartType('series')}
              className={`segmented-btn ${chartType === 'series' ? 'segmented-btn-active' : ''}`}
            >
              <SlidersHorizontal size={14} />
              <span>Trajectories</span>
            </button>
            <button
              type="button"
              onClick={() => setChartType('errors')}
              className={`segmented-btn ${chartType === 'errors' ? 'segmented-btn-active' : ''}`}
            >
              <span>Residual Errors |e|</span>
            </button>
          </div>
        </div>
      </div>

      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={340}>
          {chartType === 'series' ? (
            <LineChart data={processedSeries} margin={{ top: 20, right: 30, left: 0, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.6} />
              <XAxis dataKey="date" stroke="#94A3B8" tick={{ fontSize: 11 }} tickMargin={8} />
              <YAxis stroke="#94A3B8" tick={{ fontSize: 11 }} unit="%" domain={['dataMin - 2', 'dataMax + 2']} />
              <Tooltip content={<BacktestTooltip />} />
              <Legend verticalAlign="top" height={36} iconType="circle" />

              {/* Actual Ground Truth Realized Volatility */}
              <Line
                type="monotone"
                dataKey="actual_realized"
                name="Actual Realized Volatility (Target)"
                stroke="#F43F5E"
                strokeWidth={3}
                dot={{ r: 3, fill: '#F43F5E' }}
              />

              {/* GARCH Prediction */}
              <Line
                type="monotone"
                dataKey="garch_pred"
                name="GARCH(1,1) Forecast"
                stroke="#38BDF8"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={false}
              />

              {/* Baseline Prediction */}
              <Line
                type="monotone"
                dataKey="baseline_pred"
                name="20-Day Baseline Forecast"
                stroke="#F59E0B"
                strokeWidth={2}
                strokeDasharray="2 2"
                dot={false}
              />
            </LineChart>
          ) : (
            <BarChart data={processedSeries} margin={{ top: 20, right: 30, left: 0, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.6} />
              <XAxis dataKey="date" stroke="#94A3B8" tick={{ fontSize: 11 }} tickMargin={8} />
              <YAxis stroke="#94A3B8" tick={{ fontSize: 11 }} unit="%" />
              <Tooltip content={<ErrorTooltip />} />
              <Legend verticalAlign="top" height={36} />

              <Bar dataKey="baseline_err" name="Baseline Error |Actual - Base|" fill="#F59E0B" opacity={0.8} />
              <Bar dataKey="garch_err" name="GARCH Error |Actual - GARCH|" fill="#38BDF8" opacity={0.8} />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>

      <div className="backtest-footer-alert">
        <CheckCircle2 size={16} className="text-emerald" />
        <span>
          <strong>Zero-Lookahead Guarantee:</strong> Every forecast point was calculated strictly using past closing prices up to date $t$. Target evaluated on held-out days $t+1 \dots t+5$.
        </span>
      </div>
    </div>
  );
}

function BacktestTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip">
        <p className="tooltip-date">Test Date: {label}</p>
        {payload.map((entry, idx) => (
          <div key={`bt-tt-${idx}`} className="tooltip-row" style={{ color: entry.color }}>
            <span className="tooltip-name">{entry.name}:</span>
            <span className="tooltip-val">{Number(entry.value).toFixed(2)}%</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
}

function ErrorTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip">
        <p className="tooltip-date">{label}</p>
        {payload.map((entry, idx) => (
          <div key={`err-tt-${idx}`} className="tooltip-row" style={{ color: entry.color }}>
            <span className="tooltip-name">{entry.name}:</span>
            <span className="tooltip-val">{Number(entry.value).toFixed(2)} pts</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
}
