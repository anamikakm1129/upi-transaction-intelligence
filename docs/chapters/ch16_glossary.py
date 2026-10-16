"""
Chapter 16: Comprehensive Technical Glossary
"""
from reportlab.platypus import Paragraph, Spacer, PageBreak
from .common import (
    p, bullet, callout, hr, make_table, STYLES, CONTENT_WIDTH
)

def get_markdown() -> str:
    return """# Chapter 16 — Comprehensive Technical Glossary (25+ Terms)

Neeche software engineering, data analytics aur fintech domain ke 25 core technical terms ki practical Hinglish definitions di gayi hain:

1. **Frontend:**
   Application ka visual user interface (UI) jo user ke browser mein run hota hai (hamare project mein React 18 SPA aur Vanilla CSS).
2. **Backend:**
   Server-side engine jo business logic, data processing, aur database operations execute karta hai (hamare project mein Python FastAPI).
3. **API (Application Programming Interface):**
   Ek bridge ya contract jiske zariye do alag systems (jaise React frontend aur Python backend) aapas mein data exchange karte hain.
4. **Endpoint:**
   API server par ek specific web address (URL path) jahan client kisi specific resource ko access karta hai (jaise `/api/dashboard/summary`).
5. **Request:**
   Client (browser) dwara server ko bheja gaya HTTP message jisme method (GET, POST), headers, aur payload data shamil hota hai.
6. **Response:**
   Request process karne ke baad server dwara client ko bheja gaya answer jisme HTTP status code (200, 422) aur JSON data hota hai.
7. **Component:**
   React ka reusable, independent code block (jaise `KpiCard`, `DataTable`, `SvgCharts`) jo apna specific UI render karta hai.
8. **State:**
   React component ke andar ka dynamic internal data jo user actions (jaise button click ya file upload) ke baad change hota hai aur UI ko update karta hai.
9. **Database:**
   Structured data ko securely aur permanently store karne wala system (hamare project mein SQLite3).
10. **SQL Query:**
    Relational database se specific data select, insert, update ya delete karne ke liye likhi gayi standardized command.
11. **DataFrame:**
    Pandas library ka two-dimensional tabular data structure (rows aur columns) jo in-memory mathematical calculations ke liye use hota hai.
12. **Data Validation:**
    Check karna ki aane wala data required rules (mandatory columns, correct data types, valid status) ko follow kar raha hai ya nahi.
13. **Data Cleaning:**
    Corrupt amounts, unparseable dates, aur duplicate records ko identify karke data ko normalize karna aur bad records ko quarantine mein isolate karna.
14. **Aggregation:**
    Multiple rows ke data ko combine karke single summary metric calculate karna (jaise `SUM(amount)`, `AVG(amount)`, `COUNT(*)`).
15. **Common Table Expression (CTE):**
    `WITH` clause se banaya gaya temporary named result set jo complex multi-stage SQL queries ko readable aur fast banata hai.
16. **Window Function:**
    SQL ka advanced function (`ROW_NUMBER`, `DENSE_RANK`, `LAG`) jo table rows ke across calculation karta hai bina group by aggregation ke rows ko collapse kiye.
17. **Variance ($\sigma^2$):**
    Ek statistical measurement jo yeh batata hai ki transaction amounts apne average (mean) se kitna widely spread hain.
18. **Standard Deviation ($\sigma$):**
    Variance ka square root jo original currency unit (₹) mein yeh batata hai ki typical transaction average se kitna deviate karta hai.
19. **Anomaly:**
    Koi aisa transaction pattern jo normal spending behavior se significantly alag ho (jaise high amount ya rapid burst) aur review ke yogya ho.
20. **CSV (Comma-Separated Values):**
    Plain text file format jahan rows newline se aur columns comma (`,`) se separate hote hain.
21. **Apache Parquet:**
    Ek highly compressed, columnar data storage format jo analytical BI tools (Snowflake, Spark) mein fast scans provide karta hai.
22. **Logging:**
    Application execution ke waqt events, errors aur milestones ko timestamped text messages ke roop mein terminal ya file mein record karna.
23. **Exception Handling:**
    Runtime par aane wale unexpected errors (jaise file not found, bad format) ko gracefully catch karna taaki application crash na ho.
24. **CORS (Cross-Origin Resource Sharing):**
    Browser ka security protocol jo yeh decide karta hai ki ek origin (e.g. port 3000) doosre origin (e.g. port 8000) se data fetch kar sakta hai ya nahi.
25. **Environment Variable:**
    Operating system level par set kiye gaye dynamic configuration values (jaise database paths, API keys, port numbers) jo code ke bahar define hote hain.
"""

def get_flowables() -> list:
    story = []
    story.append(p("CHAPTER 16", 'CoverMeta'))
    story.append(p("Comprehensive Technical Glossary", 'ChapterTitle'))
    story.append(p("25+ core software engineering, data analytics aur fintech domain terms ki simple Hinglish definitions.", 'ChapterSubtitle'))
    story.append(hr())

    terms = [
        ("Frontend", "Browser mein run hone wala visual user interface (React 18 SPA aur CSS)."),
        ("Backend", "Server-side business logic, APIs, aur data processing engine (Python FastAPI)."),
        ("API & Endpoint", "Systems ke beech data exchange bridge (API) aur uska specific URL path (Endpoint)."),
        ("Request & Response", "Client dwara bheja gaya HTTP message (Request) aur server ka JSON answer (Response)."),
        ("React Component & State", "Reusable UI building blocks (Components) aur unke andar ka dynamic reactive data (State)."),
        ("DataFrame", "Pandas library ka tabular 2D structure jo in-memory transformation ke liye use hota hai."),
        ("Data Quarantine", "Bad aur duplicate records ko silently drop karne ke bajaye reason ke sath isolate karna."),
        ("CTE (Common Table Expression)", "WITH clause se banaya gaya temporary SQL result set jo query readability badhata hai."),
        ("Window Function", "Rows ke across calculation karne wala SQL function (LAG, ROW_NUMBER) bina rows ko collapse kiye."),
        ("Mean, Variance & StdDev", "Statistical metrics: Mean (average), Variance (spread), aur StdDev (currency deviation)."),
        ("Anomaly Review Candidate", "Unusual behavior flag jo fraud prove nahi karta balki human audit ke liye highlight hota hai."),
        ("Apache Parquet", "Columnar binary format jo 80% disk compression aur high-speed BI queries allow karta hai."),
        ("CORS Middleware", "Browser security restriction jo frontend dev ports ko backend access allow karti hai.")
    ]

    headers = ["Technical Term", "Simple Hinglish Meaning & Project Context"]
    rows = [[t[0], t[1]] for t in terms]
    col_widths = [140, 392]
    story.append(make_table(headers, rows, col_widths, mono_cols=[0]))
    story.append(Spacer(1, 10))

    story.append(callout(
        "Fintech Engineering Viva Summary",
        "Yeh glossary terms har interview round mein core vocabulary ka kaam karte hain. "
        "In concepts ko hamesha code context (jaise queries.py ya cleaning.py) ke sath explain karein.",
        'interview'
    ))

    return story

