from fastapi import APIRouter, Query
from typing import Optional, List, Dict, Any
from ...services.analytics_service import AnalyticsService
from ...models.schemas import (
    DashboardKpiResponse,
    DailyTrendItem,
    HourlyTrendItem,
    CategoryDistributionItem,
    PatternInsightsResponse
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardKpiResponse)
def get_dashboard_summary(
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD")
):
    """Retrieve core UPI KPI metrics (Total Volume, Value, Average Ticket, Flagged Rate)."""
    return AnalyticsService.get_dashboard_summary(start_date=start_date, end_date=end_date)

@router.get("/daily-trends", response_model=List[DailyTrendItem])
def get_daily_trends(
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD")
):
    """Retrieve daily transaction volumes, values, day-over-day growth, and rolling averages."""
    return AnalyticsService.get_daily_trends(start_date=start_date, end_date=end_date)

@router.get("/hourly-trends", response_model=List[HourlyTrendItem])
def get_hourly_trends(
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD")
):
    """Retrieve 24-hour diurnal volume and percentage distribution."""
    return AnalyticsService.get_hourly_trends(start_date=start_date, end_date=end_date)

@router.get("/category-distribution", response_model=List[CategoryDistributionItem])
def get_category_distribution(
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD")
):
    """Retrieve transaction distribution by category with percentage shares."""
    return AnalyticsService.get_category_distribution(start_date=start_date, end_date=end_date)

@router.get("/patterns", response_model=PatternInsightsResponse)
def get_pattern_insights():
    """Retrieve calculated diurnal and category pattern metrics with factual narratives."""
    return AnalyticsService.get_pattern_insights()

