import React, { useState, useMemo } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ReferenceLine
} from 'recharts';
import { BarChart3, DollarSign, Activity } from 'lucide-react';

const TIMEFRAMES = [
  { label: '1M', days: 22 },
  { label: '3M', days: 65 },
  { label: '6M', days: 130 },
  { label: 'ALL', days: 250 }
];

export default function VolatilityChart({ historyData, symbol, forecastData }) {
  const [viewMode, setViewMode] = useState('volatility'); // 'volatility' | 'price'
  const [timeframe, setTimeframe] = useState(65);

  const filteredData = useMemo(() => {
    if (!historyData || !historyData.data || historyData.data.length === 0) return [];
    const sliceCount = Math.min(historyData.data.length, timeframe);
    return historyData.data.slice(-sliceCount);
  }, [historyData, timeframe]);

  // Projected forecast forward points
  const chartDataWithForecast = useMemo(() => {
    if (filteredData.length === 0) return [];
    const baseList = filteredData.map(item => ({
      ...item,
      forecast_garch: null,
      forecast_baseline: null
    }));

    if (forecastData && baseList.length > 0) {
      const lastPoint = baseList[baseList.length - 1];
      baseList[baseList.length - 1].forecast_garch = lastPoint.rolling_vol_20d;
      baseList[baseList.length - 1].forecast_baseline = lastPoint.rolling_vol_20d;

      const horizon = forecastData.forecast_horizon_days || 5;
      for (let i = 1; i <= horizon; i++) {
        const lastDate = new Date(lastPoint.date);
        lastDate.setDate(lastDate.getDate() + i);

        baseList.push({
          date: `+${i}d (${lastDate.toISOString().split('T')[0].slice(5)})`,
          close: null,
          rolling_vol_20d: null,
          forecast_garch: forecastData.garch_forecast,
          forecast_baseline: forecastData.baseline_forecast,
          isForecast: true
        });
      }
    }
    return baseList;
  }, [filteredData, forecastData]);

  if (!historyData || !historyData.data || historyData.data.length === 0) {
    return (
      <div className="card chart-card empty-chart">
        <Activity size={24} className="text-secondary" aria-hidden="true" />
        <p className="label-uppercase">NO HISTORICAL DATA RECORDED FOR {symbol}</p>
      </div>
    );
  }

  return (
    <section className="card chart-card" aria-label="Sovereign Volatility Trajectory Dossier">
      <div className="chart-header">
        <div className="chart-title-wrap">
          <div className="chart-icon-box" aria-hidden="true">
            <BarChart3 size={16} />
          </div>
          <div>
            <h2 className="chart-title">
              {viewMode === 'volatility' ? 'Historical & Projected Realized Volatility Dossier' : `${symbol} Closing Spot Trajectory Matrix`}
            </h2>
            <span className="chart-subtitle label-uppercase">
              {viewMode === 'volatility' 
                ? '20-DAY ROLLING ANNUALIZED VARIANCE (σ) WITH 5-DAY FORWARD CONE' 
                : 'ADJUSTED CLOSE TIME-SERIES WITH COMPOUND LOGARITHMIC RETURNS'}
            </span>
          </div>
        </div>

        <div className="chart-controls">
          {/* Segmented Matrix Switcher */}
          <div className="segmented-control" role="group" aria-label="Chart metric toggle">
            <button
              type="button"
              onClick={() => setViewMode('volatility')}
              className={`segmented-btn ${viewMode === 'volatility' ? 'segmented-btn-active' : ''}`}
              aria-pressed={viewMode === 'volatility'}
            >
              <Activity size={13} aria-hidden="true" />
              <span>VOLATILITY (σ %)</span>
            </button>
            <button
              type="button"
              onClick={() => setViewMode('price')}
              className={`segmented-btn ${viewMode === 'price' ? 'segmented-btn-active' : ''}`}
              aria-pressed={viewMode === 'price'}
            >
              <DollarSign size={13} aria-hidden="true" />
              <span>SPOT PRICE ($)</span>
            </button>
          </div>

          {/* Timeframe Filter */}
          <div className="timeframe-group" role="group" aria-label="Timeframe selection">
            {TIMEFRAMES.map((tf) => (
              <button
                key={tf.label}
                type="button"
                onClick={() => setTimeframe(tf.days)}
                className={`tf-btn ${timeframe === tf.days ? 'tf-btn-active' : ''}`}
                aria-pressed={timeframe === tf.days}
              >
                {tf.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={360}>
          {viewMode === 'volatility' ? (
            <AreaChart data={chartDataWithForecast} margin={{ top: 16, right: 24, left: 0, bottom: 8 }}>
              <defs>
                <linearGradient id="volGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#334155" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#334155" stopOpacity={0.0} />
                </linearGradient>
              </defs>

              <CartesianGrid strokeDasharray="2 2" stroke="#1E293B" />
              <XAxis 
                dataKey="date" 
                stroke="#475569" 
                tick={{ fontSize: 11, fill: '#94A3B8', fontFamily: 'Geist, sans-serif' }} 
                tickMargin={8} 
              />
              <YAxis 
                stroke="#475569" 
                tick={{ fontSize: 11, fill: '#94A3B8', fontFamily: 'Geist, sans-serif' }} 
                unit="%" 
                domain={['dataMin - 3', 'dataMax + 5']} 
              />
              <Tooltip content={<CustomVolTooltip />} />
              <Legend verticalAlign="top" height={36} iconType="rect" />

              {/* Sovereign Regime Thresholds */}
              <ReferenceLine y={15} stroke="#10B981" strokeDasharray="3 3" label={{ value: '15% STABLE', fill: '#10B981', fontSize: 10, position: 'insideTopRight' }} />
              <ReferenceLine y={25} stroke="#F59E0B" strokeDasharray="3 3" label={{ value: '25% ELEVATED', fill: '#F59E0B', fontSize: 10, position: 'insideTopRight' }} />
              <ReferenceLine y={35} stroke="#EF4444" strokeDasharray="3 3" label={{ value: '35% CRISIS TAIL', fill: '#EF4444', fontSize: 10, position: 'insideTopRight' }} />

              {/* Historical Realized Vol */}
              <Area
                type="monotone"
                dataKey="rolling_vol_20d"
                name="20-Day Rolling Realized Vol (%)"
                stroke="#94A3B8"
                strokeWidth={1.8}
                fillOpacity={1}
                fill="url(#volGradient)"
              />

              {/* GARCH Core Forecast - Signature Amber */}
              <Line
                type="monotone"
                dataKey="forecast_garch"
                name="GARCH(1,1) Core Forecast (%)"
                stroke="#F59E0B"
                strokeWidth={2.5}
                strokeDasharray="4 4"
                dot={{ r: 4, fill: '#F59E0B', stroke: '#090D14', strokeWidth: 1.5 }}
              />

              {/* Baseline Forecast - Cyan Informational */}
              <Line
                type="monotone"
                dataKey="forecast_baseline"
                name="Baseline Benchmark Forecast (%)"
                stroke="#38BDF8"
                strokeWidth={1.8}
                strokeDasharray="2 2"
                dot={{ r: 3, fill: '#38BDF8', stroke: '#090D14', strokeWidth: 1 }}
              />
            </AreaChart>
          ) : (
            <LineChart data={filteredData} margin={{ top: 16, right: 24, left: 10, bottom: 8 }}>
              <CartesianGrid strokeDasharray="2 2" stroke="#1E293B" />
              <XAxis dataKey="date" stroke="#475569" tick={{ fontSize: 11, fill: '#94A3B8', fontFamily: 'Geist, sans-serif' }} tickMargin={8} />
              <YAxis 
                stroke="#475569" 
                tick={{ fontSize: 11, fill: '#94A3B8', fontFamily: 'Geist, sans-serif' }} 
                domain={['auto', 'auto']}
                tickFormatter={(val) => `$${val.toLocaleString()}`}
              />
              <Tooltip content={<CustomPriceTooltip />} />
              <Legend verticalAlign="top" height={36} iconType="rect" />

              <Line
                type="monotone"
                dataKey="close"
                name="Adjusted Close Price ($)"
                stroke="#F59E0B"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>
    </section>
  );
}

function CustomVolTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip" role="tooltip">
        <p className="tooltip-date label-uppercase">INTERVAL: {label}</p>
        {payload.map((entry, idx) => (
          entry.value != null && (
            <div key={`tooltip-${idx}`} className="tooltip-row" style={{ color: entry.color }}>
              <span className="tooltip-square-block" style={{ backgroundColor: entry.color }} aria-hidden="true" />
              <span className="tooltip-name">{entry.name}:</span>
              <span className="tooltip-val tabular-nums">{Number(entry.value).toFixed(2)}%</span>
            </div>
          )
        ))}
      </div>
    );
  }
  return null;
}

function CustomPriceTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="custom-tooltip" role="tooltip">
        <p className="tooltip-date label-uppercase">INTERVAL: {label}</p>
        <div className="tooltip-row" style={{ color: '#F8FAFC' }}>
          <span className="tooltip-name">Adjusted Close:</span>
          <span className="tooltip-val tabular-nums">${data.close?.toFixed(2)}</span>
        </div>
        {data.log_return != null && (
          <div className="tooltip-row" style={{ color: data.log_return >= 0 ? '#10B981' : '#EF4444' }}>
            <span className="tooltip-name">Log Return (r_t):</span>
            <span className="tooltip-val tabular-nums">{(data.log_return * 100).toFixed(2)}%</span>
          </div>
        )}
        {data.rolling_vol_20d != null && (
          <div className="tooltip-row" style={{ color: '#94A3B8' }}>
            <span className="tooltip-name">20d Historical Vol:</span>
            <span className="tooltip-val tabular-nums">{data.rolling_vol_20d.toFixed(2)}%</span>
          </div>
        )}
      </div>
    );
  }
  return null;
}
