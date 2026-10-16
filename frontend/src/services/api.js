// Central API service module using Fetch API

const API_BASE = import.meta.env.VITE_API_URL || '/api';

/**
 * Format number in Indian currency format (e.g. ₹1,24,500.00).
 * Displays '—' when amount is null/undefined or invalid.
 */
export function formatINR(amount, includeSymbol = true, fallback = '—') {
  if (amount === undefined || amount === null || isNaN(amount) || amount === '') return fallback;
  const num = Number(amount);
  const formatted = new Intl.NumberFormat('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(num);
  return includeSymbol ? `₹${formatted}` : formatted;
}

/**
 * Format standard number with Indian grouping (e.g. 12,450).
 * Displays '—' when value is null/undefined.
 */
export function formatNumber(num, fallback = '—') {
  if (num === undefined || num === null || isNaN(num) || num === '') return fallback;
  return new Intl.NumberFormat('en-IN').format(Number(num));
}

/**
 * Format ISO datetime to clean readable string
 */
export function formatDateTime(dateStr) {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    return d.toLocaleString('en-IN', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  } catch {
    return dateStr;
  }
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: {
        'Accept': 'application/json',
        ...options.headers
      },
      ...options
    });

    if (!res.ok) {
      let errorMsg = `Server responded with ${res.status}`;
      try {
        const errJson = await res.json();
        errorMsg = errJson.detail || errJson.message || errorMsg;
      } catch {
        // use default error message
      }
      throw new Error(errorMsg);
    }

    return await res.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Health
  getHealth: () => request('/health'),

  // Dashboard
  getDashboardSummary: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/dashboard/summary${qs ? `?${qs}` : ''}`);
  },
  getDailyTrends: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/dashboard/daily-trends${qs ? `?${qs}` : ''}`);
  },
  getHourlyTrends: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/dashboard/hourly-trends${qs ? `?${qs}` : ''}`);
  },
  getCategoryDistribution: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/dashboard/category-distribution${qs ? `?${qs}` : ''}`);
  },
  getPatterns: () => request('/dashboard/patterns'),

  // Transactions
  getTransactions: (params = {}) => {
    const cleanParams = {};
    Object.keys(params).forEach(k => {
      if (params[k] !== undefined && params[k] !== null && params[k] !== '') {
        cleanParams[k] = params[k];
      }
    });
    const qs = new URLSearchParams(cleanParams).toString();
    return request(`/transactions?${qs}`);
  },
  getTransactionById: (id) => request(`/transactions/${encodeURIComponent(id)}`),

  // Customers
  getCustomers: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/customers${qs ? `?${qs}` : ''}`);
  },
  getCustomerProfile: (id) => request(`/customers/${encodeURIComponent(id)}`),

  // Merchants
  getMerchants: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/merchants${qs ? `?${qs}` : ''}`);
  },
  getMerchantProfile: (id) => request(`/merchants/${encodeURIComponent(id)}`),

  // Anomalies
  getAnomalies: (params = {}) => {
    const cleanParams = {};
    Object.keys(params).forEach(k => {
      if (params[k] !== undefined && params[k] !== null && params[k] !== '') {
        cleanParams[k] = params[k];
      }
    });
    const qs = new URLSearchParams(cleanParams).toString();
    return request(`/anomalies?${qs}`);
  },
  getAnomalyConfig: () => request('/anomalies/config'),
  updateAnomalyConfig: (updates) => request('/anomalies/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates)
  }),

  // Data Quality & Ingestion
  getDataQualitySummary: () => request('/data-quality/summary'),
  getQuarantinedRecords: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/data-quality/quarantined${qs ? `?${qs}` : ''}`);
  },
  validateCsv: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/data-quality/validate-upload`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Validation failed' }));
      throw new Error(err.detail || 'Validation failed');
    }
    return await res.json();
  },
  uploadCsv: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/data-quality/upload`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return await res.json();
  },

  // Reprocessing
  reprocessDataset: () => request('/processing/run', { method: 'POST' }),

  getExportUrl: (reportType, format = 'csv') =>
    `${API_BASE}/reports/export?report_type=${encodeURIComponent(reportType)}&format=${encodeURIComponent(format)}`
};
