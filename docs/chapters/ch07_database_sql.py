"""
Chapter 7: Database aur SQL Analytics
"""
from reportlab.platypus import Paragraph, Spacer, PageBreak
from .common import (
    p, bullet, callout, hr, code_block, STYLES, CONTENT_WIDTH
)

def get_markdown() -> str:
    return """# Chapter 7 — Database aur Advanced SQL Analytics

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
3. `dod_growth_pct`: Formula $((tx_{today} - tx_{yesterday}) / tx_{yesterday}) \times 100$ se daily growth percentage nikalta hai.
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
"""

def get_flowables() -> list:
    story = []
    story.append(p("CHAPTER 7", 'CoverMeta'))
    story.append(p("Database Architecture & Advanced SQL Analytics", 'ChapterTitle'))
    story.append(p("SQLite WAL concurrency, schema structure, indexes, and in-depth analysis of 7 SQL master queries.", 'ChapterSubtitle'))
    story.append(hr())

    story.append(p("7.1 Storage Engine Configuration: SQLite3 in WAL Mode", 'SectionTitle'))
    story.append(p(
        "Financial systems mein read-write locking ek bada bottleneck hota hai. "
        "Hamne <code>PRAGMA journal_mode = WAL;</code> enforce kiya hai. Isse readers bina writers ko block kiye "
        "high-frequency analytical queries execute kar sakte hain."
    ))

    code_conn = """conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30.0)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA journal_mode = WAL;")       # Concurrency
conn.execute("PRAGMA synchronous = NORMAL;")     # Speed with safety
conn.execute("PRAGMA foreign_keys = ON;")"""
    story.append(code_block(code_conn, "SQLite Connection PRAGMAs"))
    story.append(Spacer(1, 8))

    story.append(p("7.2 Master SQL Query 1: Primary Dashboard KPIs", 'SectionTitle'))
    story.append(p(
        "Dashboard ke core KPI cards ke liye <code>SQL_DASHBOARD_KPIS</code> execute hota hai. "
        "Yeh query total volume, processed GMV, average ticket size aur status distribution nikalta hai:"
    ))

    code_kpi = """SELECT
    COUNT(*) AS total_transactions,
    COALESCE(SUM(amount), 0.0) AS total_value,
    COALESCE(AVG(amount), 0.0) AS avg_amount,
    COALESCE(SUM(CASE WHEN anomaly_flag = 1 THEN 1 ELSE 0 END), 0) AS flagged_count,
    ROUND(COALESCE(SUM(CASE WHEN anomaly_flag = 1 THEN 1.0 ELSE 0.0 END) * 100.0 / NULLIF(COUNT(*), 0), 0.0), 2) AS flagged_rate_pct,
    COALESCE(SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END), 0) AS success_count,
    COALESCE(SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END), 0) AS failed_count
FROM cleaned_transactions
WHERE (:start_date IS NULL OR tx_date >= :start_date)
  AND (:end_date IS NULL OR tx_date <= :end_date);"""
    story.append(code_block(code_kpi, "SQL_DASHBOARD_KPIS"))
    story.append(Spacer(1, 8))

    story.append(callout(
        "Verification: Are Failed Transactions Counted in Total GMV?",
        "Codebase verification: Ha! <code>COUNT(*)</code> aur <code>SUM(amount)</code> poore <code>cleaned_transactions</code> "
        "par calculate hote hain, jisme SUCCESS aur FAILED dono shamil hain. Lekin saath hi <code>success_count</code> aur "
        "<code>failed_count</code> conditional sums alag se compute hote hain taaki dashboard exact status bifurcation show kar sake.",
        'interview'
    ))
    story.append(Spacer(1, 8))

    story.append(p("7.3 Master SQL Query 2: CTEs & Window Functions (LAG & Rolling Avg)", 'SectionTitle'))
    story.append(p(
        "Daily trend analytics ke liye <code>SQL_DAILY_TRENDS</code> mein CTE aur advanced window functions use kiye gaye hain. "
        "<code>LAG()</code> previous day ke count ko current day se subtract karke Day-over-Day growth nikalta hai, aur "
        "<code>ROWS BETWEEN 2 PRECEDING AND CURRENT ROW</code> 3-day rolling moving average calculate karta hai."
    ))

    story.append(PageBreak())
    return story

