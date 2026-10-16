import React from 'react';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'transactions', label: 'Transaction Explorer', icon: '💳' },
  { id: 'customers', label: 'Customer Analytics', icon: '👤' },
  { id: 'merchants', label: 'Merchant Analytics', icon: '🏪' },
  { id: 'patterns', label: 'Transaction Patterns', icon: '📈' },
  { id: 'anomalies', label: 'Anomaly Report', icon: '⚠️' },
  { id: 'data_quality', label: 'Data Quality', icon: '🛡️' },
  { id: 'reports', label: 'Reports & Exports', icon: '📥' },
];

export function Sidebar({ currentTab, onSelectTab, isHealthy = true }) {
  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="brand-section">
        <div className="brand-logo-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="5" width="20" height="14" rx="2" />
            <line x1="2" y1="10" x2="22" y2="10" />
          </svg>
        </div>
        <div className="brand-title-wrap">
          <span className="brand-title">UPI Intelligence</span>
          <span className="brand-tagline">Financial Analytics</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="nav-menu">
        {NAV_ITEMS.map((item) => {
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => onSelectTab(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Sidebar Footer */}
      <div className="sidebar-footer">
        <div className="system-status-badge">
          <span className="status-dot" style={{ backgroundColor: isHealthy ? '#10B981' : '#F59E0B' }} />
          <span>Pipeline: {isHealthy ? 'Operational' : 'Syncing'}</span>
        </div>
        <div style={{ fontSize: 12.5, color: 'var(--text-light)', textAlign: 'center', marginTop: 4 }}>
          UPI Intelligence v1.0.0
        </div>
      </div>
    </aside>
  );
}

