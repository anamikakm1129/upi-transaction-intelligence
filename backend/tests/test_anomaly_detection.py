import pytest
import pandas as pd
from backend.app.processing.anomaly_detection import detect_anomalies

def test_high_value_anomaly_detection():
    cleaned_df = pd.DataFrame([
        {
            "transaction_id": "TX_HIGH",
            "timestamp": "2026-10-10 10:00:00",
            "tx_date": "2026-10-10",
            "tx_hour": 10,
            "customer_id": "cust1@oksbi",
            "merchant_id": "croma@tata",
            "amount": 75000.0, # > 50,000
            "category": "Shopping & E-Commerce",
            "status": "SUCCESS",
            "payment_method": "UPI-Collect",
            "bank_reference_number": "421111222233",
            "device_type": "Android",
            "anomaly_flag": 0,
            "anomaly_reason": None
        }
    ])
    quarantined_df = pd.DataFrame([])
    config = {"high_value_threshold": 50000.0}

    res_df, findings = detect_anomalies(cleaned_df, quarantined_df, config)
    assert res_df.iloc[0]["anomaly_flag"] == 1
    assert any(f["rule_name"] == "High-Value Transaction" for f in findings)

def test_velocity_burst_anomaly_detection():
    # 3 transactions within 3 minutes by same customer
    cleaned_df = pd.DataFrame([
        {
            "transaction_id": f"TX_VEL_{i}",
            "timestamp": f"2026-10-10 10:0{i}:00",
            "tx_date": "2026-10-10",
            "tx_hour": 10,
            "customer_id": "burst_cust@oksbi",
            "merchant_id": "blinkit@axis",
            "amount": 500.0,
            "category": "Grocery & Supermarket",
            "status": "SUCCESS",
            "payment_method": "UPI-QR",
            "bank_reference_number": f"42111122223{i}",
            "device_type": "Android",
            "anomaly_flag": 0,
            "anomaly_reason": None
        }
        for i in range(3)
    ])
    quarantined_df = pd.DataFrame([])
    config = {
        "velocity_window_minutes": 5.0,
        "velocity_count_threshold": 3
    }

    res_df, findings = detect_anomalies(cleaned_df, quarantined_df, config)
    assert all(res_df["anomaly_flag"] == 1)
    assert any(f["rule_name"] == "Velocity Spike" for f in findings)

