import pytest
import pandas as pd
from backend.app.processing.cleaning import clean_and_segregate_data

def test_clean_and_segregate_data_quarantines_duplicates():
    raw_df = pd.DataFrame([
        {
            "transaction_id": "TX_DUP",
            "timestamp": "2026-10-10 10:00:00",
            "customer_id": "cust1@oksbi",
            "merchant_id": "swiggy@icici",
            "amount": 250.0,
            "category": "Food & Dining",
            "status": "SUCCESS"
        },
        {
            "transaction_id": "TX_DUP", # duplicate
            "timestamp": "2026-10-10 10:05:00",
            "customer_id": "cust1@oksbi",
            "merchant_id": "swiggy@icici",
            "amount": 250.0,
            "category": "Food & Dining",
            "status": "SUCCESS"
        }
    ])
    cleaned_df, quarantined_df, stats = clean_and_segregate_data(raw_df)
    assert len(cleaned_df) == 1
    assert len(quarantined_df) == 1
    assert "Duplicate transaction ID" in quarantined_df.iloc[0]["quarantine_reason"]

def test_clean_and_segregate_data_quarantines_invalid_amounts():
    raw_df = pd.DataFrame([
        {
            "transaction_id": "TX_NEG",
            "timestamp": "2026-10-10 10:00:00",
            "customer_id": "cust1@oksbi",
            "merchant_id": "swiggy@icici",
            "amount": -50.0, # invalid
            "category": "Food & Dining",
            "status": "SUCCESS"
        }
    ])
    cleaned_df, quarantined_df, stats = clean_and_segregate_data(raw_df)
    assert len(cleaned_df) == 0
    assert len(quarantined_df) == 1
    assert "non-positive amount" in quarantined_df.iloc[0]["quarantine_reason"]

