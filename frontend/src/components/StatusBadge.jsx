import React from 'react';

export function StatusBadge({ status }) {
  if (!status) return null;
  const s = status.toUpperCase();

  if (s === 'SUCCESS') {
    return <span className="badge badge-success">● Success</span>;
  }
  if (s === 'FAILED') {
    return <span className="badge badge-failed">● Failed</span>;
  }
  if (s === 'PENDING') {
    return <span className="badge badge-pending">● Pending</span>;
  }
  return <span className="badge badge-normal">{status}</span>;
}

export function AnomalyBadge({ flag, reason }) {
  if (flag === 1 || flag === true) {
    return (
      <span
        className="badge badge-flagged"
        title={reason || 'Rule-based anomaly detected for review'}
      >
        ⚠ Review Flag
      </span>
    );
  }
  return <span className="badge badge-normal">Normal</span>;
}

export function SeverityBadge({ severity }) {
  if (!severity) return null;
  const s = severity.toUpperCase();
  if (s === 'HIGH') return <span className="badge badge-high">High</span>;
  if (s === 'MEDIUM') return <span className="badge badge-medium">Medium</span>;
  return <span className="badge badge-low">Low</span>;
}

