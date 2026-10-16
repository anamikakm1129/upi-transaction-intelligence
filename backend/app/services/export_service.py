import os
import io
import pandas as pd
from typing import Optional, Dict, Any, Tuple
from ..database.connection import execute_query, DB_DIR
from ..database.queries import (
    SQL_DAILY_TRENDS,
    SQL_CUSTOMER_SUMMARIES,
    SQL_MERCHANT_SUMMARIES,
    SQL_HOURLY_TRENDS
)
from ..processing.ingestion import PARQUET_PATH
from ..utils.logging_config import logger

class ExportService:
    @staticmethod
    def generate_report_csv(report_type: str) -> Tuple[str, str]:
        """
        Generate CSV content and filename for dashboard-ready reports from user uploaded data.
        Supported report_types:
        - daily: Daily transaction summaries
        - customers: Customer summaries
        - merchants: Merchant summaries
        - hourly: Hourly activity
        - anomalies: Anomaly findings
        - data_quality: Data-quality findings
        - transactions: Cleaned transaction records
        """
        report_type = report_type.lower().strip()

        if report_type == "daily":
            rows = execute_query(SQL_DAILY_TRENDS, {"start_date": None, "end_date": None})
            df = pd.DataFrame(rows)
            filename = "upi_daily_transaction_summary.csv"

        elif report_type == "customers":
            rows = execute_query(SQL_CUSTOMER_SUMMARIES, {"search": None, "limit": 10000, "offset": 0})
            df = pd.DataFrame(rows)
            filename = "upi_customer_summaries.csv"

        elif report_type == "merchants":
            rows = execute_query(SQL_MERCHANT_SUMMARIES, {"search": None, "limit": 10000, "offset": 0})
            df = pd.DataFrame(rows)
            filename = "upi_merchant_summaries.csv"

        elif report_type == "hourly":
            rows = execute_query(SQL_HOURLY_TRENDS, {"start_date": None, "end_date": None})
            df = pd.DataFrame(rows)
            filename = "upi_hourly_activity_summary.csv"

        elif report_type == "anomalies":
            rows = execute_query("SELECT * FROM anomaly_findings ORDER BY finding_id DESC;")
            df = pd.DataFrame(rows)
            filename = "upi_anomaly_findings.csv"

        elif report_type == "data_quality":
            rows = execute_query("SELECT * FROM data_quality_reports ORDER BY report_id DESC;")
            df = pd.DataFrame(rows)
            filename = "upi_data_quality_reports.csv"

        elif report_type == "transactions":
            rows = execute_query("SELECT * FROM cleaned_transactions ORDER BY timestamp DESC;")
            df = pd.DataFrame(rows)
            filename = "upi_cleaned_transactions.csv"

        else:
            raise ValueError(f"Unsupported report type '{report_type}'")

        if df.empty:
            raise ValueError(f"No records available to export for report '{report_type}'. Please upload and process a transaction CSV first.")

        output = io.StringIO()
        df.to_csv(output, index=False)
        return output.getvalue(), filename

    @staticmethod
    def get_parquet_path() -> Optional[str]:
        """Return path to processed cleaned parquet file if it exists."""
        if os.path.exists(PARQUET_PATH):
            return PARQUET_PATH
        return None
