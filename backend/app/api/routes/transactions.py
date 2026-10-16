from fastapi import APIRouter, Query, HTTPException, status
from typing import Optional
from ...services.transaction_service import TransactionService
from ...models.schemas import TransactionsResponse, TransactionItem

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("", response_model=TransactionsResponse)
def get_transactions(
    search: Optional[str] = Query(None, description="Search by transaction ID or customer ID"),
    category: Optional[str] = Query(None, description="Filter by Category"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by Status: SUCCESS, FAILED, PENDING"),
    merchant_id: Optional[str] = Query(None, description="Filter by Merchant ID"),
    anomaly_flag: Optional[int] = Query(None, description="0 = Normal, 1 = Flagged Anomaly"),
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    min_amount: Optional[float] = Query(None, description="Minimum transaction amount"),
    max_amount: Optional[float] = Query(None, description="Maximum transaction amount"),
    sort_by: str = Query("timestamp", description="Sort column: timestamp, amount, transaction_id, customer_id, merchant_id, category, status"),
    sort_dir: str = Query("desc", description="Sort direction: asc, desc"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size limit")
):
    """Search, filter, sort, and paginate through validated UPI transactions."""
    return TransactionService.get_transactions(
        search=search,
        category=category,
        status=status_filter,
        merchant_id=merchant_id,
        anomaly_flag=anomaly_flag,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size
    )

@router.get("/{transaction_id}", response_model=TransactionItem)
def get_transaction(transaction_id: str):
    """Retrieve detailed record for a specific transaction ID."""
    tx = TransactionService.get_transaction_by_id(transaction_id)
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' was not found in cleaned dataset."
        )
    return tx

