"""
Chapter 12: Project ko Practically Use Kaise Karein
"""
from reportlab.platypus import Paragraph, Spacer, PageBreak
from .common import (
    p, bullet, callout, hr, code_block, STYLES, CONTENT_WIDTH
)

def get_markdown() -> str:
    return """# Chapter 12 — Project ko Practically Use Kaise Karein

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
cd c:\\Users\\Mahesh\\Documents\\upi
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
"""

def get_flowables() -> list:
    story = []
    story.append(p("CHAPTER 12", 'CoverMeta'))
    story.append(p("Project ko Practically Use Kaise Karein", 'ChapterTitle'))
    story.append(p("Prerequisites, installation commands, starting local servers, and complete UI workflow walkthrough.", 'ChapterSubtitle'))
    story.append(hr())

    story.append(p("12.1 Local Installation Commands", 'SectionTitle'))
    story.append(p("Terminal mein commands execute karke environment setup karein:"))

    cmd_setup = """# Backend setup:
pip install -r backend/requirements.txt

# Frontend setup:
cd frontend && npm install && cd ..

# Start Backend Server (Terminal 1):
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# Start Frontend Server (Terminal 2):
cd frontend && npm run dev"""
    story.append(code_block(cmd_setup, "BASH / POWERSHELL COMMANDS"))
    story.append(Spacer(1, 8))

    story.append(p("12.2 End-to-End User Actions in Browser UI", 'SectionTitle'))
    story.append(bullet("<b>1. Open Browser:</b> Navigate to <code>http://localhost:3000</code>."))
    story.append(bullet("<b>2. Click 'Upload Dataset':</b> Header button opens two-stage ingestion modal."))
    story.append(bullet("<b>3. Inspect & Validate:</b> Pre-audit validates 7 required columns and shows 5 preview rows."))
    story.append(bullet("<b>4. Confirm & Ingest:</b> Runs deduplication, quarantine segregation, and anomaly engine."))
    story.append(bullet("<b>5. Explore Dashboard:</b> KPIs, diurnal curves, customer spend ranks and merchant analytics appear."))
    story.append(bullet("<b>6. Download Reports:</b> Instant CSV summaries and high-speed columnar Apache Parquet files."))

    story.append(PageBreak())
    return story

