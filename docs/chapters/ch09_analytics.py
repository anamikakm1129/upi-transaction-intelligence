"""
Chapter 9: Transaction Analytics, Diurnal Curves & Business KPIs
"""
from reportlab.platypus import Paragraph, Spacer, PageBreak
from .common import (
    p, bullet, callout, hr, code_block, STYLES, CONTENT_WIDTH
)

def get_markdown() -> str:
    return """# Chapter 9 — Transaction Analytics, Diurnal Curves & Business KPIs

## 9.1 Core Financial KPIs & Exact Mathematical Formulas

Hamare system ke executive dashboard par 6 primary metrics display hote hain. Neeche unke exact mathematical formulas aur code paths diye gaye hain:

### 1. Total Transactions ($N_{total}$)
- **Formula:**
  $$N_{total} = \text{COUNT}(*)$$
- **Code Path:** `backend/app/database/queries.py` -> `SQL_DASHBOARD_KPIS`
- **Logic:** `cleaned_transactions` table mein maujood sabhi validated transaction rows ka count.

### 2. Total Transaction Value / Gross Merchandise Value ($V_{total}$)
- **Formula:**
  $$V_{total} = \sum_{i=1}^{N} \text{amount}_i$$
- **Code Path:** `SQL_DASHBOARD_KPIS` -> `COALESCE(SUM(amount), 0.0)`
- **Logic:** Sabhi valid transaction amounts ka sum (in Indian Rupees ₹). Agar table empty ho, toh `COALESCE` NULL ke bajaye `0.0` return karta hai.

### 3. Average Transaction Amount / Ticket Size ($\bar{X}$)
- **Formula:**
  $$\bar{X} = \frac{V_{total}}{N_{total}} = \frac{\sum_{i=1}^{N} \text{amount}_i}{N}$$
- **Code Path:** `SQL_DASHBOARD_KPIS` -> `COALESCE(AVG(amount), 0.0)`

### 4. Anomaly Review Candidate Rate ($R_{flagged}$)
- **Formula:**
  $$R_{flagged} = \left(\frac{N_{flagged}}{N_{total}}\right) \times 100$$
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
- **Total Transaction Value:** $100 + 200 + 300 = \text{₹}600.00$
- **Average Ticket Size:** $\frac{600}{3} = \text{₹}200.00$
- **Status Breakdown:** `success_count = 2`, `failed_count = 1`, `pending_count = 0`.
- **Success Rate:** $\frac{2}{3} \times 100 = 66.67\%$.

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
$$\text{DoD Growth \%} = \left(\frac{\text{Count}_{today} - \text{Count}_{yesterday}}{\text{Count}_{yesterday}}\right) \times 100$$
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
$$\text{MA}_{3\text{-day}} = \frac{\text{Count}_{today} + \text{Count}_{yesterday} + \text{Count}_{day\_before}}{3}$$
Query mein:
```sql
ROUND(AVG(tx_count) OVER (
    ORDER BY tx_date ASC
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
), 1) AS rolling_3day_avg
```
"""

def get_flowables() -> list:
    story = []
    story.append(p("CHAPTER 9", 'CoverMeta'))
    story.append(p("Transaction Analytics, Diurnal Curves & Business KPIs", 'ChapterTitle'))
    story.append(p("Mathematical formulas, KPI aggregations, Indian UPI diurnal behavior, and DoD growth analytics.", 'ChapterSubtitle'))
    story.append(hr())

    story.append(p("9.1 Core Financial Metric Calculations", 'SectionTitle'))
    story.append(p(
        "Fintech executive dashboards par decision-making ke liye 4 primary KPIs track hote hain: "
        "<b>Total Volume (N_total)</b>, <b>Gross Merchandise Value (V_total)</b>, "
        "<b>Average Ticket Size (Avg_Ticket)</b>, aur <b>Review Candidate Flag Rate (Flag_Rate)</b>."
    ))

    story.append(callout(
        "Numerical Demonstration",
        "Agar 3 transactions hain: ₹100 (Success), ₹200 (Success), ₹300 (Failed):<br/>"
        "• Total Volume = 3 records<br/>"
        "• Total Value = ₹600.00<br/>"
        "• Average Ticket Size = ₹200.00<br/>"
        "• Success Count = 2, Failed Count = 1 (Failed Rate = 33.33%)<br/>"
        "Actual codebase mein <code>COUNT(*)</code> aur <code>SUM(amount)</code> poore cleaned records ko count karte hain, "
        "jabki conditional sums status bifurcation expose karte hain.",
        'tip'
    ))
    story.append(Spacer(1, 8))

    story.append(p("9.2 Indian UPI Diurnal Traffic Behavior (Peak 7–10 PM)", 'SectionTitle'))
    story.append(p(
        "Indian UPI payment traffic 24 ghante mein random nahi chalti, balki ek predictable diurnal curve follow karti hai: "
        "raat ko 1 AM se 5 AM lull period hota hai (<1%), subah 8 AM se groceries ramp hoti hain, dopahar 1 PM lunch spike aata hai, "
        "aur sham <b>7:00 PM se 10:00 PM</b> ke beech super-peak (30%+ daily volume) banta hai. "
        "Hamara <code>SQL_HOURLY_TRENDS</code> query har ghante ka <code>volume_share_pct</code> calculate karta hai."
    ))

    story.append(Spacer(1, 8))

    story.append(p("9.3 Day-over-Day (DoD) Growth & 3-Day Moving Averages", 'SectionTitle'))
    story.append(p(
        "SQL Window Functions <code>LAG()</code> aur <code>ROWS BETWEEN 2 PRECEDING AND CURRENT ROW</code> "
        "ke zariye daily volatility smooth hoti hai aur growth trends instantly compute hote hain:"
    ))

    code_dod = """-- Day-over-Day Growth & Rolling Moving Average
LAG(tx_count, 1, tx_count) OVER (ORDER BY tx_date ASC) AS prev_day_count,
ROUND((tx_count - LAG(tx_count, 1, tx_count) OVER (ORDER BY tx_date ASC)) * 100.0 /
      NULLIF(LAG(tx_count, 1, tx_count) OVER (ORDER BY tx_date ASC), 0), 2) AS dod_growth_pct,
ROUND(AVG(tx_count) OVER (ORDER BY tx_date ASC ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 1) AS rolling_3day_avg"""
    story.append(code_block(code_dod, "Window Functions DoD Growth"))

    story.append(PageBreak())
    return story
