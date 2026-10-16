import React, { useState, useEffect } from 'react';
import { api, formatINR, formatNumber, formatDateTime } from '../services/api';
import { DataTable } from '../components/DataTable';
import { Drawer } from '../components/Drawer';
import { StatusBadge, AnomalyBadge } from '../components/StatusBadge';
import { LoadingState } from '../components/LoadingState';

export function Customers({ refreshKey, onOpenUpload }) {
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  // Profile Drawer
  const [selectedCustomerId, setSelectedCustomerId] = useState(null);
  const [customerProfile, setCustomerProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    async function fetchCustomers() {
      setLoading(true);
      try {
        const res = await api.getCustomers({
          page,
          page_size: pageSize,
          search: search || undefined
        });
        if (isMounted) {
          setData(res.data || []);
          setTotal(res.total || 0);
        }
      } catch (err) {
        console.error('Failed to fetch customers:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    fetchCustomers();
    return () => { isMounted = false; };
  }, [page, pageSize, search, refreshKey]);

  // Load customer detail & transaction history when clicked
  useEffect(() => {
    let isMounted = true;
    if (!selectedCustomerId) {
      setCustomerProfile(null);
      return;
    }

    async function fetchProfile() {
      setProfileLoading(true);
      try {
        const prof = await api.getCustomerProfile(selectedCustomerId);
        if (isMounted) setCustomerProfile(prof);
      } catch (err) {
        console.error('Failed to load customer profile:', err);
      } finally {
        if (isMounted) setProfileLoading(false);
      }
    }

    fetchProfile();
    return () => { isMounted = false; };
  }, [selectedCustomerId]);

  const columns = [
    {
      key: 'spend_rank',
      label: 'Rank',
      render: (val) => <span style={{ fontWeight: 700, color: 'var(--text-light)', fontSize: 13.5 }}>#{val}</span>
    },
    {
      key: 'customer_id',
      label: 'Customer VPA',
      render: (val) => <span className="mono" style={{ fontWeight: 600, color: 'var(--primary)' }}>{val}</span>
    },
    {
      key: 'total_transactions',
      label: 'Transactions',
      render: (val) => <span className="mono">{formatNumber(val)}</span>
    },
    {
      key: 'total_spent',
      label: 'Total Spent (₹)',
      render: (val) => <strong className="mono">{formatINR(val)}</strong>
    },
    {
      key: 'avg_amount',
      label: 'Avg Ticket (₹)',
      render: (val) => <span className="mono">{formatINR(val)}</span>
    },
    {
      key: 'favorite_category',
      label: 'Primary Category',
      render: (val) => <span style={{ padding: '4px 10px', borderRadius: 6, background: '#FAF6F2', fontSize: 13.5 }}>{val}</span>
    },
    {
      key: 'flagged_count',
      label: 'Flagged Txns',
      render: (val) => (
        val > 0 ? (
          <span className="badge badge-flagged">{val} Flagged</span>
        ) : (
          <span style={{ color: 'var(--text-light)', fontSize: 13.5 }}>0</span>
        )
      )
    },
    {
      key: 'last_tx',
      label: 'Last Active',
      render: (val) => <span style={{ fontSize: 13.5 }}>{formatDateTime(val)}</span>
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
            placeholder="Search customers by handle or VPA (e.g. cust_aarav@oksbi)..."
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
            <h3 className="card-title">Customer Behavioral Profiles</h3>
            <p className="card-subtitle">
              Calculated via SQL CTEs, window functions (DENSE_RANK), and aggregation grouping.
            </p>
          </div>
          <span style={{ fontSize: 14, color: 'var(--text-muted)' }}>
            Total Customers: <strong className="mono">{total > 0 ? formatNumber(total) : '—'}</strong>
          </span>
        </div>

        <DataTable
          columns={columns}
          data={data}
          total={total}
          page={page}
          pageSize={pageSize}
          onPageChange={(p) => setPage(p)}
          onRowClick={(c) => setSelectedCustomerId(c.customer_id)}
          isLoading={loading}
          emptyTitle={search ? "No matching customer profiles found" : "No customer records available"}
          emptyDescription={search ? "Try searching for another customer handle." : "Upload your transaction CSV to generate customer analytics, spend rankings, and behavioral profiles."}
          emptyAction={!search && onOpenUpload && (
            <button className="btn btn-primary" onClick={onOpenUpload}>
              <span>📤 Upload Transaction CSV</span>
            </button>
          )}
        />
      </div>

      {/* Customer Profile & Transaction History Drawer */}
      <Drawer
        isOpen={Boolean(selectedCustomerId)}
        onClose={() => setSelectedCustomerId(null)}
        title="Customer Intelligence Profile"
        subtitle={selectedCustomerId}
      >
        {profileLoading ? (
          <LoadingState message="Fetching customer history..." />
        ) : customerProfile ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {/* Quick Metrics */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div style={{ padding: 14, borderRadius: 10, background: '#FAF6F2', border: '1px solid var(--border-main)' }}>
                <span style={{ fontSize: 12.5, color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em' }}>TOTAL SPEND</span>
                <div className="mono" style={{ fontSize: 20, fontWeight: 700, color: 'var(--primary)', marginTop: 4 }}>
                  {formatINR(customerProfile.total_spent)}
                </div>
              </div>
              <div style={{ padding: 14, borderRadius: 10, background: '#FAF6F2', border: '1px solid var(--border-main)' }}>
                <span style={{ fontSize: 12.5, color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em' }}>TRANSACTIONS</span>
                <div className="mono" style={{ fontSize: 20, fontWeight: 700, marginTop: 4 }}>
                  {formatNumber(customerProfile.total_transactions)}
                </div>
              </div>
            </div>

            <div className="detail-row">
              <span className="detail-label">Average Ticket Size</span>
              <span className="detail-value mono">{formatINR(customerProfile.avg_amount)}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Min / Max Transaction</span>
              <span className="detail-value mono">{formatINR(customerProfile.min_amount)} / {formatINR(customerProfile.max_amount)}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Favorite Category</span>
              <span className="detail-value">{customerProfile.favorite_category}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">First Seen</span>
              <span className="detail-value">{formatDateTime(customerProfile.first_tx)}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Last Activity</span>
              <span className="detail-value">{formatDateTime(customerProfile.last_tx)}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Flagged Transactions</span>
              <span className="detail-value" style={{ color: customerProfile.flagged_count > 0 ? 'var(--primary)' : 'inherit' }}>
                {customerProfile.flagged_count}
              </span>
            </div>

            {/* Transaction History Section */}
            <div style={{ marginTop: 12 }}>
              <h4 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12, color: 'var(--text-main)' }}>Recent Transaction History</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {customerProfile.history && customerProfile.history.length > 0 ? (
                  customerProfile.history.map((tx) => (
                    <div
                      key={tx.transaction_id}
                      style={{
                        padding: '12px 14px',
                        borderRadius: 8,
                        background: '#FFFFFF',
                        border: '1px solid var(--border-main)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        fontSize: 13.5
                      }}
                    >
                      <div>
                        <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>{tx.merchant_id}</div>
                        <div style={{ color: 'var(--text-muted)', fontSize: 12.5, marginTop: 3 }}>
                          {formatDateTime(tx.timestamp)} • {tx.category}
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div className="mono" style={{ fontWeight: 700, fontSize: 14 }}>{formatINR(tx.amount)}</div>
                        <div style={{ marginTop: 3 }}>
                          {tx.anomaly_flag ? (
                            <span className="badge badge-flagged" style={{ fontSize: 12 }}>Flagged</span>
                          ) : (
                            <StatusBadge status={tx.status} />
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div style={{ color: 'var(--text-muted)', fontSize: 13.5 }}>No history found.</div>
                )}
              </div>
            </div>
          </div>
        ) : null}
      </Drawer>
    </div>
  );
}

