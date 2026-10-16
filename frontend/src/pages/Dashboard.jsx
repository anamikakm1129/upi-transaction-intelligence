import React, { useState, useEffect } from 'react';
import { api, formatINR, formatNumber, formatDateTime } from '../services/api';
import { KpiCard } from '../components/KpiCard';
import { LineAreaTrendChart, BarHourlyChart, CategoryDistributionBars } from '../components/SvgCharts';
import { DataTable } from '../components/DataTable';
import { StatusBadge, AnomalyBadge } from '../components/StatusBadge';
import { LoadingState } from '../components/LoadingState';
import { Drawer } from '../components/Drawer';

export function Dashboard({ dateRange, refreshKey, onNavigateTo, onOpenUpload }) {
  const [loading, setLoading] = useState(true);
  const [kpis, setKpis] = useState(null);
  const [dailyTrends, setDailyTrends] = useState([]);
  const [hourlyTrends, setHourlyTrends] = useState([]);
  const [categories, setCategories] = useState([]);
  const [recentFlagged, setRecentFlagged] = useState([]);
  const [dqSummary, setDqSummary] = useState(null);
  const [patternInsights, setPatternInsights] = useState(null);
  const [activeMetric, setActiveMetric] = useState('tx_count');
  const [selectedTx, setSelectedTx] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function loadDashboardData() {
      setLoading(true);
      try {
        const params = {};
        if (dateRange.startDate) params.start_date = dateRange.startDate;
        if (dateRange.endDate) params.end_date = dateRange.endDate;

        const [kpiRes, dailyRes, hourlyRes, catRes, flaggedRes, dqRes, patRes] = await Promise.all([
          api.getDashboardSummary(params),
          api.getDailyTrends(params),
          api.getHourlyTrends(params),
          api.getCategoryDistribution(params),
          api.getTransactions({ anomaly_flag: 1, page: 1, page_size: 5 }),
          api.getDataQualitySummary(),
          api.getPatterns()
        ]);

        if (isMounted) {
          setKpis(kpiRes);
          setDailyTrends(dailyRes || []);
          setHourlyTrends(hourlyRes || []);
          setCategories(catRes || []);
          setRecentFlagged(flaggedRes.data || []);
          setDqSummary(dqRes);
          setPatternInsights(patRes);
        }
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadDashboardData();
    return () => { isMounted = false; };
  }, [dateRange, refreshKey]);

  if (loading && !kpis) {
    return <LoadingState message="Connecting to analytics engine..." />;
  }

  const hasData = Boolean(kpis && kpis.total_transactions > 0);

  const flaggedColumns = [
    { key: 'transaction_id', label: 'Transaction ID', sortable: false, render: (val) => <span className="mono" style={{ fontWeight: 600 }}>{val}</span> },
    { key: 'timestamp', label: 'Timestamp', render: (val) => formatDateTime(val) },
    { key: 'customer_id', label: 'Customer', render: (val) => <span className="mono" style={{ fontSize: 13.5 }}>{val}</span> },
    { key: 'amount', label: 'Amount', render: (val) => <strong className="mono">{formatINR(val)}</strong> },
    { key: 'category', label: 'Category' },
    { key: 'status', label: 'Status', render: (val) => <StatusBadge status={val} /> },
    { key: 'anomaly_flag', label: 'Review Flag', render: (val, row) => <AnomalyBadge flag={val} reason={row.anomaly_reason} /> }
  ];

  return (
    <div>
      {/* Empty State Hero Banner when no real dataset exists */}
      {!hasData && (
        <div className="empty-hero-card">
          <div className="empty-hero-content">
            <div className="empty-hero-icon">💳</div>
            <div>
              <h2 className="empty-hero-title">No transaction data available</h2>
              <p className="empty-hero-desc">
                Upload your transaction CSV to generate real-time analytics, customer profiles, merchant summaries, diurnal traffic curves, and rule-based anomaly reports.
              </p>
              <div className="empty-hero-badges">
                <span className="empty-pill-badge">📄 Format: CSV (.csv), UTF-8</span>
                <span className="empty-pill-badge">📦 Max Size: 25 MB</span>
                <span className="empty-pill-badge">🏷️ Schema: transaction_id, timestamp, customer_id, merchant_id, amount, category, status</span>
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'flex-start' }}>
            <button className="btn btn-primary" onClick={onOpenUpload}>
              <span>📤 Upload Transaction CSV</span>
            </button>
            <button
              className="btn btn-ghost btn-sm"
              style={{ fontSize: 13.5, paddingLeft: 0 }}
              onClick={() => onNavigateTo('data_quality')}
            >
              Open Data Quality & Ingestion →
            </button>
          </div>
        </div>
      )}

      {/* 4 Primary KPI Cards */}
      <div className="kpi-grid">
        <KpiCard
          title="Total Transactions"
          value={hasData ? formatNumber(kpis.total_transactions) : '—'}
          subtitle={hasData ? `${kpis.active_customers || 0} unique customers` : 'No transactions uploaded'}
          icon="💳"
          badgeText={hasData && kpis.success_count ? `${Math.round((kpis.success_count / (kpis.total_transactions || 1)) * 100)}% Success` : null}
        />
        <KpiCard
          title="Total Transaction Value"
          value={hasData ? formatINR(kpis.total_value) : '—'}
          subtitle={hasData ? "Processed volume in selected period" : "Awaiting uploaded dataset"}
          icon="₹"
          highlight={hasData}
        />
        <KpiCard
          title="Average Ticket Size"
          value={hasData ? formatINR(kpis.avg_amount) : '—'}
          subtitle={hasData ? "Mean amount per validated transaction" : "Awaiting uploaded dataset"}
          icon="📈"
        />
        <KpiCard
          title="Flagged for Review"
          value={hasData ? formatNumber(kpis.flagged_count) : '—'}
          subtitle={hasData ? `${kpis.flagged_rate_pct}% anomaly candidate rate` : "Analysis not yet run"}
          icon="⚠️"
          badgeText={hasData ? "Rule-Based" : null}
          badgeColor="#F5EEFE"
        />
      </div>

      {/* Main Grid: Trends & Hourly Activity */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 2fr) minmax(0, 1.2fr)', gap: 24, marginBottom: 24 }}>
        {/* Trend Chart Card */}
        <div className="card-white" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <div className="card-title-group">
              <h3 className="card-title">Transaction Trend Analysis</h3>
              <p className="card-subtitle">Daily throughput, volume growth, and rolling average</p>
            </div>
            {hasData && (
              <div style={{ display: 'flex', gap: 6, background: '#FAF6F2', padding: 3, borderRadius: 8 }}>
                <button
                  className={`btn btn-sm ${activeMetric === 'tx_count' ? 'btn-primary' : 'btn-ghost'}`}
                  onClick={() => setActiveMetric('tx_count')}
                >
                  Volume (Count)
                </button>
                <button
                  className={`btn btn-sm ${activeMetric === 'tx_value' ? 'btn-primary' : 'btn-ghost'}`}
                  onClick={() => setActiveMetric('tx_value')}
                >
                  Value (₹)
                </button>
              </div>
            )}
          </div>
          <LineAreaTrendChart
            data={dailyTrends}
            metricKey={activeMetric}
            label={activeMetric === 'tx_count' ? 'Transactions' : 'Amount'}
            isCurrency={activeMetric === 'tx_value'}
            height={220}
          />
        </div>

        {/* Hourly Diurnal Distribution Card */}
        <div className="card-white" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <div className="card-title-group">
              <h3 className="card-title">Diurnal Hourly Curve</h3>
              <p className="card-subtitle">
                {hasData && patternInsights?.peak_hour !== null
                  ? `24-hour traffic profile (Peak at ${patternInsights.peak_hour}:00)`
                  : '24-hour traffic distribution'}
              </p>
            </div>
          </div>
          <BarHourlyChart data={hourlyTrends} height={200} />
        </div>
      </div>

      {/* Secondary Grid: Category Distribution & Data Quality Snapshot */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.3fr) minmax(0, 1fr)', gap: 24, marginBottom: 24 }}>
        {/* Category Breakdown */}
        <div className="card-white" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <div className="card-title-group">
              <h3 className="card-title">Category Spend Breakdown</h3>
              <p className="card-subtitle">Volume contribution and total spend by merchant category</p>
            </div>
            {hasData && (
              <button className="btn btn-ghost btn-sm" onClick={() => onNavigateTo('patterns')}>
                View Patterns →
              </button>
            )}
          </div>
          <CategoryDistributionBars data={categories} />
        </div>

        {/* Data Quality Snapshot */}
        <div className="card-white" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <div className="card-title-group">
              <h3 className="card-title">Data Quality Snapshot</h3>
              <p className="card-subtitle">Input validation and quarantine audit status</p>
            </div>
            <span
              className={`badge ${
                dqSummary?.status === 'HEALTHY'
                  ? 'badge-success'
                  : dqSummary?.status === 'WARNING'
                  ? 'badge-pending'
                  : dqSummary?.status === 'CRITICAL'
                  ? 'badge-failed'
                  : 'badge-normal'
              }`}
            >
              {dqSummary?.status === 'NOT_ANALYZED' ? 'Not Yet Run' : (dqSummary?.status || 'Not Yet Run')}
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div className="detail-row">
              <span className="detail-label">Total Ingested Records</span>
              <span className="detail-value mono">{hasData ? formatNumber(dqSummary?.total_records) : '—'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Validated & Cleaned</span>
              <span className="detail-value mono" style={{ color: hasData ? 'var(--status-success)' : 'inherit' }}>
                {hasData ? formatNumber(dqSummary?.valid_records) : '—'}
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Quarantined (Duplicates / Invalid)</span>
              <span className="detail-value mono" style={{ color: dqSummary?.invalid_records > 0 ? 'var(--status-failed)' : 'var(--text-muted)' }}>
                {hasData ? formatNumber(dqSummary?.invalid_records) : '—'}
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Duplicate Transaction IDs</span>
              <span className="detail-value mono">{hasData ? formatNumber(dqSummary?.duplicate_records) : '—'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Active Anomaly Findings</span>
              <span className="detail-value mono" style={{ color: hasData ? 'var(--primary)' : 'inherit' }}>
                {hasData ? formatNumber(kpis?.flagged_count) : '—'}
              </span>
            </div>

            <div style={{ marginTop: 8 }}>
              <button
                className="btn btn-secondary btn-sm"
                style={{ width: '100%' }}
                onClick={() => onNavigateTo('data_quality')}
              >
                Inspect Data Quality & Ingestion →
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Flagged Transactions Table */}
      <div className="card-white">
        <div className="card-header">
          <div className="card-title-group">
            <h3 className="card-title">Recent Flagged Transactions</h3>
            <p className="card-subtitle">Latest rule-based anomaly review candidates</p>
          </div>
          {hasData && recentFlagged.length > 0 && (
            <button className="btn btn-ghost btn-sm" onClick={() => onNavigateTo('anomalies')}>
              View All Anomalies →
            </button>
          )}
        </div>

        <DataTable
          columns={flaggedColumns}
          data={recentFlagged}
          total={recentFlagged.length}
          page={1}
          pageSize={5}
          onPageChange={() => {}}
          onRowClick={(tx) => setSelectedTx(tx)}
          emptyTitle="No flagged transactions"
          emptyDescription={hasData ? "All recent transactions passed rule-based anomaly thresholds." : "No transaction data available. Upload a CSV to run anomaly detection."}
        />
      </div>

      {/* Transaction Detail Drawer */}
      <Drawer
        isOpen={Boolean(selectedTx)}
        onClose={() => setSelectedTx(null)}
        title="Transaction Intelligence Detail"
        subtitle={selectedTx?.transaction_id}
      >
        {selectedTx && (
          <div>
            <div style={{ marginBottom: 18, padding: 14, borderRadius: 8, backgroundColor: selectedTx.anomaly_flag ? '#F5EEFE' : '#F3F1EF', border: '1px solid #ECE8E5' }}>
              <div style={{ fontSize: 12.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: selectedTx.anomaly_flag ? '#8A63F4' : '#77736F' }}>
                Anomaly Evaluation
              </div>
              <div style={{ fontSize: 14.5, marginTop: 6, color: 'var(--text-main)', lineHeight: 1.5 }}>
                {selectedTx.anomaly_reason || 'Normal transaction. No rule thresholds exceeded.'}
              </div>
            </div>

            <div className="detail-row">
              <span className="detail-label">Transaction ID</span>
              <span className="detail-value mono">{selectedTx.transaction_id}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Timestamp</span>
              <span className="detail-value">{formatDateTime(selectedTx.timestamp)}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Amount</span>
              <span className="detail-value mono" style={{ fontSize: 18, color: 'var(--primary)', fontWeight: 700 }}>
                {formatINR(selectedTx.amount)}
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Status</span>
              <span className="detail-value"><StatusBadge status={selectedTx.status} /></span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Customer VPA</span>
              <span className="detail-value mono">{selectedTx.customer_id}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Merchant VPA</span>
              <span className="detail-value mono">{selectedTx.merchant_id}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Category</span>
              <span className="detail-value">{selectedTx.category}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Payment Method</span>
              <span className="detail-value">{selectedTx.payment_method || 'UPI-QR'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Bank Reference No (RRN)</span>
              <span className="detail-value mono">{selectedTx.bank_reference_number || 'N/A'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Device Type</span>
              <span className="detail-value">{selectedTx.device_type || 'Android'}</span>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}
