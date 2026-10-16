import React, { useState, useEffect, useRef } from 'react';
import { api, formatNumber, formatDateTime } from '../services/api';
import { DataTable } from '../components/DataTable';
import { LoadingState } from '../components/LoadingState';

export function DataQuality({ refreshKey, showToast, onOpenUpload }) {
  const [summary, setSummary] = useState(null);
  const [quarantined, setQuarantined] = useState([]);
  const [qTotal, setQTotal] = useState(0);
  const [qPage, setQPage] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    async function fetchDQData() {
      setLoading(true);
      try {
        const [sumRes, qRes] = await Promise.all([
          api.getDataQualitySummary(),
          api.getQuarantinedRecords({ page: qPage, page_size: 10 })
        ]);
        if (isMounted) {
          setSummary(sumRes);
          setQuarantined(qRes.data || []);
          setQTotal(qRes.total || 0);
        }
      } catch (err) {
        console.error('Failed to load DQ data:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    fetchDQData();
    return () => { isMounted = false; };
  }, [qPage, refreshKey]);

  if (loading && !summary) {
    return <LoadingState message="Auditing dataset health and quarantine logs..." />;
  }

  const hasData = Boolean(summary && summary.total_records > 0);

  const quarantinedColumns = [
    { key: 'raw_id', label: 'Row #', render: (val) => <span className="mono">#{val}</span> },
    { key: 'transaction_id', label: 'Transaction ID', render: (val) => val ? <span className="mono" style={{ fontWeight: 600 }}>{val}</span> : <span style={{ color: 'var(--text-light)' }}>Missing</span> },
    { key: 'customer_id', label: 'Customer', render: (val) => val ? <span className="mono" style={{ fontSize: 13.5 }}>{val}</span> : <span style={{ color: 'var(--text-light)' }}>Missing</span> },
    { key: 'amount', label: 'Amount', render: (val) => val !== null && val !== undefined ? <span className="mono">₹{val}</span> : <span style={{ color: 'var(--text-light)' }}>Invalid</span> },
    { key: 'quarantine_reason', label: 'Quarantine Reason', render: (val) => <span style={{ color: 'var(--status-failed)', fontWeight: 600, fontSize: 13.5 }}>{val}</span> },
    { key: 'quarantined_at', label: 'Quarantined At', render: (val) => <span style={{ fontSize: 13 }}>{formatDateTime(val)}</span> }
  ];

  const missingValuesList = summary?.missing_values_json && hasData
    ? Object.entries(summary.missing_values_json)
    : [];

  return (
    <div>
      {/* Empty State Banner if no data uploaded */}
      {!hasData && (
        <div className="empty-hero-card">
          <div className="empty-hero-content">
            <div className="empty-hero-icon">🛡️</div>
            <div>
              <h2 className="empty-hero-title">Data quality analysis has not yet run</h2>
              <p className="empty-hero-desc">
                Upload your transaction CSV to audit column completeness, isolate duplicates to quarantine storage, and calculate data hygiene ratios.
              </p>
              <div className="empty-hero-badges">
                <span className="empty-pill-badge">🔍 Automated Schema Validation</span>
                <span className="empty-pill-badge">🚫 Duplicate ID Isolation</span>
                <span className="empty-pill-badge">📁 Immutable Raw Ingestion</span>
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

      {/* Upload and Ingestion Actions */}
      <div className="card-white" style={{ background: '#FAF6F2', border: '1px solid rgba(185, 160, 245, 0.4)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-main)' }}>
              Dataset Ingestion & Quality Governance
            </h3>
            <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 4 }}>
              Upload any real UPI transaction CSV dataset with pre-validation schema inspection and quarantine segregation.
            </p>
          </div>

          <div style={{ display: 'flex', gap: 10 }}>
            {onOpenUpload && (
              <button
                className="btn btn-primary"
                onClick={onOpenUpload}
              >
                📤 Upload Transaction CSV
              </button>
            )}
          </div>
        </div>

        {/* Deduplication & Governance Policy Pill */}
        <div style={{ marginTop: 14, paddingTop: 12, borderTop: '1px solid #ECE8E5', fontSize: 13.5, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 8, lineHeight: 1.5 }}>
          <span>🛡️</span>
          <span>
            <strong>Data Integrity Policy:</strong> Raw input records are stored immutably in <code>raw_transactions</code>. Duplicates and corrupted rows are segregated to <code>quarantined_transactions</code> without silent mutation.
          </span>
        </div>
      </div>

      {/* Primary Data Quality Metric Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-top">
            <span className="kpi-label">Total Ingested Records</span>
            <div className="kpi-icon-pill">📄</div>
          </div>
          <div className="kpi-value mono">{hasData ? formatNumber(summary.total_records) : '—'}</div>
          <div className="kpi-bottom">
            <span>Source: {hasData && summary?.source_filename ? summary.source_filename : 'None (Awaiting Upload)'}</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-top">
            <span className="kpi-label">Valid Cleaned Records</span>
            <div className="kpi-icon-pill" style={{ color: 'var(--status-success)' }}>✓</div>
          </div>
          <div className="kpi-value mono" style={{ color: hasData ? 'var(--status-success)' : 'inherit' }}>
            {hasData ? formatNumber(summary.valid_records) : '—'}
          </div>
          <div className="kpi-bottom">
            <span>
              {hasData && summary?.total_records
                ? `${Math.round((summary.valid_records / summary.total_records) * 100)}% compliance rate`
                : 'Awaiting uploaded dataset'}
            </span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-top">
            <span className="kpi-label">Duplicate Records</span>
            <div className="kpi-icon-pill" style={{ color: 'var(--status-failed)' }}>≠</div>
          </div>
          <div className="kpi-value mono" style={{ color: hasData && summary?.duplicate_records > 0 ? 'var(--status-failed)' : 'inherit' }}>
            {hasData ? formatNumber(summary.duplicate_records) : '—'}
          </div>
          <div className="kpi-bottom">
            <span>{hasData ? 'Quarantined & preserved for audit' : 'Awaiting uploaded dataset'}</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-top">
            <span className="kpi-label">Dataset Health Status</span>
            <div className="kpi-icon-pill">🛡️</div>
          </div>
          <div style={{ marginTop: 4 }}>
            {hasData ? (
              <span
                className={`badge ${
                  summary?.status === 'HEALTHY'
                    ? 'badge-success'
                    : summary?.status === 'WARNING'
                    ? 'badge-pending'
                    : 'badge-failed'
                }`}
                style={{ fontSize: 13, padding: '6px 12px' }}
              >
                ● {summary?.status || 'HEALTHY'}
              </span>
            ) : (
              <span
                className="badge"
                style={{ fontSize: 13, padding: '6px 12px', background: '#ECE8E5', color: '#77736F' }}
              >
                ● NOT ANALYZED
              </span>
            )}
          </div>
          <div className="kpi-bottom" style={{ marginTop: 8 }}>
            <span>Last audited: {hasData && summary?.run_timestamp ? formatDateTime(summary.run_timestamp) : 'Never'}</span>
          </div>
        </div>
      </div>

      {/* Missing Values Breakdown & Validation Counters */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 }}>
        <div className="card-white" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <div className="card-title-group">
              <h3 className="card-title">Column-Wise Missing Field Audit</h3>
              <p className="card-subtitle">Count of null/empty values discovered per attribute</p>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {hasData && missingValuesList.length > 0 ? (
              missingValuesList.map(([col, count]) => (
                <div key={col} className="detail-row">
                  <span className="detail-label mono">{col}</span>
                  <span className="detail-value mono" style={{ color: count > 0 ? 'var(--status-failed)' : 'var(--text-muted)' }}>
                    {count > 0 ? `${count} missing` : '0 missing (100% complete)'}
                  </span>
                </div>
              ))
            ) : (
              <div style={{ color: 'var(--text-muted)', fontSize: 14.5, padding: '12px 0', lineHeight: 1.5 }}>
                {hasData ? 'No missing values found across all columns.' : 'No dataset has been uploaded. Column completeness audit will execute automatically upon CSV ingestion.'}
              </div>
            )}
          </div>
        </div>

        <div className="card-white" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <div className="card-title-group">
              <h3 className="card-title">Integrity Violation Breakdown</h3>
              <p className="card-subtitle">Specific reasons triggering quarantine segregation</p>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div className="detail-row">
              <span className="detail-label">Invalid Non-Positive Amounts</span>
              <span className="detail-value mono" style={{ color: hasData && summary?.invalid_amounts > 0 ? 'var(--status-failed)' : 'inherit' }}>
                {hasData ? summary?.invalid_amounts || 0 : '—'}
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Corrupted / Unparseable Timestamps</span>
              <span className="detail-value mono" style={{ color: hasData && summary?.invalid_timestamps > 0 ? 'var(--status-failed)' : 'inherit' }}>
                {hasData ? summary?.invalid_timestamps || 0 : '—'}
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Duplicate Transaction IDs</span>
              <span className="detail-value mono" style={{ color: hasData && summary?.duplicate_records > 0 ? 'var(--status-failed)' : 'inherit' }}>
                {hasData ? summary?.duplicate_records || 0 : '—'}
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Total Quarantined Rows</span>
              <span className="detail-value mono" style={{ fontWeight: 700 }}>
                {hasData ? formatNumber(summary?.invalid_records || 0) : '—'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Quarantined Records Table */}
      <div className="card-white">
        <div className="card-header">
          <div className="card-title-group">
            <h3 className="card-title">Quarantined Records Log</h3>
            <p className="card-subtitle">
              Audit log of all isolated records that failed data quality validation checks
            </p>
          </div>
          <span style={{ fontSize: 14, color: 'var(--text-muted)' }}>
            Quarantine Total: <strong className="mono">{hasData ? formatNumber(qTotal) : '—'}</strong>
          </span>
        </div>

        <DataTable
          columns={quarantinedColumns}
          data={quarantined}
          total={qTotal}
          page={qPage}
          pageSize={10}
          onPageChange={(p) => setQPage(p)}
          isLoading={loading}
          emptyTitle="Quarantine is empty"
          emptyDescription={hasData ? "Zero invalid or duplicate transactions encountered." : "No dataset has been audited yet. Invalid and duplicate records are isolated automatically during CSV ingestion."}
          emptyAction={!hasData && onOpenUpload && (
            <button className="btn btn-primary" onClick={onOpenUpload}>
              <span>📤 Upload Transaction CSV</span>
            </button>
          )}
        />
      </div>
    </div>
  );
}

