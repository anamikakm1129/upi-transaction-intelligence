"""
Chapter 14: Testing, Security, Limitations & Roadmap
"""
from reportlab.platypus import Paragraph, Spacer, PageBreak
from .common import (
    p, bullet, callout, hr, make_table, code_block, STYLES, CONTENT_WIDTH
)

def get_markdown() -> str:
    return """# Chapter 14 — Testing, Security, Limitations & Roadmap

## 14.1 Automated Test Suite Analysis (29 Passing Tests)

Hamare backend mein **PyTest** test suite (`backend/tests/`) implemented hai jo pure business logic, data cleaning, anomaly rules, SQL window functions, aur API endpoints ko verify karta hai.

### Test Execution Command:
```bash
pytest backend/tests -v
```

### Verified Test Results Breakdown:
Sabhi 29 unit aur integration tests successfully pass hote hain:

1. **`test_validation.py` (3 Tests):**
   - `test_validate_dataframe_schema_valid`: Valid 7-column schema verification.
   - `test_validate_dataframe_schema_missing_columns`: Missing column rejection check.
   - `test_inspect_data_quality_detects_issues`: Null counts, corrupt amounts, aur bad dates identification.
2. **`test_cleaning.py` (2 Tests):**
   - `test_clean_and_segregate_data_quarantines_duplicates`: Deduplication policy verification (first kept, subsequent quarantined).
   - `test_clean_and_segregate_data_quarantines_invalid_amounts`: Negative aur non-numeric amounts segregation.
3. **`test_anomaly_detection.py` (2 Tests):**
   - `test_high_value_anomaly_detection`: High-value threshold (> ₹50k) verification.
   - `test_velocity_burst_anomaly_detection`: Rapid burst (3+ transactions within 5 minutes) detection.
4. **`test_sql_analytics.py` (5 Tests):**
   - `test_sql_dashboard_kpis`: Aggregate KPI calculations.
   - `test_sql_daily_trends_window_functions`: `LAG()` and rolling 3-day average window functions verification.
   - `test_sql_hourly_trends`: Diurnal hourly distribution and share %.
   - `test_sql_customer_summaries_cte_and_rank`: CTE, `ROW_NUMBER()`, and `DENSE_RANK()`.
   - `test_sql_merchant_summaries_cte_and_rank`: Peak hour ranking and volume ranks.
5. **`test_api.py` (11 Tests):**
   - `test_api_health`, `test_api_empty_state`, `test_api_dashboard_summary`, `test_api_dashboard_daily_trends`, `test_api_dashboard_hourly_trends`, `test_api_dashboard_patterns`, `test_api_transactions_pagination_and_filter`, `test_api_customers`, `test_api_merchants`, `test_api_anomalies`, `test_api_data_quality_summary`.
6. **`test_exports.py` (6 Tests):**
   - Empty dataset 400/404 handling, CSV generation for daily, customer, and merchant reports, aur Parquet binary serialization.

---

## 14.2 What is NOT Covered in Current Tests?

Honest engineering audit ke anusaar:
- **Frontend End-to-End Tests:** Cypress ya Playwright browser automation tests implemented nahi hain.
- **Concurrent Load Testing:** Locust ya k6 ke through 1,000+ simultaneous uploads ka load test suite shamil nahi hai.
- **WebSocket Streaming:** Real-time push updates ke tests nahi hain kyunki application REST polling/refresh par operate karti hai.

---

## 14.3 Data Integrity & Security Considerations

1. **SQL Injection Protection:**
   Sabhi dynamic queries (`transaction_service.py`, `queries.py`) strictly parameterized bind variables (`:param`) use karti hain. Koi bhi user input query string mein concatenate nahi hota.
2. **File Size & Denial of Service (DoS) Mitigation:**
   Inbound upload route par 25 MB hard boundary enforce ki gayi hai (`MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024`).
3. **Immutability of Source Data:**
   Raw records `raw_transactions` table mein original format mein persist hote hain, jisse financial auditability bani rehti hai.

---

## 14.4 Architectural Trade-Offs & Current Limitations

| Area | Current Implementation | Production Limitation |
|---|---|---|
| **Database** | SQLite3 in WAL mode | Single-writer limitation; distributed multi-region failover support nahi karta. |
| **Ingestion** | Synchronous in-memory pipeline | 100MB+ files par HTTP request timeout ho sakti hai. |
| **Anomaly Scoring** | Heuristic mathematical rules | Unsupervised ML patterns (jaise complex collusion rings) catch nahi karta. |
| **Real-time Flow** | Batch CSV upload based | Real-time live Kafka transaction stream nahi hai. |

---

## 14.5 Future Production Roadmap

Agar is platform ko PhonePe ya Razorpay enterprise scale par expand karna ho, toh yeh 5 architectural enhancements planned hain:

1. **Distributed Database Migration:** SQLite se **PostgreSQL 16** ya **TimescaleDB** par transition, with read replicas.
2. **Asynchronous Task Queue:** **Celery + Redis** integrate karna taaki 1GB+ CSV files background worker threads mein process hon.
3. **Apache Kafka Event Streaming:** Webhooks aur live payment gateway events ke liye real-time streaming pipeline.
4. **Machine Learning Model (Isolation Forest):** Unsupervised ML model add karna jo multi-dimensional anomaly scores generate kare.
5. **Docker & Kubernetes Deployment:** `Dockerfile` aur Helm charts for cloud-native orchestration.
"""

def get_flowables() -> list:
    story = []
    story.append(p("CHAPTER 14", 'CoverMeta'))
    story.append(p("Testing, Security, Limitations & Roadmap", 'ChapterTitle'))
    story.append(p("Test suite verification (29 passing tests), security protections, architectural limitations, and production roadmap.", 'ChapterSubtitle'))
    story.append(hr())

    story.append(p("14.1 Automated Test Suite Verification (PyTest)", 'SectionTitle'))
    story.append(p(
        "Codebase mein 6 automated test files implemented hain. Total <b>29 automated tests</b> successfully pass hote hain:"
    ))
    story.append(bullet("<b>test_validation.py (3 tests):</b> Schema validation aur null count audits."))
    story.append(bullet("<b>test_cleaning.py (2 tests):</b> Deduplication quarantine aur amount validation."))
    story.append(bullet("<b>test_anomaly_detection.py (2 tests):</b> High-value (> ₹50k) aur velocity burst rules."))
    story.append(bullet("<b>test_sql_analytics.py (5 tests):</b> SQL CTEs, LAG(), rolling averages aur rankings."))
    story.append(bullet("<b>test_api.py (11 tests):</b> REST endpoints, status codes, pagination aur filtering."))
    story.append(bullet("<b>test_exports.py (6 tests):</b> CSV reports generation aur Apache Parquet serialization."))
    story.append(Spacer(1, 8))

    story.append(callout(
        "Security Standard: Zero SQL Injection",
        "Puri application mein kahi bhi string formatting se SQL query construct nahi hoti. "
        "SQLite bind parameters (:search, :category, :limit) use hote hain jo user inputs ko query plan se alag rakhte hain.",
        'tip'
    ))
    story.append(Spacer(1, 8))

    story.append(p("14.2 Implemented vs. Planned Feature Matrix", 'SectionTitle'))
    headers = ["Component", "Status", "Current Implementation", "Planned Enterprise Evolution"]
    rows = [
        ["Data Cleaning", "Implemented", "Pandas deduplication & quarantine", "Distributed Apache Spark / PySpark"],
        ["Database", "Implemented", "SQLite3 with WAL concurrency", "PostgreSQL / TimescaleDB with Replicas"],
        ["Anomaly Detection", "Implemented", "5 Transparent heuristic rules", "Unsupervised Isolation Forest ML"],
        ["Parquet Export", "Implemented", "PyArrow columnar dataset", "Delta Lake / Apache Iceberg table"],
        ["Ingestion Mode", "Implemented", "Synchronous HTTP multipart", "Celery + Redis asynchronous worker queue"],
        ["Live Streaming", "Planned", "Batch CSV upload interface", "Apache Kafka real-time event pipeline"]
    ]
    col_widths = [85, 65, 180, 202]
    story.append(make_table(headers, rows, col_widths, mono_cols=[0, 1]))

    story.append(PageBreak())
    return story

