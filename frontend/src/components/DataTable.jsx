import React from 'react';
import { LoadingState } from './LoadingState';
import { EmptyState } from './EmptyState';

export function DataTable({
  columns = [],
  data = [],
  total = 0,
  page = 1,
  pageSize = 20,
  onPageChange,
  sortBy,
  sortDir,
  onSortChange,
  onRowClick,
  isLoading = false,
  emptyTitle = 'No transactions found',
  emptyDescription = 'No records match the current criteria.',
  emptyAction = null
}) {
  const totalPages = Math.ceil(total / pageSize) || 1;

  const handleSort = (col) => {
    if (!col.sortable || !onSortChange) return;
    if (sortBy === col.key) {
      onSortChange(col.key, sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      onSortChange(col.key, 'desc');
    }
  };

  return (
    <div className="table-container">
      {isLoading ? (
        <LoadingState />
      ) : data.length === 0 ? (
        <EmptyState title={emptyTitle} description={emptyDescription} action={emptyAction} />
      ) : (
        <>
          <table className="data-table">
            <thead>
              <tr>
                {columns.map((col) => (
                  <th
                    key={col.key}
                    className={col.sortable ? 'sortable' : ''}
                    onClick={() => handleSort(col)}
                    style={col.style}
                  >
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                      <span>{col.label}</span>
                      {col.sortable && sortBy === col.key && (
                        <span style={{ fontSize: 12, color: 'var(--primary)' }}>
                          {sortDir === 'asc' ? '▲' : '▼'}
                        </span>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, idx) => (
                <tr
                  key={row.transaction_id || row.customer_id || row.merchant_id || row.finding_id || idx}
                  onClick={() => onRowClick && onRowClick(row)}
                  style={{ cursor: onRowClick ? 'pointer' : 'default' }}
                >
                  {columns.map((col) => (
                    <td key={col.key} style={col.style}>
                      {col.render ? col.render(row[col.key], row) : (row[col.key] !== null && row[col.key] !== undefined ? String(row[col.key]) : '—')}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>

          {/* Footer with Pagination */}
          <div className="table-footer">
            <div style={{ fontSize: 14 }}>
              Showing <strong className="mono">{Math.min(total, (page - 1) * pageSize + 1)}</strong> to{' '}
              <strong className="mono">{Math.min(total, page * pageSize)}</strong> of{' '}
              <strong className="mono">{total}</strong> records
            </div>

            <div className="pagination-controls">
              <button
                className="page-btn"
                disabled={page <= 1}
                onClick={() => onPageChange(page - 1)}
              >
                Previous
              </button>
              <span style={{ padding: '0 8px', fontSize: 14 }}>
                Page <strong className="mono">{page}</strong> of <strong className="mono">{totalPages}</strong>
              </span>
              <button
                className="page-btn"
                disabled={page >= totalPages}
                onClick={() => onPageChange(page + 1)}
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

