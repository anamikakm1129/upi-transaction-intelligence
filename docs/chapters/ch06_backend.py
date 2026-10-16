"""
Chapter 6: Backend aur FastAPI Architecture
"""
from reportlab.platypus import Paragraph, Spacer, PageBreak
from .common import (
    p, bullet, callout, hr, make_table, code_block, STYLES, CONTENT_WIDTH
)

def get_markdown() -> str:
    return """# Chapter 6 — Backend aur FastAPI Architecture

## 6.1 FastAPI Application Lifecycle & Router Configuration

FastAPI modern Python ka asynchronous ASGI framework hai. Hamara backend server startup aur shutdown lifecycle ko manage karne ke liye **`@asynccontextmanager` lifespan protocol** use karta hai:

```python
# backend/app/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing UPI Transaction Intelligence System backend...")
    init_db()  # Schema tables auto-create hoti hain
    row = execute_one("SELECT COUNT(*) AS total FROM cleaned_transactions;")
    tx_count = row['total'] if row else 0
    logger.info(f"Database ready. Active user-uploaded transactions: {tx_count}")
    yield
    logger.info("Shutting down UPI Transaction Intelligence backend.")

app = FastAPI(
    title="UPI Transaction Intelligence System API",
    version="1.0.0",
    lifespan=lifespan
)
```

Saare feature routers modularly register hote hain under `/api` prefix:
```python
app.include_router(dashboard.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(merchants.router, prefix="/api")
app.include_router(anomalies.router, prefix="/api")
app.include_router(data_quality.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
```

---

## 6.2 HTTP Methods & Pydantic Data Contracts

Backend mein standard REST principles follow kiye gaye hain:

- **`GET` Endpoints:** Read-only analytics, paginated queries, aur health inspections ke liye (jaise `/api/dashboard/summary`, `/api/transactions`).
- **`POST` Endpoints:** Data mutation aur state creation ke liye (jaise `/api/data-quality/upload`, `/api/anomalies/config`).

### Pydantic v2 Serialization Contracts (`schemas.py`)
Request payloads aur response structures strongly typed hain:
```python
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
```
Jab database se query result aata hai, FastAPI ise automatically JSON contract mein convert karta hai. Agar koi data type mismatch ho, toh automatic validation error catch hota hai.

---

## 6.3 CORS Middleware: Cross-Origin Resource Sharing

Jab frontend React server (`http://localhost:3000` ya `5173`) par chal raha ho aur backend FastAPI server (`http://127.0.0.1:8000`) par chal raha ho, toh browser security restrictions (Same-Origin Policy) request ko block kar sakti hain.
Isse bachne ke liye `main.py` mein **CORSMiddleware** configure kiya gaya hai:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 6.4 Complete Implemented Endpoints Reference Table

Neeche di gayi table mein repository mein verified aur implemented sabhi endpoints listed hain:

| HTTP Method | Endpoint Path | Feature / Purpose | Input Parameters | Response Model | Source Route File |
|---|---|---|---|---|---|
| `GET` | `/api/health` | System status & table row counts | None | Health JSON status | `app/main.py` |
| `GET` | `/api/dashboard/summary` | Core KPIs (Volume, GMV, Avg Ticket) | `start_date`, `end_date` | `DashboardKpiResponse` | `routes/dashboard.py` |
| `GET` | `/api/dashboard/daily-trends` | Day-by-day volume & DoD growth | `start_date`, `end_date` | `List[DailyTrendItem]` | `routes/dashboard.py` |
| `GET` | `/api/dashboard/hourly-trends`| 24-hour diurnal activity curve | `start_date`, `end_date` | `List[HourlyTrendItem]` | `routes/dashboard.py` |
| `GET` | `/api/dashboard/category-distribution`| Category volume & spend shares | `start_date`, `end_date` | `List[CategoryDistributionItem]` | `routes/dashboard.py` |
| `GET` | `/api/dashboard/patterns` | Diurnal narrative insights | None | `PatternInsightsResponse`| `routes/dashboard.py` |
| `GET` | `/api/transactions` | Search, filter & paginated records | `search`, `category`, `page`... | `TransactionsResponse` | `routes/transactions.py` |
| `GET` | `/api/transactions/{id}` | Single transaction detail profile | `transaction_id` (path) | `TransactionItem` | `routes/transactions.py` |
| `GET` | `/api/customers` | Spend ranking & favorite category | `search`, `page`, `page_size` | `CustomersResponse` | `routes/customers.py` |
| `GET` | `/api/customers/{id}` | Customer profile & transaction history| `customer_id` (path) | Profile JSON | `routes/customers.py` |
| `GET` | `/api/merchants` | Volume ranking & diurnal peak hours | `search`, `page`, `page_size` | `MerchantsResponse` | `routes/merchants.py` |
| `GET` | `/api/merchants/{id}` | Merchant profile & 24hr breakdown | `merchant_id` (path) | Profile JSON | `routes/merchants.py` |
| `GET` | `/api/anomalies` | Audit log of review candidates | `rule_name`, `severity`, `page`| `AnomaliesResponse` | `routes/anomalies.py` |
| `GET` | `/api/anomalies/config` | Retrieve configurable thresholds | None | List of config rows | `routes/anomalies.py` |
| `POST`| `/api/anomalies/config` | Update thresholds (high-val, Z-score)| `SystemConfigUpdate` JSON | Updated config JSON | `routes/anomalies.py` |
| `GET` | `/api/data-quality/summary` | Dataset validation report | None | `DataQualitySummaryResponse`| `routes/data_quality.py` |
| `GET` | `/api/data-quality/quarantined`| Paginated list of isolated rows | `page`, `page_size` | Quarantined records JSON | `routes/data_quality.py` |
| `POST`| `/api/data-quality/validate-upload`| Stage 1: Inspect CSV before ingestion| Multipart `file: UploadFile` | Preview & health summary | `routes/data_quality.py` |
| `POST`| `/api/data-quality/upload` | Stage 2: Full cleaning & ingestion | Multipart `file: UploadFile` | `ProcessingRunResponse` | `routes/data_quality.py` |
| `POST`| `/api/processing/run` | Re-process existing raw dataset | None | `ProcessingRunResponse` | `routes/reports.py` |
| `GET` | `/api/reports/export` | Download CSV reports or Parquet | `report_type`, `format` | File / Stream download | `routes/reports.py` |

---

## 6.5 Real Request-Response Example Walkthrough

### Example: Fetching Core Dashboard KPIs
**Request:**
```http
GET /api/dashboard/summary HTTP/1.1
Host: 127.0.0.1:8000
Accept: application/json
```

**FastAPI Internal Execution:**
1. Router `routes/dashboard.py` matches endpoint `/summary`.
2. Controller `AnalyticsService.get_dashboard_summary()` execute hota hai.
3. Parametric SQL query `SQL_DASHBOARD_KPIS` SQLite database par chalti hai.
4. Database returns raw aggregate dictionary.
5. Pydantic schema `DashboardKpiResponse` data validate karke clean types enforce karta hai.

**Response (HTTP 200 OK):**
```json
{
  "total_transactions": 1184,
  "total_value": 2489240.50,
  "avg_amount": 2102.40,
  "flagged_count": 28,
  "flagged_rate_pct": 2.36,
  "success_count": 1113,
  "failed_count": 59,
  "pending_count": 12,
  "active_customers": 60,
  "active_merchants": 30
}
```
Is response ko frontend `api.js` parse karta hai aur Dashboard UI par KPI numbers display ho jaate hain.
"""

def get_flowables() -> list:
    story = []
    story.append(p("CHAPTER 6", 'CoverMeta'))
    story.append(p("Backend aur FastAPI Architecture", 'ChapterTitle'))
    story.append(p("FastAPI lifespan architecture, REST endpoints, Pydantic data contracts, CORS and error handling.", 'ChapterSubtitle'))
    story.append(hr())

    story.append(p("6.1 Application Startup & Router Registration", 'SectionTitle'))
    story.append(p(
        "FastAPI modern Python ASGI standard use karta hai. Startup par <code>lifespan</code> context manager "
        "database schema initialize karta hai aur active transaction count log karta hai. "
        "Iske baad 7 modular domain routers <code>/api</code> prefix ke sath register hote hain."
    ))

    story.append(callout(
        "Why Pydantic v2 for Financial Data Contracts?",
        "Pydantic v2 Rust-based core engine par run hota hai jo serialization ko 5x fast banata hai. "
        "Financial applications mein floating-point roundings (jaise GMV amounts ko 2 decimal places tak round rakhna) "
        "aur null-safety guarantee karna mandatory hota hai, jo Pydantic models automatically handle karte hain.",
        'interview'
    ))
    story.append(Spacer(1, 8))

    story.append(p("6.2 Implemented REST Endpoints Matrix", 'SectionTitle'))
    story.append(p("Hamare actual backend codebase mein implemented sabhi REST routes:"))

    headers = ["Method", "Endpoint Path", "Purpose", "Response Type", "Actual File"]
    rows = [
        ["GET", "/api/health", "System status & counts", "JSON status", "main.py"],
        ["GET", "/api/dashboard/summary", "Core KPIs (Volume, GMV)", "DashboardKpiResponse", "dashboard.py"],
        ["GET", "/api/dashboard/daily-trends", "DoD growth & 3-day avg", "List[DailyTrendItem]", "dashboard.py"],
        ["GET", "/api/dashboard/hourly-trends", "24hr diurnal volume curve", "List[HourlyTrendItem]", "dashboard.py"],
        ["GET", "/api/transactions", "Search, filter & paginate", "TransactionsResponse", "transactions.py"],
        ["GET", "/api/customers", "Customer spend ranking", "CustomersResponse", "customers.py"],
        ["GET", "/api/merchants", "Merchant peak hour analysis", "MerchantsResponse", "merchants.py"],
        ["GET", "/api/anomalies", "Rule-based audit log", "AnomaliesResponse", "anomalies.py"],
        ["POST", "/api/anomalies/config", "Update thresholds", "Config JSON", "anomalies.py"],
        ["POST", "/api/data-quality/validate-upload", "Stage 1 schema inspection", "Preview JSON", "data_quality.py"],
        ["POST", "/api/data-quality/upload", "Stage 2 ingestion pipeline", "ProcessingRunResponse", "data_quality.py"],
        ["GET", "/api/reports/export", "CSV & Parquet export", "File stream", "reports.py"]
    ]
    col_widths = [45, 150, 135, 120, 82]
    story.append(make_table(headers, rows, col_widths, mono_cols=[0, 1, 4]))
    story.append(Spacer(1, 8))

    story.append(p("6.3 Global Exception Handling & CORS Configuration", 'SectionTitle'))
    story.append(p(
        "<code>main.py</code> mein global exception handler kisi bhi unhandled runtime error ko intercept karta hai "
        "aur internal server trace leak kiye bina standard 500 JSON error return karta hai. "
        "Saath hi <code>CORSMiddleware</code> React dev server ports (3000, 5173) ko explicitly allow karta hai."
    ))

    story.append(PageBreak())
    return story

