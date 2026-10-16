"""
Chapter 3: Project Folder Structure & Module Architecture
"""
from reportlab.platypus import Paragraph, Spacer, PageBreak
from .common import (
    p, bullet, callout, hr, code_block, STYLES, CONTENT_WIDTH
)

def get_markdown() -> str:
    return """# Chapter 3 — Project Folder Structure

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
"""

def get_flowables() -> list:
    story = []
    story.append(p("CHAPTER 3", 'CoverMeta'))
    story.append(p("Project Folder Structure & Module Architecture", 'ChapterTitle'))
    story.append(p("Clean Layered Architecture: Separation of Concerns across UI, APIs, Processing and Storage.", 'ChapterSubtitle'))
    story.append(hr())

    story.append(p("3.1 Complete Project Hierarchy", 'SectionTitle'))
    story.append(p(
        "Project mein strict <b>Separation of Concerns (SoC)</b> follow kiya gaya hai. "
        "Frontend aur Backend completely decoupled hain aur sirf HTTP REST APIs ke through interact karte hain:"
    ))

    tree_str = """upi/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app & CORS middleware
│   │   ├── api/routes/          # 7 modular REST router files
│   │   ├── database/            # SQLite connection, schema.sql, queries.py
│   │   ├── models/schemas.py    # Pydantic v2 schemas
│   │   ├── processing/          # Validation, cleaning, anomalies, ingestion
│   │   └── services/            # Domain business logic services
│   ├── data/                    # upi_transactions.db & cleaned_transactions.parquet
│   └── tests/                   # 6 automated test files (29 passing tests)
├── frontend/
│   └── src/
│       ├── App.jsx              # Main shell, reactive refresh & state
│       ├── components/          # SvgCharts, DataTable, UploadModal, Drawer...
│       ├── pages/               # 8 full-page analytical modules
│       ├── services/api.js      # Central Fetch API service & INR formatters
│       └── styles/              # Vanilla CSS (global, layout, components)
└── docs/                        # Architecture diagrams, guide scripts & PDF"""

    story.append(code_block(tree_str, "DIRECTORY TREE"))
    story.append(Spacer(1, 10))

    story.append(p("3.2 Architectural Flow & Dependencies", 'SectionTitle'))
    story.append(p(
        "Har layer ka responsibility well-defined hai: "
        "<code>App.jsx</code> tab switch aur global state coordinate karta hai; "
        "<code>api.js</code> HTTP requests dispatch karta hai; "
        "FastAPI router <code>routes/</code> request ko validate karke <code>services/</code> ko delegate karta hai; "
        "<code>services/</code> calculation ke liye <code>queries.py</code> aur <code>processing/</code> pipeline ko invoke karta hai; "
        "aur data finally SQLite3 WAL tables aur Apache Parquet files mein persist hota hai."
    ))

    story.append(callout(
        "Why is there No ORM (like SQLAlchemy)?",
        "Fintech analytics systems mein heavy ORMs (jaise SQLAlchemy ya Django ORM) complex window functions aur CTEs ke liye "
        "slow SQL generate karte hain ya unhe cleanly support nahi karte. Is project mein parameterized raw SQL queries "
        "(<code>queries.py</code>) use kiye gaye hain jo maximum performance, zero injection risk, aur pure SQL transparency provide karte hain.",
        'interview'
    ))

    story.append(PageBreak())
    return story

