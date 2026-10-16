import React from 'react';

export function KpiCard({ title, value, subtitle, icon, highlight, badgeText, badgeColor }) {
  return (
    <div className="kpi-card">
      <div className="kpi-top">
        <span className="kpi-label">{title}</span>
        <div className="kpi-icon-pill">
          {icon || '📊'}
        </div>
      </div>
      <div className="kpi-value mono" style={{ color: highlight ? 'var(--primary)' : 'var(--text-main)' }}>
        {value}
      </div>
      {(subtitle || badgeText) && (
        <div className="kpi-bottom">
          {badgeText && (
            <span
              style={{
                fontSize: 12.5,
                fontWeight: 700,
                padding: '3px 8px',
                borderRadius: 6,
                backgroundColor: badgeColor || 'var(--primary-tint)',
                color: 'var(--primary)'
              }}
            >
              {badgeText}
            </span>
          )}
          {subtitle && <span>{subtitle}</span>}
        </div>
      )}
    </div>
  );
}

