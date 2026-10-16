"""
SQL Analytics Queries for UPI Transaction Intelligence System.
Demonstrates:
- Aggregations and grouping
- INNER JOIN and LEFT JOIN
- Common Table Expressions (CTEs)
- Window functions (ROW_NUMBER, DENSE_RANK, LAG, rolling AVG)
- Parameterized execution for security
"""

# 1. Primary Dashboard KPIs
SQL_DASHBOARD_KPIS = """
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
"""

# 2. Daily Trends with CTE and Window Functions (LAG, Rolling 3-Day Average)
SQL_DAILY_TRENDS = """
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
    -- Window Function 1: LAG to compare volume with previous day
    LAG(tx_count, 1, tx_count) OVER (ORDER BY tx_date ASC) AS prev_day_count,
    -- Day over Day growth percentage
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
"""

# 3. Hourly Activity (Diurnal distribution across 24 hours)
SQL_HOURLY_TRENDS = """
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
    -- Window Function: Calculate % share of total daily volume
    ROUND(tx_count * 100.0 / NULLIF(SUM(tx_count) OVER (), 0), 2) AS volume_share_pct
FROM hour_totals
ORDER BY tx_hour ASC;
"""

# 4. Category-Wise Distribution with Window Function for share percentages
SQL_CATEGORY_DISTRIBUTION = """
WITH category_metrics AS (
    SELECT
        category,
        COUNT(*) AS tx_count,
        ROUND(SUM(amount), 2) AS tx_value,
        ROUND(AVG(amount), 2) AS avg_amount,
        SUM(CASE WHEN anomaly_flag = 1 THEN 1 ELSE 0 END) AS flagged_count
    FROM cleaned_transactions
    WHERE (:start_date IS NULL OR tx_date >= :start_date)
      AND (:end_date IS NULL OR tx_date <= :end_date)
    GROUP BY category
)
SELECT
    category,
    tx_count,
    tx_value,
    avg_amount,
    flagged_count,
    ROUND(tx_count * 100.0 / NULLIF(SUM(tx_count) OVER (), 0), 2) AS count_share_pct,
    ROUND(tx_value * 100.0 / NULLIF(SUM(tx_value) OVER (), 0), 2) AS value_share_pct
FROM category_metrics
ORDER BY tx_value DESC;
"""

# 5. Customer Summaries with CTEs, ROW_NUMBER for favorite category, LEFT JOIN, and DENSE_RANK
SQL_CUSTOMER_SUMMARIES = """
WITH customer_category_ranks AS (
    -- Rank categories per customer by volume to find each customer's favorite category
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
"""

SQL_CUSTOMER_COUNT = """
SELECT COUNT(DISTINCT customer_id) AS total_customers
FROM cleaned_transactions
WHERE (:search IS NULL OR customer_id LIKE '%' || :search || '%');
"""

# Customer Profile Detail with History
SQL_CUSTOMER_DETAIL = """
WITH customer_cat AS (
    SELECT
        customer_id,
        category,
        COUNT(*) AS cat_count,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY COUNT(*) DESC) AS rn
    FROM cleaned_transactions
    WHERE customer_id = :customer_id
    GROUP BY customer_id, category
)
SELECT
    c.customer_id,
    COUNT(c.transaction_id) AS total_transactions,
    ROUND(SUM(c.amount), 2) AS total_spent,
    ROUND(AVG(c.amount), 2) AS avg_amount,
    ROUND(MIN(c.amount), 2) AS min_amount,
    ROUND(MAX(c.amount), 2) AS max_amount,
    MIN(c.timestamp) AS first_tx,
    MAX(c.timestamp) AS last_tx,
    SUM(CASE WHEN c.anomaly_flag = 1 THEN 1 ELSE 0 END) AS flagged_count,
    SUM(CASE WHEN c.status = 'SUCCESS' THEN 1 ELSE 0 END) AS success_count,
    SUM(CASE WHEN c.status = 'FAILED' THEN 1 ELSE 0 END) AS failed_count,
    (SELECT category FROM customer_cat WHERE rn = 1) AS favorite_category
FROM cleaned_transactions c
WHERE c.customer_id = :customer_id
GROUP BY c.customer_id;
"""

SQL_CUSTOMER_HISTORY = """
SELECT
    transaction_id,
    timestamp,
    tx_date,
    tx_hour,
    merchant_id,
    amount,
    category,
    status,
    payment_method,
    bank_reference_number,
    anomaly_flag,
    anomaly_reason
FROM cleaned_transactions
WHERE customer_id = :customer_id
ORDER BY timestamp DESC
LIMIT :limit;
"""

# 6. Merchant Summaries with CTEs, Peak Hour ranking, and Volume Ranking
SQL_MERCHANT_SUMMARIES = """
WITH merchant_hourly AS (
    SELECT
        merchant_id,
        tx_hour,
        COUNT(*) AS hour_count,
        ROW_NUMBER() OVER (PARTITION BY merchant_id ORDER BY COUNT(*) DESC) AS hr_rank
    FROM cleaned_transactions
    GROUP BY merchant_id, tx_hour
),
merchant_peak_hr AS (
    SELECT merchant_id, tx_hour AS peak_hour
    FROM merchant_hourly
    WHERE hr_rank = 1
),
merchant_stats AS (
    SELECT
        merchant_id,
        category,
        COUNT(*) AS total_transactions,
        ROUND(SUM(amount), 2) AS total_value,
        ROUND(AVG(amount), 2) AS avg_amount,
        SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) AS success_count,
        SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) AS failed_count,
        SUM(CASE WHEN anomaly_flag = 1 THEN 1 ELSE 0 END) AS flagged_count
    FROM cleaned_transactions
    GROUP BY merchant_id
)
SELECT
    ms.merchant_id,
    ms.category,
    ms.total_transactions,
    ms.total_value,
    ms.avg_amount,
    ms.success_count,
    ms.failed_count,
    ms.flagged_count,
    COALESCE(mph.peak_hour, 12) AS peak_hour,
    DENSE_RANK() OVER (ORDER BY ms.total_value DESC) AS volume_rank
FROM merchant_stats ms
LEFT JOIN merchant_peak_hr mph ON ms.merchant_id = mph.merchant_id
WHERE (:search IS NULL OR ms.merchant_id LIKE '%' || :search || '%' OR ms.category LIKE '%' || :search || '%')
ORDER BY ms.total_value DESC
LIMIT :limit OFFSET :offset;
"""

SQL_MERCHANT_COUNT = """
SELECT COUNT(DISTINCT merchant_id) AS total_merchants
FROM cleaned_transactions
WHERE (:search IS NULL OR merchant_id LIKE '%' || :search || '%' OR category LIKE '%' || :search || '%');
"""

SQL_MERCHANT_DETAIL = """
SELECT
    merchant_id,
    category,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount), 2) AS total_value,
    ROUND(AVG(amount), 2) AS avg_amount,
    ROUND(MIN(amount), 2) AS min_amount,
    ROUND(MAX(amount), 2) AS max_amount,
    MIN(timestamp) AS first_tx,
    MAX(timestamp) AS last_tx,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) AS success_count,
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) AS failed_count,
    SUM(CASE WHEN anomaly_flag = 1 THEN 1 ELSE 0 END) AS flagged_count,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM cleaned_transactions
WHERE merchant_id = :merchant_id
GROUP BY merchant_id;
"""

SQL_MERCHANT_HOURLY = """
SELECT
    tx_hour,
    COUNT(*) AS tx_count,
    ROUND(SUM(amount), 2) AS tx_value,
    ROUND(AVG(amount), 2) AS avg_amount
FROM cleaned_transactions
WHERE merchant_id = :merchant_id
GROUP BY tx_hour
ORDER BY tx_hour ASC;
"""

# 7. Dynamic Pattern Insights (Peak hour, top category, highest velocity day)
SQL_PATTERN_INSIGHTS = """
WITH peak_hour_calc AS (
    SELECT
        tx_hour,
        COUNT(*) AS tx_count,
        ROUND(SUM(amount), 2) AS tx_value,
        ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS rn
    FROM cleaned_transactions
    GROUP BY tx_hour
),
top_category_calc AS (
    SELECT
        category,
        COUNT(*) AS tx_count,
        ROUND(SUM(amount), 2) AS tx_value,
        ROW_NUMBER() OVER (ORDER BY SUM(amount) DESC) AS rn
    FROM cleaned_transactions
    GROUP BY category
),
peak_day_calc AS (
    SELECT
        tx_date,
        COUNT(*) AS tx_count,
        ROUND(SUM(amount), 2) AS tx_value,
        ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS rn
    FROM cleaned_transactions
    GROUP BY tx_date
),
overall_stats AS (
    SELECT
        COUNT(*) AS total_tx,
        ROUND(SUM(amount), 2) AS total_val,
        ROUND(AVG(amount), 2) AS avg_amt
    FROM cleaned_transactions
)
SELECT
    (SELECT tx_hour FROM peak_hour_calc WHERE rn = 1) AS peak_hour,
    (SELECT tx_count FROM peak_hour_calc WHERE rn = 1) AS peak_hour_count,
    (SELECT tx_value FROM peak_hour_calc WHERE rn = 1) AS peak_hour_value,
    (SELECT category FROM top_category_calc WHERE rn = 1) AS top_category_by_value,
    (SELECT tx_value FROM top_category_calc WHERE rn = 1) AS top_category_value,
    (SELECT tx_date FROM peak_day_calc WHERE rn = 1) AS busiest_date,
    (SELECT tx_count FROM peak_day_calc WHERE rn = 1) AS busiest_date_count,
    (SELECT total_tx FROM overall_stats) AS overall_count,
    (SELECT total_val FROM overall_stats) AS overall_value,
    (SELECT avg_amt FROM overall_stats) AS overall_avg
;
"""

