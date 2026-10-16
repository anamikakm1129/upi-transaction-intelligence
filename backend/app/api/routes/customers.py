from fastapi import APIRouter, Query, HTTPException, status
from typing import Optional, Dict, Any
from ...services.customer_service import CustomerService
from ...models.schemas import CustomersResponse

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("", response_model=CustomersResponse)
def get_customers(
    search: Optional[str] = Query(None, description="Search by customer handle or VPA"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size limit")
):
    """Retrieve aggregated customer summaries computed via SQL CTEs and Window Functions."""
    return CustomerService.get_customers(search=search, page=page, page_size=page_size)

@router.get("/{customer_id}")
def get_customer_profile(customer_id: str):
    """Retrieve customer behavioral profile and transaction history."""
    profile = CustomerService.get_customer_profile(customer_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{customer_id}' not found."
        )
    return profile

