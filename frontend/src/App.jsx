import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import AssetSelector from './components/AssetSelector';
import RiskBadge from './components/RiskBadge';
import ForecastPanel from './components/ForecastPanel';
import VolatilityChart from './components/VolatilityChart';
import ModelComparisonChart from './components/ModelComparisonChart';
import BacktestSummary from './components/BacktestSummary';
import MethodologyModal from './components/MethodologyModal';
import LoadingState from './components/LoadingState';
import ErrorState from './components/ErrorState';
import EmptyState from './components/EmptyState';
import { fetchForecast, fetchHistory, fetchBacktest } from './api';
import './App.css';

export default function App() {
  const [symbol, setSymbol] = useState('SPY');
  const [horizon, setHorizon] = useState(5);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [forecastData, setForecastData] = useState(null);
  const [historyData, setHistoryData] = useState(null);
  const [backtestData, setBacktestData] = useState(null);
  const [isMethodologyOpen, setIsMethodologyOpen] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(() => new Date());

  const loadData = useCallback(async (targetSymbol, targetHorizon) => {
    setLoading(true);
    setError(null);
    try {
      const [forecastRes, historyRes, backtestRes] = await Promise.all([
        fetchForecast(targetSymbol, targetHorizon),
        fetchHistory(targetSymbol, 90),
        fetchBacktest(targetSymbol)
      ]);

      setForecastData(forecastRes);
      setHistoryData(historyRes);
      setBacktestData(backtestRes);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Failed to load volatility data:', err);
      setError(err.message || 'Error communicating with VolGuard forecasting service');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData(symbol, horizon);
  }, [symbol, horizon, loadData]);

  const handleSelectAsset = (newSymbol) => {
    setSymbol(newSymbol);
  };

  const handleSelectHorizon = (newHorizon) => {
    setHorizon(newHorizon);
  };

  const handleRefresh = () => {
    loadData(symbol, horizon);
  };

  const isSimulated = forecastData?.isSimulated ?? true;

  return (
    <div className="app-container">
      {/* Header */}
      <Header
        symbol={symbol}
        isSimulated={isSimulated}
        onRefresh={handleRefresh}
        loading={loading}
        onOpenMethodology={() => setIsMethodologyOpen(true)}
        lastUpdated={lastUpdated}
      />

      <main className="main-content">
        {/* Asset & Horizon Selector Bar */}
        <AssetSelector
          currentSymbol={symbol}
          currentHorizon={horizon}
          onSelectAsset={handleSelectAsset}
          onSelectHorizon={handleSelectHorizon}
          loading={loading}
        />

        {/* Content Body with Conditionals */}
        {loading && !forecastData ? (
          <LoadingState symbol={symbol} />
        ) : error ? (
          <ErrorState
            error={error}
            onRetry={handleRefresh}
            onSwitchToDemo={() => loadData(symbol, horizon)}
          />
        ) : !forecastData ? (
          <EmptyState symbol={symbol} onReset={(s) => setSymbol(s)} />
        ) : (
          <div className="dashboard-grid">
            {/* Top Row: Risk Warning Badge & Overview */}
            <div className="dashboard-row">
              <RiskBadge forecastData={forecastData} />
            </div>

            {/* Second Row: 3-Column Metric Forecast Cards */}
            <div className="dashboard-row">
              <ForecastPanel 
                forecastData={forecastData} 
                onOpenMethodology={() => setIsMethodologyOpen(true)} 
              />
            </div>

            {/* Third Row: Main Volatility & Price Interactive Chart */}
            <div className="dashboard-row">
              <VolatilityChart
                historyData={historyData}
                symbol={symbol}
                forecastData={forecastData}
              />
            </div>

            {/* Fourth Row: Walk-Forward Model Comparison Chart */}
            <div className="dashboard-row">
              <ModelComparisonChart
                backtestData={backtestData}
                symbol={symbol}
              />
            </div>

            {/* Fifth Row: Quantitative Backtest Benchmark Summary */}
            <div className="dashboard-row">
              <BacktestSummary
                backtestData={backtestData}
                symbol={symbol}
              />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="footer-container" role="contentinfo">
        <div className="footer-content label-uppercase">
          <span className="footer-brand">VOLGUARD AI</span>
          <span className="footer-dot" aria-hidden="true">•</span>
          <span>SOVEREIGN RISK MATRIX // MACRO INTELLIGENCE</span>
          <span className="footer-dot" aria-hidden="true">•</span>
          <span>TARGET: 5-DAY ANNUALIZED REALIZED VOLATILITY (σ 5D)</span>
          <span className="footer-dot" aria-hidden="true">•</span>
          <span className="footer-spec">ZERO-LOOKAHEAD GARCH(1,1) WALKING MATRIX</span>
        </div>
      </footer>

      {/* Methodology & Formulas Modal */}
      <MethodologyModal
        isOpen={isMethodologyOpen}
        onClose={() => setIsMethodologyOpen(false)}
      />
    </div>
  );
}
