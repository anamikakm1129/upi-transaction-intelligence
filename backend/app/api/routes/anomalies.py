from fastapi import APIRouter, Query, Body
from typing import Optional, Dict, Any, List
from ...services.anomaly_service import AnomalyService
from ...models.schemas import AnomaliesResponse, SystemConfigUpdate

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])

@router.get("", response_model=AnomaliesResponse)
def get_anomalies(
    rule_name: Optional[str] = Query(None, description="Filter by rule: High-Value Transaction, Velocity Spike, Unusual Customer Activity (Z-Score), Duplicate Record, Invalid Entry"),
    severity: Optional[str] = Query(None, description="Filter by severity: HIGH, MEDIUM, LOW"),
    search: Optional[str] = Query(None, description="Search by transaction, customer, or merchant"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size limit")
):
    """Retrieve rule-based anomaly findings flagged for review."""
    return AnomalyService.get_anomalies(
        rule_name=rule_name,
        severity=severity,
        search=search,
        page=page,
        page_size=page_size
    )

@router.get("/config")
def get_config():
    """Retrieve current configurable threshold parameters."""
    return AnomalyService.get_system_config()

@router.post("/config")
def update_config(config_updates: SystemConfigUpdate):
    """Update threshold configuration parameters (e.g. high_value_threshold, velocity_window)."""
    updates_dict = config_updates.model_dump(exclude_unset=True)
    return AnomalyService.update_system_config(updates_dict)

