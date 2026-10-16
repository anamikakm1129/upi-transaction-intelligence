import pytest
import pandas as pd
from backend.app.processing.validation import validate_dataframe_schema, inspect_data_quality

def test_validate_dataframe_schema_valid():
    df = pd.DataFrame([{
        "transaction_id": "TX100",
        "timestamp": "2026-10-10 10:00:00",
        "customer_id": "cust1@oksbi",
        "merchant_id": "swiggy@icici",
        "amount": 500.0,
        "category": "Food & Dining",
        "status": "SUCCESS"
    }])
    is_valid, errors = validate_dataframe_schema(df)
    assert is_valid is True
    assert len(errors) == 0

def test_validate_dataframe_schema_missing_columns():
    df = pd.DataFrame([{
        "transaction_id": "TX100",
        "amount": 500.0
    }])
    is_valid, errors = validate_dataframe_schema(df)
    assert is_valid is False
    assert any("timestamp" in err for err in errors)
    assert any("customer_id" in err for err in errors)

def test_inspect_data_quality_detects_issues():
    df = pd.DataFrame([
        {"transaction_id": "TX1", "timestamp": "2026-10-10 10:00:00", "amount": 250.0},
        {"transaction_id": "TX2", "timestamp": "invalid_date", "amount": 300.0},
        {"transaction_id": "TX3", "timestamp": "2026-10-10 11:00:00", "amount": -100.0}, # negative
        {"transaction_id": "TX1", "timestamp": "2026-10-10 12:00:00", "amount": 400.0}, # duplicate TX1
    ])
    dq = inspect_data_quality(df)
    assert dq["total_records"] == 4
    assert dq["duplicate_records"] == 1
    assert dq["invalid_amounts"] == 1
    assert dq["invalid_timestamps"] == 1
    assert dq["status"] in ["WARNING", "CRITICAL"]

