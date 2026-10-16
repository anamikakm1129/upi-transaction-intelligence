import React, { useState, useEffect } from 'react';
import { api, formatINR, formatNumber, formatDateTime } from '../services/api';
import { DataTable } from '../components/DataTable';
import { StatusBadge, AnomalyBadge } from '../components/StatusBadge';
import { Drawer } from '../components/Drawer';

const CATEGORIES = [
  'Grocery & Supermarket',
  'Food & Dining',
  'Shopping & E-Commerce',
  'Utilities & Bill Pay',
  'Travel & Transport',
  'Health & Wellness',
  'Entertainment & Subscriptions',
  'Peer-to-Peer (P2P)'
];

export function Transactions({ dateRange, refreshKey, onOpenUpload }) {
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [sortBy, setSortBy] = useState('timestamp');
  const [sortDir, setSortDir] = useState('desc');
  const [loading, setLoading] = useState(false);

  // Filters
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [anomalyFilter, setAnomalyFilter] = useState('');
  const [selectedTx, setSelectedTx] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function fetchTransactions() {
      setLoading(true);
      try {
        const params = {
          page,
          page_size: pageSize,
          sort_by: sortBy,
          sort_dir: sortDir
        };
        if (search) params.search = search;
        if (category) params.category = category;
        if (statusFilter) params.status = statusFilter;
        if (anomalyFilter !== '') params.anomaly_flag = anomalyFilter;
        if (dateRange.startDate) params.start_date = dateRange.startDate;
        if (dateRange.endDate) params.end_date = dateRange.endDate;

        const res = await api.getTransactions(params);
        if (isMounted) {
          setData(res.data || []);
          setTotal(res.total || 0);
        }
      } catch (err) {
        console.error('Failed to fetch transactions:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    fetchTransactions();
    return () => { isMounted = false; };
  }, [page, pageSize, sortBy, sortDir, search, category, statusFilter, anomalyFilter, dateRange, refreshKey]);

  const handleClearFilters = () => {
    setSearch('');
    setCategory('');
    setStatusFilter('');
    setAnomalyFilter('');
    setPage(1);
  };

  const columns = [
    {
      key: 'transaction_id',
      label: 'Transaction ID',
      sortable: true,
      render: (val) => <span className="mono" style={{ fontWeight: 600, color: 'var(--primary)' }}>{val}</span>
    },
    {
      key: 'timestamp',
      label: 'Date & Time',
      sortable: true,
      render: (val) => formatDateTime(val)
    },
    {
      key: 'customer_id',
      label: 'Customer VPA',
      sortable: true,
      render: (val) => <span className="mono" style={{ fontSize: 13.5 }}>{val}</span>
    },
    {
      key: 'merchant_id',
      label: 'Merchant VPA',
      sortable: true,
      render: (val) => <span className="mono" style={{ fontSize: 13.5 }}>{val}</span>
    },
    {
      key: 'amount',
      label: 'Amount (₹)',
      sortable: true,
      render: (val) => <strong className="mono">{formatINR(val)}</strong>
    },
    {
      key: 'category',
      label: 'Category',
      sortable: true
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      render: (val) => <StatusBadge status={val} />
    },
    {
      key: 'anomaly_flag',
      label: 'Anomaly Flag',
      sortable: true,
      render: (val, row) => <AnomalyBadge flag={val} reason={row.anomaly_reason} />
    }
  ];

  return (
    <div>
      {/* Filter Bar */}
      <div className="filter-bar">
        {/* Search */}
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            className="search-input"
            placeholder="Search by Transaction ID or Customer handle..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>

        {/* Category filter */}
        <select
          className="select-input"
          value={category}
          onChange={(e) => { setCategory(e.target.value); setPage(1); }}
        >
          <option value="">All Categories</option>
          {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>

        {/* Status filter */}
        <select
          className="select-input"
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
        >
          <option value="">All Statuses</option>
          <option value="SUCCESS">Success</option>
          <option value="FAILED">Failed</option>
          <option value="PENDING">Pending</option>
        </select>

        {/* Anomaly filter */}
        <select
          className="select-input"
          value={anomalyFilter}
          onChange={(e) => { setAnomalyFilter(e.target.value); setPage(1); }}
        >
          <option value="">All Flag States</option>
          <option value="0">Normal Transactions Only</option>
          <option value="1">Flagged Review Candidates</option>
        </select>

        {/* Clear filters button */}
        {(search || category || statusFilter || anomalyFilter !== '') && (
          <button className="btn btn-secondary btn-sm" onClick={handleClearFilters}>
            Clear Filters
          </button>
        )}
      </div>

      {/* Main Table Card */}
      <div className="card-white">
        <div className="card-header">
          <div className="card-title-group">
            <h3 className="card-title">All Validated Transactions</h3>
            <p className="card-subtitle">
              Showing <span className="mono">{formatNumber(total)}</span> total matching records. Click any row for deep details.
            </p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 14, color: 'var(--text-muted)' }}>Page Size:</span>
            <select
              className="select-input"
              style={{ padding: '6px 12px', fontSize: 14 }}
              value={pageSize}
              onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }}
            >
              <option value="15">15 per page</option>
              <option value="30">30 per page</option>
              <option value="50">50 per page</option>
            </select>
          </div>
        </div>

        <DataTable
          columns={columns}
          data={data}
          total={total}
          page={page}
          pageSize={pageSize}
          onPageChange={(p) => setPage(p)}
          sortBy={sortBy}
          sortDir={sortDir}
          onSortChange={(col, dir) => { setSortBy(col); setSortDir(dir); }}
          onRowClick={(tx) => setSelectedTx(tx)}
          isLoading={loading}
          emptyTitle={search || category || statusFilter || anomalyFilter ? "No matching transactions found" : "No transactions available"}
          emptyDescription={search || category || statusFilter || anomalyFilter ? "Try clearing your filters or search keywords." : "Upload your transaction CSV to search, filter, and audit payment transactions."}
          emptyAction={!(search || category || statusFilter || anomalyFilter) && onOpenUpload && (
            <button className="btn btn-primary" onClick={onOpenUpload}>
              <span>📤 Upload Transaction CSV</span>
            </button>
          )}
        />
      </div>

      {/* Transaction Details Drawer */}
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
                Anomaly Assessment
              </div>
              <div style={{ fontSize: 14.5, marginTop: 6, color: 'var(--text-main)', lineHeight: 1.5 }}>
                {selectedTx.anomaly_reason || 'Verified legitimate transaction. No anomaly rules triggered.'}
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

