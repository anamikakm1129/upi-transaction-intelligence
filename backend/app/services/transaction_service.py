from typing import Dict, Any, List, Optional
import math
from ..database.connection import execute_query, execute_one
from ..utils.logging_config import logger

ALLOWED_SORT_COLUMNS = {
    'timestamp': 'timestamp',
    'amount': 'amount',
    'transaction_id': 'transaction_id',
    'customer_id': 'customer_id',
    'merchant_id': 'merchant_id',
    'category': 'category',
    'status': 'status',
    'anomaly_flag': 'anomaly_flag'
}

class TransactionService:
    @staticmethod
    def get_transactions(
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        merchant_id: Optional[str] = None,
        anomaly_flag: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        sort_by: str = 'timestamp',
        sort_dir: str = 'desc',
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Retrieve filtered, parameterized, paginated transactions.
        Guarantees protection against SQL injection.
        """
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        offset = (page - 1) * page_size

        where_clauses = ["1=1"]
        params: Dict[str, Any] = {}

        if search and search.strip():
            where_clauses.append("(transaction_id LIKE :search OR customer_id LIKE :search OR bank_reference_number LIKE :search)")
            params["search"] = f"%{search.strip()}%"

        if category and category.strip():
            where_clauses.append("category = :category")
            params["category"] = category.strip()

        if status and status.strip():
            where_clauses.append("status = :status")
            params["status"] = status.strip().upper()

        if merchant_id and merchant_id.strip():
            where_clauses.append("merchant_id = :merchant_id")
            params["merchant_id"] = merchant_id.strip()

        if anomaly_flag is not None:
            where_clauses.append("anomaly_flag = :anomaly_flag")
            params["anomaly_flag"] = int(anomaly_flag)

        if start_date and start_date.strip():
            where_clauses.append("tx_date >= :start_date")
            params["start_date"] = start_date.strip()

        if end_date and end_date.strip():
            where_clauses.append("tx_date <= :end_date")
            params["end_date"] = end_date.strip()

        if min_amount is not None:
            where_clauses.append("amount >= :min_amount")
            params["min_amount"] = float(min_amount)

        if max_amount is not None:
            where_clauses.append("amount <= :max_amount")
            params["max_amount"] = float(max_amount)

        where_sql = " AND ".join(where_clauses)

        # Count total matching
        count_sql = f"SELECT COUNT(*) AS total FROM cleaned_transactions WHERE {where_sql};"
        count_row = execute_one(count_sql, params)
        total = int(count_row["total"]) if count_row else 0

        # Validate sorting
        col = ALLOWED_SORT_COLUMNS.get(sort_by, 'timestamp')
        direction = 'ASC' if sort_dir.lower() == 'asc' else 'DESC'

        # Fetch records
        data_sql = f"""
            SELECT
                transaction_id, timestamp, tx_date, tx_hour, customer_id,
                merchant_id, amount, category, status, payment_method,
                bank_reference_number, device_type, anomaly_flag, anomaly_reason
            FROM cleaned_transactions
            WHERE {where_sql}
            ORDER BY {col} {direction}
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
    def get_transaction_by_id(transaction_id: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT
                transaction_id, timestamp, tx_date, tx_hour, customer_id,
                merchant_id, amount, category, status, payment_method,
                bank_reference_number, device_type, anomaly_flag, anomaly_reason
            FROM cleaned_transactions
            WHERE transaction_id = :tx_id;
        """
        return execute_one(sql, {"tx_id": transaction_id})

