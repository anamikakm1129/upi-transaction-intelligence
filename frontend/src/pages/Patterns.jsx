import React, { useState, useEffect } from 'react';
import { api, formatINR, formatNumber } from '../services/api';
import { LineAreaTrendChart, BarHourlyChart, CategoryDistributionBars } from '../components/SvgCharts';
import { LoadingState } from '../components/LoadingState';

export function Patterns({ dateRange, refreshKey, onOpenUpload }) {
  const [loading, setLoading] = useState(true);
  const [dailyData, setDailyData] = useState([]);
  const [hourlyData, setHourlyData] = useState([]);
  const [categoryData, setCategoryData] = useState([]);
  const [patternInsights, setPatternInsights] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function loadPatterns() {
      setLoading(true);
      try {
        const params = {};
        if (dateRange.startDate) params.start_date = dateRange.startDate;
        if (dateRange.endDate) params.end_date = dateRange.endDate;

        const [daily, hourly, cats, insights] = await Promise.all([
          api.getDailyTrends(params),
          api.getHourlyTrends(params),
          api.getCategoryDistribution(params),
          api.getPatterns()
        ]);

        if (isMounted) {
          setDailyData(daily || []);
          setHourlyData(hourly || []);
          setCategoryData(cats || []);
          setPatternInsights(insights);
        }
      } catch (err) {
        console.error('Failed to load patterns:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadPatterns();
    return () => { isMounted = false; };
  }, [dateRange, refreshKey]);

  if (loading && !patternInsights) {
    return <LoadingState message="Calculating diurnal and category patterns..." />;
  }

  const hasData = Boolean(patternInsights && patternInsights.overall_count > 0);

  return (
    <div>
      {/* Empty State Hero Banner when no real dataset exists */}
      {!hasData && (
        <div className="empty-hero-card">
          <div className="empty-hero-content">
            <div className="empty-hero-icon">📈</div>
            <div>
              <h2 className="empty-hero-title">No transaction patterns available</h2>
              <p className="empty-hero-desc">
                Upload your transaction CSV to compute 24-hour diurnal volume cycles, hourly ticket sizes, category distributions, and deterministic SQL findings.
              </p>
              <div className="empty-hero-badges">
                <span className="empty-pill-badge">🕒 24-Hour Diurnal Cycles</span>
                <span className="empty-pill-badge">📊 Category Share Analysis</span>
                <span className="empty-pill-badge">📐 Deterministic Probability</span>
              </div>
            </div>
          </div>
          {onOpenUpload && (
            <button className="btn btn-primary" onClick={onOpenUpload}>
              <span>📤 Upload Transaction CSV</span>
            </button>
          )}
        </div>
      )}

      {/* Factual Narrative Insights Section */}
      <div className="card-white" style={{ background: '#FAF6F2', border: '1px solid rgba(185, 160, 245, 0.4)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 }}>
          <span style={{ fontSize: 24 }}>💡</span>
          <div>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-main)' }}>
              Analytical Pattern Findings
            </h3>
            <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 2 }}>
              Deterministic insights computed directly from SQL window functions, probability curves, and dataset aggregations.
            </p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14, marginTop: 14 }}>
          {patternInsights?.insights_narrative && patternInsights.insights_narrative.map((insight, idx) => (
            <div
              key={idx}
              style={{
                background: '#FFFFFF',
                borderRadius: 12,
                padding: '16px 18px',
                border: '1px solid var(--border-main)',
                fontSize: 14.5,
                lineHeight: 1.6,
                color: 'var(--text-main)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8, color: 'var(--primary)', fontWeight: 700, fontSize: 12.5, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                <span>●</span> Insight #{idx + 1}
              </div>
              {insight}
            </div>
          ))}
        </div>
      </div>

      {/* Hourly Diurnal Patterns & Average Ticket by Hour */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 }}>
        <div className="card-white" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <div className="card-title-group">
              <h3 className="card-title">Hourly Transaction Volume</h3>
              <p className="card-subtitle">Diurnal curve highlighting consumer payment cycles across 24 hours</p>
            </div>
          </div>
          <BarHourlyChart data={hourlyData} height={220} />
        </div>

        <div className="card-white" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <div className="card-title-group">
              <h3 className="card-title">Average Transaction Amount by Hour</h3>
              <p className="card-subtitle">Ticket size distribution (₹) reflecting evening dining & e-commerce</p>
            </div>
          </div>
          <LineAreaTrendChart
            data={hourlyData.map(h => ({ tx_date: `${h.tx_hour}:00`, avg_amount: h.avg_amount }))}
            metricKey="avg_amount"
            label="Avg Ticket"
            isCurrency
            height={220}
          />
        </div>
      </div>

      {/* Daily Volume & Value Patterns */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: 24 }}>
        <div className="card-white">
          <div className="card-header">
            <div className="card-title-group">
              <h3 className="card-title">Daily Transaction Value Trend</h3>
              <p className="card-subtitle">Total settlement volume (₹) over consecutive operational days</p>
            </div>
          </div>
          <LineAreaTrendChart
            data={dailyData}
            metricKey="tx_value"
            label="Total Value"
            isCurrency
            height={240}
          />
        </div>

        <div className="card-white">
          <div className="card-header">
            <div className="card-title-group">
              <h3 className="card-title">Category Distribution</h3>
              <p className="card-subtitle">Share percentage by merchant category</p>
            </div>
          </div>
          <CategoryDistributionBars data={categoryData} />
        </div>
      </div>
    </div>
  );
}

