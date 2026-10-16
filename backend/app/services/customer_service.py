from typing import Dict, Any, List, Optional
import math
from ..database.connection import execute_query, execute_one
from ..database.queries import (
    SQL_CUSTOMER_SUMMARIES,
    SQL_CUSTOMER_COUNT,
    SQL_CUSTOMER_DETAIL,
    SQL_CUSTOMER_HISTORY
)
from ..utils.logging_config import logger

class CustomerService:
    @staticmethod
    def get_customers(
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        offset = (page - 1) * page_size

        search_val = search.strip() if search and search.strip() else None
        params = {"search": search_val, "limit": page_size, "offset": offset}

        count_row = execute_one(SQL_CUSTOMER_COUNT, {"search": search_val})
        total = int(count_row["total_customers"]) if count_row else 0

        rows = execute_query(SQL_CUSTOMER_SUMMARIES, params)
        total_pages = math.ceil(total / page_size) if total > 0 else 1

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "data": rows
        }

    @staticmethod
    def get_customer_profile(customer_id: str, history_limit: int = 30) -> Optional[Dict[str, Any]]:
        detail = execute_one(SQL_CUSTOMER_DETAIL, {"customer_id": customer_id})
        if not detail:
            return None
        
        history = execute_query(SQL_CUSTOMER_HISTORY, {"customer_id": customer_id, "limit": history_limit})
        detail["history"] = history
        return detail

