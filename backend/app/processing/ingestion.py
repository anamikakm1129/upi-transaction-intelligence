import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional
from .validation import validate_dataframe_schema, inspect_data_quality
from .cleaning import clean_and_segregate_data
from .anomaly_detection import detect_anomalies
from ..database.connection import get_db_connection, execute_query, ensure_db_dir, DB_DIR
from ..utils.logging_config import logger

PARQUET_PATH = os.path.join(DB_DIR, "processed", "cleaned_transactions.parquet")

def get_current_system_config() -> Dict[str, float]:
    """Retrieve active system config thresholds from database."""
    try:
        rows = execute_query("SELECT config_key, config_value FROM system_config;")
        return {r['config_key']: float(r['config_value']) for r in rows}
    except Exception as e:
        logger.warning(f"Could not load system_config from DB: {e}. Using defaults.")
        return {
            'high_value_threshold': 50000.0,
            'velocity_window_minutes': 5.0,
            'velocity_count_threshold': 3.0,
            'customer_zscore_threshold': 2.5,
            'min_customer_history_for_zscore': 3.0
        }

def process_and_load_dataset(
    df_raw: pd.DataFrame,
    source_filename: str = "dataset.csv",
    clear_existing: bool = True
) -> Dict[str, Any]:
    """
    Execute full end-to-end data processing pipeline:
    1. Validate schema
    2. Inspect data quality
    3. Clean and segregate valid vs quarantined records
    4. Detect rule-based anomalies
    5. Persist to SQLite (raw, cleaned, quarantined, anomalies, DQ report)
    6. Export cleaned dataset to Parquet
    """
    logger.info(f"Processing dataset '{source_filename}' with {len(df_raw)} records (clear_existing={clear_existing})")
    ensure_db_dir()

    # Step 1: Validate Schema
    is_valid_schema, errors = validate_dataframe_schema(df_raw)
    if not is_valid_schema:
        raise ValueError(f"Schema validation failed: {'; '.join(errors)}")

    # Step 2: Data Quality Inspection
    dq_summary = inspect_data_quality(df_raw)
    dq_summary['source_filename'] = source_filename
    dq_summary['run_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Step 3: Clean and Segregate
    cleaned_df, quarantined_df, clean_stats = clean_and_segregate_data(df_raw)

    # Step 4: Detect Rule-based Anomalies
    config = get_current_system_config()
    final_cleaned_df, anomaly_findings = detect_anomalies(cleaned_df, quarantined_df, config)

    # Step 5: Persist to SQLite
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if clear_existing:
            cursor.execute("DELETE FROM cleaned_transactions;")
            cursor.execute("DELETE FROM quarantined_transactions;")
            cursor.execute("DELETE FROM anomaly_findings;")
            cursor.execute("DELETE FROM data_quality_reports;")
            cursor.execute("DELETE FROM raw_transactions;")

        # Save raw transactions
        raw_records = []
        batch_id = datetime.now().strftime('%Y%m%d%H%M%S')
        for idx, row in df_raw.iterrows():
            raw_records.append((
                str(row.get('transaction_id', '')),
                str(row.get('timestamp', '')),
                str(row.get('customer_id', '')),
                str(row.get('merchant_id', '')),
                float(row['amount']) if pd.notna(row.get('amount')) and isinstance(row.get('amount'), (int, float)) else None,
                str(row.get('category', '')),
                str(row.get('status', '')),
                str(row.get('payment_method', '')),
                str(row.get('bank_reference_number', '')),
                str(row.get('device_type', '')),
                f"{source_filename}_{batch_id}"
            ))
        cursor.executemany("""
            INSERT INTO raw_transactions (
                transaction_id, timestamp, customer_id, merchant_id, amount,
                category, status, payment_method, bank_reference_number, device_type, source_batch
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, raw_records)

        # Save cleaned transactions
        if not final_cleaned_df.empty:
            cleaned_records = []
            for _, r in final_cleaned_df.iterrows():
                cleaned_records.append((
                    r['transaction_id'],
                    r['timestamp'],
                    r['tx_date'],
                    int(r['tx_hour']),
                    r['customer_id'],
                    r['merchant_id'],
                    float(r['amount']),
                    r['category'],
                    r['status'],
                    r.get('payment_method'),
                    r.get('bank_reference_number'),
                    r.get('device_type'),
                    int(r['anomaly_flag']),
                    r['anomaly_reason']
                ))
            cursor.executemany("""
                INSERT OR REPLACE INTO cleaned_transactions (
                    transaction_id, timestamp, tx_date, tx_hour, customer_id,
                    merchant_id, amount, category, status, payment_method,
                    bank_reference_number, device_type, anomaly_flag, anomaly_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, cleaned_records)

        # Save quarantined transactions
        if not quarantined_df.empty:
            quarantined_records = []
            for _, q in quarantined_df.iterrows():
                quarantined_records.append((
                    int(q.get('raw_id', 0)),
                    q.get('transaction_id'),
                    q.get('timestamp'),
                    q.get('customer_id'),
                    q.get('merchant_id'),
                    q.get('amount'),
                    q.get('category'),
                    q.get('status'),
                    q.get('quarantine_reason')
                ))
            cursor.executemany("""
                INSERT INTO quarantined_transactions (
                    raw_id, transaction_id, timestamp, customer_id, merchant_id,
                    amount, category, status, quarantine_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, quarantined_records)

        # Save anomaly findings
        if anomaly_findings:
            findings_records = []
            for f in anomaly_findings:
                findings_records.append((
                    f.get('transaction_id'),
                    f.get('customer_id'),
                    f.get('merchant_id'),
                    f['rule_name'],
                    f['reason'],
                    f['severity'],
                    f.get('metric_value'),
                    f.get('threshold_value'),
                    f['detected_at'],
                    f.get('details')
                ))
            cursor.executemany("""
                INSERT INTO anomaly_findings (
                    transaction_id, customer_id, merchant_id, rule_name, reason,
                    severity, metric_value, threshold_value, detected_at, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, findings_records)

        # Save data quality report
        cursor.execute("""
            INSERT INTO data_quality_reports (
                run_timestamp, source_filename, total_records, valid_records,
                invalid_records, duplicate_records, missing_values_json,
                invalid_amounts, invalid_timestamps, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            dq_summary['run_timestamp'],
            dq_summary['source_filename'],
            dq_summary['total_records'],
            dq_summary['valid_records'],
            dq_summary['invalid_records'],
            dq_summary['duplicate_records'],
            json.dumps(dq_summary['missing_values_json']),
            dq_summary['invalid_amounts'],
            dq_summary['invalid_timestamps'],
            dq_summary['status']
        ))
        dq_summary['report_id'] = cursor.lastrowid
        conn.commit()

    # Step 6: Export Cleaned Dataset to Parquet
    parquet_saved_path = None
    if not final_cleaned_df.empty:
        try:
            final_cleaned_df.to_parquet(PARQUET_PATH, index=False, engine='pyarrow')
            parquet_saved_path = PARQUET_PATH
            logger.info(f"Cleaned dataset saved to Parquet: {PARQUET_PATH}")
        except Exception as e:
            logger.error(f"Failed to export Parquet: {e}")

    return {
        "success": True,
        "message": f"Successfully processed {len(df_raw)} records ({len(final_cleaned_df)} valid, {len(quarantined_df)} quarantined)",
        "data_quality": dq_summary,
        "cleaned_records_count": len(final_cleaned_df),
        "anomalies_detected_count": len(anomaly_findings),
        "parquet_saved_path": parquet_saved_path
    }

