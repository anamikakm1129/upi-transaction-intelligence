from fastapi import APIRouter, Query, HTTPException, status
from typing import Optional
from ...services.merchant_service import MerchantService
from ...models.schemas import MerchantsResponse

router = APIRouter(prefix="/merchants", tags=["Merchants"])

@router.get("", response_model=MerchantsResponse)
def get_merchants(
    search: Optional[str] = Query(None, description="Search by merchant ID or category"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size limit")
):
    """Retrieve aggregated merchant summaries computed via SQL CTEs."""
    return MerchantService.get_merchants(search=search, page=page, page_size=page_size)

@router.get("/{merchant_id}")
def get_merchant_profile(merchant_id: str):
    """Retrieve merchant metrics, peak hour activity, and diurnal hourly breakdown."""
    profile = MerchantService.get_merchant_profile(merchant_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Merchant '{merchant_id}' not found."
        )
    return profile

