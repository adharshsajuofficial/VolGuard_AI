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
        <GitCompare size={24} className="text-secondary" aria-hidden="true" />
        <p className="label-uppercase">NO BACKTEST MATRIX RECORDED FOR {symbol}</p>
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
    <section className="card chart-card" aria-label="Walk-Forward Model Comparison Matrix">
      <div className="chart-header">
        <div className="chart-title-wrap">
          <div className="chart-icon-box" aria-hidden="true">
            <GitCompare size={16} />
          </div>
          <div>
            <h2 className="chart-title">Model Comparison &amp; Out-of-Sample Backtest</h2>
            <span className="chart-subtitle label-uppercase">
              CHRONOLOGICAL TEST WINDOW: GARCH(1,1) VS. BASELINE VS. REALIZED GROUND TRUTH (σ 5-DAY)
            </span>
          </div>
        </div>

        <div className="chart-controls">
          <div className="segmented-control" role="group" aria-label="Backtest display mode">
            <button
              type="button"
              onClick={() => setChartType('series')}
              className={`segmented-btn ${chartType === 'series' ? 'segmented-btn-active' : ''}`}
              aria-pressed={chartType === 'series'}
            >
              <SlidersHorizontal size={13} aria-hidden="true" />
              <span>TRAJECTORIES</span>
            </button>
            <button
              type="button"
              onClick={() => setChartType('errors')}
              className={`segmented-btn ${chartType === 'errors' ? 'segmented-btn-active' : ''}`}
              aria-pressed={chartType === 'errors'}
            >
              <span>RESIDUAL ERRORS |e|</span>
            </button>
          </div>
        </div>
      </div>

      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={340}>
          {chartType === 'series' ? (
            <LineChart data={processedSeries} margin={{ top: 16, right: 24, left: 0, bottom: 8 }}>
              <CartesianGrid strokeDasharray="2 2" stroke="#1E293B" />
              <XAxis dataKey="date" stroke="#475569" tick={{ fontSize: 11, fill: '#94A3B8', fontFamily: 'Geist, sans-serif' }} tickMargin={8} />
              <YAxis stroke="#475569" tick={{ fontSize: 11, fill: '#94A3B8', fontFamily: 'Geist, sans-serif' }} unit="%" domain={['dataMin - 2', 'dataMax + 2']} />
              <Tooltip content={<BacktestTooltip />} />
              <Legend verticalAlign="top" height={36} iconType="rect" />

              {/* Actual Ground Truth Realized Volatility - Crimson */}
              <Line
                type="monotone"
                dataKey="actual_realized"
                name="Actual Realized Volatility (Ground Truth σ 5d)"
                stroke="#EF4444"
                strokeWidth={2.5}
                dot={{ r: 3, fill: '#EF4444' }}
              />

              {/* GARCH Prediction - Amber */}
              <Line
                type="monotone"
                dataKey="garch_pred"
                name="GARCH(1,1) Core Forecast"
                stroke="#F59E0B"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={false}
              />

              {/* Baseline Prediction - Cyan */}
              <Line
                type="monotone"
                dataKey="baseline_pred"
                name="20-Day Baseline Benchmark"
                stroke="#38BDF8"
                strokeWidth={1.8}
                strokeDasharray="2 2"
                dot={false}
              />
            </LineChart>
          ) : (
            <BarChart data={processedSeries} margin={{ top: 16, right: 24, left: 0, bottom: 8 }}>
              <CartesianGrid strokeDasharray="2 2" stroke="#1E293B" />
              <XAxis dataKey="date" stroke="#475569" tick={{ fontSize: 11, fill: '#94A3B8', fontFamily: 'Geist, sans-serif' }} tickMargin={8} />
              <YAxis stroke="#475569" tick={{ fontSize: 11, fill: '#94A3B8', fontFamily: 'Geist, sans-serif' }} unit="%" />
              <Tooltip content={<ErrorTooltip />} />
              <Legend verticalAlign="top" height={36} />

              <Bar dataKey="baseline_err" name="Baseline Error |Actual - Base|" fill="#38BDF8" opacity={0.8} />
              <Bar dataKey="garch_err" name="GARCH Error |Actual - GARCH|" fill="#F59E0B" opacity={0.9} />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>

      <div className="backtest-footer-alert" role="note">
        <CheckCircle2 size={15} className="text-emerald" aria-hidden="true" />
        <span className="label-uppercase">
          <strong>ZERO-LOOKAHEAD GUARANTEE:</strong> ALL ESTIMATION PARAMETERS RIGOROUSLY TRAINED ON PRIOR TIME-SERIES UP TO DATE <em>t</em>. EVALUATION PERFORMED STRICTLY ON HELD-OUT INTERVAL <em>t+1 … t+5</em>.
        </span>
      </div>
    </section>
  );
}

function BacktestTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip" role="tooltip">
        <p className="tooltip-date label-uppercase">WALK-FORWARD DATE: {label}</p>
        {payload.map((entry, idx) => (
          <div key={`bt-tt-${idx}`} className="tooltip-row" style={{ color: entry.color }}>
            <span className="tooltip-square-block" style={{ backgroundColor: entry.color }} aria-hidden="true" />
            <span className="tooltip-name">{entry.name}:</span>
            <span className="tooltip-val tabular-nums">{Number(entry.value).toFixed(2)}%</span>
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
      <div className="custom-tooltip" role="tooltip">
        <p className="tooltip-date label-uppercase">WALK-FORWARD DATE: {label}</p>
        {payload.map((entry, idx) => (
          <div key={`err-tt-${idx}`} className="tooltip-row" style={{ color: entry.color }}>
            <span className="tooltip-square-block" style={{ backgroundColor: entry.color }} aria-hidden="true" />
            <span className="tooltip-name">{entry.name}:</span>
            <span className="tooltip-val tabular-nums">{Number(entry.value).toFixed(2)} pts</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
}
