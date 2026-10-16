# UPI Transaction Intelligence System

> **Target Relevance:** PhonePe, Razorpay, Visa, Mastercard  
> A production-ready, full-stack financial analytics and rule-based anomaly detection platform built with **FastAPI**, **React**, **SQLite**, and **Apache Parquet**.

---

## 1. Project Overview

The **UPI Transaction Intelligence System** provides payment companies, acquirers, and network operators with actionable intelligence into UPI payment behavior. It features:
- **Executive KPI Tracking:** Total volume, transaction value in Indian Rupees (₹), average ticket size, and review candidate rates.
- **Diurnal Traffic Curves:** 24-hour diurnal volume distribution modeling real-world Indian payment behavior (morning ramp, lunch spike, evening peak 7:00–10:00 PM).
- **Transaction Explorer:** Server-side search, multi-criteria filtering, sorting, pagination, and slide-in inspection drawers.
- **Customer & Merchant Analytics:** Behavioral summaries powered by SQL Common Table Expressions (CTEs) and window functions (`DENSE_RANK`, `ROW_NUMBER`).
- **Rule-Based Anomaly Detection:** Explainable, transparent rules with configurable mathematical thresholds (statistical Z-score, velocity windows, high-value outliers).
- **Data Quality & Quarantine Governance:** Raw file preservation, duplicate quarantine policy, and column-wise missing value audits.
- **Multi-Format Reporting:** Instant CSV exports and columnar Apache Parquet downloads.

---

## 2. Visual Design Language

Adheres to a minimalist, full-screen SaaS aesthetic:
- **Full Viewport Layout:** Occupies 100% available browser width with `min-height: 100vh` without restrictive centered containers or excessive margins.
- **Main Surface:** Warm off-white workspace canvas (`#F8F3EF`).
- **Sidebar & Header:** Clean sticky navigation with lavender accents (`#8A63F4` / `#B9A0F5`).
- **Content Surface:** Clean white cards (`#FFFFFF`) with rounded corners (`16px`), subtle borders (`#ECE8E5`), and restrained shadows.
- **Typography & Formatting:** Dark charcoal headings (`#20201F`), muted warm grey descriptions (`#77736F`), with `JetBrains Mono` for currency (`₹`) and transaction IDs.
- **Zero Mock / Pure Empty State:** Defaults to a clean, professional empty state (`—` for uncalculated metrics, informative empty banners, zero fabricated records) until a real transaction CSV is uploaded.

---

## 3. Technology Stack & Architectural Constraints

- **Frontend:** React 18, HTML5, CSS3, Fetch API, pure SVG dynamic charts (zero external charting libraries, zero heavy UI frameworks).
- **Backend:** Python 3.11, FastAPI, Pydantic v2, Uvicorn, structured Python logging.
- **Data Processing:** Pandas, NumPy, PyArrow for Parquet serialization.
- **Database:** SQLite with WAL mode, parameterized queries, CTEs, and window functions.
- **Strict Adherence:** No AI/ML blackboxes, no Next.js, no TypeScript, no Tailwind CSS, no Redux, no Celery, no Kafka, no Docker, and no extraneous ORMs.

---

## 4. System Architecture & Processing Pipeline

The system operates strictly on **user-uploaded transaction records**:

```
[User CSV File Upload]
           │
           ▼
[1] Two-Stage Schema Inspection (POST /api/data-quality/validate-upload)
    - Validates mandatory columns: transaction_id, timestamp, customer_id, merchant_id, amount, category, status
    - Pre-audits null counts, duplicate candidates, and invalid amount rows
    - Displays interactive preview table (first 5 rows) and validation summary in UI
           │
           ▼
[2] User Confirms Ingestion (POST /api/data-quality/upload)
    - Records stored immutably in `raw_transactions`
           │
           ▼
[3] Data Cleaning & Deduplication Segregation
    - Valid transactions normalized and deduplicated: first occurrence kept in `cleaned_transactions`
    - Corrupt amounts, unparseable dates, and duplicate IDs isolated to `quarantined_transactions` with reasons
           │
           ▼
[4] Rule-Based Anomaly Detection
    - Evaluates mathematical rules: High-value (₹50,000+), Velocity spikes (3+ tx / 5m), Customer Z-Score (Z >= 2.5)
    - Review candidates saved to `anomaly_findings`
           │
           ▼
[5] High-Performance Columnar Serialization
    - Cleaned transaction dataset exported to Apache Parquet (`cleaned_transactions.parquet`) via PyArrow
           │
           ▼
[6] Dynamic Dashboard Analytics
    - Instant SQL analytics update across KPIs, diurnal charts, customer rankings, and merchant summaries
```

---

## 5. SQL Analytics Demonstrated

The system demonstrates advanced SQL analytical querying on SQLite:

1. **Common Table Expressions (CTEs):**
   - Multi-stage aggregations (`WITH daily_aggregates AS (...)`, `WITH customer_category_ranks AS (...)`).
2. **Window Functions:**
   - `ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY COUNT(*) DESC)` to determine each customer's favorite merchant category.
   - `DENSE_RANK() OVER (ORDER BY total_spent DESC)` to rank customers and merchants by volume.
   - `LAG(tx_count, 1) OVER (ORDER BY tx_date ASC)` to calculate day-over-day transaction volume growth.
   - `AVG(tx_count) OVER (ORDER BY tx_date ASC ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)` to generate 3-day rolling throughput trends.
   - `SUM(amount) * 100.0 / SUM(SUM(amount)) OVER ()` for dynamic category share percentages.
3. **Strict Parameterization:**
   - All user-supplied filter criteria (`search`, `start_date`, `end_date`, `category`, `status`, `min_amount`, `max_amount`) use parameterized bind variables (`:param`) to eliminate SQL injection vulnerabilities.

---

## 6. Mathematical & Anomaly Detection Rules

The anomaly engine uses explainable heuristics and statistical rules:

1. **High-Value Transactions:**
   $$\text{amount} > \text{high\_value\_threshold} \quad (\text{Default: ₹50,000.00})$$
2. **Customer Velocity Spike (Rapid Burst):**
   Flags multiple transactions by the same customer initiated within a configurable rolling window:
   $$\Delta t \le \text{velocity\_window\_minutes} \quad (\text{Default: 5 mins, Count} \ge 3)$$
3. **Unusual Customer Spend (Statistical Z-Score):**
   For customers with sufficient transaction history ($N \ge 3$):
   $$\mu = \frac{1}{N} \sum_{i=1}^N x_i, \quad \sigma^2 = \frac{1}{N-1} \sum_{i=1}^N (x_i - \mu)^2, \quad Z = \frac{X - \mu}{\sigma}$$
   Flags transactions where $Z \ge \text{customer\_zscore\_threshold}$ (Default: 2.5).
   *Documented Limitation:* Assumes approximately normal distribution; legitimate one-off major purchases (festivals, medical bills) may trigger review flags.
4. **Duplicate Record Review:**
   Flags duplicate transaction IDs for review and isolates them in quarantine.
5. **Invalid Entries:**
   Detects negative amounts, zero amounts, missing customer VPAs, and corrupt timestamps.

> **Governance Notice:** Flagged transactions are categorized as **review candidates**, not definitive proof of fraud.

---

## 7. REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check returning status and database row counts |
| `GET` | `/api/dashboard/summary` | Core KPIs (Volume, Value, Avg Ticket, Flagged Rate) |
| `GET` | `/api/dashboard/daily-trends` | Day-by-day throughput, DoD growth, and 3-day rolling averages |
| `GET` | `/api/dashboard/hourly-trends` | 24-hour diurnal activity distribution |
| `GET` | `/api/dashboard/category-distribution`| Category-wise volume, spend, and percentage share |
| `GET` | `/api/dashboard/patterns` | Dynamic pattern insights with factual descriptions |
| `GET` | `/api/transactions` | Search, filter, sort, and paginate through cleaned transactions |
| `GET` | `/api/transactions/{id}` | Detailed profile for an individual transaction |
| `GET` | `/api/customers` | Customer summaries with rankings and favorite categories |
| `GET` | `/api/customers/{id}` | Customer detail profile and full transaction history |
| `GET` | `/api/merchants` | Merchant summaries with peak hours and volume rankings |
| `GET` | `/api/merchants/{id}` | Merchant profile with 24-hour hourly activity breakdown |
| `GET` | `/api/anomalies` | Audit log of all rule-based anomaly findings |
| `GET` | `/api/anomalies/config` | Retrieve configurable threshold parameters |
| `POST`| `/api/anomalies/config` | Update threshold parameters and trigger re-evaluation |
| `GET` | `/api/data-quality/summary` | Dataset validation report and health metrics |
| `GET` | `/api/data-quality/quarantined`| Paginated log of isolated invalid and duplicate rows |
| `POST`| `/api/data-quality/upload` | Upload CSV dataset for ingestion and processing |
| `POST`| `/api/processing/run` | Re-process benchmark synthetic dataset |
| `GET` | `/api/reports/export` | Download reports as CSV or processed dataset as Parquet |

---

## 8. Installation & Local Setup

### Prerequisites
- **Python 3.10+** (Python 3.11 recommended)
- **Node.js 18+** & **npm 9+**

### Step 1: Clone and Environment Setup
```bash
cd c:\Users\Mahesh\Documents\upi
cp .env.example .env
```

### Step 2: Backend Setup
Install Python dependencies:
```bash
pip install -r backend/requirements.txt
```

### Step 3: Frontend Setup
Install frontend packages:
```bash
cd frontend
npm install
cd ..
```

---

## 9. Running the Application

### Option A: Run Backend Server
From the root directory:
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
*The backend initializes the SQLite schema on startup in clean empty mode, ready for user CSV uploads.*
- API Base URL: `http://127.0.0.1:8000`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`

### Option B: Run Frontend Development Server
In a separate terminal:
```bash
cd frontend
npm run dev
```
- Open browser at: `http://localhost:3000`

---

## 10. Automated Testing

Run the full automated test suite using `pytest`:
```bash
pytest backend/tests -v
```

### Test Suite Coverage:
- `test_validation.py`: Schema validation, missing columns, invalid amounts, unparseable dates.
- `test_cleaning.py`: Deduplication policy, quarantine segregation, status normalization.
- `test_anomaly_detection.py`: High-value rule, velocity burst rule, Z-score variance calculation.
- `test_sql_analytics.py`: SQL CTEs, window functions (`LAG`, `ROW_NUMBER`, `DENSE_RANK`), aggregations.
- `test_api.py`: FastAPI endpoints, health check, pagination, filtering, pattern narratives.
- `test_exports.py`: CSV generation for all report types and Parquet dataset serialization.

