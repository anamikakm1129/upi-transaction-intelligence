import React, { useState } from 'react';
import { api } from '../services/api';

const REPORT_CARDS = [
  {
    id: 'daily',
    title: 'Daily Transaction Summary',
    description: 'Day-by-day throughput, aggregate spend, day-over-day growth rate, and 3-day rolling averages computed with SQL CTEs and window functions.',
    columns: ['tx_date', 'tx_count', 'tx_value', 'avg_amount', 'flagged_count', 'prev_day_count', 'dod_growth_pct', 'rolling_3day_avg'],
    format: 'csv'
  },
  {
    id: 'customers',
    title: 'Customer Analytics Summary',
    description: 'Customer profile table with lifetime spend, transaction counts, favorite categories, spend rankings, and flagged transaction counts.',
    columns: ['customer_id', 'total_transactions', 'total_spent', 'avg_amount', 'favorite_category', 'first_tx', 'last_tx', 'spend_rank'],
    format: 'csv'
  },
  {
    id: 'merchants',
    title: 'Merchant Analytics Summary',
    description: 'Merchant settlement aggregates, category classification, diurnal peak operating hour, volume rank, and failure metrics.',
    columns: ['merchant_id', 'category', 'total_transactions', 'total_value', 'avg_amount', 'success_count', 'failed_count', 'peak_hour'],
    format: 'csv'
  },
  {
    id: 'hourly',
    title: 'Hourly Diurnal Activity',
    description: '24-hour diurnal volume distribution across operational hours (00 to 23), ticket sizes, and percentage share of daily volume.',
    columns: ['tx_hour', 'tx_count', 'tx_value', 'avg_amount', 'volume_share_pct'],
    format: 'csv'
  },
  {
    id: 'anomalies',
    title: 'Rule-Based Anomaly Findings',
    description: 'Full audit log of flagged transactions, triggered rule names, mathematical reasons, severity ratings, and detection timestamps.',
    columns: ['finding_id', 'transaction_id', 'customer_id', 'merchant_id', 'rule_name', 'reason', 'severity', 'metric_value', 'detected_at'],
    format: 'csv'
  },
  {
    id: 'data_quality',
    title: 'Data Quality & Validation Audit',
    description: 'Historical records of all dataset ingestion runs, validity ratios, missing field distributions, and quarantine metrics.',
    columns: ['report_id', 'run_timestamp', 'source_filename', 'total_records', 'valid_records', 'invalid_records', 'duplicate_records', 'status'],
    format: 'csv'
  },
  {
    id: 'parquet_cleaned',
    title: 'Cleaned Dataset (Parquet Engine)',
    description: 'High-performance columnar Apache Parquet storage of the complete validated and deduplicated transaction dataset.',
    columns: ['transaction_id', 'timestamp', 'tx_date', 'tx_hour', 'customer_id', 'merchant_id', 'amount', 'category', 'status', 'anomaly_flag'],
    format: 'parquet'
  }
];

export function Reports({ showToast, onOpenUpload, refreshKey }) {
  const [downloadingId, setDownloadingId] = useState(null);
  const [hasData, setHasData] = useState(false);
  const [checkingData, setCheckingData] = useState(true);

  React.useEffect(() => {
    let isMounted = true;
    api.getKpis()
      .then((k) => {
        if (isMounted) setHasData(Boolean(k && k.total_transactions > 0));
      })
      .catch(() => {
        if (isMounted) setHasData(false);
      })
      .finally(() => {
        if (isMounted) setCheckingData(false);
      });
    return () => { isMounted = false; };
  }, [refreshKey]);

  const handleDownload = (report) => {
    if (!hasData) {
      if (showToast) showToast('No transaction data available. Please upload a dataset first.', 'error');
      if (onOpenUpload) onOpenUpload();
      return;
    }

    setDownloadingId(report.id);
    try {
      let url;
      if (report.format === 'parquet') {
        url = api.getExportUrl('cleaned_dataset', 'parquet');
      } else {
        url = api.getExportUrl(report.id, 'csv');
      }

      // Trigger browser download via invisible anchor
      const a = document.createElement('a');
      a.href = url;
      a.download = '';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      if (showToast) {
        showToast(`Exporting ${report.title} (${report.format.toUpperCase()})...`, 'success');
      }
    } catch (err) {
      console.error('Export download error:', err);
      if (showToast) {
        showToast(`Export failed: ${err.message}`, 'error');
      }
    } finally {
      setTimeout(() => setDownloadingId(null), 1000);
    }
  };

  return (
    <div>
      {/* Empty State Hero Banner when no data available */}
      {!checkingData && !hasData && (
        <div className="empty-hero-card">
          <div className="empty-hero-content">
            <div className="empty-hero-icon">📦</div>
            <div>
              <h2 className="empty-hero-title">No transaction data available for export</h2>
              <p className="empty-hero-desc">
                Upload your transaction CSV to generate downloadable CSV summaries and Apache Parquet datasets for downstream data warehousing.
              </p>
              <div className="empty-hero-badges">
                <span className="empty-pill-badge">📄 CSV Reports (Daily, Customer, Merchant, Diurnal, Anomaly)</span>
                <span className="empty-pill-badge">📦 Columnar Apache Parquet Storage</span>
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

      <div className="card-white" style={{ background: '#FAF6F2', border: '1px solid rgba(185, 160, 245, 0.4)' }}>
        <h3 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-main)' }}>
          Export Financial & Compliance Reports
        </h3>
        <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 4, lineHeight: 1.5 }}>
          Download clean, reproducible SQL reporting datasets in standardized CSV format or production-grade Apache Parquet for downstream data warehousing.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: 20 }}>
        {REPORT_CARDS.map((report) => (
          <div key={report.id} className="card-white" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                <span
                  style={{
                    fontSize: 12.5,
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.04em',
                    padding: '4px 10px',
                    borderRadius: 6,
                    backgroundColor: report.format === 'parquet' ? '#EDE7F6' : '#F3F1EF',
                    color: report.format === 'parquet' ? '#5E35B1' : '#77736F'
                  }}
                >
                  {report.format.toUpperCase()} EXPORT
                </span>
                <span style={{ fontSize: 20 }}>{report.format === 'parquet' ? '📦' : '📄'}</span>
              </div>

              <h4 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-main)', marginBottom: 8 }}>
                {report.title}
              </h4>
              <p style={{ fontSize: 14, color: 'var(--text-muted)', lineHeight: 1.55, marginBottom: 16 }}>
                {report.description}
              </p>

              {/* Column tags */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 20 }}>
                {report.columns.map((col) => (
                  <span
                    key={col}
                    className="mono"
                    style={{
                      fontSize: 12,
                      background: '#FAF8F6',
                      border: '1px solid #ECE8E5',
                      padding: '3px 8px',
                      borderRadius: 4,
                      color: 'var(--text-muted)'
                    }}
                  >
                    {col}
                  </span>
                ))}
              </div>
            </div>

            <button
              className={`btn ${report.format === 'parquet' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ width: '100%' }}
              onClick={() => handleDownload(report)}
              disabled={downloadingId === report.id}
            >
              <span>{report.format === 'parquet' ? '⬇ Download Parquet Dataset' : '⬇ Export Report (CSV)'}</span>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

