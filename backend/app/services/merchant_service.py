from typing import Dict, Any, List, Optional
import math
from ..database.connection import execute_query, execute_one
from ..database.queries import (
    SQL_MERCHANT_SUMMARIES,
    SQL_MERCHANT_COUNT,
    SQL_MERCHANT_DETAIL,
    SQL_MERCHANT_HOURLY
)
from ..utils.logging_config import logger

class MerchantService:
    @staticmethod
    def get_merchants(
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        offset = (page - 1) * page_size

        search_val = search.strip() if search and search.strip() else None
        params = {"search": search_val, "limit": page_size, "offset": offset}

        count_row = execute_one(SQL_MERCHANT_COUNT, {"search": search_val})
        total = int(count_row["total_merchants"]) if count_row else 0

        rows = execute_query(SQL_MERCHANT_SUMMARIES, params)
        total_pages = math.ceil(total / page_size) if total > 0 else 1

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "data": rows
        }

    @staticmethod
    def get_merchant_profile(merchant_id: str) -> Optional[Dict[str, Any]]:
        detail = execute_one(SQL_MERCHANT_DETAIL, {"merchant_id": merchant_id})
        if not detail:
            return None
        
        hourly = execute_query(SQL_MERCHANT_HOURLY, {"merchant_id": merchant_id})
        detail["hourly_activity"] = hourly
        return detail

