import pytest
import pandas as pd
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.connection import init_db, clear_all_data
from backend.app.processing.ingestion import process_and_load_dataset

client = TestClient(app)

def create_export_test_df():
    return pd.DataFrame([
        {
            "transaction_id": f"TXN_EXP_{i:04d}",
            "timestamp": f"2026-10-{i%20+1:02d} {10+i%12:02d}:30:00",
            "customer_id": f"cust_{i%3}@okaxis",
            "merchant_id": f"merch_{i%2}@hdfc",
            "amount": float(250 * (i + 1)),
            "category": "Food" if i % 2 == 0 else "Shopping",
            "status": "SUCCESS" if i % 4 != 0 else "FAILED",
            "payment_method": "UPI_QR",
            "bank_reference_number": f"REF{3000+i}",
            "device_type": "Android"
        }
        for i in range(20)
    ])

def test_export_csv_when_empty_returns_400():
    clear_all_data()
    res = client.get("/api/reports/export?report_type=daily&format=csv")
    assert res.status_code == 400
    assert "No records available" in res.json()["detail"]

def test_export_parquet_when_empty_returns_404():
    clear_all_data()
    res = client.get("/api/reports/export?format=parquet")
    assert res.status_code == 404
    assert "Parquet processed dataset not found" in res.json()["detail"]

@pytest.fixture(scope="module")
def loaded_export_dataset():
    clear_all_data()
    process_and_load_dataset(create_export_test_df(), "export_test.csv", clear_existing=True)
    yield
    clear_all_data()

def test_export_csv_daily(loaded_export_dataset):
    res = client.get("/api/reports/export?report_type=daily&format=csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "tx_date" in res.text

def test_export_csv_customers(loaded_export_dataset):
    res = client.get("/api/reports/export?report_type=customers&format=csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "customer_id" in res.text

def test_export_csv_merchants(loaded_export_dataset):
    res = client.get("/api/reports/export?report_type=merchants&format=csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "merchant_id" in res.text

def test_export_parquet(loaded_export_dataset):
    res = client.get("/api/reports/export?format=parquet")
    assert res.status_code == 200
    assert "application/octet-stream" in res.headers["content-type"]
    assert len(res.content) > 0


