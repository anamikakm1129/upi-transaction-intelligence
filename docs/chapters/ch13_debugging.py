"""
Chapter 13: Debugging aur Common Errors
"""
from reportlab.platypus import Paragraph, Spacer, PageBreak
from .common import (
    p, bullet, callout, hr, code_block, make_table, STYLES, CONTENT_WIDTH
)

def get_markdown() -> str:
    return """# Chapter 13 — Debugging aur Common Errors

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
"""

def get_flowables() -> list:
    story = []
    story.append(p("CHAPTER 13", 'CoverMeta'))
    story.append(p("Debugging aur Common Errors", 'ChapterTitle'))
    story.append(p("10 common production/development errors, root cause analysis, diagnostic commands, and code-level fixes.", 'ChapterSubtitle'))
    story.append(hr())

    story.append(p("13.1 Troubleshooting Matrix (10 Core Scenarios)", 'SectionTitle'))
    story.append(p(
        "Fintech systems develop karte waqt aane wale standard errors aur unke verified fixes:"
    ))

    headers = ["Error Scenario", "Root Cause", "Diagnostic Command", "Exact Resolution"]
    rows = [
        ["Backend Start Fail", "Missing library", "pip list | grep fastapi", "pip install -r backend/requirements.txt"],
        ["Port 8000 Locked", "Zombie uvicorn process", "Get-NetTCPConnection -Port 8000", "Stop-Process -Id <PID> -Force"],
        ["Database Locked", "Concurrent write lock", "PRAGMA journal_mode;", "Ensure WAL mode & timeout=30.0"],
        ["CORS Blocked", "Origin mismatch in browser", "Browser console inspect", "Add client URL to allow_origins in main.py"],
        ["CSV Missing Cols", "Misspelled required col", "df.columns.tolist()", "Ensure 7 mandatory headers exist"],
        ["Bad Timestamp", "Unparseable date format", "Check quarantined table", "Normalize to YYYY-MM-DD HH:MM:SS"],
        ["Failed to Fetch", "Backend server is down", "curl http://127.0.0.1:8000/api/health", "Start uvicorn on port 8000"],
        ["Dashboard Empty", "Zero mock empty state", "Check cleaned row count", "Upload transaction CSV to populate metrics"],
        ["Parquet Missing", "No dataset processed yet", "Check data/processed/ path", "Upload CSV first to trigger pyarrow export"],
        ["413 Payload Large", "File > 25MB boundary", "Check file size in bytes", "Split CSV or adjust MAX_FILE_SIZE_BYTES"]
    ]
    col_widths = [90, 110, 150, 182]
    story.append(make_table(headers, rows, col_widths, mono_cols=[2]))

    story.append(Spacer(1, 10))
    story.append(callout(
        "Proactive Diagnostic Command",
        "System health verify karne ke liye hamesha sabse pehle Health endpoint test karein:<br/>"
        "<code>curl -s http://127.0.0.1:8000/api/health</code><br/>"
        "Agar response mein <code>\"status\": \"UP\"</code> aur database row counts aa rahe hain, "
        "toh backend aur SQLite connectivity 100% operational hai.",
        'tip'
    ))

    story.append(PageBreak())
    return story
