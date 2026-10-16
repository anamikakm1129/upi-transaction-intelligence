import pytest
import pandas as pd
from backend.app.database.connection import init_db, clear_all_data, execute_query, execute_one
from backend.app.processing.ingestion import process_and_load_dataset
from backend.app.database.queries import (
    SQL_DASHBOARD_KPIS,
    SQL_DAILY_TRENDS,
    SQL_HOURLY_TRENDS,
    SQL_CATEGORY_DISTRIBUTION,
    SQL_CUSTOMER_SUMMARIES,
    SQL_MERCHANT_SUMMARIES
)

def create_test_df():
    return pd.DataFrame([
        {
            "transaction_id": f"TXN_TEST_{i:04d}",
            "timestamp": f"2026-10-{i%20+1:02d} {10+i%12:02d}:30:00",
            "customer_id": f"cust_{i%4}@okaxis",
            "merchant_id": f"merch_{i%3}@hdfc",
            "amount": float(150 * (i + 1)),
            "category": "Food" if i % 2 == 0 else "Shopping",
            "status": "SUCCESS" if i % 5 != 0 else "FAILED",
            "payment_method": "UPI_QR",
            "bank_reference_number": f"REF{1000+i}",
            "device_type": "Android"
        }
        for i in range(30)
    ])

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    clear_all_data()
    process_and_load_dataset(create_test_df(), "test_dataset.csv", clear_existing=True)
    yield
    clear_all_data()

def test_sql_dashboard_kpis():
    row = execute_one(SQL_DASHBOARD_KPIS, {"start_date": None, "end_date": None})
    assert row is not None
    assert row["total_transactions"] > 0
    assert row["total_value"] > 0
    assert row["avg_amount"] > 0
    assert row["active_customers"] > 0

def test_sql_daily_trends_window_functions():
    rows = execute_query(SQL_DAILY_TRENDS, {"start_date": None, "end_date": None})
    assert len(rows) > 0
    # Check window function output
    first_row = rows[0]
    assert "rolling_3day_avg" in first_row
    assert "prev_day_count" in first_row

def test_sql_hourly_trends():
    rows = execute_query(SQL_HOURLY_TRENDS, {"start_date": None, "end_date": None})
    assert len(rows) > 0
    assert any(r["volume_share_pct"] > 0 for r in rows)

def test_sql_customer_summaries_cte_and_rank():
    rows = execute_query(SQL_CUSTOMER_SUMMARIES, {"search": None, "limit": 10, "offset": 0})
    assert len(rows) > 0
    assert "favorite_category" in rows[0]
    assert "spend_rank" in rows[0]
    assert rows[0]["spend_rank"] == 1

def test_sql_merchant_summaries_cte_and_rank():
    rows = execute_query(SQL_MERCHANT_SUMMARIES, {"search": None, "limit": 10, "offset": 0})
    assert len(rows) > 0
    assert "peak_hour" in rows[0]
    assert "volume_rank" in rows[0]

