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
import { BarChart3, DollarSign, Activity, Maximize2 } from 'lucide-react';

const TIMEFRAMES = [
  { label: '1M', days: 22 },
  { label: '3M', days: 65 },
  { label: '6M', days: 130 },
  { label: 'All', days: 250 }
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
      // Bridge current to projected
      baseList[baseList.length - 1].forecast_garch = lastPoint.rolling_vol_20d;
      baseList[baseList.length - 1].forecast_baseline = lastPoint.rolling_vol_20d;

      // Add forward points
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
        <Activity size={32} className="text-secondary" />
        <p>No historical price or volatility data available for {symbol}.</p>
      </div>
    );
  }

  return (
    <div className="card chart-card">
      <div className="chart-header">
        <div className="chart-title-wrap">
          <div className="chart-icon-box">
            <BarChart3 size={20} />
          </div>
          <div>
            <h3 className="chart-title">
              {viewMode === 'volatility' ? 'Historical & Projected Realized Volatility' : `${symbol} Closing Price Trajectory`}
            </h3>
            <span className="chart-subtitle">
              {viewMode === 'volatility' 
                ? '20-Day Rolling Annualized Volatility (%) with 5-Day Forward Forecast Cone' 
                : 'Daily Adjusted Closing Prices with Log Returns'}
            </span>
          </div>
        </div>

        <div className="chart-controls">
          {/* View Mode Toggle */}
          <div className="segmented-control">
            <button
              type="button"
              onClick={() => setViewMode('volatility')}
              className={`segmented-btn ${viewMode === 'volatility' ? 'segmented-btn-active' : ''}`}
            >
              <Activity size={14} />
              <span>Volatility (%)</span>
            </button>
            <button
              type="button"
              onClick={() => setViewMode('price')}
              className={`segmented-btn ${viewMode === 'price' ? 'segmented-btn-active' : ''}`}
            >
              <DollarSign size={14} />
              <span>Price ($)</span>
            </button>
          </div>

          {/* Timeframe Filter */}
          <div className="timeframe-group">
            {TIMEFRAMES.map((tf) => (
              <button
                key={tf.label}
                type="button"
                onClick={() => setTimeframe(tf.days)}
                className={`tf-btn ${timeframe === tf.days ? 'tf-btn-active' : ''}`}
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
            <AreaChart data={chartDataWithForecast} margin={{ top: 20, right: 30, left: 0, bottom: 10 }}>
              <defs>
                <linearGradient id="volGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10B981" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="forecastGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#38BDF8" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#38BDF8" stopOpacity={0.05} />
                </linearGradient>
              </defs>

              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.6} />
              <XAxis 
                dataKey="date" 
                stroke="#94A3B8" 
                tick={{ fontSize: 11 }} 
                tickMargin={8} 
              />
              <YAxis 
                stroke="#94A3B8" 
                tick={{ fontSize: 11 }} 
                unit="%" 
                domain={['dataMin - 3', 'dataMax + 5']} 
              />
              <Tooltip content={<CustomVolTooltip />} />
              <Legend verticalAlign="top" height={36} iconType="circle" />

              {/* Risk Level Threshold Reference Lines */}
              <ReferenceLine y={15} stroke="#10B981" strokeDasharray="4 4" label={{ value: '15% Low/Mod', fill: '#10B981', fontSize: 10 }} />
              <ReferenceLine y={25} stroke="#F59E0B" strokeDasharray="4 4" label={{ value: '25% Mod/High', fill: '#F59E0B', fontSize: 10 }} />
              <ReferenceLine y={35} stroke="#EF4444" strokeDasharray="4 4" label={{ value: '35% Extreme', fill: '#EF4444', fontSize: 10 }} />

              {/* Historical Realized Vol */}
              <Area
                type="monotone"
                dataKey="rolling_vol_20d"
                name="20-Day Rolling Realized Vol (%)"
                stroke="#10B981"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#volGradient)"
              />

              {/* Forecast GARCH */}
              <Line
                type="monotone"
                dataKey="forecast_garch"
                name="GARCH(1,1) Forecast (%)"
                stroke="#38BDF8"
                strokeWidth={2.5}
                strokeDasharray="5 5"
                dot={{ r: 4, fill: '#38BDF8' }}
              />

              {/* Forecast Baseline */}
              <Line
                type="monotone"
                dataKey="forecast_baseline"
                name="Baseline Forecast (%)"
                stroke="#F59E0B"
                strokeWidth={2}
                strokeDasharray="3 3"
                dot={{ r: 3, fill: '#F59E0B' }}
              />
            </AreaChart>
          ) : (
            <LineChart data={filteredData} margin={{ top: 20, right: 30, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.6} />
              <XAxis dataKey="date" stroke="#94A3B8" tick={{ fontSize: 11 }} tickMargin={8} />
              <YAxis 
                stroke="#94A3B8" 
                tick={{ fontSize: 11 }} 
                domain={['auto', 'auto']}
                tickFormatter={(val) => `$${val.toLocaleString()}`}
              />
              <Tooltip content={<CustomPriceTooltip />} />
              <Legend verticalAlign="top" height={36} iconType="circle" />

              <Line
                type="monotone"
                dataKey="close"
                name="Closing Price ($)"
                stroke="#6366F1"
                strokeWidth={2.5}
                dot={false}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function CustomVolTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip">
        <p className="tooltip-date">{label}</p>
        {payload.map((entry, idx) => (
          entry.value != null && (
            <div key={`tooltip-${idx}`} className="tooltip-row" style={{ color: entry.color }}>
              <span className="tooltip-dot" style={{ backgroundColor: entry.color }} />
              <span className="tooltip-name">{entry.name}:</span>
              <span className="tooltip-val">{Number(entry.value).toFixed(2)}%</span>
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
      <div className="custom-tooltip">
        <p className="tooltip-date">{label}</p>
        <div className="tooltip-row" style={{ color: '#818CF8' }}>
          <span className="tooltip-name">Close:</span>
          <span className="tooltip-val">${data.close?.toFixed(2)}</span>
        </div>
        {data.log_return != null && (
          <div className="tooltip-row" style={{ color: data.log_return >= 0 ? '#10B981' : '#EF4444' }}>
            <span className="tooltip-name">Log Return:</span>
            <span className="tooltip-val">{(data.log_return * 100).toFixed(2)}%</span>
          </div>
        )}
        {data.rolling_vol_20d != null && (
          <div className="tooltip-row" style={{ color: '#F59E0B' }}>
            <span className="tooltip-name">20d Vol:</span>
            <span className="tooltip-val">{data.rolling_vol_20d.toFixed(2)}%</span>
          </div>
        )}
      </div>
    );
  }
  return null;
}
