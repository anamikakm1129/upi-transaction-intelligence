import React, { useState, useEffect } from 'react';
import { api, formatINR, formatNumber, formatDateTime } from '../services/api';
import { DataTable } from '../components/DataTable';
import { SeverityBadge } from '../components/StatusBadge';
import { Drawer } from '../components/Drawer';

const RULES = [
  'High-Value Transaction',
  'Velocity Spike',
  'Unusual Customer Activity (Z-Score)',
  'Duplicate Record',
  'Invalid Entry'
];

export function Anomalies({ refreshKey, showToast, onOpenUpload }) {
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [ruleFilter, setRuleFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  // Settings Panel Drawer
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [configList, setConfigList] = useState([]);
  const [configInputs, setConfigInputs] = useState({
    high_value_threshold: 50000,
    velocity_window_minutes: 5,
    velocity_count_threshold: 3,
    customer_zscore_threshold: 2.5
  });
  const [savingConfig, setSavingConfig] = useState(false);

  // Detail Modal
  const [selectedFinding, setSelectedFinding] = useState(null);

  // Load anomalies
  useEffect(() => {
    let isMounted = true;
    async function fetchAnomalies() {
      setLoading(true);
      try {
        const params = {
          page,
          page_size: pageSize
        };
        if (ruleFilter) params.rule_name = ruleFilter;
        if (severityFilter) params.severity = severityFilter;
        if (search) params.search = search;

        const res = await api.getAnomalies(params);
        if (isMounted) {
          setData(res.data || []);
          setTotal(res.total || 0);
        }
      } catch (err) {
        console.error('Failed to load anomalies:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    fetchAnomalies();
    return () => { isMounted = false; };
  }, [page, pageSize, ruleFilter, severityFilter, search, refreshKey]);

  // Load config
  useEffect(() => {
    let isMounted = true;
    async function fetchConfig() {
      try {
        const cfg = await api.getAnomalyConfig();
        if (isMounted) {
          setConfigList(cfg);
          const map = {};
          cfg.forEach(c => { map[c.config_key] = c.config_value; });
          setConfigInputs(prev => ({ ...prev, ...map }));
        }
      } catch (err) {
        console.error('Failed to load anomaly config:', err);
      }
    }
    fetchConfig();
    return () => { isMounted = false; };
  }, [refreshKey]);

  const handleSaveConfig = async () => {
    setSavingConfig(true);
    try {
      await api.updateAnomalyConfig(configInputs);
      if (showToast) showToast('Threshold parameters updated successfully. Re-running analysis...', 'success');
      // Re-run processing to apply new thresholds
      await api.runProcessing();
      setIsConfigOpen(false);
      window.location.reload();
    } catch (err) {
      console.error('Failed to update config:', err);
      if (showToast) showToast(`Failed to update config: ${err.message}`, 'error');
    } finally {
      setSavingConfig(false);
    }
  };

  const columns = [
    {
      key: 'severity',
      label: 'Severity',
      render: (val) => <SeverityBadge severity={val} />
    },
    {
      key: 'rule_name',
      label: 'Rule Triggered',
      render: (val) => <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{val}</span>
    },
    {
      key: 'reason',
      label: 'Detection Reason',
      render: (val) => <span style={{ fontSize: 14, color: 'var(--text-main)' }}>{val}</span>
    },
    {
      key: 'transaction_id',
      label: 'Transaction ID',
      render: (val) => val ? <span className="mono" style={{ color: 'var(--primary)', fontWeight: 600 }}>{val}</span> : <span style={{ color: 'var(--text-light)' }}>N/A</span>
    },
    {
      key: 'customer_id',
      label: 'Customer VPA',
      render: (val) => val ? <span className="mono" style={{ fontSize: 13.5 }}>{val}</span> : <span style={{ color: 'var(--text-light)' }}>—</span>
    },
    {
      key: 'detected_at',
      label: 'Detected At',
      render: (val) => <span style={{ fontSize: 13 }}>{formatDateTime(val)}</span>
    }
  ];

  const hasFilters = Boolean(search || ruleFilter || severityFilter);
  const isAnalysisNotRun = total === 0 && !hasFilters;

  return (
    <div>
      {/* Empty State Banner if analysis not yet run */}
      {isAnalysisNotRun && (
        <div className="empty-hero-card">
          <div className="empty-hero-content">
            <div className="empty-hero-icon">⚠️</div>
            <div>
              <h2 className="empty-hero-title">Analysis has not yet run</h2>
              <p className="empty-hero-desc">
                Upload your transaction CSV to evaluate anomaly detection rules, flag velocity spikes, isolate high-value outliers, and track z-score deviations.
              </p>
              <div className="empty-hero-badges">
                <span className="empty-pill-badge">⚡ Velocity Spikes</span>
                <span className="empty-pill-badge">💰 High-Value Outliers</span>
                <span className="empty-pill-badge">📐 Z-Score Activity Deviation</span>
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

      {/* Disclaimer Banner */}
      <div style={{ background: '#FAF6F2', border: '1px solid #ECE8E5', padding: '14px 20px', borderRadius: 12, marginBottom: 20, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 14, color: 'var(--text-muted)', lineHeight: 1.5 }}>
          <span style={{ fontSize: 20 }}>ℹ️</span>
          <span>
            <strong>Governance Notice:</strong> A flagged record indicates a rule-based statistical anomaly for manual or automated review. It does not constitute proof of fraudulent intent.
          </span>
        </div>
        <button
          className="btn btn-secondary btn-sm"
          onClick={() => setIsConfigOpen(true)}
        >
          ⚙️ Configure Thresholds
        </button>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            className="search-input"
            placeholder="Search anomalies by transaction, customer, or reason..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>

        <select
          className="select-input"
          value={ruleFilter}
          onChange={(e) => { setRuleFilter(e.target.value); setPage(1); }}
        >
          <option value="">All Rules</option>
          {RULES.map(r => <option key={r} value={r}>{r}</option>)}
        </select>

        <select
          className="select-input"
          value={severityFilter}
          onChange={(e) => { setSeverityFilter(e.target.value); setPage(1); }}
        >
          <option value="">All Severities</option>
          <option value="HIGH">High Severity</option>
          <option value="MEDIUM">Medium Severity</option>
          <option value="LOW">Low Severity</option>
        </select>

        {hasFilters && (
          <button className="btn btn-secondary btn-sm" onClick={() => { setSearch(''); setRuleFilter(''); setSeverityFilter(''); setPage(1); }}>
            Clear Filters
          </button>
        )}
      </div>

      {/* Main Table */}
      <div className="card-white">
        <div className="card-header">
          <div className="card-title-group">
            <h3 className="card-title">Rule-Based Anomaly Findings</h3>
            <p className="card-subtitle">
              {isAnalysisNotRun ? (
                <span>Analysis has not yet run. Upload a dataset to begin anomaly review.</span>
              ) : (
                <span>Showing <span className="mono">{formatNumber(total)}</span> review candidates flagged by deterministic rules.</span>
              )}
            </p>
          </div>
        </div>

        <DataTable
          columns={columns}
          data={data}
          total={total}
          page={page}
          pageSize={pageSize}
          onPageChange={(p) => setPage(p)}
          onRowClick={(item) => setSelectedFinding(item)}
          isLoading={loading}
          emptyTitle={hasFilters ? "No matching anomalies found" : "Analysis has not yet run"}
          emptyDescription={hasFilters ? "Try adjusting your filter or search criteria." : "Upload your transaction CSV to evaluate anomaly detection rules and identify review candidates."}
          emptyAction={isAnalysisNotRun && onOpenUpload && (
            <button className="btn btn-primary" onClick={onOpenUpload}>
              <span>📤 Upload Transaction CSV</span>
            </button>
          )}
        />
      </div>

      {/* Detail Drawer */}
      <Drawer
        isOpen={Boolean(selectedFinding)}
        onClose={() => setSelectedFinding(null)}
        title="Anomaly Finding Details"
        subtitle={selectedFinding?.rule_name}
      >
        {selectedFinding && (
          <div>
            <div style={{ marginBottom: 18, padding: 14, borderRadius: 8, backgroundColor: '#FAF6F2', border: '1px solid #ECE8E5' }}>
              <div style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Rule Description & Rationale
              </div>
              <div style={{ fontSize: 14.5, marginTop: 6, color: 'var(--text-main)', lineHeight: 1.5 }}>
                {selectedFinding.reason}
              </div>
            </div>

            <div className="detail-row">
              <span className="detail-label">Severity Level</span>
              <span className="detail-value"><SeverityBadge severity={selectedFinding.severity} /></span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Associated Transaction</span>
              <span className="detail-value mono">{selectedFinding.transaction_id || 'N/A (Pre-quarantine)'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Customer VPA</span>
              <span className="detail-value mono">{selectedFinding.customer_id || 'N/A'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Merchant VPA</span>
              <span className="detail-value mono">{selectedFinding.merchant_id || 'N/A'}</span>
            </div>
            {selectedFinding.metric_value !== null && (
              <div className="detail-row">
                <span className="detail-label">Observed Metric Value</span>
                <span className="detail-value mono">{selectedFinding.metric_value}</span>
              </div>
            )}
            {selectedFinding.threshold_value !== null && (
              <div className="detail-row">
                <span className="detail-label">Configured Threshold</span>
                <span className="detail-value mono">{selectedFinding.threshold_value}</span>
              </div>
            )}
            <div className="detail-row">
              <span className="detail-label">Detection Timestamp</span>
              <span className="detail-value">{formatDateTime(selectedFinding.detected_at)}</span>
            </div>
            {selectedFinding.details && (
              <div className="detail-row">
                <span className="detail-label">Context Details</span>
                <span className="detail-value" style={{ fontSize: 13.5 }}>{selectedFinding.details}</span>
              </div>
            )}
          </div>
        )}
      </Drawer>

      {/* Config Drawer */}
      <Drawer
        isOpen={isConfigOpen}
        onClose={() => setIsConfigOpen(false)}
        title="Configure Anomaly Thresholds"
        subtitle="Fine-tune mathematical and statistical rule parameters"
        footer={(
          <>
            <button className="btn btn-secondary" onClick={() => setIsConfigOpen(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleSaveConfig} disabled={savingConfig}>
              {savingConfig ? 'Saving & Recomputing...' : 'Save & Re-evaluate'}
            </button>
          </>
        )}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div>
            <label style={{ fontSize: 14.5, fontWeight: 600, color: 'var(--text-main)', display: 'block', marginBottom: 6 }}>
              High-Value Amount Threshold (₹)
            </label>
            <input
              type="number"
              className="search-input"
              style={{ paddingLeft: 12 }}
              value={configInputs.high_value_threshold}
              onChange={(e) => setConfigInputs({ ...configInputs, high_value_threshold: Number(e.target.value) })}
            />
            <span style={{ fontSize: 12.5, color: 'var(--text-muted)', display: 'block', marginTop: 4 }}>
              Transactions exceeding this amount will be flagged for review (Default: ₹50,000).
            </span>
          </div>

          <div>
            <label style={{ fontSize: 14.5, fontWeight: 600, color: 'var(--text-main)', display: 'block', marginBottom: 6 }}>
              Customer Velocity Window (Minutes)
            </label>
            <input
              type="number"
              className="search-input"
              style={{ paddingLeft: 12 }}
              value={configInputs.velocity_window_minutes}
              onChange={(e) => setConfigInputs({ ...configInputs, velocity_window_minutes: Number(e.target.value) })}
            />
            <span style={{ fontSize: 12.5, color: 'var(--text-muted)', display: 'block', marginTop: 4 }}>
              Rolling time window for rapid-fire transaction detection (Default: 5 mins).
            </span>
          </div>

          <div>
            <label style={{ fontSize: 14.5, fontWeight: 600, color: 'var(--text-main)', display: 'block', marginBottom: 6 }}>
              Velocity Burst Count Threshold
            </label>
            <input
              type="number"
              className="search-input"
              style={{ paddingLeft: 12 }}
              value={configInputs.velocity_count_threshold}
              onChange={(e) => setConfigInputs({ ...configInputs, velocity_count_threshold: Number(e.target.value) })}
            />
            <span style={{ fontSize: 12.5, color: 'var(--text-muted)', display: 'block', marginTop: 4 }}>
              Number of transactions by same customer within the window to trigger alert (Default: 3).
            </span>
          </div>

          <div>
            <label style={{ fontSize: 14.5, fontWeight: 600, color: 'var(--text-main)', display: 'block', marginBottom: 6 }}>
              Customer Spend Z-Score Threshold (Standard Deviations)
            </label>
            <input
              type="number"
              step="0.1"
              className="search-input"
              style={{ paddingLeft: 12 }}
              value={configInputs.customer_zscore_threshold}
              onChange={(e) => setConfigInputs({ ...configInputs, customer_zscore_threshold: Number(e.target.value) })}
            />
            <span style={{ fontSize: 12.5, color: 'var(--text-muted)', display: 'block', marginTop: 4 }}>
              Standard deviations above customer personal mean to flag (Default: 2.5). Formula: Z = (X - μ) / σ.
            </span>
          </div>
        </div>
      </Drawer>
    </div>
  );
}

