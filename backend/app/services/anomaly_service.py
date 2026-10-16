from typing import Dict, Any, List, Optional
import math
from ..database.connection import execute_query, execute_one, execute_commit
from ..utils.logging_config import logger

class AnomalyService:
    @staticmethod
    def get_anomalies(
        rule_name: Optional[str] = None,
        severity: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        offset = (page - 1) * page_size

        where_clauses = ["1=1"]
        params: Dict[str, Any] = {}

        if rule_name and rule_name.strip():
            where_clauses.append("rule_name = :rule_name")
            params["rule_name"] = rule_name.strip()

        if severity and severity.strip():
            where_clauses.append("severity = :severity")
            params["severity"] = severity.strip().upper()

        if search and search.strip():
            where_clauses.append("(transaction_id LIKE :search OR customer_id LIKE :search OR merchant_id LIKE :search OR reason LIKE :search)")
            params["search"] = f"%{search.strip()}%"

        where_sql = " AND ".join(where_clauses)

        count_sql = f"SELECT COUNT(*) AS total FROM anomaly_findings WHERE {where_sql};"
        count_row = execute_one(count_sql, params)
        total = int(count_row["total"]) if count_row else 0

        data_sql = f"""
            SELECT
                finding_id, transaction_id, customer_id, merchant_id,
                rule_name, reason, severity, metric_value, threshold_value,
                detected_at, details
            FROM anomaly_findings
            WHERE {where_sql}
            ORDER BY finding_id DESC
            LIMIT :limit OFFSET :offset;
        """
        params["limit"] = page_size
        params["offset"] = offset

        rows = execute_query(data_sql, params)
        total_pages = math.ceil(total / page_size) if total > 0 else 1

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "data": rows
        }

    @staticmethod
    def get_system_config() -> List[Dict[str, Any]]:
        return execute_query("SELECT config_key, config_value, description, updated_at FROM system_config;")

    @staticmethod
    def update_system_config(updates: Dict[str, float]) -> Dict[str, Any]:
        for key, val in updates.items():
            if val is not None:
                execute_commit(
                    "UPDATE system_config SET config_value = :val, updated_at = datetime('now') WHERE config_key = :key;",
                    {"val": float(val), "key": key}
                )
        return {item["config_key"]: item["config_value"] for item in execute_query("SELECT config_key, config_value FROM system_config;")}

