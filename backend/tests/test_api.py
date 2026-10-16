import pytest
import pandas as pd
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.connection import init_db, clear_all_data
from backend.app.processing.ingestion import process_and_load_dataset

client = TestClient(app)

def create_api_test_df():
    return pd.DataFrame([
        {
            "transaction_id": f"TXN_API_{i:04d}",
            "timestamp": f"2026-10-{i%20+1:02d} {10+i%12:02d}:30:00",
            "customer_id": f"cust_{i%3}@okaxis",
            "merchant_id": f"merch_{i%2}@hdfc",
            "amount": float(120 * (i + 1)),
            "category": "Food" if i % 2 == 0 else "Shopping",
            "status": "SUCCESS" if i % 4 != 0 else "FAILED",
            "payment_method": "UPI_QR",
            "bank_reference_number": f"REF{2000+i}",
            "device_type": "Android"
        }
        for i in range(25)
    ])

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "UP"
    assert data["database_connected"] is True

def test_api_empty_state():
    """Verify that when no data is uploaded, endpoints return genuine empty state contracts."""
    clear_all_data()
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_transactions"] == 0
    assert data["total_value"] == 0.0

    res_dq = client.get("/api/data-quality/summary")
    assert res_dq.status_code == 200
    assert res_dq.json()["status"] == "NOT_ANALYZED"
    assert res_dq.json()["total_records"] == 0

    res_pat = client.get("/api/dashboard/patterns")
    assert res_pat.status_code == 200
    assert res_pat.json()["peak_hour"] is None

@pytest.fixture(scope="module")
def loaded_dataset():
    clear_all_data()
    process_and_load_dataset(create_api_test_df(), "api_test.csv", clear_existing=True)
    yield
    clear_all_data()

def test_api_dashboard_summary(loaded_dataset):
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_transactions" in data
    assert "total_value" in data
    assert data["total_transactions"] > 0

def test_api_dashboard_daily_trends(loaded_dataset):
    res = client.get("/api/dashboard/daily-trends")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_api_dashboard_hourly_trends(loaded_dataset):
    res = client.get("/api/dashboard/hourly-trends")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0 and len(data) <= 24

def test_api_dashboard_patterns(loaded_dataset):
    res = client.get("/api/dashboard/patterns")
    assert res.status_code == 200
    data = res.json()
    assert "peak_hour" in data
    assert "insights_narrative" in data
    assert len(data["insights_narrative"]) > 0

def test_api_transactions_pagination_and_filter(loaded_dataset):
    res = client.get("/api/transactions?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["data"]) <= 10

def test_api_customers(loaded_dataset):
    res = client.get("/api/customers?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert len(data["data"]) > 0

def test_api_merchants(loaded_dataset):
    res = client.get("/api/merchants?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert len(data["data"]) > 0

def test_api_anomalies(loaded_dataset):
    res = client.get("/api/anomalies?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data

def test_api_data_quality_summary(loaded_dataset):
    res = client.get("/api/data-quality/summary")
    assert res.status_code == 200
    data = res.json()
    assert "valid_records" in data
    assert "duplicate_records" in data
    assert data["status"] in ["HEALTHY", "WARNING", "ALERT"]


