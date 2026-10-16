import React from 'react';

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

