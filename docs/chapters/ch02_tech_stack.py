"""
Chapter 2: Complete Tech Stack Deep Dive
"""
from reportlab.platypus import Paragraph, Spacer, PageBreak
from .common import (
    p, bullet, callout, hr, make_table, STYLES, CONTENT_WIDTH
)

def get_markdown() -> str:
    return """# Chapter 2 — Complete Tech Stack

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
"""

def get_flowables() -> list:
    story = []
    story.append(p("CHAPTER 2", 'CoverMeta'))
    story.append(p("Complete Tech Stack Deep Dive", 'ChapterTitle'))
    story.append(p("Implemented libraries, architectural selection rationale aur production alternatives.", 'ChapterSubtitle'))
    story.append(hr())

    story.append(p("2.1 Comprehensive Technology Matrix", 'SectionTitle'))
    story.append(p("Yeh table hamare project ke verified code components aur unke architectural rationale ko darshati hai:"))

    headers = ["Technology", "Role in Project", "Selection Rationale", "Actual Path", "Alternative"]
    rows = [
        ["React 18", "Frontend SPA UI", "Component state management, zero reload", "frontend/src/App.jsx", "Vue, Svelte"],
        ["Vite 5", "Build Tool / HMR", "Sub-second dev server startup, ES modules", "frontend/vite.config.js", "Webpack"],
        ["Vanilla CSS3", "Theme & Layout", "Custom lavender design, zero package bloat", "frontend/src/styles/", "Tailwind"],
        ["Pure SVG", "Dynamic Charts", "Zero chart library dependencies, lightweight", "src/components/SvgCharts.jsx", "Recharts"],
        ["Python 3.11", "Backend Engine", "High performance, robust data ecosystem", "Root environment", "Go, Java"],
        ["FastAPI", "REST API Engine", "Fast ASGI, auto OpenAPI /docs, validation", "backend/app/main.py", "Flask, Django"],
        ["Pydantic v2", "Data Schemas", "Type safety, serialization, automatic 422", "backend/app/models/", "Marshmallow"],
        ["Pandas 2.2", "Data Quality & Clean", "Vectorized parsing, missing value audits", "backend/app/processing/", "Polars"],
        ["PyArrow 15", "Parquet Export", "Columnar serialization, 80% compression", "services/export_service.py", "Fastparquet"],
        ["SQLite 3 (WAL)", "Relational Store", "Embedded, zero config, CTEs & window fn", "app/database/connection.py", "PostgreSQL"],
        ["PyTest", "Automated Tests", "29 verified passing test cases", "backend/tests/", "Unittest"],
        ["ReportLab 5", "PDF Generation", "Programmatic layout, vector flowables", "docs/generate_guide.py", "WeasyPrint"]
    ]
    col_widths = [62, 85, 160, 140, 85]
    story.append(make_table(headers, rows, col_widths, mono_cols=[3]))
    story.append(Spacer(1, 10))

    story.append(p("2.2 Frontend Stack Architecture: Pure SVG & Zero Heavy Bloat", 'SectionTitle'))
    story.append(p(
        "Frontend mein <b>React 18</b> aur <b>Vite 5</b> ka combination use kiya gaya hai. "
        "Sabse unique baat yeh hai ki charting ke liye kisi external package (jaise Recharts ya Chart.js) par depend nahi kiya gaya hai. "
        "<code>SvgCharts.jsx</code> component seedhe math calculate karke SVG coordinates draw karta hai. Isse page load instant hota hai "
        "aur koi npm dependency conflict nahi aati."
    ))

    story.append(callout(
        "Why SQLite in WAL Mode?",
        "Standard SQLite default rollback journal mode mein write operations ke waqt database ko poori tarah lock kar deta hai. "
        "Hamne <code>PRAGMA journal_mode = WAL;</code> (Write-Ahead Logging) enable kiya hai. Isse read operations write operations ko "
        "block nahi karte, jo analytical dashboards ke liye high read concurrency provide karta hai.",
        'tip'
    ))
    story.append(Spacer(1, 8))

    story.append(p("2.3 Planned but Not Implemented (Production Architecture)", 'SectionTitle'))
    story.append(p(
        "Agar is project ko PhonePe ya Razorpay ke production scale par scale karna ho, toh future roadmap mein yeh components aayenge:"
    ))
    story.append(bullet("<b>Apache Kafka:</b> Real-time streaming transaction pipeline ke liye."))
    story.append(bullet("<b>Celery / Redis:</b> Background worker queue 100MB+ batch files ke asynchronous ingestion ke liye."))
    story.append(bullet("<b>PostgreSQL:</b> Multi-node distributed OLTP storage ke liye."))
    story.append(bullet("<b>Isolation Forest:</b> Unsupervised machine learning based fraud scoring ke liye."))

    story.append(PageBreak())
    return story

