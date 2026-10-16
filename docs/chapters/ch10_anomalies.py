"""
Chapter 10: Rule-Based Anomaly Detection & Fraud Governance
"""
from reportlab.platypus import Paragraph, Spacer, PageBreak
from .common import (
    p, bullet, callout, hr, code_block, make_table, STYLES, CONTENT_WIDTH
)

def get_markdown() -> str:
    return """# Chapter 10 — Rule-Based Anomaly Detection & Fraud Governance

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
  $$\text{amount} > \text{high\_value\_threshold} \quad (\text{Default: ₹50,000.00})$$
- **Severity Evaluation:**
  Agar amount threshold ke 1.5x se zyada ho (jaise ₹75,000+), toh Severity `HIGH` hoti hai, warna `MEDIUM`.
- **Business Rationale:** UPI par high-value outflows account takeover ya skimming scams ke primary indicators hote hain.
- **Implemented Function:** `detect_anomalies()` in `anomaly_detection.py`.

---

### Rule 2: Repeated Rapid Transactions (Customer Velocity Spike)
- **Condition:**
  $$\Delta t = t_j - t_i \le \text{velocity\_window\_minutes} \quad (\text{Default: 5 mins, Count} \ge 3)$$
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
   $$\mu = \frac{1}{N} \sum_{i=1}^{N} x_i$$
   *Example:* Agar customer ne pichhle 4 transactions ₹200, ₹250, ₹300, ₹250 ke kiye hain, toh mean $\mu = \frac{1000}{4} = \text{₹}250$.
2. **Variance ($\sigma^2$) & Standard Deviation ($\sigma$):**
   Variance yeh measure karta hai ki customer ke transactions average se kitna fluctuate (faile) hue hain.
   Sample Variance ($ddof=1$):
   $$\sigma^2 = \frac{1}{N - 1} \sum_{i=1}^{N} (x_i - \mu)^2$$
   Standard Deviation $\sigma$ variance ka square root hota hai:
   $$\sigma = \sqrt{\sigma^2}$$
3. **Z-Score Formula:**
   $$Z = \frac{X_{current} - \mu}{\sigma}$$
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
"""

def get_flowables() -> list:
    story = []
    story.append(p("CHAPTER 10", 'CoverMeta'))
    story.append(p("Rule-Based Anomaly Detection & Fraud Governance", 'ChapterTitle'))
    story.append(p("Explainable heuristic rules, statistical Z-score, sliding velocity windows aur banking compliance.", 'ChapterSubtitle'))
    story.append(hr())

    story.append(p("10.1 Why Explainable Heuristics over ML Black-Boxes?", 'SectionTitle'))
    story.append(p(
        "Banking aur RBI regulations ke tehat har flagged payment ka reason customer aur auditor ko "
        "<b>100% explainable</b> hona chahiye. Black-box deep learning models audit trails provide nahi kar paate. "
        "Isliye hamara platform transparent mathematical rules use karta hai."
    ))

    story.append(callout(
        "Governance Policy: Review Candidates, Not Fraud Proof",
        "System kisi bhi transaction ko 'Fraudulent' declare nahi karta. Unhe 'Review Candidate' flag milta hai. "
        "Example ke liye, festival ke din ₹65,000 ka television khareedna High-Value trigger karega, "
        "par woh genuine customer purchase ho sakti hai.",
        'governance'
    ))
    story.append(Spacer(1, 8))

    story.append(p("10.2 Statistical Z-Score Spending Outlier (Mean & Variance)", 'SectionTitle'))
    story.append(p(
        "Z-score statistical rule customer ke personal spending pattern par calculate hota hai: "
        "<b>Mean ($\mu$)</b> historical average spend batata hai, <b>Variance ($\sigma^2$)</b> standard deviation $(\sigma)$ "
        "ke zariye fluctuation measure karta hai, aur $Z = (X - \mu) / \sigma$ yeh measure karta hai ki transaction "
        "personal average se kitne standard deviations door hai. Agar $Z \ge 2.5$ ho aur minimum 3 transactions ka history ho, "
        "toh transaction review candidate banti hai."
    ))

    story.append(Spacer(1, 8))

    story.append(p("10.3 5 Implemented Rules Summary Table", 'SectionTitle'))
    headers = ["Rule Name", "Condition / Threshold", "Severity", "Mathematical Logic"]
    rows = [
        ["High-Value", "amount > ₹50,000", "HIGH / MED", "Amount exceeds configured threshold"],
        ["Velocity Spike", ">= 3 txns in 5 mins", "HIGH", "Sliding time-window burst count"],
        ["Customer Z-Score", "Z >= 2.5 (N >= 3)", "MEDIUM", "Deviation from personal historical mean"],
        ["Duplicate Record", "Duplicate TXN ID", "HIGH", "Quarantine deduplication candidate"],
        ["Invalid Entry", "Amount <= 0 / Bad Date", "LOW", "Data corruption review candidate"]
    ]
    col_widths = [110, 120, 75, 227]
    story.append(make_table(headers, rows, col_widths, mono_cols=[0]))

    story.append(PageBreak())
    return story
