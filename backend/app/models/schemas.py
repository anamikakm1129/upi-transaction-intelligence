from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SystemConfigItem(BaseModel):
    config_key: str
    config_value: float
    description: Optional[str] = None

class SystemConfigUpdate(BaseModel):
    high_value_threshold: Optional[float] = None
    velocity_window_minutes: Optional[float] = None
    velocity_count_threshold: Optional[float] = None
    customer_zscore_threshold: Optional[float] = None

class TransactionItem(BaseModel):
    transaction_id: str
    timestamp: str
    tx_date: str
    tx_hour: int
    customer_id: str
    merchant_id: str
    amount: float
    category: str
    status: str
    payment_method: Optional[str] = None
    bank_reference_number: Optional[str] = None
    device_type: Optional[str] = None
    anomaly_flag: int = 0
    anomaly_reason: Optional[str] = None

class TransactionsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[TransactionItem]

class DashboardKpiResponse(BaseModel):
    total_transactions: int
    total_value: float
    avg_amount: float
    flagged_count: int
    flagged_rate_pct: float
    success_count: int
    failed_count: int
    pending_count: int
    active_customers: int
    active_merchants: int

class DailyTrendItem(BaseModel):
    tx_date: str
    tx_count: int
    tx_value: float
    avg_amount: float
    flagged_count: int
    success_count: int
    failed_count: int
    prev_day_count: Optional[int] = None
    dod_growth_pct: Optional[float] = None
    rolling_3day_avg: Optional[float] = None

class HourlyTrendItem(BaseModel):
    tx_hour: int
    tx_count: int
    tx_value: float
    avg_amount: float
    flagged_count: int
    volume_share_pct: float

class CategoryDistributionItem(BaseModel):
    category: str
    tx_count: int
    tx_value: float
    avg_amount: float
    flagged_count: int
    count_share_pct: float
    value_share_pct: float

class CustomerSummaryItem(BaseModel):
    customer_id: str
    total_transactions: int
    total_spent: float
    avg_amount: float
    first_tx: str
    last_tx: str
    flagged_count: int
    success_count: int
    failed_count: int
    favorite_category: str
    spend_rank: int

class CustomersResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[CustomerSummaryItem]

class MerchantSummaryItem(BaseModel):
    merchant_id: str
    category: str
    total_transactions: int
    total_value: float
    avg_amount: float
    success_count: int
    failed_count: int
    flagged_count: int
    peak_hour: int
    volume_rank: int

class MerchantsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[MerchantSummaryItem]

class AnomalyFindingItem(BaseModel):
    finding_id: int
    transaction_id: Optional[str] = None
    customer_id: Optional[str] = None
    merchant_id: Optional[str] = None
    rule_name: str
    reason: str
    severity: str
    metric_value: Optional[float] = None
    threshold_value: Optional[float] = None
    detected_at: str
    details: Optional[str] = None

class AnomaliesResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[AnomalyFindingItem]

class DataQualitySummaryResponse(BaseModel):
    report_id: Optional[int] = None
    run_timestamp: Optional[str] = None
    source_filename: Optional[str] = None
    total_records: int
    valid_records: int
    invalid_records: int
    duplicate_records: int
    missing_values_json: Dict[str, int]
    invalid_amounts: int
    invalid_timestamps: int
    status: str

class ProcessingRunResponse(BaseModel):
    success: bool
    message: str
    data_quality: DataQualitySummaryResponse
    cleaned_records_count: int
    anomalies_detected_count: int
    parquet_saved_path: Optional[str] = None

class PatternInsightsResponse(BaseModel):
    peak_hour: Optional[int] = None
    peak_hour_count: int = 0
    peak_hour_value: float = 0.0
    top_category_by_value: str = "—"
    top_category_value: float = 0.0
    busiest_date: str
    busiest_date_count: int
    overall_count: int
    overall_value: float
    overall_avg: float
    insights_narrative: List[str]

