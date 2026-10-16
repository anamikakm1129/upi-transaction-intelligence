import React, { useState, useEffect } from 'react';
import { api, formatINR, formatNumber, formatDateTime } from '../services/api';
import { DataTable } from '../components/DataTable';
import { Drawer } from '../components/Drawer';
import { BarHourlyChart } from '../components/SvgCharts';
import { LoadingState } from '../components/LoadingState';

export function Merchants({ refreshKey, onOpenUpload }) {
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  // Profile Drawer
  const [selectedMerchantId, setSelectedMerchantId] = useState(null);
  const [merchantProfile, setMerchantProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    async function fetchMerchants() {
      setLoading(true);
      try {
        const res = await api.getMerchants({
          page,
          page_size: pageSize,
          search: search || undefined
        });
        if (isMounted) {
          setData(res.data || []);
          setTotal(res.total || 0);
        }
      } catch (err) {
        console.error('Failed to fetch merchants:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    fetchMerchants();
    return () => { isMounted = false; };
  }, [page, pageSize, search, refreshKey]);

  useEffect(() => {
    let isMounted = true;
    if (!selectedMerchantId) {
      setMerchantProfile(null);
      return;
    }

    async function fetchProfile() {
      setProfileLoading(true);
      try {
        const prof = await api.getMerchantProfile(selectedMerchantId);
        if (isMounted) setMerchantProfile(prof);
      } catch (err) {
        console.error('Failed to load merchant profile:', err);
      } finally {
        if (isMounted) setProfileLoading(false);
      }
    }

    fetchProfile();
    return () => { isMounted = false; };
  }, [selectedMerchantId]);

  const columns = [
    {
      key: 'volume_rank',
      label: 'Rank',
      render: (val) => <span style={{ fontWeight: 700, color: 'var(--text-light)', fontSize: 13.5 }}>#{val}</span>
    },
    {
      key: 'merchant_id',
      label: 'Merchant VPA',
      render: (val) => <span className="mono" style={{ fontWeight: 600, color: 'var(--primary)' }}>{val}</span>
    },
    {
      key: 'category',
      label: 'Category',
      render: (val) => <span style={{ padding: '4px 10px', borderRadius: 6, background: '#FAF6F2', fontSize: 13.5 }}>{val}</span>
    },
    {
      key: 'total_transactions',
      label: 'Transactions',
      render: (val) => <span className="mono">{formatNumber(val)}</span>
    },
    {
      key: 'total_value',
      label: 'Total Value (₹)',
      render: (val) => <strong className="mono">{formatINR(val)}</strong>
    },
    {
      key: 'avg_amount',
      label: 'Avg Ticket (₹)',
      render: (val) => <span className="mono">{formatINR(val)}</span>
    },
    {
      key: 'peak_hour',
      label: 'Peak Hour',
      render: (val) => <span className="mono" style={{ fontWeight: 600 }}>{val}:00</span>
    },
    {
      key: 'success_count',
      label: 'Success / Failed',
      render: (val, row) => (
        <span style={{ fontSize: 13.5 }}>
          <span style={{ color: 'var(--status-success)', fontWeight: 600 }}>{row.success_count}</span>
          {' / '}
          <span style={{ color: row.failed_count > 0 ? 'var(--status-failed)' : 'var(--text-muted)' }}>{row.failed_count}</span>
        </span>
      )
    }
  ];

  return (
    <div>
      {/* Search Header */}
      <div className="filter-bar">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            className="search-input"
            placeholder="Search merchants by VPA or category (e.g. swiggy@icici, Blinkit)..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>
        {search && (
          <button className="btn btn-secondary btn-sm" onClick={() => { setSearch(''); setPage(1); }}>
            Clear
          </button>
        )}
      </div>

      {/* Main Table */}
      <div className="card-white">
        <div className="card-header">
          <div className="card-title-group">
            <h3 className="card-title">Merchant Volume & Settlement Performance</h3>
            <p className="card-subtitle">
              Calculated via SQL CTEs, window functions (peak hour rank, volume rank), and aggregations.
            </p>
          </div>
          <span style={{ fontSize: 14, color: 'var(--text-muted)' }}>
            Active Merchants: <strong className="mono">{total > 0 ? formatNumber(total) : '—'}</strong>
          </span>
        </div>

        <DataTable
          columns={columns}
          data={data}
          total={total}
          page={page}
          pageSize={pageSize}
          onPageChange={(p) => setPage(p)}
          onRowClick={(m) => setSelectedMerchantId(m.merchant_id)}
          isLoading={loading}
          emptyTitle={search ? "No matching merchant records found" : "No merchant records available"}
          emptyDescription={search ? "Try adjusting your search criteria." : "Upload your transaction CSV to calculate merchant volumes, peak hours, and settlement performance."}
          emptyAction={!search && onOpenUpload && (
            <button className="btn btn-primary" onClick={onOpenUpload}>
              <span>📤 Upload Transaction CSV</span>
            </button>
          )}
        />
      </div>

      {/* Merchant Profile Drawer */}
      <Drawer
        isOpen={Boolean(selectedMerchantId)}
        onClose={() => setSelectedMerchantId(null)}
        title="Merchant Intelligence Detail"
        subtitle={selectedMerchantId}
      >
        {profileLoading ? (
          <LoadingState message="Fetching merchant analytics..." />
        ) : merchantProfile ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {/* Quick Metrics */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div style={{ padding: 14, borderRadius: 10, background: '#FAF6F2', border: '1px solid var(--border-main)' }}>
                <span style={{ fontSize: 12.5, color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em' }}>TOTAL VOLUME</span>
                <div className="mono" style={{ fontSize: 20, fontWeight: 700, color: 'var(--primary)', marginTop: 4 }}>
                  {formatINR(merchantProfile.total_value)}
                </div>
              </div>
              <div style={{ padding: 14, borderRadius: 10, background: '#FAF6F2', border: '1px solid var(--border-main)' }}>
                <span style={{ fontSize: 12.5, color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em' }}>TRANSACTIONS</span>
                <div className="mono" style={{ fontSize: 20, fontWeight: 700, marginTop: 4 }}>
                  {formatNumber(merchantProfile.total_transactions)}
                </div>
              </div>
            </div>

            <div className="detail-row">
              <span className="detail-label">Merchant Category</span>
              <span className="detail-value">{merchantProfile.category}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Average Ticket Size</span>
              <span className="detail-value mono">{formatINR(merchantProfile.avg_amount)}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Min / Max Transaction</span>
              <span className="detail-value mono">{formatINR(merchantProfile.min_amount)} / {formatINR(merchantProfile.max_amount)}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Unique Customers Served</span>
              <span className="detail-value mono">{formatNumber(merchantProfile.unique_customers || 0)}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Successful Transactions</span>
              <span className="detail-value" style={{ color: 'var(--status-success)' }}>
                {merchantProfile.success_count}
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Failed Transactions</span>
              <span className="detail-value" style={{ color: merchantProfile.failed_count > 0 ? 'var(--status-failed)' : 'inherit' }}>
                {merchantProfile.failed_count}
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Flagged Transactions</span>
              <span className="detail-value" style={{ color: merchantProfile.flagged_count > 0 ? 'var(--primary)' : 'inherit' }}>
                {merchantProfile.flagged_count}
              </span>
            </div>

            {/* Merchant 24-hr Activity Chart */}
            <div style={{ marginTop: 12 }}>
              <h4 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12, color: 'var(--text-main)' }}>Diurnal Hourly Distribution</h4>
              <BarHourlyChart data={merchantProfile.hourly_activity || []} height={180} />
            </div>
          </div>
        ) : null}
      </Drawer>
    </div>
  );
}

