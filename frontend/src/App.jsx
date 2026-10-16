import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { UploadModal } from './components/UploadModal';
import { api } from './services/api';

import { Dashboard } from './pages/Dashboard';
import { Transactions } from './pages/Transactions';
import { Customers } from './pages/Customers';
import { Merchants } from './pages/Merchants';
import { Patterns } from './pages/Patterns';
import { Anomalies } from './pages/Anomalies';
import { DataQuality } from './pages/DataQuality';
import { Reports } from './pages/Reports';

const VIEW_METADATA = {
  dashboard: {
    title: 'UPI Transaction Intelligence',
    subtitle: 'Daily financial analytics, volume distribution, and anomaly candidate tracking'
  },
  transactions: {
    title: 'Transaction Explorer',
    subtitle: 'Search, filter, and audit individual transaction records with backend pagination'
  },
  customers: {
    title: 'Customer Analytics',
    subtitle: 'Behavioral spend profiles, volume rankings, and transaction histories'
  },
  merchants: {
    title: 'Merchant Analytics',
    subtitle: 'Settlement performance, diurnal peak hour analysis, and volume aggregations'
  },
  patterns: {
    title: 'Transaction Patterns',
    subtitle: 'Diurnal traffic curves, ticket sizes, and deterministic analytical findings'
  },
  anomalies: {
    title: 'Anomaly Report',
    subtitle: 'Transparent, rule-based review candidate flags and threshold configurations'
  },
  data_quality: {
    title: 'Data Quality & Governance',
    subtitle: 'Dataset validation, duplicate isolation policy, and CSV ingestion pipeline'
  },
  reports: {
    title: 'Reports & Exports',
    subtitle: 'Download dashboard-ready CSV summaries and Parquet columnar datasets'
  }
};

export function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [dateRange, setDateRange] = useState({ startDate: '', endDate: '' });
  const [refreshKey, setRefreshKey] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isHealthy, setIsHealthy] = useState(true);
  const [toasts, setToasts] = useState([]);
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  const showToast = (message, type = 'success') => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setRefreshKey((k) => k + 1);
    try {
      const health = await api.getHealth();
      setIsHealthy(health.status === 'UP');
      showToast('Data refreshed successfully.', 'success');
    } catch {
      setIsHealthy(false);
    } finally {
      setTimeout(() => setIsRefreshing(false), 500);
    }
  };

  const handleOpenUpload = () => {
    setIsUploadOpen(true);
  };

  const handleUploadSuccess = (res) => {
    setRefreshKey((k) => k + 1);
    showToast(`Dataset ready: ${res.cleaned_records_count} transactions processed successfully!`, 'success');
  };

  useEffect(() => {
    api.getHealth()
      .then((h) => setIsHealthy(h.status === 'UP'))
      .catch(() => setIsHealthy(false));
  }, []);

  const meta = VIEW_METADATA[currentTab] || VIEW_METADATA.dashboard;

  return (
    <div className="app-shell">
      {/* Left Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={(tab) => setCurrentTab(tab)}
        isHealthy={isHealthy}
      />

      {/* Main App Canvas */}
      <div className="main-wrapper">
        <Header
          title={meta.title}
          subtitle={meta.subtitle}
          dateRange={dateRange}
          onDateChange={(dr) => setDateRange(dr)}
          onRefresh={handleRefresh}
          onOpenUpload={handleOpenUpload}
          isRefreshing={isRefreshing}
        />

        <main className="content-body">
          {currentTab === 'dashboard' && (
            <Dashboard
              dateRange={dateRange}
              refreshKey={refreshKey}
              onNavigateTo={(tab) => setCurrentTab(tab)}
              onOpenUpload={handleOpenUpload}
            />
          )}
          {currentTab === 'transactions' && (
            <Transactions
              dateRange={dateRange}
              refreshKey={refreshKey}
              onOpenUpload={handleOpenUpload}
            />
          )}
          {currentTab === 'customers' && (
            <Customers
              refreshKey={refreshKey}
              onOpenUpload={handleOpenUpload}
            />
          )}
          {currentTab === 'merchants' && (
            <Merchants
              refreshKey={refreshKey}
              onOpenUpload={handleOpenUpload}
            />
          )}
          {currentTab === 'patterns' && (
            <Patterns
              dateRange={dateRange}
              refreshKey={refreshKey}
              onOpenUpload={handleOpenUpload}
            />
          )}
          {currentTab === 'anomalies' && (
            <Anomalies
              refreshKey={refreshKey}
              showToast={showToast}
              onOpenUpload={handleOpenUpload}
            />
          )}
          {currentTab === 'data_quality' && (
            <DataQuality
              refreshKey={refreshKey}
              showToast={showToast}
              onOpenUpload={handleOpenUpload}
            />
          )}
          {currentTab === 'reports' && (
            <Reports
              showToast={showToast}
              onOpenUpload={handleOpenUpload}
              refreshKey={refreshKey}
            />
          )}
        </main>
      </div>

      {/* Upload & Ingestion Modal */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={handleUploadSuccess}
        showToast={showToast}
      />

      {/* Floating Toast Alerts */}
      <div className="toast-container">
        {toasts.map((t) => (
          <div key={t.id} className={`toast ${t.type}`}>
            <span>{t.type === 'success' ? '✓' : '⚠️'}</span>
            <span>{t.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
export default App;

