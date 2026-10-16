"""
Chapter 1: Project Overview & Real-World Business Context
"""
from reportlab.platypus import Paragraph, Spacer, PageBreak
from .common import (
    p, bullet, callout, hr, STYLES, CONTENT_WIDTH
)

def get_markdown() -> str:
    return """# Chapter 1 — Project Overview & Business Context

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
"""

def get_flowables() -> list:
    story = []
    story.append(p("CHAPTER 1", 'CoverMeta'))
    story.append(p("Project Overview & Real-World Fintech Context", 'ChapterTitle'))
    story.append(p("UPI Transaction Intelligence System ka vision, problem statement aur architecture scope.", 'ChapterSubtitle'))
    story.append(hr())

    story.append(p("1.1 Project Kya Hai aur Iska Vision Kya Hai?", 'SectionTitle'))
    story.append(p(
        "<b>UPI Transaction Intelligence System</b> ek production-grade financial analytics aur rule-based anomaly detection platform hai. "
        "Is system ko Indian digital payment ecosystem (jaise <b>PhonePe, Razorpay, Visa, Mastercard</b>) ke operational scale aur "
        "analytical challenges ko solve karne ke liye design kiya gaya hai. Yeh system raw transaction CSV files ko ingest karta hai, "
        "data cleaning aur quarantine governance apply karta hai, advanced SQL CTEs aur window functions se business metrics compute karta hai, "
        "aur lightweight React 18 dashboard par interactive SVG charts ke through display karta hai."
    ))

    story.append(callout(
        "Core Philosophy: Zero Hallucination & Pure Explainability",
        "Hamara system banking compliance (RBI audit standards) ko follow karta hai. Kisi bhi transaction ko 'Fraud' label karne ke bajaye "
        "'Review Candidate' kaha jaata hai, aur har flag ke peeche ka mathematical threshold (jaise High Value > ₹50,000 ya Z-Score >= 2.5) "
        "dashboard par 100% transparently explain hota hai.",
        'governance'
    ))
    story.append(Spacer(1, 8))

    story.append(p("1.2 Real-World Problem: Fintech Industry ke 4 Operational Blindspots", 'SectionTitle'))
    story.append(bullet("<b>Diurnal Traffic Bursts:</b> Sham ke 7 PM se 10 PM ke beech UPI volume peak karta hai. Real-time hourly visibility ke bina infrastructure scaling aur failure mitigation mushkil ho jaata hai."))
    story.append(bullet("<b>Dirty Data Ingestion:</b> Raw batch files mein duplicate IDs, negative corrupt amounts, aur missing VPAs aate hain. Bina quarantine layer ke reporting data corrupt ho jaata hai."))
    story.append(bullet("<b>Black-Box ML Inauditability:</b> Unexplainable neural network models banking audits mein fail ho jaate hain kyunki customer ya regulator ko reason explain nahi kiya ja sakta."))
    story.append(bullet("<b>Analytical Bottlenecks:</b> Millions of rows par rolling trends aur customer rankings nikalne ke liye fast SQL window functions aur columnar Parquet storage ki zaroorat hoti hai."))
    story.append(Spacer(1, 6))

    story.append(p("1.3 Business Value Matrix", 'SectionTitle'))
    story.append(p(
        "Different fintech departments is system ka use karke apne operations ko streamline karte hain:"
    ))
    story.append(bullet("<b>Fraud & Risk Operations:</b> Heuristic anomaly rules se review candidates instantly identify hote hain."))
    story.append(bullet("<b>Merchant Operations:</b> Settlement analysis, hourly peak distribution, aur volume ranking milti hai."))
    story.append(bullet("<b>Data Quality Officers:</b> Raw data preservation aur quarantined records ka transparent log milta hai."))
    story.append(bullet("<b>Engineering Aspirants:</b> Full-stack FastAPI + React + SQLite + Parquet ka practical reference milta hai."))
    story.append(Spacer(1, 8))

    story.append(p("1.4 Practical Walkthrough: Raw Record se Business Insight Tak", 'SectionTitle'))
    story.append(p(
        "Maan lijiye user ne CSV upload kiya jisme <code>TXN_101</code> (₹500, Grocery), <code>TXN_102</code> (₹65,000, Electronics), "
        "aur wapas <code>TXN_101</code> (Duplicate) aaye. System duplicate record ko quarantine table mein filter kar dega, valid transactions "
        "ko clean table mein daalega, <code>TXN_102</code> ko High-Value flag lagayega (kyunki amount > ₹50,000 hai), aur dashboard par "
        "GMV ₹65,500 aur Average Ticket ₹32,750 display karega."
    ))

    story.append(callout(
        "Current System Limitations (Architectural Honesty)",
        "Yeh system batch-based CSV upload par kaam karta hai (real-time Kafka stream nahi hai). "
        "Database SQLite3 WAL mode par based hai (production high-concurrency ke liye PostgreSQL recommend kiya gaya hai). "
        "Processing synchronous hai aur ML black-box ke bajaye explainable mathematical rules engine use karta hai.",
        'warning'
    ))

    story.append(PageBreak())
    return story

