# UPI Transaction Intelligence System
## Complete Hinglish Technical Guide & Architectural Reference

> **Target Standard:** PhonePe • Razorpay • Visa • Mastercard  
> **Architecture:** FastAPI • React 18 • SQLite WAL • Apache Parquet • Pure SVG  
> **Language:** Natural Hinglish (Technical Hindi-English Mix)  
> **Document Version:** 1.0.0 (Production Verified)

---

## Table of Contents
1. [Chapter 1 — Project Overview & Business Context](#chapter-1--project-overview--business-context)
2. [Chapter 2 — Complete Tech Stack](#chapter-2--complete-tech-stack)
3. [Chapter 3 — Project Folder Structure](#chapter-3--project-folder-structure)
4. [Chapter 4 — Har Important File ka Code Explanation](#chapter-4--har-important-file-ka-code-explanation)
5. [Chapter 5 — Frontend Architecture (React 18 & Pure SVG UI)](#chapter-5--frontend-architecture-react-18--pure-svg-ui)
6. [Chapter 6 — Backend aur FastAPI Architecture](#chapter-6--backend-aur-fastapi-architecture)
7. [Chapter 7 — Database aur Advanced SQL Analytics](#chapter-7--database-aur-advanced-sql-analytics)
8. [Chapter 8 — CSV Upload aur Data Cleaning Pipeline](#chapter-8--csv-upload-aur-data-cleaning-pipeline)
9. [Chapter 9 — Transaction Analytics, Diurnal Curves & Business KPIs](#chapter-9--transaction-analytics-diurnal-curves--business-kpis)
10. [Chapter 10 — Rule-Based Anomaly Detection & Fraud Governance](#chapter-10--rule-based-anomaly-detection--fraud-governance)
11. [Chapter 11 — Frontend, Backend aur Database Integration](#chapter-11--frontend-backend-aur-database-integration)
12. [Chapter 12 — Project ko Practically Use Kaise Karein](#chapter-12--project-ko-practically-use-kaise-karein)
13. [Chapter 13 — Debugging aur Common Errors](#chapter-13--debugging-aur-common-errors)
14. [Chapter 14 — Testing, Security, Limitations & Roadmap](#chapter-14--testing-security-limitations--roadmap)
15. [Chapter 15 — Master Interview & Viva Preparation (35+ Q&As)](#chapter-15--master-interview--viva-preparation-35-qas)
16. [Chapter 16 — Comprehensive Technical Glossary (25+ Terms)](#chapter-16--comprehensive-technical-glossary-25-terms)

---

# Chapter 1 — Project Overview & Business Context

## 1.1 Project Kya Hai aur Iska Vision Kya Hai?

**UPI Transaction Intelligence System** ek production-grade, full-stack financial analytics aur rule-based anomaly detection platform hai. Is system ko specially Indian digital payment ecosystem (jaise **PhonePe, Razorpay, Paytm, Visa, Mastercard**) ke operational scale aur analytical challenges ko dhyan mein rakh kar develop kiya gaya hai.

Yeh project raw, unorganized UPI transaction CSV files ko ingest karta hai, unka strict schema validation aur data quality audit karta hai, corrupt aur duplicate transactions ko isolate karta hai, statistical aur heuristic anomaly rules run karta hai, aur clean data ko high-performance **SQLite3** relational tables aur columnar **Apache Parquet** files mein store karta hai.

Iske baad, hamara custom **React 18 frontend dashboard** in transactions ko dynamic diurnal traffic curves (24-hour volume distribution), customer behavioral profiles, merchant rankings, aur explainable fraud review candidates ke form mein real-time visualize karta hai.

---

## 1.2 Real-World Problem Kya Hai? (Fintech Operational Blindspots)

India mein har mahine **14 Billion+ UPI transactions** process hote hain. National Payments Corporation of India (NPCI), banks aur payment aggregators (Paytm, Razorpay, PhonePe) ke samne sabse badi challenges hoti hain:

1. **Volume & Velocity Spikes:** Sham ke peak hours (7:00 PM se 10:00 PM) mein transaction velocity exponentially badh jaati hai. System ke paas diurnal trends ka exact visibility hona zaroori hai.
2. **Data Quality Degradation:** CSV batch settlements mein network dropouts ki wajah se duplicate transaction IDs, unparseable timestamps, null customer identifiers, ya corrupt negative amounts aa jaate hain. Agar inko raw database mein ghusne diya gaya toh financial reports corrupt ho jaati hain.
3. **Black-Box ML vs. Regulatory Compliance:** Modern banking regulations (RBI guidelines) require karti hain ki agar kisi customer ki payment hold ya flag ki gayi hai, toh uska reason **100% explainable aur transparent** hona chahiye. Black-box machine learning algorithms (jaise deep neural nets) aksar audit trails provide nahi kar paate.
4. **Fast Analytical Querying without Server Overload:** Daily millions of records par aggregate metrics (DoD growth, 3-day rolling averages, customer rankings) calculate karne ke liye heavy OLTP operations expensive hote hain.

Hamara **UPI Transaction Intelligence System** inhi chaaron critical problems ko solve karta hai.

---

## 1.3 Payment Business ko Isse Kya Benefit Milta Hai?

| Stakeholder / Business Unit | Business Impact & Benefit |
|---|---|
| **Risk & Fraud Operations** | Har flagged transaction ke peeche ka exact mathematical rule (High-Value, Velocity Burst, Z-Score Outlier) dekh sakte hain, jisse investigation time 80% reduce ho jaata hai. |
| **Merchant Settlement Team** | Merchants ki hourly peak volume aur failure rates dekh kar dynamic server capacity allot kar sakte hain aur reconciliation expedite kar sakte hain. |
| **Data Engineering & BI** | Raw files preserve hoti hain (`raw_transactions`), invalid rows separate quarantine table mein jaati hain, aur clean data columnar Parquet format mein export hota hai data lake ingestion ke liye. |
| **Executive Leadership** | Single-screen dashboard par Daily Active Customers, Gross Merchandise Value (GMV in ₹), Average Ticket Size, aur Diurnal curves ka instant view milta hai. |

---

## 1.4 Kaun Is Project ko Use Kar Sakta Hai? (Target Personas)

1. **Fintech Fraud Analyst:** Jo suspicious rapid bursts ya high-value review candidates ko audit karna chahta hai.
2. **Merchant Relationship Manager:** Jo top 100 volume-generating merchants aur unke diurnal peak traffic hours ko analyze karta hai.
3. **Data Quality Engineer:** Jo raw CSV uploads mein missing values, duplicates, aur invalid amounts ka audit trail dekhna chahta hai.
4. **B.Tech CSE Student / Engineering Candidate:** Jo full-stack architecture, FastAPI REST APIs, SQLite window functions, aur PyArrow columnar serialization ko deeply samajhna aur interviews mein explain karna chahta hai.

---

## 1.5 User CSV Upload Karne ke Baad End-to-End Kya Hota Hai?

Jab user frontend par apna transaction CSV dataset upload karta hai:
1. **Schema Pre-Inspection:** Frontend file ko FastAPI ke `/api/data-quality/validate-upload` endpoint par bhejta hai. Backend mandatory columns check karta hai aur first 5 preview rows return karta hai.
2. **Ingestion & Dual Persistence:** User confirmation ke baad `/api/data-quality/upload` par raw data stream hota hai aur immutable `raw_transactions` table mein store hota hai.
3. **Cleaning & Quarantine Segregation:** Invalids aur duplicate IDs `quarantined_transactions` mein reason ke saath alag ho jaate hain. Valid data `cleaned_transactions` mein chala jaata hai.
4. **Rule-Based Anomaly Scoring:** High-value, velocity bursts, aur historical Z-score algorithms execute hote hain aur `anomaly_findings` table create hoti hai.
5. **Parquet Columnar Serialization:** Clean dataset `cleaned_transactions.parquet` file mein serialize hota hai fast analytical downloads ke liye.
6. **Reactive Dashboard Refresh:** React state update hoti hai aur zero page reload ke saath poore KPIs, charts, aur rankings refresh ho jaate hain.

---

## 1.6 Dashboard par Kaunse Results Milte Hain?

- **Executive KPI Cards:** Total Valid Transactions, Total Processed Value (₹), Average Ticket Size (₹), Flagged Review Rate (%), Active Customers, Active Merchants.
- **24-Hour Diurnal Activity Chart:** Har ghante ka transaction count, spend value, aur percentage share.
- **Day-by-Day Trend Analysis:** Daily volume, Day-over-Day (DoD) growth %, aur 3-day rolling moving average.
- **Category Market Share:** Grocery, Dining, Shopping, Utilities, P2P ka volume aur value share.
- **Customer & Merchant Rankings:** Top spenders, dense ranks, aur har customer ki favorite shopping category.
- **Explainable Anomaly Log:** Audit trail with rule name, severity, detected value vs configured threshold.
- **Data Quality Scorecard:** Total records, valid count, invalid count, missing columns distribution.

---

## 1.7 Practical Example: Raw Records se Actionable Insights

Maan lijiye CSV mein yeh 3 raw records aaye:
1. `TXN_101`: ₹500 (Grocery, 08:30 PM, Customer: rahul@oksbi)
2. `TXN_102`: ₹65,000 (Electronics, 08:32 PM, Customer: rahul@oksbi)
3. `TXN_101`: ₹500 (Grocery, 08:30 PM, Customer: rahul@oksbi) — *Duplicate Record!*

**Hamara System kya karega:**
- Duplicate `TXN_101` ko detect karke `quarantined_transactions` mein isolate karega (Reason: "Duplicate transaction ID: TXN_101").
- Pehle valid `TXN_101` ko accept karega.
- `TXN_102` ko check karega. Amount ₹65,000 configured threshold (₹50,000) se zyada hai, isliye ise `High-Value Transaction` (Severity: HIGH) flag dega aur review candidate banayega.
- Dono valid transactions ka total count = 2, total GMV = ₹65,500, average ticket = ₹32,750 calculate hoga.
- Dashboard par customer `rahul@oksbi` ka profile update hoga aur high-value alert flash hoga.

---

## 1.8 Project ki Current Limitations (Honest Technical Boundaries)

Ek professional engineer ki tarah limitations ko clearly acknowledge karna zaroori hai:
1. **Batch Upload vs. Real-Time Streaming:** Current system user-uploaded CSV batches par operate karta hai. Yeh real-time Kafka event streaming architecture par based nahi hai.
2. **Single-Writer Database (SQLite3):** Production OLAP ke liye SQLite ke bajaye distributed PostgreSQL ya ClickHouse better choice hote hain, halanki WAL mode mein SQLite single-node benchmark ke liye robust hai.
3. **Synchronous Ingestion:** Ingestion pipeline request-response thread mein synchronously run hoti hai. 100MB+ files ke liye background worker (Celery/RQ) planned improvement hai.
4. **Rule-Based Heuristics (No ML Blackbox):** Yeh machine learning based classification model (jaise Isolation Forest ya Random Forest) nahi hai, balki explainable financial rules engine hai.


---

# Chapter 2 — Complete Tech Stack

## 2.1 Complete Technology Matrix

Neeche di gayi table mein hamare repository mein implemented har technology ka complete overview diya gaya hai:

| Technology | Project Mein Iska Use | Kyun Use Ki? (Technical Rationale) | Actual File Path | Production Alternative |
|---|---|---|---|---|
| **React 18** | Frontend Single-Page Application (SPA) UI | Declarative component model, virtual DOM state updates | `frontend/src/App.jsx` | Vue.js, Angular, Svelte |
| **Vite 5** | Frontend Build Tool & Dev Server | Ultra-fast Hot Module Replacement (HMR) & ES modules | `frontend/vite.config.js` | Webpack, Turbopack |
| **Vanilla CSS3** | Custom Styling & Lavender Design System | Zero heavy framework bloat, CSS variables for theme | `frontend/src/styles/` | Tailwind CSS, Sass, Chakra |
| **Pure SVG** | Dynamic Charts (Diurnal Curve, Line Chart) | Zero external charting dependency, full CSS control | `frontend/src/components/SvgCharts.jsx` | Recharts, Chart.js, D3.js |
| **Fetch API** | Frontend HTTP Client | Native browser support, zero external npm package | `frontend/src/services/api.js` | Axios, Ky |
| **Python 3.11** | Backend Programming Language | Rich data science ecosystem, fast execution, typing | Root runtime | Go, Java, Rust |
| **FastAPI** | REST API Backend Framework | High-performance ASGI framework, automatic OpenAPI docs | `backend/app/main.py` | Flask, Django REST |
| **Uvicorn** | ASGI Web Server | Lightning-fast asynchronous request serving | CLI / `backend/app/main.py` | Gunicorn, Hypercorn |
| **Pydantic v2** | Request & Response Data Validation | Fast schema validation, type safety, automatic JSON | `backend/app/models/schemas.py` | Marshmallow, Cerberus |
| **Pandas 2.2** | Data Ingestion, Cleaning & Quality Audit | Vectorized operations, dataframe manipulation | `backend/app/processing/` | Polars, Dask |
| **PyArrow 15** | Columnar Apache Parquet Serialization | High compression, fast columnar analytical export | `backend/app/services/export_service.py` | Fastparquet |
| **SQLite3 (WAL)**| Primary Relational Database Engine | Embedded, zero external database setup, WAL concurrency | `backend/app/database/connection.py`| PostgreSQL, MySQL |
| **PyTest** | Automated Backend Testing | Clean assertion syntax, fixture support, fast execution| `backend/tests/` | Unittest, Nose2 |
| **ReportLab 5** | High-Definition PDF Documentation Builder | Programmatic PDF rendering, Flowables, exact layout | `docs/generate_guide.py` | WeasyPrint, LaTeX |

---

## 2.2 Frontend Stack Explained

### React 18 & Vite 5
React 18 hamare frontend application ka core engine hai. Iska declarative component architecture hamare dashboard ko modular banata hai.
- **Kyun use ki:** Jab backend naya processed dataset return karta hai, toh React virtual DOM reconciliation ke zariye sirf badle hue KPI cards aur charts ko re-render karta hai, bina poora page reload kiye.
- **Vite 5:** Traditional Webpack ke muqable Vite browser ke native ES modules use karta hai, jisse cold startup time milliseconds mein ho jaata hai.

### Vanilla CSS3 vs Heavy UI Frameworks
Project mein Tailwind CSS ya Bootstrap ki jagah pure CSS3 use ki gayi hai (`frontend/src/styles/` folder mein `global.css`, `layout.css`, `components.css`).
- **Kyun use ki:** Fintech SaaS dashboards mein specific lavender accents (`#8A63F4`), crisp borders (`#ECE8E5`), aur warm off-white canvases (`#F8F3EF`) required the. Vanilla CSS zero build overhead aur zero bundle bloat deta hai.

### Pure SVG Dynamic Charts
Charts banane ke liye kisi third-party library (jaise Chart.js ya Recharts) ko install nahi kiya gaya hai.
- **Kyun use ki:** `frontend/src/components/SvgCharts.jsx` mein hum pure SVG `<svg>`, `<rect>`, `<path>`, `<circle>` elements se dynamic diurnal bar charts aur line trend charts render karte hain. Isse bundle size minimal rehti hai aur vector graphics kisi bhi screen resolution par crisp rehte hain.

---

## 2.3 Backend Stack Explained

### Python 3.11 & FastAPI
FastAPI modern Python ka leading API framework hai jo Starlette aur Pydantic par build hai.
- **Kyun use ki:** Automatic OpenAPI documentation (`/docs`), asynchronous endpoint capability, aur high throughput.
- **Pydantic v2:** Pydantic models (`backend/app/models/schemas.py`) define karte hain ki request aur response mein kaunsa field kis data type ka hona chahiye. Agar invalid data aata hai, toh FastAPI automatically 422 Unprocessable Entity error throw karta hai.

---

## 2.4 Data Processing & Storage Stack Explained

### Pandas 2.2 & PyArrow (Apache Parquet)
CSV processing ke liye Pandas industry standard hai:
- Raw CSV ko DataFrame mein load karke missing values (`df.isna().sum()`), duplicates (`df.duplicated()`), aur invalid amounts filter kiye jaate hain.
- Clean data ko **Apache Parquet** format (`cleaned_transactions.parquet`) mein serialize karne ke liye **PyArrow** use kiya gaya hai. Parquet ek columnar format hai jo disk par CSV se 80% kam space leta hai aur analytical queries mein 10x tezi deta hai.

### SQLite3 in WAL (Write-Ahead Logging) Mode
Project default database ke roop mein SQLite3 (`data/upi_transactions.db`) use karta hai.
- **PRAGMA journal_mode = WAL;** set karne se database ek hi waqt par multiple concurrent readers aur ek writer ko allow karta hai bina lock contention ke.
- Parametric SQL queries aur advanced Window Functions (`ROW_NUMBER`, `DENSE_RANK`, `LAG`) SQLite 3.25+ par native chalte hain.

---

## 2.5 Planned but Not Implemented (Production Roadmap)

Agar is project ko PhonePe ya Razorpay ke production enterprise scale par deploy karna ho, toh yeh technologies add hongi:

1. **Apache Kafka / Redpanda:** Current system batch CSV ingest karta hai. Real-time stream processing ke liye Kafka cluster chahiye hoga.
2. **Celery / Redis Worker Queue:** Current upload synchronous hai. 1GB+ CSV files ke liye asynchronous background task worker zaroori hai.
3. **PostgreSQL / TimescaleDB:** Distributed high-availability OLTP ke liye SQLite se PostgreSQL par migrate karna planned hai.
4. **Machine Learning Model (Isolation Forest / Autoencoders):** Current system 100% rule-based heuristic hai. Future mein unsupervised anomaly scoring integrate ki ja sakti hai.
5. **Docker & Kubernetes:** Containerized deployment pipeline.


---

# Chapter 3 — Project Folder Structure

## 3.1 Actual Project Directory Tree

Hamare repository ka actual structure modular micro-layered design follow karta hai:

```
upi/
├── .env.example                     # Environment configuration sample
├── .gitignore                       # Git exclusions (data/, pycache, node_modules)
├── README.md                        # Master project documentation
├── backend/
│   ├── .env.example                 # Backend environment variable template
│   ├── requirements.txt             # Python production dependencies
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint, CORS & routes
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── anomalies.py     # Anomaly review candidate endpoints & config
│   │   │       ├── customers.py     # Customer summary & profile endpoints
│   │   │       ├── dashboard.py     # Core KPIs, diurnal & category endpoints
│   │   │       ├── data_quality.py  # Validation preview & CSV upload endpoints
│   │   │       ├── merchants.py     # Merchant analytics & peak hour endpoints
│   │   │       ├── reports.py       # CSV and Parquet export endpoints
│   │   │       └── transactions.py  # Filtered transaction explorer endpoints
│   │   ├── database/
│   │   │   ├── connection.py        # SQLite connection manager, WAL mode setup
│   │   │   ├── queries.py           # SQL CTEs, window functions, analytics queries
│   │   │   └── schema.sql           # DDL schema for 6 core database tables
│   │   ├── models/
│   │   │   └── schemas.py           # Pydantic v2 validation models & responses
│   │   ├── processing/
│   │   │   ├── anomaly_detection.py # Heuristic rules: high-value, velocity, z-score
│   │   │   ├── cleaning.py          # Data cleansing, quarantine segregation
│   │   │   ├── ingestion.py         # End-to-end pipeline orchestrator & persistence
│   │   │   └── validation.py        # Schema checks, null counts, invalid amount audit
│   │   ├── services/
│   │   │   ├── analytics_service.py # Dashboard KPI aggregation & pattern logic
│   │   │   ├── anomaly_service.py   # Anomaly audit queries & threshold updates
│   │   │   ├── customer_service.py  # Customer ranking & history service
│   │   │   ├── data_quality_service.py # Ingestion & quarantine log service
│   │   │   ├── export_service.py    # Report CSV generator & Parquet locator
│   │   │   ├── merchant_service.py  # Merchant peak hours & volume rankings
│   │   │   ├── synthetic_generator.py# Realistic benchmark UPI transaction generator
│   │   │   └── transaction_service.py# Parameterized search, filter & pagination
│   │   └── utils/
│   │       └── logging_config.py    # Structured Python logging utility
│   ├── data/
│   │   ├── upi_transactions.db      # SQLite production database file
│   │   └── processed/
│   │       └── cleaned_transactions.parquet # Serialized Parquet analytical dataset
│   └── tests/
│       ├── test_anomaly_detection.py# Tests for Z-score, velocity, high-value rules
│       ├── test_api.py              # Tests for FastAPI endpoints & HTTP statuses
│       ├── test_cleaning.py         # Tests for quarantine segregation & dedup
│       ├── test_exports.py          # Tests for CSV & Parquet download generators
│       ├── test_sql_analytics.py    # Tests for SQL CTEs & window functions
│       └── test_validation.py       # Tests for required columns & null audits
├── docs/
│   ├── architecture_diagram.svg     # Scalable vector system architecture diagram
│   ├── architecture_diagram.png     # Rendered high-resolution diagram image
│   ├── generate_guide.py            # PDF documentation compiler script
│   └── chapters/                    # Modular chapter content definitions
└── frontend/
    ├── package.json                 # Node package configuration (React, Vite)
    ├── vite.config.js               # Vite bundler configuration & dev server port
    ├── index.html                   # HTML5 root shell
    └── src/
        ├── main.jsx                 # React root DOM mounting script
        ├── App.jsx                  # Main application shell, state & tab routing
        ├── components/
        │   ├── DataTable.jsx        # Reusable table with sorting & pagination
        │   ├── Drawer.jsx           # Slide-in transaction & profile detail drawer
        │   ├── EmptyState.jsx       # Zero-mock empty state banner with upload CTA
        │   ├── Header.jsx           # Sticky header with date filter & upload trigger
        │   ├── KpiCard.jsx          # Metric cards for volume, GMV, ticket size
        │   ├── LoadingState.jsx     # Minimalist loading spinners & skeletons
        │   ├── Sidebar.jsx          # Left navigation bar with health indicator
        │   ├── StatusBadge.jsx      # Colored status badges (Success, High, Medium)
        │   ├── SvgCharts.jsx        # Pure SVG line, diurnal bar & donut charts
        │   └── UploadModal.jsx      # Two-stage upload & validation modal
        ├── pages/
        │   ├── Anomalies.jsx        # Rule audit log & threshold config manager
        │   ├── Customers.jsx        # Customer behavioral profiles & spend rankings
        │   ├── Dashboard.jsx        # Executive overview, KPIs & diurnal curve
        │   ├── DataQuality.jsx      # Data health summary & quarantine table
        │   ├── Merchants.jsx        # Merchant volume summaries & peak hours
        │   ├── Patterns.jsx         # Diurnal traffic narratives & ticket insights
        │   ├── Reports.jsx          # Multi-format report & Parquet downloader
        │   └── Transactions.jsx     # Full transaction explorer with search
        ├── services/
        │   └── api.js               # Centralized Fetch API client & formatters
        └── styles/
            ├── components.css       # Styling for cards, tables, modals, badges
            ├── global.css           # CSS root variables, typography & colors
            └── layout.css           # App shell, sidebar, responsive main canvas
```

---

## 3.2 Backend Folders ka Role aur Responsibility

### `backend/app/api/routes/`
- **Purpose:** Har domain feature ke HTTP routes define karna.
- **Responsibility:** Inbound HTTP requests ko receive karna, request query parameters aur upload files ko parse karna, respective Service function ko call karna, aur standard Pydantic response models return karna.

### `backend/app/database/`
- **Purpose:** Database connectivity, DDL schema, aur advanced SQL analytical queries.
- **Responsibility:** `connection.py` connection pooling aur WAL mode manage karta hai; `schema.sql` 6 tables create karta hai; `queries.py` complex CTEs aur window functions store karta hai.

### `backend/app/processing/`
- **Purpose:** Heavy lifting data transformation, validation, and analytics.
- **Responsibility:** `validation.py` CSV schema check karta hai; `cleaning.py` duplicate aur invalid records ko quarantine karta hai; `anomaly_detection.py` statistical rules evaluate karta hai; `ingestion.py` in sabko orchestrate karke database aur Parquet mein persist karta hai.

### `backend/app/services/`
- **Purpose:** Business logic layer.
- **Responsibility:** Routes aur database ke beech bridge ka kaam karta hai. Data format karta hai, mathematical calculations execute karta hai, aur errors ko gracefully handle karta hai.

---

## 3.3 Frontend Folders ka Role aur Responsibility

### `frontend/src/components/`
- **Responsibility:** Reusable atomic UI elements (Buttons, Tables, KPI Cards, SVG Charts, Drawers, Modals). Yeh components direct API call nahi karte, balki props ke through data accept karte hain.

### `frontend/src/pages/`
- **Responsibility:** 8 major functional views (Dashboard, Transactions, Customers, Merchants, Patterns, Anomalies, Data Quality, Reports). Yeh pages lifecycle hook `useEffect` mein `api.js` ko call karke data fetch karte hain aur loading/empty states handle karte hain.

### `frontend/src/services/`
- **Responsibility:** `api.js` browser ke native `fetch` API ko wrap karta hai. Indian currency formatters (`formatINR`) aur date formatters (`formatDateTime`) provide karta hai.


---

# Chapter 4 — Har Important File ka Code Explanation

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
   $$\mu = rac{1}{N}\sum x_i, \quad \sigma = \sqrt{rac{1}{N-1}\sum (x_i - \mu)^2}, \quad Z = rac{x - \mu}{\sigma}$$
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


---

# Chapter 5 — Frontend Architecture (React 18 & Pure SVG UI)

## 5.1 React Application Start Kaise Hoti Hai?

Hamari React application ka execution flow standard Vite modern web build follow karta hai:

1. **`index.html`:** Browser sabse pehle `index.html` load karta hai, jisme root container `<div id="root"></div>` define hota hai aur script tag `<script type="module" src="/src/main.jsx"></script>` ko call kiya jaata hai.
2. **`main.jsx`:** React ka entrypoint:
   ```javascript
   import React from 'react';
   import ReactDOM from 'react-dom/client';
   import App from './App';
   import './styles/global.css';
   import './styles/layout.css';
   import './styles/components.css';

   ReactDOM.createRoot(document.getElementById('root')).render(
     <React.StrictMode>
       <App />
     </React.StrictMode>
   );
   ```
   Yeh `createRoot` ke zariye virtual DOM ko actual HTML document ke `root` element par mount karta hai aur global CSS styles apply karta hai.
3. **`App.jsx`:** Main application shell render hota hai, jo Sidebar navigation, Top Header, 8 Functional Pages, aur Two-Stage CSV Upload Modal ko hold karta hai.

---

## 5.2 Layout Architecture & Component Hierarchy

Hamara frontend ek clean, full-viewport SaaS layout follow karta hai:

```
[ App.jsx Root Shell ]
├── <Sidebar />                     (Fixed left navigation: 8 tabs, health indicator)
└── <div className="main-wrapper">
    ├── <Header />                  (Dynamic Title/Subtitle, Date Picker, Refresh & Upload Buttons)
    └── <main className="content-body">
        ├── <Dashboard />           (Executive KPIs, Diurnal SVG Bar Chart, Trend Line Chart)
        ├── <Transactions />        (Search, Category Filter, Sortable DataTable, Slide-in Drawer)
        ├── <Customers />           (Spend Rankings, Favorite Categories, Profile Modal)
        ├── <Merchants />           (Volume Rankings, Diurnal Peak Hours, Settlement Profile)
        ├── <Patterns />            (Factual Diurnal Traffic Narrative Cards)
        ├── <Anomalies />           (Rule-based Audit Log & Threshold Sliders / Config)
        ├── <DataQuality />         (Missing Values Audit, Quarantine Table, Re-run Pipeline)
        └── <Reports />             (Instant CSV Report & Columnar Parquet Downloaders)
    └── <UploadModal />             (Two-Step: Schema Inspection Preview -> Ingestion Confirmation)
    └── <ToastContainer />          (Floating non-blocking success/warning alert pills)
```

---

## 5.3 CSS Design System: Lavender Palette & Zero Framework Bloat

Project mein Bootstrap ya Tailwind CSS jaise heavy frameworks ke bajaye **Vanilla CSS3** (`frontend/src/styles/`) use ki gayi hai:

- **CSS Custom Properties (Variables in `global.css`):**
  - Primary Lavender Accent: `--color-primary: #8A63F4;`
  - Deep Lavender / Headers: `--color-primary-dark: #5E35B1;`
  - Soft Lavender Background: `--color-primary-soft: #F5EEFE;`
  - Off-white Canvas: `--color-bg: #F8F3EF;`
  - Surface Card White: `--color-surface: #FFFFFF;`
  - Crisp Borders: `--color-border: #ECE8E5;`
  - Dark Charcoal Headings: `--color-text: #20201F;`
  - Muted Grey Secondary: `--color-text-muted: #77736F;`
- **Typography:** System font stack (`Segoe UI`, `-apple-system`, `Roboto`, `Helvetica`) with `JetBrains Mono` / `Consolas` for currency (`₹`) and transaction IDs.
- **Full Viewport Layout (`layout.css`):** `.app-shell` uses `display: flex; min-height: 100vh; width: 100%;` preventing cramped centered boxes.

---

## 5.4 Pure SVG Charts vs Heavy Chart Libraries (`SvgCharts.jsx`)

Fintech applications mein external charting libraries (Chart.js, Recharts) bundle size ko 500KB+ badha deti hain aur canvas blurriness produce karti hain.
Hamne `frontend/src/components/SvgCharts.jsx` mein **Pure Vector SVG** develop kiya hai:

1. **`HourlyDiurnalBarChart`:**
   - 24 bars render karta hai (Hours 00 to 23).
   - Har bar ki height mathematically normalize hoti hai:
     $$	ext{barHeight} = \left(rac{	ext{tx\_count}}{\max(	ext{tx\_count})}ight) 	imes 	ext{chartHeight}$$
   - Hover karne par dynamic tooltip display hota hai with transaction count, volume value (₹), aur volume share %.
2. **`DailyTrendLineChart`:**
   - Pure SVG `<path d="M x0 y0 L x1 y1 ...">` generate karta hai.
   - Smooth lavender gradient area fill `<linearGradient id="areaGrad">` apply karta hai.
3. **`CategoryShareDonut` / Progress Bars:**
   - Dynamic SVG arc strokes aur percentage labels.

---

## 5.5 State Management & The `refreshKey` Broadcast Pattern

Redux ya Zustand jaise heavy state stores ke bajaye, application lightweight reactive state pattern use karti hai:

```javascript
// App.jsx
const [refreshKey, setRefreshKey] = useState(0);

const handleUploadSuccess = (res) => {
  setRefreshKey((k) => k + 1); // Triggers re-fetch across all sub-components!
  showToast(`Dataset ready: ${res.cleaned_records_count} transactions processed!`, 'success');
};
```
Har child page (jaise `Dashboard.jsx`, `Transactions.jsx`) apne `useEffect` dependency array mein `refreshKey` listen karta hai:
```javascript
useEffect(() => {
  fetchDashboardData();
}, [dateRange, refreshKey]);
```
Jab bhi user CSV upload karta hai ya Header mein Refresh button dabata hai, `refreshKey` increment hota hai aur saare active components silently fresh data re-fetch kar lete hain.

---

## 5.6 Two-Stage CSV Upload Interface (`UploadModal.jsx`)

User experience aur data governance ke liye modal do stages mein split hai:

- **Stage 1 (Inspect & Validate):**
  User file choose karta hai aur "Inspect & Validate" click karta hai. File backend ke `/api/data-quality/validate-upload` par jaati hai. Backend schema check karta hai, missing columns batata hai, aur first 5 rows ka preview table dikhata hai.
- **Stage 2 (Confirm & Ingest):**
  User data preview inspect karne ke baad "Confirm & Ingest" click karta hai. File `/api/data-quality/upload` par stream hoti hai, full cleaning aur anomaly detection run hota hai, aur dataset ready ho jaata hai.

---

## 5.7 End-to-End Event Trace: Button Click se UI Render Tak

```
[User clicks "Confirm & Ingest" in UploadModal.jsx]
           │
           ▼
[api.uploadCsv(file) in src/services/api.js]
  - Sends multipart/form-data POST request to /api/data-quality/upload
           │
           ▼
[FastAPI Backend processes CSV]
  - Cleans data, quarantines corrupt rows, runs anomaly rules, saves to SQLite & Parquet
  - Returns HTTP 200 JSON with record counts
           │
           ▼
[UploadModal receives response & calls onUploadSuccess(res)]
           │
           ▼
[App.jsx executes handleUploadSuccess()]
  - Closes modal: setIsUploadOpen(false)
  - Broadcasts refresh: setRefreshKey(k => k + 1)
  - Displays floating green toast alert: "Dataset ready: 1,200 transactions processed!"
           │
           ▼
[Dashboard.jsx useEffect fires due to refreshKey change]
  - Calls api.getDashboardSummary(), api.getDailyTrends(), api.getHourlyTrends()
  - Sets kpis state, hourlyTrends state, dailyTrends state
           │
           ▼
[React Virtual DOM reconciles]
  - KPI Cards update from "—" to "₹12,45,000"
  - Pure SVG diurnal curves animate into view!
```


---

# Chapter 6 — Backend aur FastAPI Architecture

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


---

# Chapter 7 — Database aur Advanced SQL Analytics

## 7.1 SQLite Storage Engine & Concurrency Configuration

Hamara project database ke roop mein **SQLite3** (`backend/data/upi_transactions.db`) use karta hai. SQLite ko financial analytics ke liye prepare karne ke liye `connection.py` mein specific PRAGMAs configure kiye gaye hain:

```python
conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30.0)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA journal_mode = WAL;")
conn.execute("PRAGMA synchronous = NORMAL;")
conn.execute("PRAGMA foreign_keys = ON;")
```

- **`PRAGMA journal_mode = WAL;` (Write-Ahead Logging):** Standard rollback mode mein readers writers ko block karte hain. WAL mode mein database separate `.wal` file maintain karta hai, jisse multiple concurrent readers data read karte waqt single writer ko interfere nahi karte.
- **`conn.row_factory = sqlite3.Row`:** Tuple index ke bajaye column name dictionary mapping (`row["total_value"]`) provide karta hai.
- **`timeout = 30.0`:** File locks par instant crash hone ke bajaye 30 seconds tak retry window deta hai.

---

## 7.2 Database Schema: 6 Core Tables

1. **`raw_transactions`:** Raw uploaded CSV records immutable form mein store karta hai. Agar future mein kisi validation logic ko audit karna ho, toh original source row hamesha yahan preserved milti hai.
2. **`cleaned_transactions`:** Cleaned, validated aur normalized transactions store karta hai. Primary key `transaction_id` hai. Columns: `tx_date`, `tx_hour`, `amount`, `category`, `status`, `anomaly_flag`, `anomaly_reason`.
3. **`quarantined_transactions`:** Reject hue corrupt records ko hold karta hai. Har row ke sath `quarantine_reason` (jaise "Duplicate transaction ID", "Non-numeric amount") recorded hoti hai.
4. **`anomaly_findings`:** Anomaly detection engine dwara flag kiye gaye review candidates ka audit log. Columns: `rule_name`, `severity`, `metric_value`, `threshold_value`, `details`.
5. **`data_quality_reports`:** Har dataset upload run ki overall health (total records, valid count, missing columns distribution JSON) store karta hai.
6. **`system_config`:** Mathematical thresholds (high-value limit, velocity window, Z-score threshold) store karta hai jo runtime par bina code change ke update ho sakte hain.

### Indexing Strategy
Query execution time ko sub-millisecond rakhne ke liye indexed columns:
- `idx_cleaned_tx_date` on `cleaned_transactions(tx_date)`
- `idx_cleaned_customer` on `cleaned_transactions(customer_id)`
- `idx_cleaned_merchant` on `cleaned_transactions(merchant_id)`
- `idx_cleaned_category` on `cleaned_transactions(category)`
- `idx_cleaned_status` on `cleaned_transactions(status)`

---

## 7.3 Advanced SQL Analytics: 7 Master Queries

Hamara analytics engine ORM ke slow auto-generated queries ke bajaye pure, optimized raw SQL queries (`backend/app/database/queries.py`) execute karta hai.

---

### Query 1: Primary Dashboard KPIs (`SQL_DASHBOARD_KPIS`)

```sql
SELECT
    COUNT(*) AS total_transactions,
    COALESCE(SUM(amount), 0.0) AS total_value,
    COALESCE(AVG(amount), 0.0) AS avg_amount,
    COALESCE(SUM(CASE WHEN anomaly_flag = 1 THEN 1 ELSE 0 END), 0) AS flagged_count,
    ROUND(COALESCE(SUM(CASE WHEN anomaly_flag = 1 THEN 1.0 ELSE 0.0 END) * 100.0 / NULLIF(COUNT(*), 0), 0.0), 2) AS flagged_rate_pct,
    COALESCE(SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END), 0) AS success_count,
    COALESCE(SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END), 0) AS failed_count,
    COALESCE(SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END), 0) AS pending_count,
    COUNT(DISTINCT customer_id) AS active_customers,
    COUNT(DISTINCT merchant_id) AS active_merchants
FROM cleaned_transactions
WHERE (:start_date IS NULL OR tx_date >= :start_date)
  AND (:end_date IS NULL OR tx_date <= :end_date);
```

#### Line-by-Line Explanation:
- `COUNT(*) AS total_transactions`: Validated dataset ke total confirmed records count karta hai.
- `COALESCE(SUM(amount), 0.0)`: Total processed gross value nikalta hai. Agar table empty ho, toh NULL ke bajaye `0.0` return hota hai.
- `COALESCE(AVG(amount), 0.0)`: Average ticket size calculate karta hai.
- `COALESCE(SUM(CASE WHEN anomaly_flag = 1 THEN 1 ELSE 0 END), 0)`: Review candidate flagged transactions count karta hai.
- `ROUND(... * 100.0 / NULLIF(COUNT(*), 0), 2)`: Flagged transaction percentage nikalta hai. `NULLIF(COUNT(*), 0)` division-by-zero error ko prevent karta hai.
- `COUNT(DISTINCT customer_id)`: Unique active customers count karta hai.
- Parameterized date filter `:start_date` aur `:end_date` date picker se dynamically bind hote hain.

> **Verification on Failed Transactions:**
> Actual query mein `COUNT(*)` aur `SUM(amount)` poore `cleaned_transactions` dataset par execute hote hain (jisme SUCCESS, FAILED, aur PENDING sabhi validly parsed transactions shamil hain). Saath hi conditional aggregations `success_count`, `failed_count`, aur `pending_count` ke through exact breakdown bhi calculate hota hai.

---

### Query 2: Daily Trends with CTE & Window Functions (`SQL_DAILY_TRENDS`)

```sql
WITH daily_aggregates AS (
    SELECT
        tx_date,
        COUNT(*) AS tx_count,
        SUM(amount) AS tx_value,
        AVG(amount) AS avg_amount,
        SUM(CASE WHEN anomaly_flag = 1 THEN 1 ELSE 0 END) AS flagged_count,
        SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) AS success_count,
        SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) AS failed_count
    FROM cleaned_transactions
    WHERE (:start_date IS NULL OR tx_date >= :start_date)
      AND (:end_date IS NULL OR tx_date <= :end_date)
    GROUP BY tx_date
)
SELECT
    tx_date,
    tx_count,
    ROUND(tx_value, 2) AS tx_value,
    ROUND(avg_amount, 2) AS avg_amount,
    flagged_count,
    success_count,
    failed_count,
    -- Window Function 1: LAG to fetch previous day volume
    LAG(tx_count, 1, tx_count) OVER (ORDER BY tx_date ASC) AS prev_day_count,
    -- Day-over-Day growth percentage calculation
    ROUND(
        (tx_count - LAG(tx_count, 1, tx_count) OVER (ORDER BY tx_date ASC)) * 100.0 /
        NULLIF(LAG(tx_count, 1, tx_count) OVER (ORDER BY tx_date ASC), 0),
        2
    ) AS dod_growth_pct,
    -- Window Function 2: Rolling 3-day average volume
    ROUND(AVG(tx_count) OVER (
        ORDER BY tx_date ASC
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 1) AS rolling_3day_avg
FROM daily_aggregates
ORDER BY tx_date ASC;
```

#### Line-by-Line Explanation:
1. `WITH daily_aggregates AS (...)`: Common Table Expression (CTE) daily grouping banata hai.
2. `LAG(tx_count, 1, tx_count) OVER (ORDER BY tx_date ASC)`: Window function jo pichhle din ka transaction count fetch karta hai. Pehle din ke liye fallback value same day count hoti hai.
3. `dod_growth_pct`: Formula $((tx_{today} - tx_{yesterday}) / tx_{yesterday}) 	imes 100$ se daily growth percentage nikalta hai.
4. `AVG(tx_count) OVER (ORDER BY tx_date ASC ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`: Rolling 3-day moving average volume calculate karta hai jo volume smoothing ke liye use hota hai.

---

### Query 3: Hourly Activity Curve with Ratio Window Function (`SQL_HOURLY_TRENDS`)

```sql
WITH hour_totals AS (
    SELECT
        tx_hour,
        COUNT(*) AS tx_count,
        ROUND(SUM(amount), 2) AS tx_value,
        ROUND(AVG(amount), 2) AS avg_amount,
        SUM(CASE WHEN anomaly_flag = 1 THEN 1 ELSE 0 END) AS flagged_count
    FROM cleaned_transactions
    WHERE (:start_date IS NULL OR tx_date >= :start_date)
      AND (:end_date IS NULL OR tx_date <= :end_date)
    GROUP BY tx_hour
)
SELECT
    tx_hour,
    tx_count,
    tx_value,
    avg_amount,
    flagged_count,
    -- Window Function: % share of overall volume
    ROUND(tx_count * 100.0 / NULLIF(SUM(tx_count) OVER (), 0), 2) AS volume_share_pct
FROM hour_totals
ORDER BY tx_hour ASC;
```
- **`SUM(tx_count) OVER ()`:** Unpartitioned window function jo poore dataset ka grand total volume calculate karta hai, jisse har ghante ka percentage share dynamically compute ho jaata hai.

---

### Query 4: Customer Analytics with ROW_NUMBER, CTE & DENSE_RANK (`SQL_CUSTOMER_SUMMARIES`)

```sql
WITH customer_category_ranks AS (
    SELECT
        customer_id,
        category,
        COUNT(*) AS cat_tx_count,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY COUNT(*) DESC, SUM(amount) DESC) AS cat_rank
    FROM cleaned_transactions
    GROUP BY customer_id, category
),
favorite_category_cte AS (
    SELECT customer_id, category AS favorite_category
    FROM customer_category_ranks
    WHERE cat_rank = 1
),
customer_aggregates AS (
    SELECT
        c.customer_id,
        COUNT(c.transaction_id) AS total_transactions,
        ROUND(SUM(c.amount), 2) AS total_spent,
        ROUND(AVG(c.amount), 2) AS avg_amount,
        MIN(c.timestamp) AS first_tx,
        MAX(c.timestamp) AS last_tx,
        SUM(CASE WHEN c.anomaly_flag = 1 THEN 1 ELSE 0 END) AS flagged_count,
        SUM(CASE WHEN c.status = 'SUCCESS' THEN 1 ELSE 0 END) AS success_count,
        SUM(CASE WHEN c.status = 'FAILED' THEN 1 ELSE 0 END) AS failed_count
    FROM cleaned_transactions c
    GROUP BY c.customer_id
)
SELECT
    ca.customer_id,
    ca.total_transactions,
    ca.total_spent,
    ca.avg_amount,
    ca.first_tx,
    ca.last_tx,
    ca.flagged_count,
    ca.success_count,
    ca.failed_count,
    COALESCE(fc.favorite_category, 'General') AS favorite_category,
    DENSE_RANK() OVER (ORDER BY ca.total_spent DESC) AS spend_rank
FROM customer_aggregates ca
LEFT JOIN favorite_category_cte fc ON ca.customer_id = fc.customer_id
WHERE (:search IS NULL OR ca.customer_id LIKE '%' || :search || '%')
ORDER BY ca.total_spent DESC
LIMIT :limit OFFSET :offset;
```

#### Key Concepts Explained:
- `ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY COUNT(*) DESC, SUM(amount) DESC)`: Har customer ke liye categories ko transaction count aur spend value ke hisab se rank karta hai. Rank 1 wali category customer ki **Favorite Shopping Category** ban jaati hai.
- `LEFT JOIN favorite_category_cte fc ON ca.customer_id = fc.customer_id`: Aggregated metrics ke saath favorite category ko join karta hai.
- `DENSE_RANK() OVER (ORDER BY ca.total_spent DESC)`: Spenders ko rank deta hai bina kisi rank gap ke.


---

# Chapter 8 — CSV Upload aur Data Cleaning Pipeline

## 8.1 Ingestion Pipeline Architecture Overview

Hamara data pipeline 6 strict stages mein execute hota hai jo data corruption aur silent failure ko rokte hain:

```
[ User CSV File Upload via Frontend Modal ]
                  │
                  ▼
[ Stage 1: File Parsing & Format Inspection ]
  - Verify .csv extension
  - Check file size boundary (MAX 25 MB limit)
  - Parse bytes into in-memory buffer via io.BytesIO(content)
                  │
                  ▼
[ Stage 2: Schema Validation (REQUIRED_COLUMNS Check) ]
  - Verify mandatory columns:
    1. transaction_id  2. timestamp  3. customer_id
    4. merchant_id     5. amount     6. category  7. status
  - Missing column par instant HTTP 422 Unprocessable Entity
                  │
                  ▼
[ Stage 3: Deep Data Quality Audit ]
  - Calculate column-wise null counts
  - Audit duplicate transaction_id candidates
  - Identify non-positive or non-numeric amount rows
  - Audit unparseable dates
  - Evaluate health status: HEALTHY / WARNING / CRITICAL
                  │
                  ▼
[ Stage 4: Cleaning & Quarantine Segregation ]
  - Valid rows normalized: tx_date, tx_hour extracted
  - Duplicates: First occurrence kept if valid, rest isolated to quarantined_transactions
  - Corrupt rows quarantined with explicit reason strings
                  │
                  ▼
[ Stage 5: Rule-Based Anomaly Scoring ]
  - Evaluate High-Value (> ₹50k), Velocity Burst (3+ tx in 5m), Customer Z-Score (>= 2.5)
  - Mark anomaly_flag = 1 in clean dataset
  - Write detailed findings into anomaly_findings table
                  │
                  ▼
[ Stage 6: Dual Persistence & Parquet Serialization ]
  - Insert raw rows into raw_transactions (immutable audit preservation)
  - Insert clean rows into cleaned_transactions (indexed SQL querying)
  - Insert reject rows into quarantined_transactions
  - Serialize cleaned dataset to data/processed/cleaned_transactions.parquet
```

---

## 8.2 Stage-by-Stage Implementation Deep Dive

### Stage 1: In-Memory File Buffering (`routes/data_quality.py`)
```python
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024 # 25 MB

content = await file.read()
if len(content) > MAX_FILE_SIZE_BYTES:
    raise HTTPException(status_code=413, detail="File exceeds 25 MB limit.")

df = pd.read_csv(io.BytesIO(content))
```
- **Kyun is tarah likha gaya?** Disk par temporary file write karne ke bajaye memory buffer (`io.BytesIO`) use kiya gaya hai. Isse I/O overhead zero ho jaata hai aur fast serverless execution possible hoti hai.

### Stage 2 & 3: Schema & Data Quality Audit (`processing/validation.py`)
7 mandatory columns ko verify kiya jaata hai:
- `transaction_id`, `timestamp`, `customer_id`, `merchant_id`, `amount`, `category`, `status`.
- Agar koi column missing ho, toh pipeline execute nahi hoti:
  `{"is_valid_schema": false, "errors": ["Missing required columns: amount, category"]}`.

### Stage 4: Strict Quarantine Segregation Policy (`processing/cleaning.py`)
1. **Deduplication Policy:** First occurrence of a valid `transaction_id` is kept in `cleaned_rows`. Har subsequent duplicate entry ko `quarantined_rows` mein daal diya jaata hai:
   `quarantine_reason = "Duplicate transaction ID: TXN_98741"`.
2. **Amount Sanitation:**
   Agar amount `<= 0`, `NaN`, ya non-numeric string ho, toh row reject hoti hai:
   `quarantine_reason = "Invalid non-positive amount: -150.00"`.
3. **Timestamp Parsing:**
   `pd.to_datetime()` use karke ISO format parse hota hai. Successfully parse hone par:
   - `tx_date_str = parsed_dt.strftime('%Y-%m-%d')`
   - `tx_hour = int(parsed_dt.hour)`
   Agar date corrupt ho (`"invalid-date-format"`), toh row quarantine hoti hai:
   `quarantine_reason = "Invalid timestamp format: 'invalid-date-format'"`.
4. **Status Normalization:**
   Agar status `'SUCCESS'`, `'FAILED'`, ya `'PENDING'` ke alawa kuch ho, toh use standard fallback `'SUCCESS'` assign hota hai.

### Stage 5: Dual Persistence & Parquet Export (`processing/ingestion.py`)
- **SQLite Batch Insert:** SQLite `cursor.executemany()` use karke thousand records single transaction block mein commit hote hain.
- **Apache Parquet Serialization:**
  ```python
  final_cleaned_df.to_parquet(PARQUET_PATH, index=False, engine='pyarrow')
  ```
  PyArrow engine clean dataset ko columnar format mein serialize karta hai. Parquet format Big Data tools (jaise Apache Spark, AWS Athena, Snowflake) ke sath direct integration permit karta hai.

---

## 8.3 Practical Row Transformation Example

### Raw Input Row (CSV):
```csv
transaction_id,timestamp,customer_id,merchant_id,amount,category,status
TXN_78945,2026-10-14 20:45:10,aditya@okhdfcbank,zomato@hdfc,850.50,Food & Dining,success
```

### Cleaned & Enriched Transformation:
- `transaction_id`: `"TXN_78945"`
- `timestamp`: `"2026-10-14 20:45:10"`
- `tx_date`: `"2026-10-14"` *(Auto-extracted for daily indexing)*
- `tx_hour`: `20` *(Auto-extracted for diurnal curve: 8 PM)*
- `customer_id`: `"aditya@okhdfcbank"`
- `merchant_id`: `"zomato@hdfc"`
- `amount`: `850.50`
- `category`: `"Food & Dining"`
- `status`: `"SUCCESS"` *(Normalized uppercase)*
- `bank_reference_number`: `"RRN589412039481"` *(Auto-generated if missing)*
- `anomaly_flag`: `0`


---

# Chapter 9 — Transaction Analytics, Diurnal Curves & Business KPIs

## 9.1 Core Financial KPIs & Exact Mathematical Formulas

Hamare system ke executive dashboard par 6 primary metrics display hote hain. Neeche unke exact mathematical formulas aur code paths diye gaye hain:

### 1. Total Transactions ($N_{total}$)
- **Formula:**
  $$N_{total} = 	ext{COUNT}(*)$$
- **Code Path:** `backend/app/database/queries.py` -> `SQL_DASHBOARD_KPIS`
- **Logic:** `cleaned_transactions` table mein maujood sabhi validated transaction rows ka count.

### 2. Total Transaction Value / Gross Merchandise Value ($V_{total}$)
- **Formula:**
  $$V_{total} = \sum_{i=1}^{N} 	ext{amount}_i$$
- **Code Path:** `SQL_DASHBOARD_KPIS` -> `COALESCE(SUM(amount), 0.0)`
- **Logic:** Sabhi valid transaction amounts ka sum (in Indian Rupees ₹). Agar table empty ho, toh `COALESCE` NULL ke bajaye `0.0` return karta hai.

### 3. Average Transaction Amount / Ticket Size ($ar{X}$)
- **Formula:**
  $$ar{X} = rac{V_{total}}{N_{total}} = rac{\sum_{i=1}^{N} 	ext{amount}_i}{N}$$
- **Code Path:** `SQL_DASHBOARD_KPIS` -> `COALESCE(AVG(amount), 0.0)`

### 4. Anomaly Review Candidate Rate ($R_{flagged}$)
- **Formula:**
  $$R_{flagged} = \left(rac{N_{flagged}}{N_{total}}ight) 	imes 100$$
- **Code Path:** `ROUND(COALESCE(SUM(CASE WHEN anomaly_flag = 1 THEN 1.0 ELSE 0.0 END) * 100.0 / NULLIF(COUNT(*), 0), 0.0), 2)`
- **Safety:** `NULLIF(COUNT(*), 0)` ensure karta hai ki empty dataset par `ZeroDivisionError` na aaye.

---

## 9.2 Practical Numerical Example

Maan lijiye 3 transactions process hue:
- `TXN_1`: ₹100.00 (Status: SUCCESS)
- `TXN_2`: ₹200.00 (Status: SUCCESS)
- `TXN_3`: ₹300.00 (Status: FAILED)

**Calculations in System:**
- **Total Transactions:** $1 + 1 + 1 = 3$
- **Total Transaction Value:** $100 + 200 + 300 = 	ext{₹}600.00$
- **Average Ticket Size:** $rac{600}{3} = 	ext{₹}200.00$
- **Status Breakdown:** `success_count = 2`, `failed_count = 1`, `pending_count = 0`.
- **Success Rate:** $rac{2}{3} 	imes 100 = 66.67\%$.

> **Verified Technical Insight on Failed Transactions:**
> Codebase verification confirm karta hai ki `COUNT(*)` aur `SUM(amount)` table ke sabhi cleaned rows par chalte hain, jisme FAILED transactions shamil hote hain. Lekin conditional `CASE WHEN status = 'FAILED'` ke zariye unka count alag se expose kiya jaata hai taaki dashboard aggregate GMV aur pure success GMV dono ko distinguish kar sake.

---

## 9.3 Indian UPI Diurnal Traffic Curves (24-Hour Distribution)

Indian digital payment ecosystem mein transaction distribution random nahi hoti, balki ek distinct diurnal curve follow karti hai:

```
Diurnal Curve Pattern (Indian UPI Real-World Behaviour):
Volume %
 12% ┤                                            ╭─╮
 10% ┤                                      ╭─────╯ ╰─╮
  8% ┤                          ╭──╮        │         │
  6% ┤                    ╭─────╯  ╰────────╯         ╰─╮
  4% ┤            ╭───────╯                             │
  2% ┤   ╭────────╯                                     ╰──╮
  0% └───┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴─
      00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 Hour
         (Night Lull)     (Morning Ramp) (Lunch Spike)   (Peak Hours 7-10 PM)
```

1. **00:00 - 05:00 AM (Night Lull):** Bare minimum volume (<1% of daily traffic).
2. **06:00 - 11:00 AM (Morning Ramp):** Milk, vegetables, groceries, breakfast transactions start ramp-up.
3. **12:00 - 02:00 PM (Lunch Spike):** Food deliveries aur office dining transactions rise karte hain.
4. **07:00 - 10:00 PM (Evening Super-Peak):** Indian UPI ka single busiest window (Dinner, e-commerce shopping, grocery deliveries). Daily traffic ka lagbhag **30% se 35%** volume isi 3 ghante ke window mein process hota hai.

Hamara `SQL_HOURLY_TRENDS` query is diurnal curve ko track karta hai aur frontend `SvgCharts.jsx` iska visual histogram banata hai.

---

## 9.4 Day-over-Day (DoD) Growth Rate & Rolling Moving Average

Financial analysts ke liye daily transaction volatility measure karna critical hota hai:

### Day-over-Day Growth Formula
$$	ext{DoD Growth \%} = \left(rac{	ext{Count}_{today} - 	ext{Count}_{yesterday}}{	ext{Count}_{yesterday}}ight) 	imes 100$$
Query mein:
```sql
ROUND(
    (tx_count - LAG(tx_count, 1, tx_count) OVER (ORDER BY tx_date ASC)) * 100.0 /
    NULLIF(LAG(tx_count, 1, tx_count) OVER (ORDER BY tx_date ASC), 0),
    2
) AS dod_growth_pct
```

### 3-Day Rolling Moving Average
Daily weekend dips aur Monday spikes ko smooth karne ke liye:
$$	ext{MA}_{3	ext{-day}} = rac{	ext{Count}_{today} + 	ext{Count}_{yesterday} + 	ext{Count}_{day\_before}}{3}$$
Query mein:
```sql
ROUND(AVG(tx_count) OVER (
    ORDER BY tx_date ASC
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
), 1) AS rolling_3day_avg
```


---

# Chapter 10 — Rule-Based Anomaly Detection & Fraud Governance

## 10.1 Why Rule-Based Heuristics over ML Blackboxes?

Banking regulations (Reserve Bank of India - RBI guidelines aur Basel III compliance) require karti hain ki financial institutions kisi bhi blocked ya flagged transaction ka **exact, auditable mathematical reason** provide karein.

Jab deep neural networks ya black-box ML models use hote hain, toh model yeh nahi bata paata ki usne transaction ko fraud kyun kaha (unexplainable feature interaction). Isliye hamara system **Transparent Heuristic & Statistical Rules Engine** (`backend/app/processing/anomaly_detection.py`) use karta hai.

> **Crucial Governance Principle: Review Candidates vs. Proven Fraud**
> Flagged transactions are categorized strictly as **Review Candidates** (sandigdh transactions jo human audit ke yogya hain), **not definitive proof of fraud**. Example: Ek customer festival ke din legitimate ₹60,000 ka sofa khareed sakta hai; system use High-Value flag karega, lekin iska matlab yeh nahi ki customer criminal hai.

---

## 10.2 Implemented Anomaly Detection Rules

Neeche codebase mein verified aur implemented 5 rules ka deep dive diya gaya hai:

### Rule 1: High-Value Transactions
- **Condition:**
  $$	ext{amount} > 	ext{high\_value\_threshold} \quad (	ext{Default: ₹50,000.00})$$
- **Severity Evaluation:**
  Agar amount threshold ke 1.5x se zyada ho (jaise ₹75,000+), toh Severity `HIGH` hoti hai, warna `MEDIUM`.
- **Business Rationale:** UPI par high-value outflows account takeover ya skimming scams ke primary indicators hote hain.
- **Implemented Function:** `detect_anomalies()` in `anomaly_detection.py`.

---

### Rule 2: Repeated Rapid Transactions (Customer Velocity Spike)
- **Condition:**
  $$\Delta t = t_j - t_i \le 	ext{velocity\_window\_minutes} \quad (	ext{Default: 5 mins, Count} \ge 3)$$
- **Logic:**
  Transactions ko `customer_id` aur `timestamp` ke according sort kiya jaata hai. Ek sliding window move hoti hai. Agar ek hi customer 5 minute ke interval ke andar 3 ya usse zyada transactions initiate karta hai, toh un sabhi transactions ko `Velocity Spike` flag milta hai.
- **Severity:** `HIGH`
- **Business Rationale:** Automated bots, rapid testing of stolen credentials (card testing), ya repeated phishing transfers ko detect karta hai.

---

### Rule 3: Unusual Customer Spend (Statistical Z-Score: Mean & Variance)
Yeh rule customer ke individual historical spend pattern ke against outlier detect karta hai.

#### Mathematical Foundation Explained in Simple Hinglish:
1. **Mean / Expected Value ($\mu$ ya $E[X]$):**
   Customer ka historical average transaction amount:
   $$\mu = rac{1}{N} \sum_{i=1}^{N} x_i$$
   *Example:* Agar customer ne pichhle 4 transactions ₹200, ₹250, ₹300, ₹250 ke kiye hain, toh mean $\mu = rac{1000}{4} = 	ext{₹}250$.
2. **Variance ($\sigma^2$) & Standard Deviation ($\sigma$):**
   Variance yeh measure karta hai ki customer ke transactions average se kitna fluctuate (faile) hue hain.
   Sample Variance ($ddof=1$):
   $$\sigma^2 = rac{1}{N - 1} \sum_{i=1}^{N} (x_i - \mu)^2$$
   Standard Deviation $\sigma$ variance ka square root hota hai:
   $$\sigma = \sqrt{\sigma^2}$$
3. **Z-Score Formula:**
   $$Z = rac{X_{current} - \mu}{\sigma}$$
   Z-Score yeh batata hai ki naya transaction historical mean se kitne standard deviations door hai.

#### Threshold & Filtering:
- Rule sirf un customers par apply hota hai jinke paas kam se kam 3 historical transactions hon ($N \ge 3$).
- Division-by-zero ya near-zero variance se bachne ke liye `std_amt > 1.0` hona zaroori hai.
- Agar $Z \ge 2.5$ ho (customer historical variance se 2.5 standard deviations upar), toh transaction flag hoti hai.
- **Documented Limitation:** Yeh rule assume karta hai ki customer spending approximately normal (Gaussian) distribution follow karti hai. Legitimate occasional emergency payments (jaise hospital bill) bhi review candidate flag trigger kar sakti hain.

---

### Rule 4: Duplicate Record Review Candidates
- **Condition:** Quarantined dataset se aane wale duplicate transaction IDs.
- **Severity:** `HIGH`
- **Output:** Quarantined duplicates ko review candidate log mein register kiya jaata hai double-debit prevention audit ke liye.

---

### Rule 5: Corrupt & Invalid Entries
- **Condition:** Non-positive amounts (negative ya zero amounts), corrupt unparseable dates, ya missing customer VPAs.
- **Severity:** `LOW`
- **Output:** Data engineering team ke cleanup audit ke liye log hota hai.

---

## 10.3 Dynamic Threshold Configuration (`system_config`)

System ke sabhi mathematical thresholds hardcoded nahi hain, balki `system_config` table mein store hote hain aur REST endpoint `POST /api/anomalies/config` se runtime par update ho sakte hain:

| Config Key | Default Value | Description |
|---|---|---|
| `high_value_threshold` | `50000.0` | Amount exceeding this is flagged as High-Value |
| `velocity_window_minutes` | `5.0` | Time window to detect rapid transactions |
| `velocity_count_threshold` | `3.0` | Minimum count within window triggering burst alert |
| `customer_zscore_threshold` | `2.5` | Standard deviations above mean to flag unusual spend |
| `min_customer_history_for_zscore`| `3.0` | Minimum history required before running Z-score rule |


---

# Chapter 11 — Frontend, Backend aur Database Integration

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


---

# Chapter 12 — Project ko Practically Use Kaise Karein

Is chapter mein hum step-by-step dekhenge ki project ko apne machine par install kaise karein, run kaise karein, aur practically CSV upload karke reports kaise generate karein.

---

## 12.1 Prerequisites (Required Software)

Application ko run karne ke liye system par following tools installed hone chahiye:
1. **Python 3.10+** (Python 3.11 recommended): `python --version`
2. **Node.js 18+** & **npm 9+**: `node -v` aur `npm -v`
3. **Git**: Clone aur version control ke liye.

---

## 12.2 Installation & Setup Commands

### Step 1: Clone Repository & Setup Root
```bash
cd c:\Users\Mahesh\Documents\upi
cp .env.example .env
```

### Step 2: Backend Dependencies Install Karna
Root directory mein command prompt ya terminal open karein:
```bash
pip install -r backend/requirements.txt
```
*Yeh FastAPI, Uvicorn, Pandas, PyArrow, Pydantic, python-multipart, pytest aur httpx install karega.*

### Step 3: Frontend Dependencies Install Karna
```bash
cd frontend
npm install
cd ..
```
*Yeh React 18, ReactDOM, aur Vite install karega.*

---

## 12.3 Application Servers Start Karna

### Option A: Start FastAPI Backend Server
Root directory se execute karein:
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Backend Base URL:** `http://127.0.0.1:8000`
- **Interactive OpenAPI Documentation:** `http://127.0.0.1:8000/docs`
- *Backend startup par console mein aayega:*
  `INFO: Database ready. Active user-uploaded transactions: 0`

### Option B: Start React Frontend Development Server
Doosre terminal window mein execute karein:
```bash
cd frontend
npm run dev
```
- Dev server terminal par URL display karega:
  `Local: http://localhost:3000/` (ya `http://localhost:5173/`)

---

## 12.4 Step-by-Step UI Usage Walkthrough

### Step 1: Application Browser Mein Kholein
Apne browser (Chrome, Edge, Firefox) mein `http://localhost:3000` open karein.
- App clean **Zero-Mock Empty State** mein open hogi.
- KPI cards par uncalculated values ke liye clean `—` display hoga.

### Step 2: "Upload Dataset" Modal Kholein
- Header ke top-right corner par purple **"Upload Dataset"** button par click karein.
- Ek sleek modal dialog open hoga.

### Step 3: File Select Karein aur Schema Inspect Karein
- Apna transaction CSV file select karein.
- **"Inspect & Validate"** button click karein.
- Backend file ka schema check karega aur modal ke andar:
  - Total records count batayega.
  - Health status (`HEALTHY` / `WARNING`) dikhayega.
  - First 5 rows ka interactive preview table render karega.

### Step 4: Confirm & Ingest
- Preview inspect karne ke baad **"Confirm & Ingest"** button click karein.
- Backend full data cleaning pipeline chalayega, corrupt data quarantine karega, anomaly rules evaluate karega, aur data SQLite & Parquet mein save karega.
- Modal automatically close hoga aur floating green toast aayega:
  `✓ Dataset ready: 1,184 transactions processed successfully!`

### Step 5: Dashboard Analytics Inspect Karein
- **Executive KPIs:** Total Volume, Gross Value (₹), Average Ticket Size (₹), aur Flagged Rate update ho jayenge.
- **Diurnal Traffic Histogram:** 24 ghante ka hourly volume distribution chart visual ho jayega.
- **Category Market Share:** Donut chart aur progress bars mein Grocery, Dining, Utilities ka spend share dikhega.

### Step 6: Customer aur Merchant Profiles Dekhna
- Left sidebar se **"Customers"** tab par click karein:
  - Har customer ka Total Spent, Spend Rank, aur Favorite Category dikhegi.
  - Kisi customer row par click karein: Slide-in Drawer open hoga jisme customer ka full transaction history audit hoga.
- **"Merchants"** tab par click karein:
  - Top volume merchants, unka peak trading hour, aur hourly breakdown graph dikhega.

### Step 7: Anomaly Review Candidates Inspect Karein
- **"Anomalies"** tab par click karein.
- Flagged transactions ka complete audit trail dikhega with Rule Name, Severity, Reason, Metric Value, aur Configured Threshold.
- Chahein toh threshold sliders adjust karke naye limits set kar sakte hain!

### Step 8: Multi-Format Reports Export Karna
- **"Reports"** tab par click karein.
- Choose karein: Daily Summary, Customer Report, Merchant Report, ya Anomaly Log.
- **"Download CSV"** click karein. Clean formatted CSV download ho jayegi.
- Columnar data ke liye **"Download Parquet Dataset"** click karein aur `cleaned_transactions.parquet` file export karein.


---

# Chapter 13 — Debugging aur Common Errors

Jab aap full-stack fintech applications run karte hain, toh local environment, network, ya data format ki wajah se errors aa sakte hain. Is chapter mein 10 most common errors, unke identification steps, diagnostic commands, aur exact code fixes diye gaye hain.

---

## 1. Backend Start Nahi Ho Raha (`ModuleNotFoundError`)

### Reason:
Python virtual environment activate nahi hai ya required libraries install nahi hui hain.
### Error Message:
`ModuleNotFoundError: No module named 'fastapi'` ya `'pyarrow'`
### Diagnostic Command:
```bash
pip list | grep -E "fastapi|uvicorn|pandas|pyarrow"
```
### Solution:
Root directory se dependencies reinstall karein:
```bash
pip install -r backend/requirements.txt
```

---

## 2. Port Already in Use Error (`Port 8000` ya `Port 3000`)

### Reason:
Pichhla Uvicorn ya Vite process background mein abhi bhi chal raha hai aur port lock hai.
### Error Message:
`ERROR: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000): only one usage of each socket address is normally permitted`
### Diagnostic Command (Windows PowerShell):
```powershell
Get-NetTCPConnection -LocalPort 8000,3000 | Select-Object OwningProcess, LocalPort, State
```
### Solution:
Process ID (PID) identify karke kill karein:
```powershell
Stop-Process -Id <PID> -Force
```
Ya uvicorn ko kisi doosre port par start karein:
```bash
python -m uvicorn backend.app.main:app --port 8005 --reload
```

---

## 3. SQLite Database Locked Error (`sqlite3.OperationalError: database is locked`)

### Reason:
Concurrent write operations ke waqt doosra process lock release hone ka wait nahi kar paaya.
### Diagnostic Command:
Check karein ki database file kis mode mein hai:
```python
import sqlite3
conn = sqlite3.connect('backend/data/upi_transactions.db')
print(conn.execute('PRAGMA journal_mode;').fetchone()[0])
```
### Solution:
Hamare code `backend/app/database/connection.py` mein `timeout=30.0` aur `PRAGMA journal_mode = WAL;` already configured hai. Agar fir bhi lock issue aaye, toh ensure karein ki koi GUI tool (jaise DB Browser for SQLite) write lock hold karke na baitha ho.

---

## 4. CORS Error: Browser Request Blocked by Same-Origin Policy

### Reason:
Frontend request origin backend ke `allow_origins` list mein matching nahi hai.
### Error Message in Browser Console:
`Access to fetch at 'http://127.0.0.1:8000/api/dashboard/summary' from origin 'http://localhost:5173' has been blocked by CORS policy.`
### Solution:
`backend/app/main.py` mein check karein ki aapka frontend port allowed hai:
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

## 5. CSV Columns Missing Validation Error (`HTTP 422 Unprocessable Entity`)

### Reason:
Uploaded CSV file mein 7 mandatory columns mein se koi column missing hai ya column name misspelled hai (jaise `txn_id` instead of `transaction_id`).
### Error Response:
`{"detail": "Schema validation failed: Missing required columns: customer_id, category"}`
### Diagnostic Step:
CSV header print karke inspect karein:
```python
import pandas as pd
df = pd.read_csv('your_file.csv')
print(df.columns.tolist())
```
### Solution:
Ensure karein ki CSV header exactly match kare:
`transaction_id, timestamp, customer_id, merchant_id, amount, category, status`.

---

## 6. Invalid Timestamp Parsing Error (`Unparseable Date`)

### Reason:
CSV mein date kisi unusual format mein hai (jaise `14/10/26` bina time ke) jo Pandas parse nahi kar paata.
### System Behavior:
System crash nahi hota! `cleaning.py` aisi rows ko reject karke `quarantined_transactions` mein bhej deta hai with reason:
`Invalid timestamp format '14/10/26': Unknown datetime string format`.
### Solution:
Ensure karein ki timestamps standard ISO format mein hon: `YYYY-MM-DD HH:MM:SS` (e.g. `2026-10-14 20:30:15`).

---

## 7. Frontend ko API Response Nahi Mil Raha (`TypeError: Failed to fetch`)

### Reason:
FastAPI backend server run nahi ho raha hai, ya URL endpoint galat hai.
### Diagnostic Step:
Browser mein `http://127.0.0.1:8000/api/health` open karke check karein:
Expected output: `{"status": "UP", "service": "UPI Transaction Intelligence System"}`.
### Solution:
Agar backend down hai, toh terminal mein restart karein:
`python -m uvicorn backend.app.main:app --port 8000 --reload`.

---

## 8. Dashboard Par Data Empty Dikh Raha Hai (`—` Em-dash everywhere)

### Reason:
Application intentionally **Zero-Mock Pure Empty State** design follow karti hai. Jab tak user real transaction CSV upload nahi karta, database mein 0 rows hoti hain.
### Solution:
Yeh koi bug nahi hai, balki intended behavior hai! Header mein "Upload Dataset" button dabayein aur transaction CSV ingest karein.

---

## 9. Parquet Export Fails (`HTTP 404 Not Found`)

### Reason:
User ne transaction data upload kiye bina seedhe Parquet file download karne ki koshish ki.
### Error Message:
`Parquet processed dataset not found. Please upload a transaction CSV first.`
### Solution:
`export_service.py` pehle check karta hai ki `data/processed/cleaned_transactions.parquet` exist karti hai ya nahi. CSV upload aur processing complete hone ke baad hi Parquet file generate hoti hai.

---

## 10. File Size Exceeded (`HTTP 413 Payload Too Large`)

### Reason:
Uploaded CSV file 25 MB size boundary se badi hai.
### Error Message:
`File exceeds maximum allowed size of 25 MB.`
### Solution:
Current in-memory buffer limit 25 MB hai. Badi files ke liye batch split karein ya `backend/app/api/routes/data_quality.py` mein `MAX_FILE_SIZE_BYTES` constant badhayein.


---

# Chapter 14 — Testing, Security, Limitations & Roadmap

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


---

# Chapter 15 — Master Interview & Viva Preparation (35+ Q&As)

Is chapter mein 36 essential technical interview questions aur unke precise Hinglish answers diye gaye hain. Yeh answers PhonePe, Razorpay, Visa, Mastercard, aur fintech startups ke interviews aur engineering viva ke liye tayyar kiye gaye hain.

---

### Q1: Is project ka main purpose aur real-world problem kya hai?
**Answer:** Yeh project Indian UPI ecosystem (jaise PhonePe, Razorpay) mein high-volume payment data ko ingest karta hai, corrupt aur duplicate transactions ko isolate karta hai, statistical aur heuristic anomaly rules se review candidates identify karta hai, aur business insights (jaise diurnal curves aur customer rankings) provide karta hai.

---

### Q2: Aapne backend ke liye FastAPI kyun choose kiya, Flask ya Django kyun nahi?
**Answer:** FastAPI asynchronous ASGI architecture par based hai, jo high-throughput I/O requests ke liye fast hai. Isme Pydantic v2 ke through automatic request validation, high-speed JSON serialization, aur automatic interactive OpenAPI documentation (`/docs`) out-of-the-box milta hai. Flask mein yeh sab manual add karna padta hai aur Django analytics ke liye unnecessarily heavy hai.

---

### Q3: React frontend mein bina external chart library ke SVG charts kyun banaye?
**Answer:** Recharts ya Chart.js bundle size ko 500KB+ badha dete hain aur styling override karna complex hota hai. `SvgCharts.jsx` mein pure SVG `<svg>`, `<rect>`, `<path>` use karke humne lightweight, high-performance charts banaye hain jo kisi bhi resolution par sharp dikhte hain aur zero external dependency rakhte hain.

---

### Q4: Frontend aur Backend aapas mein kaise communicate karte hain?
**Answer:** Frontend `src/services/api.js` module ke through browser ke native `fetch` API se HTTP REST calls bhejta hai. JSON data standard GET/POST endpoints par exchange hota hai aur CSV file upload `multipart/form-data` ke roop mein FastAPI ke `/api/data-quality/upload` endpoint par stream hota hai.

---

### Q5: CORS kya hai aur aapke project mein kaise handle kiya gaya hai?
**Answer:** CORS (Cross-Origin Resource Sharing) browser security mechanism hai jo alag ports ya domains se aane wali requests ko restrict karta hai. Hamne `backend/app/main.py` mein `CORSMiddleware` configure kiya hai jo frontend ports (`http://localhost:3000` aur `5173`) ko explicit access allow karta hai.

---

### Q6: Data validation mein kaunse 7 mandatory columns check hote hain?
**Answer:** `validation.py` mein 7 required columns verify hote hain: `transaction_id`, `timestamp`, `customer_id`, `merchant_id`, `amount`, `category`, aur `status`. Agar ek bhi column missing ho, toh pipeline execute nahi hoti aur HTTP 422 error return hota hai.

---

### Q7: Duplicate transactions ko aapka system kaise handle karta hai?
**Answer:** System **First-Occurrence Retention Policy** follow karta hai. Agar ek hi `transaction_id` baar-baar aata hai, toh pehle valid record ko `cleaned_transactions` mein rakha jaata hai aur baaki sabhi subsequent occurrences ko `quarantined_transactions` table mein reason `"Duplicate transaction ID"` ke saath isolate kar diya jaata hai.

---

### Q8: Quarantining aur Silent Dropping (`df.dropna()`) mein kya fark hai?
**Answer:** Data science mein aksar corrupt data ko `dropna()` se silently drop kar dete hain, lekin banking aur fintech mein yeh non-compliant hai. Quarantine policy mein har invalid row ko uske raw data aur reject hone ke exact reason ke saath `quarantined_transactions` table mein permanently persist kiya jaata hai taaki audit trail bani rahe.

---

### Q9: Database mein SQLite WAL mode ka kya significance hai?
**Answer:** Default SQLite rollback journal mode mein write operation ke waqt poora database file lock ho jaata hai. `PRAGMA journal_mode = WAL;` (Write-Ahead Logging) lagane se multiple readers ek hi waqt par data read kar sakte hain bina writer ko block kiye, jo analytical dashboard concurrency ke liye zaroori hai.

---

### Q10: Project mein SQL Injection vulnerabilities kaise prevent ki gayi hain?
**Answer:** Puri application mein dynamic string formatting (`f"SELECT... {user_input}"`) strictly banned hai. Sabhi queries SQLite bind variables (`:search`, `:category`, `:start_date`) ke zariye parameterize hoti hain, jisse database engine query structure aur user input ko strictly alag rakhta hai.

---

### Q11: Common Table Expressions (CTEs) kya hote hain aur project mein kahan use hue hain?
**Answer:** CTE ek temporary named result set hota hai jo `WITH cte_name AS (...)` syntax se banta hai. Project mein `SQL_DAILY_TRENDS` mein daily aggregation banane ke liye aur `SQL_CUSTOMER_SUMMARIES` mein customer category ranks compute karne ke liye CTEs use hue hain taaki complex nested queries clean aur readable rahein.

---

### Q12: Window Function `ROW_NUMBER()` ka project mein kya role hai?
**Answer:** `SQL_CUSTOMER_SUMMARIES` mein `ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY COUNT(*) DESC, SUM(amount) DESC)` use hota hai. Yeh har customer ke shopping categories ko frequency aur amount ke hisab se rank karta hai, jisse rank 1 wali category customer ki "Favorite Category" nikal aati hai.

---

### Q13: `DENSE_RANK()` aur `RANK()` mein kya difference hai?
**Answer:** `RANK()` tie hone par subsequent ranks skip kar deta hai (e.g. 1, 2, 2, 4), jabki `DENSE_RANK()` bina kisi gap ke continuous sequence deta hai (e.g. 1, 2, 2, 3). Hamne customer spend aur merchant volume ranking ke liye `DENSE_RANK()` use kiya hai taaki rankings continuous rahein.

---

### Q14: Window Function `LAG()` ka use kahan hua hai?
**Answer:** `SQL_DAILY_TRENDS` mein `LAG(tx_count, 1)` use hota hai. Yeh current row ke liye pichhle din ka transaction volume return karta hai, jisse Day-over-Day (DoD) volume growth percentage calculate hoti hai.

---

### Q15: Rolling 3-day average volume kaise calculate hota hai?
**Answer:** SQL window frame specification ke through:
`AVG(tx_count) OVER (ORDER BY tx_date ASC ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`. Yeh current day aur pichhle 2 dinon ka moving average nikalta hai jo weekend traffic volatility ko smooth karta hai.

---

### Q16: Ratio Window Function `SUM() OVER ()` kaise kaam karta hai?
**Answer:** `SQL_HOURLY_TRENDS` mein `tx_count * 100.0 / SUM(tx_count) OVER ()` use hota hai. Empty over clause `OVER ()` poore table ka aggregate total volume return karta hai, jisse bina alag sub-query ke har ghante ka percentage share nikal aata hai.

---

### Q17: Failed transactions total volume aur GMV mein count hote hain ya nahi?
**Answer:** Ha, `COUNT(*)` aur `SUM(amount)` poore validated `cleaned_transactions` table par run hote hain jisme SUCCESS, FAILED, aur PENDING shamil hote hain. Lekin conditional aggregations (`success_count`, `failed_count`) alag se nikaale jaate hain taaki exact bifurcation dikhaya ja sake.

---

### Q18: Indian UPI payment traffic ka diurnal curve kya hota hai?
**Answer:** Indian UPI traffic subah 8 AM se groceries ke liye ramp hoti hai, dopahar 1 PM lunch spike aata hai, aur sham 7:00 PM se 10:00 PM ke beech super-peak (daily traffic ka ~35%) banta hai jab dinner aur shopping transactions hote hain.

---

### Q19: Anomaly detection ke liye machine learning ke bajaye rules kyun use kiye?
**Answer:** Banking regulations require karti hain ki flagged transaction 100% explainable ho. Heuristic rules (High Value > ₹50k, Rapid Burst >= 3 in 5m, Z-Score >= 2.5) exact mathematical threshold aur reason dete hain jo regulatory compliance aur fraud operations ke audit ke liye ideal hai.

---

### Q20: Statistical Z-Score anomaly detection rule ka logic samjhaiye.
**Answer:** Yeh rule customer ke personal spend history ($N \ge 3$) par calculate hota hai. Customer ka mean $\mu$ aur standard deviation $\sigma$ calculate hota hai. Agar current transaction $Z = (X - \mu)/\sigma \ge 2.5$ ho, toh iska matlab yeh transaction personal spending variance se 2.5 standard deviations upar hai aur use review candidate flag milta hai.

---

### Q21: Standard Deviation ($\sigma$) aur Variance ($\sigma^2$) ka financial significance kya hai?
**Answer:** Variance yeh batata hai ki transaction amounts average se kitna widely spread hain. Standard deviation variance ka square root hota hai jo same currency unit (₹) mein aata hai. Low standard deviation predictable routine spending show karta hai, jabki sudden high deviation unusual spend alert trigger karta hai.

---

### Q22: Velocity Spike / Rapid Burst rule kaise kaam karta hai?
**Answer:** Transactions ko `customer_id` aur `timestamp` se sort karke sliding window check chalta hai. Agar same customer 5 minute ke interval ke andar 3 ya usse zyada transactions initiate karta hai, toh bot testing ya rapid fraud transfers ko rokne ke liye unhe High Severity Velocity Spike flag milta hai.

---

### Q23: "Review Candidate" aur "Proven Fraud" mein kya fark hai?
**Answer:** Rule flag hona fraud prove nahi karta. Example: Diwali par customer ka ₹65,000 ka genuine TV purchase High-Value flag trigger karega. System ise "Review Candidate" manta hai taaki risk analyst inspect kar sake, direct customer ko block nahi karta.

---

### Q24: Apache Parquet format kya hai aur ise kyun use kiya gaya?
**Answer:** Parquet ek columnar storage file format hai jo PyArrow engine ke through generate hota hai. Yeh CSV ke muqable 80% kam disk space leta hai aur analytical BI tools (Snowflake, AWS Athena, Spark) mein columnar compression ki wajah se 10x fast scan hota hai.

---

### Q25: Frontend mein `refreshKey` broadcast pattern kya hai?
**Answer:** CSV upload ya refresh click hone par `App.jsx` mein `setRefreshKey(k => k + 1)` execute hota hai. Saare child pages (`Dashboard`, `Transactions`) apne `useEffect` mein `refreshKey` observe karte hain aur automatically background mein fresh API metrics re-fetch kar lete hain.

---

### Q26: Backend mein Global Exception Handling kaise implement ki gayi hai?
**Answer:** `backend/app/main.py` mein `@app.exception_handler(Exception)` define hai. Yeh unhandled errors ko console mein stack trace ke sath log karta hai aur frontend client ko clean 500 JSON error contract return karta hai, jisse server crash nahi hota.

---

### Q27: `transaction_service.py` mein pagination kaise implement ki gayi hai?
**Answer:** `page` aur `page_size` parameters ke through `offset = (page - 1) * page_size` calculate hota hai. SQL query mein `LIMIT :limit OFFSET :offset` lagaya jaata hai, aur total matching rows count karke `total_pages = ceil(total / page_size)` compute hota hai.

---

### Q28: Large file uploads ke case mein server memory overflow kaise prevent hota hai?
**Answer:** Inbound upload endpoint par `MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024` (25 MB) hard check enforce kiya gaya hai. Isse badi files ko FastAPI turant HTTP 413 Payload Too Large error ke sath reject kar deta hai.

---

### Q29: PyTest test suite codebase mein kya verify karta hai?
**Answer:** 6 test files mein total 29 tests hain: schema validation, missing columns, deduplication, quarantine segregation, high-value rule, velocity burst rule, SQL window functions (`LAG`, rolling avg, rankings), API endpoints, aur Parquet exports.

---

### Q30: Project ki sabse badi architectural limitation kya hai?
**Answer:** System batch CSV upload par kaam karta hai (real-time Kafka streaming pipeline nahi hai), aur database SQLite3 hai jo single-node benchmark ke liye accha hai par multi-region high write concurrency ke liye PostgreSQL ya distributed storage require karega.

---

### Q31: Agar dataset mein negative amount aaye toh system kya karega?
**Answer:** `cleaning.py` mein `amount <= 0` check hota hai. Negative amount wali row clean table mein nahi jaati, balki `quarantined_transactions` table mein reject reason `"Invalid non-positive amount"` ke sath isolate ho jaati hai.

---

### Q32: Unparseable timestamps kaise handle hote hain?
**Answer:** `pd.to_datetime()` try-except block mein execute hota hai. Agar date format corrupt ho (jaise `"bad_date"`), toh exception catch hota hai aur row quarantine ho jaati hai without crashing the pipeline.

---

### Q33: Merchant Analytics mein Peak Trading Hour kaise nikalta hai?
**Answer:** CTE `merchant_hourly` har merchant ke 24 ghante ke transaction count par `ROW_NUMBER() OVER (PARTITION BY merchant_id ORDER BY COUNT(*) DESC)` calculate karta hai. Rank 1 wala ghanta merchant ka `peak_hour` ban jaata hai.

---

### Q34: Pattern Insights (`/api/dashboard/patterns`) narrative kaise construct hoti hai?
**Answer:** `analytics_service.py` multi-stage CTE query run karta hai jisse peak hour, highest value category, aur busiest trading date nikalte hain. In numbers ke basis par factual descriptive English sentences dynamically generate hote hain.

---

### Q35: Production mein 1GB+ files aane par system kaise evolve hoga?
**Answer:** Celery worker queue aur Redis message broker add hoga. User upload karte hi task ID return hogi aur background worker chunks mein data stream karke PostgreSQL mein batch insert karega.

---

### Q36: Is project se aapne sabse bada engineering takeaway kya seekha?
**Answer:** Real-world fintech mein data clean karna aur compliance-ready audit trails maintain karna ML algorithms run karne se zyada critical hota hai. Pure SQL window functions aur structured quarantine layers massive operational transparency provide karti hain.


---

# Chapter 16 — Comprehensive Technical Glossary (25+ Terms)

Neeche software engineering, data analytics aur fintech domain ke 25 core technical terms ki practical Hinglish definitions di gayi hain:

1. **Frontend:**
   Application ka visual user interface (UI) jo user ke browser mein run hota hai (hamare project mein React 18 SPA aur Vanilla CSS).
2. **Backend:**
   Server-side engine jo business logic, data processing, aur database operations execute karta hai (hamare project mein Python FastAPI).
3. **API (Application Programming Interface):**
   Ek bridge ya contract jiske zariye do alag systems (jaise React frontend aur Python backend) aapas mein data exchange karte hain.
4. **Endpoint:**
   API server par ek specific web address (URL path) jahan client kisi specific resource ko access karta hai (jaise `/api/dashboard/summary`).
5. **Request:**
   Client (browser) dwara server ko bheja gaya HTTP message jisme method (GET, POST), headers, aur payload data shamil hota hai.
6. **Response:**
   Request process karne ke baad server dwara client ko bheja gaya answer jisme HTTP status code (200, 422) aur JSON data hota hai.
7. **Component:**
   React ka reusable, independent code block (jaise `KpiCard`, `DataTable`, `SvgCharts`) jo apna specific UI render karta hai.
8. **State:**
   React component ke andar ka dynamic internal data jo user actions (jaise button click ya file upload) ke baad change hota hai aur UI ko update karta hai.
9. **Database:**
   Structured data ko securely aur permanently store karne wala system (hamare project mein SQLite3).
10. **SQL Query:**
    Relational database se specific data select, insert, update ya delete karne ke liye likhi gayi standardized command.
11. **DataFrame:**
    Pandas library ka two-dimensional tabular data structure (rows aur columns) jo in-memory mathematical calculations ke liye use hota hai.
12. **Data Validation:**
    Check karna ki aane wala data required rules (mandatory columns, correct data types, valid status) ko follow kar raha hai ya nahi.
13. **Data Cleaning:**
    Corrupt amounts, unparseable dates, aur duplicate records ko identify karke data ko normalize karna aur bad records ko quarantine mein isolate karna.
14. **Aggregation:**
    Multiple rows ke data ko combine karke single summary metric calculate karna (jaise `SUM(amount)`, `AVG(amount)`, `COUNT(*)`).
15. **Common Table Expression (CTE):**
    `WITH` clause se banaya gaya temporary named result set jo complex multi-stage SQL queries ko readable aur fast banata hai.
16. **Window Function:**
    SQL ka advanced function (`ROW_NUMBER`, `DENSE_RANK`, `LAG`) jo table rows ke across calculation karta hai bina group by aggregation ke rows ko collapse kiye.
17. **Variance ($\sigma^2$):**
    Ek statistical measurement jo yeh batata hai ki transaction amounts apne average (mean) se kitna widely spread hain.
18. **Standard Deviation ($\sigma$):**
    Variance ka square root jo original currency unit (₹) mein yeh batata hai ki typical transaction average se kitna deviate karta hai.
19. **Anomaly:**
    Koi aisa transaction pattern jo normal spending behavior se significantly alag ho (jaise high amount ya rapid burst) aur review ke yogya ho.
20. **CSV (Comma-Separated Values):**
    Plain text file format jahan rows newline se aur columns comma (`,`) se separate hote hain.
21. **Apache Parquet:**
    Ek highly compressed, columnar data storage format jo analytical BI tools (Snowflake, Spark) mein fast scans provide karta hai.
22. **Logging:**
    Application execution ke waqt events, errors aur milestones ko timestamped text messages ke roop mein terminal ya file mein record karna.
23. **Exception Handling:**
    Runtime par aane wale unexpected errors (jaise file not found, bad format) ko gracefully catch karna taaki application crash na ho.
24. **CORS (Cross-Origin Resource Sharing):**
    Browser ka security protocol jo yeh decide karta hai ki ek origin (e.g. port 3000) doosre origin (e.g. port 8000) se data fetch kar sakta hai ya nahi.
25. **Environment Variable:**
    Operating system level par set kiye gaye dynamic configuration values (jaise database paths, API keys, port numbers) jo code ke bahar define hote hain.


---
