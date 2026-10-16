import json
import pandas as pd
from typing import Dict, Any, List, Optional
from ..database.connection import execute_one, execute_query
from ..processing.ingestion import process_and_load_dataset
from ..processing.validation import validate_dataframe_schema, inspect_data_quality, REQUIRED_COLUMNS
from ..utils.logging_config import logger

class DataQualityService:
    @staticmethod
    def get_latest_summary() -> Dict[str, Any]:
        sql = """
            SELECT
                report_id, run_timestamp, source_filename, total_records,
                valid_records, invalid_records, duplicate_records,
                missing_values_json, invalid_amounts, invalid_timestamps, status
            FROM data_quality_reports
            ORDER BY report_id DESC
            LIMIT 1;
        """
        row = execute_one(sql)
        if not row:
            return {
                "report_id": None,
                "run_timestamp": None,
                "source_filename": None,
                "total_records": 0,
                "valid_records": 0,
                "invalid_records": 0,
                "duplicate_records": 0,
                "missing_values_json": {},
                "invalid_amounts": 0,
                "invalid_timestamps": 0,
                "status": "NOT_ANALYZED"
            }
        
        missing_json = row.get("missing_values_json")
        try:
            missing_dict = json.loads(missing_json) if missing_json else {}
        except Exception:
            missing_dict = {}

        return {
            "report_id": row["report_id"],
            "run_timestamp": row["run_timestamp"],
            "source_filename": row["source_filename"],
            "total_records": row["total_records"],
            "valid_records": row["valid_records"],
            "invalid_records": row["invalid_records"],
            "duplicate_records": row["duplicate_records"],
            "missing_values_json": missing_dict,
            "invalid_amounts": row["invalid_amounts"],
            "invalid_timestamps": row["invalid_timestamps"],
            "status": row["status"]
        }

    @staticmethod
    def get_quarantined_records(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        offset = (page - 1) * page_size

        count_row = execute_one("SELECT COUNT(*) AS total FROM quarantined_transactions;")
        total = int(count_row["total"]) if count_row else 0

        rows = execute_query(
            "SELECT * FROM quarantined_transactions ORDER BY quarantine_id ASC LIMIT :limit OFFSET :offset;",
            {"limit": page_size, "offset": offset}
        )
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": rows
        }

    @staticmethod
    def validate_uploaded_csv(df: pd.DataFrame, filename: str) -> Dict[str, Any]:
        """Validate uploaded CSV schema and inspect data quality before confirmation."""
        is_valid_schema, errors = validate_dataframe_schema(df)
        dq_summary = inspect_data_quality(df)
        dq_summary['source_filename'] = filename

        preview_rows = df.head(5).to_dict(orient='records')
        for r in preview_rows:
            for k, v in list(r.items()):
                if pd.isna(v):
                    r[k] = None

        return {
            "filename": filename,
            "total_records": len(df),
            "is_valid_schema": is_valid_schema,
            "errors": errors,
            "columns_found": list(df.columns),
            "required_columns": REQUIRED_COLUMNS,
            "missing_columns": [c for c in REQUIRED_COLUMNS if c not in df.columns],
            "data_quality_preview": dq_summary,
            "preview_rows": preview_rows
        }

    @staticmethod
    def process_uploaded_csv(df: pd.DataFrame, filename: str) -> Dict[str, Any]:
        """Processes an uploaded CSV dataset."""
        return process_and_load_dataset(df, source_filename=filename, clear_existing=True)

    @staticmethod
    def reprocess_current_dataset() -> Dict[str, Any]:
        """Re-evaluates processing against existing raw transactions."""
        rows = execute_query("""
            SELECT transaction_id, timestamp, customer_id, merchant_id, amount,
                   category, status, payment_method, bank_reference_number, device_type
            FROM raw_transactions
            ORDER BY raw_id ASC;
        """)
        if not rows:
            raise ValueError("No uploaded transaction dataset found. Please upload a transaction CSV first.")
        df = pd.DataFrame(rows)
        return process_and_load_dataset(df, source_filename="reprocessed_upload.csv", clear_existing=True)
