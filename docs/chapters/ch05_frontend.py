"""
Chapter 5: Frontend ko Samjho (React 18 & Pure SVG UI)
"""
from reportlab.platypus import Paragraph, Spacer, PageBreak
from .common import (
    p, bullet, callout, hr, code_block, STYLES, CONTENT_WIDTH
)

def get_markdown() -> str:
    return """# Chapter 5 — Frontend Architecture (React 18 & Pure SVG UI)

## 5.1 React Application Start Kaise Hoti Hai?

Hamari React application ka execution flow standard Vite modern web build follow karta hai:

1. **`index.html`:** Browser sabse pehle `index.html` load karta hai, jisme root container `<div id="root"></div>` define hota hai aur script tag `<script type="module" src="/src/main.jsx"></script>` ko call kiya jaata hai.
2. **`main.jsx`:** React ka entrypoint:
   ```javascript
   import React from 'react';
   import ReactDOM from 'react-dom/client';
   import App from './App';
   import './styles/global.css';
   import './styles/layout.css';
   import './styles/components.css';

   ReactDOM.createRoot(document.getElementById('root')).render(
     <React.StrictMode>
       <App />
     </React.StrictMode>
   );
   ```
   Yeh `createRoot` ke zariye virtual DOM ko actual HTML document ke `root` element par mount karta hai aur global CSS styles apply karta hai.
3. **`App.jsx`:** Main application shell render hota hai, jo Sidebar navigation, Top Header, 8 Functional Pages, aur Two-Stage CSV Upload Modal ko hold karta hai.

---

## 5.2 Layout Architecture & Component Hierarchy

Hamara frontend ek clean, full-viewport SaaS layout follow karta hai:

```
[ App.jsx Root Shell ]
├── <Sidebar />                     (Fixed left navigation: 8 tabs, health indicator)
└── <div className="main-wrapper">
    ├── <Header />                  (Dynamic Title/Subtitle, Date Picker, Refresh & Upload Buttons)
    └── <main className="content-body">
        ├── <Dashboard />           (Executive KPIs, Diurnal SVG Bar Chart, Trend Line Chart)
        ├── <Transactions />        (Search, Category Filter, Sortable DataTable, Slide-in Drawer)
        ├── <Customers />           (Spend Rankings, Favorite Categories, Profile Modal)
        ├── <Merchants />           (Volume Rankings, Diurnal Peak Hours, Settlement Profile)
        ├── <Patterns />            (Factual Diurnal Traffic Narrative Cards)
        ├── <Anomalies />           (Rule-based Audit Log & Threshold Sliders / Config)
        ├── <DataQuality />         (Missing Values Audit, Quarantine Table, Re-run Pipeline)
        └── <Reports />             (Instant CSV Report & Columnar Parquet Downloaders)
    └── <UploadModal />             (Two-Step: Schema Inspection Preview -> Ingestion Confirmation)
    └── <ToastContainer />          (Floating non-blocking success/warning alert pills)
```

---

## 5.3 CSS Design System: Lavender Palette & Zero Framework Bloat

Project mein Bootstrap ya Tailwind CSS jaise heavy frameworks ke bajaye **Vanilla CSS3** (`frontend/src/styles/`) use ki gayi hai:

- **CSS Custom Properties (Variables in `global.css`):**
  - Primary Lavender Accent: `--color-primary: #8A63F4;`
  - Deep Lavender / Headers: `--color-primary-dark: #5E35B1;`
  - Soft Lavender Background: `--color-primary-soft: #F5EEFE;`
  - Off-white Canvas: `--color-bg: #F8F3EF;`
  - Surface Card White: `--color-surface: #FFFFFF;`
  - Crisp Borders: `--color-border: #ECE8E5;`
  - Dark Charcoal Headings: `--color-text: #20201F;`
  - Muted Grey Secondary: `--color-text-muted: #77736F;`
- **Typography:** System font stack (`Segoe UI`, `-apple-system`, `Roboto`, `Helvetica`) with `JetBrains Mono` / `Consolas` for currency (`₹`) and transaction IDs.
- **Full Viewport Layout (`layout.css`):** `.app-shell` uses `display: flex; min-height: 100vh; width: 100%;` preventing cramped centered boxes.

---

## 5.4 Pure SVG Charts vs Heavy Chart Libraries (`SvgCharts.jsx`)

Fintech applications mein external charting libraries (Chart.js, Recharts) bundle size ko 500KB+ badha deti hain aur canvas blurriness produce karti hain.
Hamne `frontend/src/components/SvgCharts.jsx` mein **Pure Vector SVG** develop kiya hai:

1. **`HourlyDiurnalBarChart`:**
   - 24 bars render karta hai (Hours 00 to 23).
   - Har bar ki height mathematically normalize hoti hai:
     $$\text{barHeight} = \left(\frac{\text{tx\_count}}{\max(\text{tx\_count})}\right) \times \text{chartHeight}$$
   - Hover karne par dynamic tooltip display hota hai with transaction count, volume value (₹), aur volume share %.
2. **`DailyTrendLineChart`:**
   - Pure SVG `<path d="M x0 y0 L x1 y1 ...">` generate karta hai.
   - Smooth lavender gradient area fill `<linearGradient id="areaGrad">` apply karta hai.
3. **`CategoryShareDonut` / Progress Bars:**
   - Dynamic SVG arc strokes aur percentage labels.

---

## 5.5 State Management & The `refreshKey` Broadcast Pattern

Redux ya Zustand jaise heavy state stores ke bajaye, application lightweight reactive state pattern use karti hai:

```javascript
// App.jsx
const [refreshKey, setRefreshKey] = useState(0);

const handleUploadSuccess = (res) => {
  setRefreshKey((k) => k + 1); // Triggers re-fetch across all sub-components!
  showToast(`Dataset ready: ${res.cleaned_records_count} transactions processed!`, 'success');
};
```
Har child page (jaise `Dashboard.jsx`, `Transactions.jsx`) apne `useEffect` dependency array mein `refreshKey` listen karta hai:
```javascript
useEffect(() => {
  fetchDashboardData();
}, [dateRange, refreshKey]);
```
Jab bhi user CSV upload karta hai ya Header mein Refresh button dabata hai, `refreshKey` increment hota hai aur saare active components silently fresh data re-fetch kar lete hain.

---

## 5.6 Two-Stage CSV Upload Interface (`UploadModal.jsx`)

User experience aur data governance ke liye modal do stages mein split hai:

- **Stage 1 (Inspect & Validate):**
  User file choose karta hai aur "Inspect & Validate" click karta hai. File backend ke `/api/data-quality/validate-upload` par jaati hai. Backend schema check karta hai, missing columns batata hai, aur first 5 rows ka preview table dikhata hai.
- **Stage 2 (Confirm & Ingest):**
  User data preview inspect karne ke baad "Confirm & Ingest" click karta hai. File `/api/data-quality/upload` par stream hoti hai, full cleaning aur anomaly detection run hota hai, aur dataset ready ho jaata hai.

---

## 5.7 End-to-End Event Trace: Button Click se UI Render Tak

```
[User clicks "Confirm & Ingest" in UploadModal.jsx]
           │
           ▼
[api.uploadCsv(file) in src/services/api.js]
  - Sends multipart/form-data POST request to /api/data-quality/upload
           │
           ▼
[FastAPI Backend processes CSV]
  - Cleans data, quarantines corrupt rows, runs anomaly rules, saves to SQLite & Parquet
  - Returns HTTP 200 JSON with record counts
           │
           ▼
[UploadModal receives response & calls onUploadSuccess(res)]
           │
           ▼
[App.jsx executes handleUploadSuccess()]
  - Closes modal: setIsUploadOpen(false)
  - Broadcasts refresh: setRefreshKey(k => k + 1)
  - Displays floating green toast alert: "Dataset ready: 1,200 transactions processed!"
           │
           ▼
[Dashboard.jsx useEffect fires due to refreshKey change]
  - Calls api.getDashboardSummary(), api.getDailyTrends(), api.getHourlyTrends()
  - Sets kpis state, hourlyTrends state, dailyTrends state
           │
           ▼
[React Virtual DOM reconciles]
  - KPI Cards update from "—" to "₹12,45,000"
  - Pure SVG diurnal curves animate into view!
```
"""

def get_flowables() -> list:
    story = []
    story.append(p("CHAPTER 5", 'CoverMeta'))
    story.append(p("Frontend Architecture (React 18 & Pure SVG UI)", 'ChapterTitle'))
    story.append(p("React 18 SPA workflow, component hierarchy, pure SVG charting, aur reactive state synchronization.", 'ChapterSubtitle'))
    story.append(hr())

    story.append(p("5.1 Execution Lifecycle: index.html se App.jsx Tak", 'SectionTitle'))
    story.append(p(
        "React frontend browser mein <code>index.html</code> se bootstrap hota hai. "
        "<code>main.jsx</code> script React 18 ke <code>ReactDOM.createRoot()</code> ke through <code>App.jsx</code> "
        "ko mount karti hai aur modular CSS sheets inject karti hai."
    ))

    code_mount = """// main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/global.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);"""
    story.append(code_block(code_mount, "main.jsx React Root"))
    story.append(Spacer(1, 8))

    story.append(p("5.2 Why Pure SVG Charts? (Zero NPM Dependency Bloat)", 'SectionTitle'))
    story.append(p(
        "Hamne external charting packages (jaise Chart.js ya Recharts) ko reject kiya kyunki woh 500KB+ bundle weight add karte hain. "
        "<code>SvgCharts.jsx</code> component mein pure mathematical coordinates calculate karke direct <code>&lt;svg&gt;</code>, "
        "<code>&lt;rect&gt;</code>, aur <code>&lt;path&gt;</code> elements render hote hain, jo retina displays par pixel-perfect sharpness dete hain."
    ))

    story.append(callout(
        "The Reactive refreshKey Pattern",
        "Redux jaise complex boilerplate ke bina components ko sync rakhne ke liye <code>refreshKey</code> state use ki gayi hai. "
        "CSV upload hone par <code>setRefreshKey(k => k + 1)</code> call hota hai, jisse saare background pages ke <code>useEffect</code> "
        "hooks automatically trigger hokar fresh backend API metrics fetch kar lete hain.",
        'tip'
    ))
    story.append(Spacer(1, 8))

    story.append(p("5.3 Two-Stage CSV Upload Interface", 'SectionTitle'))
    story.append(p(
        "<code>UploadModal.jsx</code> data governance follow karta hai: "
        "Stage 1 par <code>validate-upload</code> endpoint schema preview deta hai taaki user missing columns inspect kar sake. "
        "Stage 2 par <code>upload</code> endpoint confirmation ke baad data ingest karta hai."
    ))

    story.append(PageBreak())
    return story

