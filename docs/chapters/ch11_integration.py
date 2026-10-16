"""
Chapter 11: Frontend, Backend aur Database Integration
"""
import os
from reportlab.platypus import Paragraph, Spacer, PageBreak, Image
from .common import (
    p, bullet, callout, hr, STYLES, CONTENT_WIDTH
)

def get_markdown() -> str:
    return """# Chapter 11 — Frontend, Backend aur Database Integration

## 11.1 Full-Stack System Architecture Diagram

Neeche poore system ka complete integration workflow visually represent kiya gaya hai:

```
+-------------------------------------------------------------------------------+
|                       1. CLIENT LAYER (React 18 SPA)                          |
|  - App.jsx (Shell & refreshKey)        - SvgCharts.jsx (Pure Vector Graphics) |
|  - UploadModal.jsx (Two-Step Ingest)   - api.js (Browser Fetch API Client)    |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼  HTTP / REST (JSON & Multipart FormData)
+-------------------------------------------------------------------------------+
|                       2. BACKEND LAYER (FastAPI ASGI)                         |
|  - main.py (Lifespan, CORS, Errors)    - 7 REST Routers (/api/dashboard, etc) |
|  - Domain Services (AnalyticsService)  - Pydantic v2 Strong Typing Contracts  |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼  In-Memory Data Pipeline
+-------------------------------------------------------------------------------+
|                  3. DATA INGESTION & QUALITY PIPELINE (Pandas)                |
|  - validation.py (Schema & Null Audit) - cleaning.py (Quarantine Segregation) |
|  - anomaly_detection.py (Heuristics)   - ingestion.py (Batch Orchestrator)    |
+-------------------------------------------------------------------------------+
                                      │
                   ┌──────────────────┴──────────────────┐
                   ▼                                     ▼
+---------------------------------------+ +-------------------------------------+
|        4. SQL ANALYTICS (SQLite WAL)  | |   5. COLUMNAR DATA LAKE (Parquet)   |
|  - raw_transactions (Immutable Source)| |  - cleaned_transactions.parquet     |
|  - cleaned_transactions (Indexed)     | |  - PyArrow High-Speed Serialization |
|  - quarantined_transactions (Rejects) | |  - Analytical BI Export Ready       |
|  - anomaly_findings (Audit Log)       | +-------------------------------------+
|  - SQL CTEs & Window Functions        |
+---------------------------------------+
```

---

## 11.2 Complete End-to-End Ingestion Trace (Stage-by-Stage)

Maan lijiye user browser mein apna CSV file upload karta hai. Yahan har stage ka exact code execution trace diya gaya hai:

### Step 1: User Actions in Frontend
- **File:** `frontend/src/components/UploadModal.jsx`
- **Action:** User transaction CSV select karke "Confirm & Ingest" click karta hai.
- **Triggered Function:** `handleSubmit()`
- **Next Transition:** Form data construct karke `api.uploadCsv(file)` ko call karta hai.

### Step 2: Browser Network Dispatch
- **File:** `frontend/src/services/api.js`
- **Function:** `uploadCsv(file)`
- **Payload:** `multipart/form-data` with binary file stream.
- **HTTP Request:** `POST /api/data-quality/upload` to `http://127.0.0.1:8000`.

### Step 3: FastAPI Inbound Processing
- **File:** `backend/app/api/routes/data_quality.py`
- **Function:** `upload_csv_dataset(file: UploadFile = File(...))`
- **Action:** 25MB size limit check karta hai aur `io.BytesIO(content)` ke through Pandas dataframe `df` load karta hai.
- **Next Transition:** Calls `DataQualityService.process_uploaded_csv(df, filename)`.

### Step 4: Domain Service Orchestration
- **File:** `backend/app/services/data_quality_service.py`
- **Function:** `process_uploaded_csv(df, filename)`
- **Next Transition:** Calls `process_and_load_dataset()` in `backend/app/processing/ingestion.py`.

### Step 5: Data Pipeline Execution
- **File:** `backend/app/processing/ingestion.py`
- **Execution Chain:**
  1. `validate_dataframe_schema(df)` in `validation.py` -> 7 required columns check.
  2. `inspect_data_quality(df)` in `validation.py` -> Null counts & invalid formats check.
  3. `clean_and_segregate_data(df)` in `cleaning.py` -> First-occurrence deduplication, amounts > 0 check, date formatting. Output: `cleaned_df`, `quarantined_df`.
  4. `detect_anomalies(cleaned_df, quarantined_df, config)` in `anomaly_detection.py` -> Runs High-Value, Velocity Burst, aur Customer Z-score rules. Output: `final_cleaned_df`, `anomaly_findings`.

### Step 6: Database Persistence & Columnar Export
- **File:** `backend/app/processing/ingestion.py`
- **Database Action:**
  - Raw rows written to `raw_transactions`.
  - Cleaned rows written to `cleaned_transactions` with `anomaly_flag`.
  - Rejects written to `quarantined_transactions` with `quarantine_reason`.
  - Anomaly alerts written to `anomaly_findings`.
  - Report metadata written to `data_quality_reports`.
- **Parquet Export:** `final_cleaned_df.to_parquet('data/processed/cleaned_transactions.parquet', engine='pyarrow')`.

### Step 7: HTTP Response Contract
- Backend returns JSON response:
  ```json
  {
    "success": true,
    "message": "Successfully processed 1200 records (1184 valid, 16 quarantined)",
    "cleaned_records_count": 1184,
    "anomalies_detected_count": 28,
    "parquet_saved_path": ".../cleaned_transactions.parquet"
  }
  ```

### Step 8: Reactive State Propagation & UI Re-render
- `UploadModal.jsx` receives response and executes `onUploadSuccess(res)`.
- `App.jsx` handles success:
  - Closes modal: `setIsUploadOpen(false)`.
  - Fires toast notification: `"Dataset ready: 1184 transactions processed!"`.
  - Increments broadcast key: `setRefreshKey(k => k + 1)`.
- `Dashboard.jsx`, `Transactions.jsx`, `Customers.jsx` ke `useEffect` hooks trigger hote hain.
- Naye SQL aggregates fetch hote hain aur SVG charts smoothly render ho jaate hain!
"""

def get_flowables() -> list:
    story = []
    story.append(p("CHAPTER 11", 'CoverMeta'))
    story.append(p("Frontend, Backend aur Database Integration", 'ChapterTitle'))
    story.append(p("Complete architectural flow: React SPA to FastAPI, Pandas Pipeline, SQLite WAL, Parquet and dynamic UI reconciliation.", 'ChapterSubtitle'))
    story.append(hr())

    story.append(p("11.1 System Architecture Diagram", 'SectionTitle'))
    diag_path = 'docs/architecture_diagram.png'
    if os.path.exists(diag_path):
        story.append(Image(diag_path, width=500, height=312.5))
        story.append(Spacer(1, 6))

    story.append(p("11.2 End-to-End Request Trace (Upload se UI Update Tak)", 'SectionTitle'))
    story.append(bullet("<b>1. Frontend Trigger:</b> <code>UploadModal.jsx</code> user input lekar <code>api.uploadCsv()</code> call karta hai."))
    story.append(bullet("<b>2. Multipart Dispatch:</b> Browser fetch <code>POST /api/data-quality/upload</code> payload deliver karta hai."))
    story.append(bullet("<b>3. In-Memory Parsing:</b> <code>routes/data_quality.py</code> file ko <code>io.BytesIO</code> buffer se DataFrame banata hai."))
    story.append(bullet("<b>4. Ingestion Engine:</b> <code>ingestion.py</code> validation, quarantine segregation, aur anomaly scoring run karta hai."))
    story.append(bullet("<b>5. Persistence Layer:</b> SQLite batch insert aur PyArrow Parquet serialization complete hota hai."))
    story.append(bullet("<b>6. State Broadcast:</b> <code>setRefreshKey(k => k + 1)</code> saare active page views ko synchronously trigger karta hai."))

    story.append(PageBreak())
    return story

