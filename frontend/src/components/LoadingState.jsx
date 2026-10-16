import React from 'react';

export function LoadingState({ message = 'Loading intelligence records...' }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '60px 20px', gap: 14 }}>
      <div className="spinner" />
      <span style={{ fontSize: 14.5, color: 'var(--text-muted)', fontWeight: 500 }}>{message}</span>
    </div>
  );
}

export function EmptyState({ title = 'No data found', description = 'Try adjusting your filters or search keywords.', icon = '🔍', action }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">{icon}</div>
      <div className="empty-title">{title}</div>
      <div className="empty-desc">{description}</div>
      {action && <div style={{ marginTop: 8 }}>{action}</div>}
    </div>
  );
}

