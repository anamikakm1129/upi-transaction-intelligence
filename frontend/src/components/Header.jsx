import React from 'react';

export function Header({
  title,
  subtitle,
  dateRange,
  onDateChange,
  onRefresh,
  onOpenUpload,
  isRefreshing = false
}) {
  return (
    <header className="top-header">
      <div className="header-left">
        <h1 className="page-title">{title}</h1>
        {subtitle && <p className="page-subtitle">{subtitle}</p>}
      </div>

      <div className="header-actions">
        {/* Date Filter Inputs */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: '#FAF8F6', padding: '6px 14px', borderRadius: 10, border: '1px solid var(--border-main)' }}>
          <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-muted)' }}>From</span>
          <input
            type="date"
            className="date-input"
            style={{ padding: '6px 10px', fontSize: 14, border: 'none', background: 'transparent' }}
            value={dateRange?.startDate || ''}
            onChange={(e) => onDateChange({ ...dateRange, startDate: e.target.value })}
          />
          <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-muted)' }}>To</span>
          <input
            type="date"
            className="date-input"
            style={{ padding: '6px 10px', fontSize: 14, border: 'none', background: 'transparent' }}
            value={dateRange?.endDate || ''}
            onChange={(e) => onDateChange({ ...dateRange, endDate: e.target.value })}
          />
          {(dateRange?.startDate || dateRange?.endDate) && (
            <button
              onClick={() => onDateChange({ startDate: '', endDate: '' })}
              style={{ fontSize: 13, color: 'var(--primary)', fontWeight: 700, padding: '4px 8px', borderRadius: 6, background: 'var(--primary-tint)' }}
            >
              Reset
            </button>
          )}
        </div>

        {/* Refresh Action */}
        <button
          className="btn btn-secondary"
          onClick={onRefresh}
          disabled={isRefreshing}
          title="Refresh current data view"
        >
          <span style={{ display: 'inline-block', transform: isRefreshing ? 'rotate(360deg)' : 'none', transition: 'transform 0.5s linear' }}>
            🔄
          </span>
          <span>Refresh</span>
        </button>

        {/* Upload Real CSV Action */}
        {onOpenUpload && (
          <button
            className="btn btn-primary"
            onClick={onOpenUpload}
            title="Upload transaction CSV file for real analytics"
          >
            <span>📤 Upload CSV</span>
          </button>
        )}
      </div>
    </header>
  );
}
