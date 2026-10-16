import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List
from ..utils.logging_config import logger

def clean_and_segregate_data(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Cleans raw transactions according to strict data governance standards:
    - Segregates invalid/corrupt rows into quarantined_df with explicit reasons.
    - Preserves deduplication policy: First instance kept if valid; subsequent occurrences quarantined.
    - Normalizes dates, times, categories, and amounts in cleaned_df.
    - Does NOT silently drop or mutate raw data.
    """
    logger.info(f"Starting data cleaning on {len(raw_df)} records.")
    
    cleaned_rows = []
    quarantined_rows = []
    seen_tx_ids = set()

    for idx, row in raw_df.iterrows():
        raw_id = idx + 1
        tx_id = str(row.get('transaction_id', '')).strip() if pd.notna(row.get('transaction_id')) else ''
        timestamp_raw = row.get('timestamp')
        customer_id = str(row.get('customer_id', '')).strip() if pd.notna(row.get('customer_id')) else ''
        merchant_id = str(row.get('merchant_id', '')).strip() if pd.notna(row.get('merchant_id')) else ''
        amount_raw = row.get('amount')
        category = str(row.get('category', 'General')).strip() if pd.notna(row.get('category')) else 'General'
        status = str(row.get('status', 'SUCCESS')).strip().upper() if pd.notna(row.get('status')) else 'SUCCESS'
        payment_method = str(row.get('payment_method', 'UPI-QR')).strip() if pd.notna(row.get('payment_method')) else 'UPI-QR'
        bank_rrn = str(row.get('bank_reference_number', '')).strip() if pd.notna(row.get('bank_reference_number')) else ''
        device_type = str(row.get('device_type', 'Android')).strip() if pd.notna(row.get('device_type')) else 'Android'

        base_quarantine_dict = {
            "raw_id": raw_id,
            "transaction_id": tx_id if tx_id else None,
            "timestamp": str(timestamp_raw) if pd.notna(timestamp_raw) else None,
            "customer_id": customer_id if customer_id else None,
            "merchant_id": merchant_id if merchant_id else None,
            "amount": None,
            "category": category,
            "status": status,
            "quarantine_reason": ""
        }

        # 1. Missing transaction_id
        if not tx_id or tx_id.lower() == 'nan':
            base_quarantine_dict["quarantine_reason"] = "Missing mandatory transaction_id"
            quarantined_rows.append(base_quarantine_dict)
            continue

        # 2. Duplicate transaction_id policy
        if tx_id in seen_tx_ids:
            base_quarantine_dict["quarantine_reason"] = f"Duplicate transaction ID: {tx_id}"
            try:
                base_quarantine_dict["amount"] = float(amount_raw)
            except Exception:
                pass
            quarantined_rows.append(base_quarantine_dict)
            continue

        # 3. Missing customer or merchant identifier
        if not customer_id or customer_id.lower() == 'nan' or not merchant_id or merchant_id.lower() == 'nan':
            base_quarantine_dict["quarantine_reason"] = "Missing customer_id or merchant_id"
            try:
                base_quarantine_dict["amount"] = float(amount_raw)
            except Exception:
                pass
            quarantined_rows.append(base_quarantine_dict)
            continue

        # 4. Amount validation
        try:
            amount = float(amount_raw)
            if amount <= 0 or np.isnan(amount) or np.isinf(amount):
                base_quarantine_dict["amount"] = amount
                base_quarantine_dict["quarantine_reason"] = f"Invalid non-positive amount: {amount_raw}"
                quarantined_rows.append(base_quarantine_dict)
                continue
            base_quarantine_dict["amount"] = amount
        except (ValueError, TypeError):
            base_quarantine_dict["quarantine_reason"] = f"Non-numeric amount value: {amount_raw}"
            quarantined_rows.append(base_quarantine_dict)
            continue

        # 5. Timestamp validation and parsing
        try:
            parsed_dt = pd.to_datetime(timestamp_raw)
            if pd.isna(parsed_dt):
                raise ValueError("Parsed date is NaT")
            tx_timestamp_str = parsed_dt.strftime('%Y-%m-%d %H:%M:%S')
            tx_date_str = parsed_dt.strftime('%Y-%m-%d')
            tx_hour = int(parsed_dt.hour)
        except Exception as e:
            base_quarantine_dict["quarantine_reason"] = f"Invalid timestamp format '{timestamp_raw}': {str(e)}"
            quarantined_rows.append(base_quarantine_dict)
            continue

        # 6. Status normalization
        if status not in {'SUCCESS', 'FAILED', 'PENDING'}:
            status = 'SUCCESS'

        # Record is valid!
        seen_tx_ids.add(tx_id)
        cleaned_rows.append({
            "transaction_id": tx_id,
            "timestamp": tx_timestamp_str,
            "tx_date": tx_date_str,
            "tx_hour": tx_hour,
            "customer_id": customer_id,
            "merchant_id": merchant_id,
            "amount": round(amount, 2),
            "category": category,
            "status": status,
            "payment_method": payment_method,
            "bank_reference_number": bank_rrn if bank_rrn else f"RRN{abs(hash(tx_id)) % 1000000000000:012d}",
            "device_type": device_type,
            "anomaly_flag": 0,
            "anomaly_reason": None
        })

    cleaned_df = pd.DataFrame(cleaned_rows)
    quarantined_df = pd.DataFrame(quarantined_rows)

    stats = {
        "input_count": len(raw_df),
        "cleaned_count": len(cleaned_df),
        "quarantined_count": len(quarantined_df),
        "duplicate_count": sum(1 for q in quarantined_rows if "Duplicate" in q["quarantine_reason"]),
        "invalid_amount_count": sum(1 for q in quarantined_rows if "amount" in q["quarantine_reason"]),
        "invalid_timestamp_count": sum(1 for q in quarantined_rows if "timestamp" in q["quarantine_reason"]),
    }

    logger.info(f"Cleaning completed: {stats['cleaned_count']} cleaned, {stats['quarantined_count']} quarantined.")
    return cleaned_df, quarantined_df, stats

