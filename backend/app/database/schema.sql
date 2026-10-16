-- Schema for UPI Transaction Intelligence System
-- Database: SQLite

-- 1. Raw Transactions Table (preserves exact source data)
CREATE TABLE IF NOT EXISTS raw_transactions (
    raw_id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT,
    timestamp TEXT,
    customer_id TEXT,
    merchant_id TEXT,
    amount REAL,
    category TEXT,
    status TEXT,
    payment_method TEXT,
    bank_reference_number TEXT,
    device_type TEXT,
    source_batch TEXT,
    ingested_at TEXT DEFAULT (datetime('now'))
);

-- 2. Cleaned Valid Transactions Table
CREATE TABLE IF NOT EXISTS cleaned_transactions (
    transaction_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    tx_date TEXT NOT NULL,
    tx_hour INTEGER NOT NULL,
    customer_id TEXT NOT NULL,
    merchant_id TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    status TEXT NOT NULL,
    payment_method TEXT,
    bank_reference_number TEXT,
    device_type TEXT,
    anomaly_flag INTEGER DEFAULT 0,
    anomaly_reason TEXT,
    processed_at TEXT DEFAULT (datetime('now'))
);

-- Indexes for high performance querying
CREATE INDEX IF NOT EXISTS idx_cleaned_tx_date ON cleaned_transactions(tx_date);
CREATE INDEX IF NOT EXISTS idx_cleaned_customer ON cleaned_transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_cleaned_merchant ON cleaned_transactions(merchant_id);
CREATE INDEX IF NOT EXISTS idx_cleaned_category ON cleaned_transactions(category);
CREATE INDEX IF NOT EXISTS idx_cleaned_status ON cleaned_transactions(status);
CREATE INDEX IF NOT EXISTS idx_cleaned_anomaly ON cleaned_transactions(anomaly_flag);

-- 3. Quarantined Transactions Table (Rejected/Corrupt/Duplicate rows)
CREATE TABLE IF NOT EXISTS quarantined_transactions (
    quarantine_id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_id INTEGER,
    transaction_id TEXT,
    timestamp TEXT,
    customer_id TEXT,
    merchant_id TEXT,
    amount REAL,
    category TEXT,
    status TEXT,
    quarantine_reason TEXT NOT NULL,
    quarantined_at TEXT DEFAULT (datetime('now'))
);

-- 4. Anomaly Findings Table
CREATE TABLE IF NOT EXISTS anomaly_findings (
    finding_id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT,
    customer_id TEXT,
    merchant_id TEXT,
    rule_name TEXT NOT NULL,
    reason TEXT NOT NULL,
    severity TEXT NOT NULL, -- 'HIGH', 'MEDIUM', 'LOW'
    metric_value REAL,
    threshold_value REAL,
    detected_at TEXT DEFAULT (datetime('now')),
    details TEXT
);

CREATE INDEX IF NOT EXISTS idx_anomaly_tx ON anomaly_findings(transaction_id);
CREATE INDEX IF NOT EXISTS idx_anomaly_rule ON anomaly_findings(rule_name);
CREATE INDEX IF NOT EXISTS idx_anomaly_severity ON anomaly_findings(severity);

-- 5. Data Quality Reports Table
CREATE TABLE IF NOT EXISTS data_quality_reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_timestamp TEXT DEFAULT (datetime('now')),
    source_filename TEXT,
    total_records INTEGER,
    valid_records INTEGER,
    invalid_records INTEGER,
    duplicate_records INTEGER,
    missing_values_json TEXT,
    invalid_amounts INTEGER,
    invalid_timestamps INTEGER,
    status TEXT -- 'HEALTHY', 'WARNING', 'CRITICAL'
);

-- 6. Configurable Thresholds Table
CREATE TABLE IF NOT EXISTS system_config (
    config_key TEXT PRIMARY KEY,
    config_value REAL NOT NULL,
    description TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Insert default threshold configurations
INSERT OR IGNORE INTO system_config (config_key, config_value, description) VALUES
('high_value_threshold', 50000.0, 'Transactions with amount exceeding this value are flagged as high-value anomalies'),
('velocity_window_minutes', 5.0, 'Time window in minutes to detect repeated transactions from the same customer'),
('velocity_count_threshold', 3.0, 'Number of transactions within velocity window that triggers rapid-fire anomaly'),
('customer_zscore_threshold', 2.5, 'Number of standard deviations above customer historical mean to flag as unusual spend'),
('min_customer_history_for_zscore', 3.0, 'Minimum historical transactions required before applying statistical z-score rule');

