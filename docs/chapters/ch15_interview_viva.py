"""
Chapter 15: Master Interview & Viva Preparation (35+ Q&As)
"""
from reportlab.platypus import Paragraph, Spacer, PageBreak
from .common import (
    p, bullet, callout, hr, STYLES, CONTENT_WIDTH
)

def get_markdown() -> str:
    return """# Chapter 15 — Master Interview & Viva Preparation (35+ Q&As)

Is chapter mein 36 essential technical interview questions aur unke precise Hinglish answers diye gaye hain. Yeh answers PhonePe, Razorpay, Visa, Mastercard, aur fintech startups ke interviews aur engineering viva ke liye tayyar kiye gaye hain.

---

### Q1: Is project ka main purpose aur real-world problem kya hai?
**Answer:** Yeh project Indian UPI ecosystem (jaise PhonePe, Razorpay) mein high-volume payment data ko ingest karta hai, corrupt aur duplicate transactions ko isolate karta hai, statistical aur heuristic anomaly rules se review candidates identify karta hai, aur business insights (jaise diurnal curves aur customer rankings) provide karta hai.

---

### Q2: Aapne backend ke liye FastAPI kyun choose kiya, Flask ya Django kyun nahi?
**Answer:** FastAPI asynchronous ASGI architecture par based hai, jo high-throughput I/O requests ke liye fast hai. Isme Pydantic v2 ke through automatic request validation, high-speed JSON serialization, aur automatic interactive OpenAPI documentation (`/docs`) out-of-the-box milta hai. Flask mein yeh sab manual add karna padta hai aur Django analytics ke liye unnecessarily heavy hai.

---

### Q3: React frontend mein bina external chart library ke SVG charts kyun banaye?
**Answer:** Recharts ya Chart.js bundle size ko 500KB+ badha dete hain aur styling override karna complex hota hai. `SvgCharts.jsx` mein pure SVG `<svg>`, `<rect>`, `<path>` use karke humne lightweight, high-performance charts banaye hain jo kisi bhi resolution par sharp dikhte hain aur zero external dependency rakhte hain.

---

### Q4: Frontend aur Backend aapas mein kaise communicate karte hain?
**Answer:** Frontend `src/services/api.js` module ke through browser ke native `fetch` API se HTTP REST calls bhejta hai. JSON data standard GET/POST endpoints par exchange hota hai aur CSV file upload `multipart/form-data` ke roop mein FastAPI ke `/api/data-quality/upload` endpoint par stream hota hai.

---

### Q5: CORS kya hai aur aapke project mein kaise handle kiya gaya hai?
**Answer:** CORS (Cross-Origin Resource Sharing) browser security mechanism hai jo alag ports ya domains se aane wali requests ko restrict karta hai. Hamne `backend/app/main.py` mein `CORSMiddleware` configure kiya hai jo frontend ports (`http://localhost:3000` aur `5173`) ko explicit access allow karta hai.

---

### Q6: Data validation mein kaunse 7 mandatory columns check hote hain?
**Answer:** `validation.py` mein 7 required columns verify hote hain: `transaction_id`, `timestamp`, `customer_id`, `merchant_id`, `amount`, `category`, aur `status`. Agar ek bhi column missing ho, toh pipeline execute nahi hoti aur HTTP 422 error return hota hai.

---

### Q7: Duplicate transactions ko aapka system kaise handle karta hai?
**Answer:** System **First-Occurrence Retention Policy** follow karta hai. Agar ek hi `transaction_id` baar-baar aata hai, toh pehle valid record ko `cleaned_transactions` mein rakha jaata hai aur baaki sabhi subsequent occurrences ko `quarantined_transactions` table mein reason `"Duplicate transaction ID"` ke saath isolate kar diya jaata hai.

---

### Q8: Quarantining aur Silent Dropping (`df.dropna()`) mein kya fark hai?
**Answer:** Data science mein aksar corrupt data ko `dropna()` se silently drop kar dete hain, lekin banking aur fintech mein yeh non-compliant hai. Quarantine policy mein har invalid row ko uske raw data aur reject hone ke exact reason ke saath `quarantined_transactions` table mein permanently persist kiya jaata hai taaki audit trail bani rahe.

---

### Q9: Database mein SQLite WAL mode ka kya significance hai?
**Answer:** Default SQLite rollback journal mode mein write operation ke waqt poora database file lock ho jaata hai. `PRAGMA journal_mode = WAL;` (Write-Ahead Logging) lagane se multiple readers ek hi waqt par data read kar sakte hain bina writer ko block kiye, jo analytical dashboard concurrency ke liye zaroori hai.

---

### Q10: Project mein SQL Injection vulnerabilities kaise prevent ki gayi hain?
**Answer:** Puri application mein dynamic string formatting (`f"SELECT... {user_input}"`) strictly banned hai. Sabhi queries SQLite bind variables (`:search`, `:category`, `:start_date`) ke zariye parameterize hoti hain, jisse database engine query structure aur user input ko strictly alag rakhta hai.

---

### Q11: Common Table Expressions (CTEs) kya hote hain aur project mein kahan use hue hain?
**Answer:** CTE ek temporary named result set hota hai jo `WITH cte_name AS (...)` syntax se banta hai. Project mein `SQL_DAILY_TRENDS` mein daily aggregation banane ke liye aur `SQL_CUSTOMER_SUMMARIES` mein customer category ranks compute karne ke liye CTEs use hue hain taaki complex nested queries clean aur readable rahein.

---

### Q12: Window Function `ROW_NUMBER()` ka project mein kya role hai?
**Answer:** `SQL_CUSTOMER_SUMMARIES` mein `ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY COUNT(*) DESC, SUM(amount) DESC)` use hota hai. Yeh har customer ke shopping categories ko frequency aur amount ke hisab se rank karta hai, jisse rank 1 wali category customer ki "Favorite Category" nikal aati hai.

---

### Q13: `DENSE_RANK()` aur `RANK()` mein kya difference hai?
**Answer:** `RANK()` tie hone par subsequent ranks skip kar deta hai (e.g. 1, 2, 2, 4), jabki `DENSE_RANK()` bina kisi gap ke continuous sequence deta hai (e.g. 1, 2, 2, 3). Hamne customer spend aur merchant volume ranking ke liye `DENSE_RANK()` use kiya hai taaki rankings continuous rahein.

---

### Q14: Window Function `LAG()` ka use kahan hua hai?
**Answer:** `SQL_DAILY_TRENDS` mein `LAG(tx_count, 1)` use hota hai. Yeh current row ke liye pichhle din ka transaction volume return karta hai, jisse Day-over-Day (DoD) volume growth percentage calculate hoti hai.

---

### Q15: Rolling 3-day average volume kaise calculate hota hai?
**Answer:** SQL window frame specification ke through:
`AVG(tx_count) OVER (ORDER BY tx_date ASC ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`. Yeh current day aur pichhle 2 dinon ka moving average nikalta hai jo weekend traffic volatility ko smooth karta hai.

---

### Q16: Ratio Window Function `SUM() OVER ()` kaise kaam karta hai?
**Answer:** `SQL_HOURLY_TRENDS` mein `tx_count * 100.0 / SUM(tx_count) OVER ()` use hota hai. Empty over clause `OVER ()` poore table ka aggregate total volume return karta hai, jisse bina alag sub-query ke har ghante ka percentage share nikal aata hai.

---

### Q17: Failed transactions total volume aur GMV mein count hote hain ya nahi?
**Answer:** Ha, `COUNT(*)` aur `SUM(amount)` poore validated `cleaned_transactions` table par run hote hain jisme SUCCESS, FAILED, aur PENDING shamil hote hain. Lekin conditional aggregations (`success_count`, `failed_count`) alag se nikaale jaate hain taaki exact bifurcation dikhaya ja sake.

---

### Q18: Indian UPI payment traffic ka diurnal curve kya hota hai?
**Answer:** Indian UPI traffic subah 8 AM se groceries ke liye ramp hoti hai, dopahar 1 PM lunch spike aata hai, aur sham 7:00 PM se 10:00 PM ke beech super-peak (daily traffic ka ~35%) banta hai jab dinner aur shopping transactions hote hain.

---

### Q19: Anomaly detection ke liye machine learning ke bajaye rules kyun use kiye?
**Answer:** Banking regulations require karti hain ki flagged transaction 100% explainable ho. Heuristic rules (High Value > ₹50k, Rapid Burst >= 3 in 5m, Z-Score >= 2.5) exact mathematical threshold aur reason dete hain jo regulatory compliance aur fraud operations ke audit ke liye ideal hai.

---

### Q20: Statistical Z-Score anomaly detection rule ka logic samjhaiye.
**Answer:** Yeh rule customer ke personal spend history ($N \ge 3$) par calculate hota hai. Customer ka mean $\mu$ aur standard deviation $\sigma$ calculate hota hai. Agar current transaction $Z = (X - \mu)/\sigma \ge 2.5$ ho, toh iska matlab yeh transaction personal spending variance se 2.5 standard deviations upar hai aur use review candidate flag milta hai.

---

### Q21: Standard Deviation ($\sigma$) aur Variance ($\sigma^2$) ka financial significance kya hai?
**Answer:** Variance yeh batata hai ki transaction amounts average se kitna widely spread hain. Standard deviation variance ka square root hota hai jo same currency unit (₹) mein aata hai. Low standard deviation predictable routine spending show karta hai, jabki sudden high deviation unusual spend alert trigger karta hai.

---

### Q22: Velocity Spike / Rapid Burst rule kaise kaam karta hai?
**Answer:** Transactions ko `customer_id` aur `timestamp` se sort karke sliding window check chalta hai. Agar same customer 5 minute ke interval ke andar 3 ya usse zyada transactions initiate karta hai, toh bot testing ya rapid fraud transfers ko rokne ke liye unhe High Severity Velocity Spike flag milta hai.

---

### Q23: "Review Candidate" aur "Proven Fraud" mein kya fark hai?
**Answer:** Rule flag hona fraud prove nahi karta. Example: Diwali par customer ka ₹65,000 ka genuine TV purchase High-Value flag trigger karega. System ise "Review Candidate" manta hai taaki risk analyst inspect kar sake, direct customer ko block nahi karta.

---

### Q24: Apache Parquet format kya hai aur ise kyun use kiya gaya?
**Answer:** Parquet ek columnar storage file format hai jo PyArrow engine ke through generate hota hai. Yeh CSV ke muqable 80% kam disk space leta hai aur analytical BI tools (Snowflake, AWS Athena, Spark) mein columnar compression ki wajah se 10x fast scan hota hai.

---

### Q25: Frontend mein `refreshKey` broadcast pattern kya hai?
**Answer:** CSV upload ya refresh click hone par `App.jsx` mein `setRefreshKey(k => k + 1)` execute hota hai. Saare child pages (`Dashboard`, `Transactions`) apne `useEffect` mein `refreshKey` observe karte hain aur automatically background mein fresh API metrics re-fetch kar lete hain.

---

### Q26: Backend mein Global Exception Handling kaise implement ki gayi hai?
**Answer:** `backend/app/main.py` mein `@app.exception_handler(Exception)` define hai. Yeh unhandled errors ko console mein stack trace ke sath log karta hai aur frontend client ko clean 500 JSON error contract return karta hai, jisse server crash nahi hota.

---

### Q27: `transaction_service.py` mein pagination kaise implement ki gayi hai?
**Answer:** `page` aur `page_size` parameters ke through `offset = (page - 1) * page_size` calculate hota hai. SQL query mein `LIMIT :limit OFFSET :offset` lagaya jaata hai, aur total matching rows count karke `total_pages = ceil(total / page_size)` compute hota hai.

---

### Q28: Large file uploads ke case mein server memory overflow kaise prevent hota hai?
**Answer:** Inbound upload endpoint par `MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024` (25 MB) hard check enforce kiya gaya hai. Isse badi files ko FastAPI turant HTTP 413 Payload Too Large error ke sath reject kar deta hai.

---

### Q29: PyTest test suite codebase mein kya verify karta hai?
**Answer:** 6 test files mein total 29 tests hain: schema validation, missing columns, deduplication, quarantine segregation, high-value rule, velocity burst rule, SQL window functions (`LAG`, rolling avg, rankings), API endpoints, aur Parquet exports.

---

### Q30: Project ki sabse badi architectural limitation kya hai?
**Answer:** System batch CSV upload par kaam karta hai (real-time Kafka streaming pipeline nahi hai), aur database SQLite3 hai jo single-node benchmark ke liye accha hai par multi-region high write concurrency ke liye PostgreSQL ya distributed storage require karega.

---

### Q31: Agar dataset mein negative amount aaye toh system kya karega?
**Answer:** `cleaning.py` mein `amount <= 0` check hota hai. Negative amount wali row clean table mein nahi jaati, balki `quarantined_transactions` table mein reject reason `"Invalid non-positive amount"` ke sath isolate ho jaati hai.

---

### Q32: Unparseable timestamps kaise handle hote hain?
**Answer:** `pd.to_datetime()` try-except block mein execute hota hai. Agar date format corrupt ho (jaise `"bad_date"`), toh exception catch hota hai aur row quarantine ho jaati hai without crashing the pipeline.

---

### Q33: Merchant Analytics mein Peak Trading Hour kaise nikalta hai?
**Answer:** CTE `merchant_hourly` har merchant ke 24 ghante ke transaction count par `ROW_NUMBER() OVER (PARTITION BY merchant_id ORDER BY COUNT(*) DESC)` calculate karta hai. Rank 1 wala ghanta merchant ka `peak_hour` ban jaata hai.

---

### Q34: Pattern Insights (`/api/dashboard/patterns`) narrative kaise construct hoti hai?
**Answer:** `analytics_service.py` multi-stage CTE query run karta hai jisse peak hour, highest value category, aur busiest trading date nikalte hain. In numbers ke basis par factual descriptive English sentences dynamically generate hote hain.

---

### Q35: Production mein 1GB+ files aane par system kaise evolve hoga?
**Answer:** Celery worker queue aur Redis message broker add hoga. User upload karte hi task ID return hogi aur background worker chunks mein data stream karke PostgreSQL mein batch insert karega.

---

### Q36: Is project se aapne sabse bada engineering takeaway kya seekha?
**Answer:** Real-world fintech mein data clean karna aur compliance-ready audit trails maintain karna ML algorithms run karne se zyada critical hota hai. Pure SQL window functions aur structured quarantine layers massive operational transparency provide karti hain.
"""

def get_flowables() -> list:
    story = []
    story.append(p("CHAPTER 15", 'CoverMeta'))
    story.append(p("Master Interview & Viva Preparation (35+ Q&As)", 'ChapterTitle'))
    story.append(p("Comprehensive viva questions and answers covering Architecture, FastAPI, React, SQL, Anomaly Rules and Fintech Governance.", 'ChapterSubtitle'))
    story.append(hr())

    qa_list = [
        ("Q1: Is project ka main purpose aur real-world problem kya hai?",
         "Yeh project Indian UPI ecosystem ke transaction data ko ingest karta hai, corrupt aur duplicate transactions ko isolate karta hai, statistical aur heuristic anomaly rules se review candidates identify karta hai, aur business insights (diurnal curves, rankings) provide karta hai."),
        
        ("Q2: Backend ke liye FastAPI kyun choose kiya?",
         "FastAPI asynchronous ASGI framework hai, jisme Pydantic v2 data validation, high-speed serialization, aur automatic interactive OpenAPI docs (/docs) milti hain."),
        
        ("Q3: React mein pure SVG charts kyun banaye?",
         "External chart libraries 500KB+ bundle weight add karti hain. SvgCharts.jsx mein pure mathematical coordinates se SVG draw karke zero-dependency lightweight performance achieve ki gayi hai."),
        
        ("Q4: Duplicate transactions ko system kaise handle karta hai?",
         "First-Occurrence Retention Policy: Pehle valid record ko cleaned_transactions mein rakhte hain, aur baaki sabhi subsequent occurrences ko quarantined_transactions table mein isolate kar dete hain."),
         
        ("Q5: Database mein SQLite WAL mode ka kya role hai?",
         "PRAGMA journal_mode = WAL; enable karne se concurrent read operations write operations ko block nahi karte, jo high-frequency analytical dashboards ke liye essential hai."),
         
        ("Q6: SQL Injection vulnerabilities kaise prevent ki gayi hain?",
         "Sabhi queries SQLite bind variables (:search, :category, :limit) use karti hain. Puri application mein dynamic string formatting strictly eliminated hai."),
         
        ("Q7: Window Function ROW_NUMBER() ka project mein kya role hai?",
         "SQL_CUSTOMER_SUMMARIES mein ROW_NUMBER() customer ki categories ko transaction count ke basis par rank karta hai, jisse rank 1 wali category customer ki Favorite Category banti hai."),
         
        ("Q8: Window Function LAG() ka use kahan hua hai?",
         "SQL_DAILY_TRENDS mein LAG(tx_count, 1) pichhle din ka volume fetch karta hai jisse Day-over-Day (DoD) growth percentage calculate hoti hai."),
         
        ("Q9: Failed transactions total GMV mein count hote hain ya nahi?",
         "Ha, COUNT(*) aur SUM(amount) cleaned_transactions ke sabhi rows par chalte hain, jabki success_count aur failed_count conditional sums alag se compute hote hain."),
         
        ("Q10: Statistical Z-Score anomaly detection rule ka logic samjhaiye.",
         "Customer ke personal spend history (N >= 3) par mean mu aur std dev sigma nikalta hai. Agar current transaction Z = (X - mu)/sigma >= 2.5 ho, toh unusual spend flag hota hai."),
         
        ("Q11: Review Candidate aur Proven Fraud mein kya fark hai?",
         "Rule flag hona fraud prove nahi karta. Example: Festival ke din bada legitimate purchase bhi High-Value flag trigger karega; isliye use 'Review Candidate' kehte hain."),
         
        ("Q12: Apache Parquet format kyun use kiya gaya?",
         "Parquet columnar storage format hai jo PyArrow se banta hai. Yeh disk par 80% compression deta hai aur Big Data analytical tools mein 10x tezi se scan hota hai.")
    ]

    for q, a in qa_list:
        story.append(p(f"<b>{q}</b>", 'BodyBold'))
        story.append(p(f"<b>Answer:</b> {a}", 'Body'))
        story.append(Spacer(1, 4))

    story.append(callout(
        "Interview Confidence Tip",
        "Viva mein hamesha explainable rules aur quarantine governance ko highlight karein: "
        "'Humne data ko silently drop karne ke bajaye quarantined_transactions table mein preserve kiya hai, "
        "aur ML black-box ke bajaye explainable mathematical rules use kiye hain jo banking compliance standards meet karte hain.'",
        'interview'
    ))

    story.append(PageBreak())
    return story

