import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from ..utils.logging_config import logger

REQUIRED_COLUMNS = [
    'transaction_id',
    'timestamp',
    'customer_id',
    'merchant_id',
    'amount',
    'category',
    'status'
]

OPTIONAL_COLUMNS = [
    'payment_method',
    'bank_reference_number',
    'device_type'
]

VALID_STATUSES = {'SUCCESS', 'FAILED', 'PENDING'}

def validate_dataframe_schema(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Validate that required columns are present in dataframe."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        return False, [f"Missing required columns: {', '.join(missing)}"]
    return True, []

def inspect_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform deep data quality analysis across dataframe.
    Calculates missing counts, duplicates, invalid amounts, and unparseable dates.
    """
    total_records = len(df)
    missing_by_col = {}
    
    for col in df.columns:
        missing_count = int(df[col].isna().sum())
        missing_by_col[col] = missing_count

    # Duplicate check on transaction_id
    duplicate_tx_count = 0
    if 'transaction_id' in df.columns:
        duplicate_tx_count = int(df['transaction_id'].duplicated().sum())

    # Invalid amount check
    invalid_amounts = 0
    if 'amount' in df.columns:
        def is_invalid_amount(val):
            try:
                num = float(val)
                return num <= 0 or np.isnan(num)
            except (ValueError, TypeError):
                return True
        invalid_amounts = int(df['amount'].apply(is_invalid_amount).sum())

    # Invalid timestamp check
    invalid_timestamps = 0
    if 'timestamp' in df.columns:
        def is_invalid_timestamp(val):
            if pd.isna(val) or str(val).strip() == '':
                return True
            try:
                pd.to_datetime(val)
                return False
            except Exception:
                return True
        invalid_timestamps = int(df['timestamp'].apply(is_invalid_timestamp).sum())

    invalid_records = invalid_amounts + invalid_timestamps + duplicate_tx_count
    valid_records = max(0, total_records - invalid_records)

    # Health status evaluation
    if total_records == 0:
        status = "CRITICAL"
    elif invalid_records == 0:
        status = "HEALTHY"
    elif (invalid_records / total_records) < 0.15:
        status = "WARNING"
    else:
        status = "CRITICAL"

    logger.info(
        f"Data quality inspected: total={total_records}, valid={valid_records}, "
        f"invalid={invalid_records}, duplicates={duplicate_tx_count}, status={status}"
    )

    return {
        "total_records": total_records,
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "duplicate_records": duplicate_tx_count,
        "missing_values_json": missing_by_col,
        "invalid_amounts": invalid_amounts,
        "invalid_timestamps": invalid_timestamps,
        "status": status
    }

