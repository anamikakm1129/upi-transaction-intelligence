"""
Chapter 4: Har Important File ka Code Explanation
"""
from reportlab.platypus import Paragraph, Spacer, PageBreak
from .common import (
    p, bullet, callout, hr, code_block, STYLES, CONTENT_WIDTH
)

def get_markdown() -> str:
    return """# Chapter 4 — Har Important File ka Code Explanation

Is chapter mein hum codebase ki har critical source file ko deeply inspect karenge: uska purpose, imports, functions, inputs/outputs, logic, practical examples aur possible improvements.

---

## 4.1 Backend Entrypoint: `backend/app/main.py`

### 1. File Path & Purpose
- **Path:** `backend/app/main.py`
- **Purpose:** FastAPI application initialize karna, lifespan events manage karna, CORS middleware configure karna, global exceptions intercept karna, aur saare domain routers ko `/api` prefix ke andar register karna.

### 2. Important Imports & Architecture Role
```python
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from .database.connection import init_db, execute_one
```
- `asynccontextmanager`: Modern FastAPI mein startup aur shutdown events ko handle karne ke liye recommended standard hai.
- `CORSMiddleware`: Cross-Origin Resource Sharing ko permit karta hai taaki frontend browser requests block na hon.

### 3. Core Functions & Logic
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing UPI Transaction Intelligence System backend...")
    init_db()  # Schema create karta hai agar tables exist nahi karti
    row = execute_one("SELECT COUNT(*) AS total FROM cleaned_transactions;")
    tx_count = row['total'] if row else 0
    logger.info(f"Database ready. Active user-uploaded transactions: {tx_count}")
    yield
    logger.info("Shutting down UPI Transaction Intelligence backend.")
```
- **Inputs:** `FastAPI` instance.
- **Outputs:** Context manager jo startup par tables verify karta hai aur transaction count log karta hai.
- **Kyun is tarah likha gaya?** Deprecated `@app.on_event("startup")` ke bajaye `lifespan` context manager resource cleanups (jaise DB connections close karna) ko leak-proof banata hai.

### 4. Global Exception Handler & Structured JSON
```python
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred while processing your request.",
            "path": request.url.path
        }
    )
```
- **Benefit:** Agar code mein koi unhandled error aata hai, toh server crash nahi hota aur frontend ko unstructured 500 HTML trace milne ke bajaye clean JSON error contract milta hai.

---

## 4.2 Database Connection: `backend/app/database/connection.py`

### 1. File Path & Purpose
- **Path:** `backend/app/database/connection.py`
- **Purpose:** SQLite database connections provide karna, WAL concurrency configuration enforce karna, aur parameterized read/write helper functions (`execute_query`, `execute_one`, `execute_commit`, `execute_batch`) expose karna.

### 2. Connection Context Manager & PRAGMAs
```python
@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    ensure_db_dir()
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()
```
- **`conn.row_factory = sqlite3.Row`:** Rows ko dictionary ki tarah key-based access (`row['amount']`) allow karta hai.
- **`PRAGMA journal_mode = WAL;`:** Write-Ahead Logging enable karta hai jisse simultaneous reads and writes fail nahi hote.
- **`timeout=30.0`:** Concurrent writes ke case mein 30 seconds tak retry karta hai instead of immediately throwing `database is locked`.

---

## 4.3 Database Schema: `backend/app/database/schema.sql`

### 1. File Path & Purpose
- **Path:** `backend/app/database/schema.sql`
- **Purpose:** 6 core tables aur unke indexes define karna.

### 2. Core Tables Overview
1. `raw_transactions`: Immutable source table jisme user ki uploaded CSV bina kisi data alteration ke store hoti hai (`raw_id`, `transaction_id`, `amount`, `source_batch`).
2. `cleaned_transactions`: Cleaned aur validated records jahan `tx_date`, `tx_hour`, `anomaly_flag`, aur `anomaly_reason` indexed format mein hote hain.
3. `quarantined_transactions`: Reject hue records (`quarantine_reason` ke saath jaise "Duplicate transaction ID", "Non-numeric amount").
4. `anomaly_findings`: Rule-based anomaly findings audit log (`rule_name`, `severity`, `metric_value`, `threshold_value`, `detected_at`).
5. `data_quality_reports`: Validation runs ka statistical summary (`total_records`, `valid_records`, `missing_values_json`, `status`).
6. `system_config`: Configurable thresholds (`high_value_threshold = 50000.0`, `velocity_window_minutes = 5.0`).

---

## 4.4 Data Validation: `backend/app/processing/validation.py`

### 1. File Path & Purpose
- **Path:** `backend/app/processing/validation.py`
- **Purpose:** CSV upload hone par schema check karna, missing columns detect karna, aur data quality audit generate karna.

### 2. Mandatory Columns & Schema Validation
```python
REQUIRED_COLUMNS = [
    'transaction_id', 'timestamp', 'customer_id',
    'merchant_id', 'amount', 'category', 'status'
]

def validate_dataframe_schema(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        return False, [f"Missing required columns: {', '.join(missing)}"]
    return True, []
```
- **Logic:** Agar user ki CSV mein in 7 mandatory columns mein se ek bhi missing hai, toh processing start hone se pehle hi stop ho jaati hai aur clear descriptive error return hota hai.

### 3. Data Quality Inspection
```python
def inspect_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    # 1. Column-wise missing value counts
    # 2. Duplicate transaction_id count
    # 3. Invalid non-positive / non-numeric amounts
    # 4. Unparseable timestamps
```
- Health status evaluate karta hai: Agar invalid ratio 0% hai toh `HEALTHY`, <15% hai toh `WARNING`, aur >=15% hai toh `CRITICAL`.

---

## 4.5 Data Cleansing & Quarantine: `backend/app/processing/cleaning.py`

### 1. File Path & Purpose
- **Path:** `backend/app/processing/cleaning.py`
- **Purpose:** Raw records ko iterate karke invalid rows ko isolate karna aur clean rows ko normalize karna.

### 2. Core Deduplication & Quarantine Logic
```python
def clean_and_segregate_data(raw_df: pd.DataFrame):
    cleaned_rows = []
    quarantined_rows = []
    seen_tx_ids = set()

    for idx, row in raw_df.iterrows():
        # Check 1: Missing transaction_id
        # Check 2: Duplicate transaction_id (first occurrence kept, next quarantined)
        if tx_id in seen_tx_ids:
            base_quarantine_dict["quarantine_reason"] = f"Duplicate transaction ID: {tx_id}"
            quarantined_rows.append(base_quarantine_dict)
            continue
        # Check 3: Missing customer_id or merchant_id
        # Check 4: Amount <= 0 or NaN/Inf
        # Check 5: Timestamp parsing to YYYY-MM-DD, tx_hour
```
- **Fintech Standard:** Corrupt data ko silently drop karne ke bajaye explicit reason ke saath quarantine table mein store kiya jaata hai, jo enterprise audit trails ke liye mandatory hota hai.

---

## 4.6 Anomaly Detection Engine: `backend/app/processing/anomaly_detection.py`

### 1. File Path & Purpose
- **Path:** `backend/app/processing/anomaly_detection.py`
- **Purpose:** 5 transparent, explainable heuristic aur statistical rules evaluate karna.

### 2. Implemented Rules & Mathematics
1. **High-Value Rule:**
   `amount > high_value_threshold (Default ₹50,000.0)`. Severity HIGH hoti hai agar amount > 1.5x threshold ho, warna MEDIUM.
2. **Velocity Spike Rule:**
   Sliding time window check. Agar same customer `velocity_window_minutes` (Default 5 mins) ke andar `>= velocity_count_threshold` (Default 3) transactions karta hai, toh use rapid-fire burst flag milta hai.
3. **Statistical Z-Score Spend Rule:**
   $$\mu = \frac{1}{N}\sum x_i, \quad \sigma = \sqrt{\frac{1}{N-1}\sum (x_i - \mu)^2}, \quad Z = \frac{x - \mu}{\sigma}$$
   Agar kisi customer ke paas kam se kam 3 historical transactions hain aur uska current transaction personal average se $Z \ge 2.5$ standard deviations upar hai, toh unusual spend flag hota hai.
4. **Duplicate Record Rule:** Quarantine se aane wale duplicate review candidates.
5. **Invalid Entry Rule:** Corrupt timestamps aur non-positive amounts.

---

## 4.7 Ingestion Pipeline: `backend/app/processing/ingestion.py`

### 1. File Path & Purpose
- **Path:** `backend/app/processing/ingestion.py`
- **Purpose:** End-to-end data flow ko coordinate karna: Validation -> Data Quality -> Cleaning & Quarantine -> Anomaly Detection -> SQLite Dual Persistence -> Columnar Parquet Serialization.

### 2. Parquet Export Integration
```python
if not final_cleaned_df.empty:
    final_cleaned_df.to_parquet(PARQUET_PATH, index=False, engine='pyarrow')
```
- PyArrow engine use karke data instantly `cleaned_transactions.parquet` file mein write hota hai.

---

## 4.8 Domain Services Layer (`backend/app/services/`)

1. **`analytics_service.py`:** Dashboard KPIs calculate karta hai, diurnal trends fetch karta hai, aur factual dynamic pattern insights (`get_pattern_insights()`) construct karta hai.
2. **`transaction_service.py`:** Search, category/status/date filter, sorting aur pagination execute karta hai. SQL injection se protect karne ke liye `where_clauses` aur bind parameters use karta hai.
3. **`customer_service.py`:** Customers ko total spend ke basis par rank karta hai aur har customer ki favorite shopping category nikalta hai.
4. **`merchant_service.py`:** Merchants ki volume ranking aur peak diurnal hour calculate karta hai.
5. **`export_service.py`:** Daily, customer, merchant, hourly, aur anomaly data ko in-memory StringIO ke through clean CSV mein convert karta hai.

---

## 4.9 Frontend Central API: `frontend/src/services/api.js`

### 1. File Path & Purpose
- **Path:** `frontend/src/services/api.js`
- **Purpose:** Centralized HTTP service using browser native `fetch`.

### 2. Indian Currency Formatter (`formatINR`)
```javascript
export function formatINR(amount, includeSymbol = true, fallback = '—') {
  if (amount === undefined || amount === null || isNaN(amount) || amount === '') return fallback;
  const num = Number(amount);
  const formatted = new Intl.NumberFormat('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(num);
  return includeSymbol ? `₹${formatted}` : formatted;
}
```
- **Zero-Mock Empty State:** Agar data null ya uncalculated hai, toh fabricated values ke bajaye standard clean em-dash (`—`) return karta hai.
"""

def get_flowables() -> list:
    story = []
    story.append(p("CHAPTER 4", 'CoverMeta'))
    story.append(p("Har Important File ka Code Explanation", 'ChapterTitle'))
    story.append(p("Source files ka line-by-line purpose, imports, inputs/outputs, logic aur mathematical implementation.", 'ChapterSubtitle'))
    story.append(hr())

    story.append(p("4.1 Backend Entrypoint & Lifecycle: backend/app/main.py", 'SectionTitle'))
    story.append(p(
        "<code>main.py</code> poore backend ka central launchpad hai. Isme FastAPI instance create hota hai, "
        "<code>lifespan</code> context manager ke through database bootstrap hota hai, CORS middleware configure hota hai, "
        "aur 7 domain routers register hote hain."
    ))

    code_main = """@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing UPI Transaction Intelligence System backend...")
    init_db()  # Tables auto-create hoti hain
    row = execute_one("SELECT COUNT(*) AS total FROM cleaned_transactions;")
    tx_count = row['total'] if row else 0
    logger.info(f"Database ready. Active user-uploaded transactions: {tx_count}")
    yield
    logger.info("Shutting down UPI Transaction Intelligence backend.")"""
    story.append(code_block(code_main, "main.py lifespan"))
    story.append(Spacer(1, 8))

    story.append(p("4.2 Database Connection & Concurrency: backend/app/database/connection.py", 'SectionTitle'))
    story.append(p(
        "Yeh module SQLite connections manage karta hai. <code>PRAGMA journal_mode = WAL;</code> set karne se "
        "Write-Ahead Logging activate hoti hai, jisse multiple frontend requests parallelly database read kar sakti hain "
        "bina write transactions ko block kiye."
    ))

    story.append(callout(
        "Parameterized Security Standard",
        "Codebase mein ek bhi dynamic string concatenation query (jaise f'SELECT * FROM tx WHERE id = {user_input}') nahi hai. "
        "Har query <code>execute_query(sql, params)</code> ke zariye SQLite bind parameters (:param) use karti hai, "
        "jo SQL Injection attacks ko 100% eliminate karta hai.",
        'tip'
    ))
    story.append(Spacer(1, 8))

    story.append(p("4.3 Anomaly Engine: backend/app/processing/anomaly_detection.py", 'SectionTitle'))
    story.append(p(
        "Is module mein 5 explainable rules implement kiye gaye hain. Kisi bhi black-box ML model ke bina, "
        "mathematical thresholds (High Value > ₹50k, Rapid Burst >= 3 tx in 5m, aur Historical Z-Score >= 2.5) "
        "ke basis par review candidates generate hote hain."
    ))

    code_zscore = """# Sample Standard Deviation & Z-Score Formula:
mean_amt = float(np.mean(amounts))
std_amt = float(np.std(amounts, ddof=1)) # sample std dev
if std_amt > 1.0:
    z_score = (amt - mean_amt) / std_amt
    if z_score >= zscore_threshold:  # Default 2.5
        flag_as_unusual_spend(tx_id, z_score)"""
    story.append(code_block(code_zscore, "anomaly_detection.py Z-score"))
    story.append(Spacer(1, 8))

    story.append(p("4.4 Central Frontend Client: frontend/src/services/api.js", 'SectionTitle'))
    story.append(p(
        "<code>api.js</code> poore frontend ka single networking bridge hai. Isme <code>request()</code> helper error handling "
        "aur standard JSON unmarshaling karta hai. Saath hi <code>formatINR()</code> Indian currency numbering format "
        "(e.g. ₹1,24,500.00) enforce karta hai."
    ))

    story.append(PageBreak())
    return story

