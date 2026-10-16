"""
Master Build Script to generate:
1. docs/UPI_Transaction_Intelligence_Technical_Guide_Hinglish.md
2. docs/UPI_Transaction_Intelligence_Technical_Guide_Hinglish.pdf
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, HRFlowable
)
from reportlab.lib import colors

# Import common utilities and chapter modules
from chapters.common import (
    NumberedCanvas, STYLES, p, hr, callout, make_table,
    PAGE_WIDTH, PAGE_HEIGHT, MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, MARGIN_BOTTOM, CONTENT_WIDTH,
    PRIMARY_DARK, PRIMARY, LAVENDER_BG, SURFACE_WHITE, BORDER_LIGHT, TEXT_DARK, TEXT_MUTED
)
from chapters import (
    ch01_overview,
    ch02_tech_stack,
    ch03_folder_structure,
    ch04_code_deep_dive,
    ch05_frontend,
    ch06_backend,
    ch07_database_sql,
    ch08_pipeline,
    ch09_analytics,
    ch10_anomalies,
    ch11_integration,
    ch12_practical_guide,
    ch13_debugging,
    ch14_testing_roadmap,
    ch15_interview_viva,
    ch16_glossary
)

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(DOCS_DIR, "UPI_Transaction_Intelligence_Technical_Guide_Hinglish.pdf")
MD_PATH = os.path.join(DOCS_DIR, "UPI_Transaction_Intelligence_Technical_Guide_Hinglish.md")

CHAPTER_MODULES = [
    (1, "Project Overview & Real-World Context", ch01_overview),
    (2, "Complete Tech Stack Deep Dive", ch02_tech_stack),
    (3, "Project Folder Structure & Module Architecture", ch03_folder_structure),
    (4, "Har Important Source File ka Code Explanation", ch04_code_deep_dive),
    (5, "Frontend Architecture (React 18 & Pure SVG)", ch05_frontend),
    (6, "Backend aur FastAPI Architecture", ch06_backend),
    (7, "Database Architecture & Advanced SQL Analytics", ch07_database_sql),
    (8, "CSV Upload aur Data Cleaning Pipeline", ch08_pipeline),
    (9, "Transaction Analytics, Diurnal Curves & KPIs", ch09_analytics),
    (10, "Rule-Based Anomaly Detection & Fraud Governance", ch10_anomalies),
    (11, "Frontend, Backend aur Database Integration", ch11_integration),
    (12, "Project ko Practically Use Kaise Karein", ch12_practical_guide),
    (13, "Debugging aur Common Errors", ch13_debugging),
    (14, "Testing, Security, Limitations & Roadmap", ch14_testing_roadmap),
    (15, "Master Interview & Viva Preparation (35+ Q&As)", ch15_interview_viva),
    (16, "Comprehensive Technical Glossary (25+ Terms)", ch16_glossary)
]

def build_markdown():
    """Compiles the complete master markdown documentation source."""
    print("Building Markdown documentation...")
    md_content = []
    
    # Title & Metadata
    md_content.append("""# UPI Transaction Intelligence System
## Complete Hinglish Technical Guide & Architectural Reference

> **Target Standard:** PhonePe • Razorpay • Visa • Mastercard  
> **Architecture:** FastAPI • React 18 • SQLite WAL • Apache Parquet • Pure SVG  
> **Language:** Natural Hinglish (Technical Hindi-English Mix)  
> **Document Version:** 1.0.0 (Production Verified)

---

## Table of Contents
1. [Chapter 1 — Project Overview & Business Context](#chapter-1--project-overview--business-context)
2. [Chapter 2 — Complete Tech Stack](#chapter-2--complete-tech-stack)
3. [Chapter 3 — Project Folder Structure](#chapter-3--project-folder-structure)
4. [Chapter 4 — Har Important File ka Code Explanation](#chapter-4--har-important-file-ka-code-explanation)
5. [Chapter 5 — Frontend Architecture (React 18 & Pure SVG UI)](#chapter-5--frontend-architecture-react-18--pure-svg-ui)
6. [Chapter 6 — Backend aur FastAPI Architecture](#chapter-6--backend-aur-fastapi-architecture)
7. [Chapter 7 — Database aur Advanced SQL Analytics](#chapter-7--database-aur-advanced-sql-analytics)
8. [Chapter 8 — CSV Upload aur Data Cleaning Pipeline](#chapter-8--csv-upload-aur-data-cleaning-pipeline)
9. [Chapter 9 — Transaction Analytics, Diurnal Curves & Business KPIs](#chapter-9--transaction-analytics-diurnal-curves--business-kpis)
10. [Chapter 10 — Rule-Based Anomaly Detection & Fraud Governance](#chapter-10--rule-based-anomaly-detection--fraud-governance)
11. [Chapter 11 — Frontend, Backend aur Database Integration](#chapter-11--frontend-backend-aur-database-integration)
12. [Chapter 12 — Project ko Practically Use Kaise Karein](#chapter-12--project-ko-practically-use-kaise-karein)
13. [Chapter 13 — Debugging aur Common Errors](#chapter-13--debugging-aur-common-errors)
14. [Chapter 14 — Testing, Security, Limitations & Roadmap](#chapter-14--testing-security-limitations--roadmap)
15. [Chapter 15 — Master Interview & Viva Preparation (35+ Q&As)](#chapter-15--master-interview--viva-preparation-35-qas)
16. [Chapter 16 — Comprehensive Technical Glossary (25+ Terms)](#chapter-16--comprehensive-technical-glossary-25-terms)

---
""")

    for num, title, mod in CHAPTER_MODULES:
        md_content.append(mod.get_markdown())
        md_content.append("\n---\n")

    full_md = "\n".join(md_content)
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write(full_md)
    print(f"Markdown successfully written to: {MD_PATH} ({len(full_md)} characters)")

def create_cover_page():
    """Generates the styled cover page flowables."""
    story = []
    story.append(Spacer(1, 20))
    story.append(p("FINTECH ENGINEERING & ARCHITECTURAL REFERENCE", 'CoverMeta'))
    story.append(Spacer(1, 10))
    story.append(p("UPI Transaction Intelligence System", 'CoverTitle'))
    story.append(p("Complete Hinglish Technical Guide, Code Analysis & Interview Viva Preparation", 'CoverSubtitle'))
    story.append(hr())
    story.append(Spacer(1, 10))

    # Architecture Banner Card
    diag_path = os.path.join(DOCS_DIR, "architecture_diagram.png")
    if os.path.exists(diag_path):
        story.append(Image(diag_path, width=500, height=312.5))
        story.append(Spacer(1, 12))

    story.append(callout(
        "Document Purpose & Compliance Standards",
        "Yeh technical guide Indian UPI digital payment systems (PhonePe, Razorpay, NPCI guidelines) "
        "ke exact engineering principles par aadharit hai. Isme raw CSV ingestion, data cleaning quarantine governance, "
        "SQL window functions (LAG, ROW_NUMBER, DENSE_RANK), rule-based anomaly detection, aur PyArrow Apache Parquet "
        "export ko natural Hinglish mein line-by-line explain kiya gaya hai.",
        'interview'
    ))
    story.append(Spacer(1, 14))

    # Metadata Table
    headers = ["Specification", "Project Implementation Details"]
    rows = [
        ["Target Relevance", "PhonePe, Razorpay, Visa, Mastercard, Fintech Startups"],
        ["Full-Stack Architecture", "React 18 SPA + FastAPI ASGI + SQLite WAL + Apache Parquet"],
        ["Data Governance", "First-Occurrence Deduplication & Quarantined Segregation Policy"],
        ["Analytics Engine", "Advanced SQL CTEs, Window Functions (ROW_NUMBER, DENSE_RANK, LAG)"],
        ["Anomaly Detection", "5 Transparent Mathematical Rules (Z-Score >= 2.5, Velocity Burst, High Value)"],
        ["Language & Tone", "Natural Hinglish (Technical Hindi-English Mix for B.Tech & Job Aspirants)"],
        ["Automated Test Suite", "29 Verified Passing Unit & Integration Tests (PyTest)"]
    ]
    col_widths = [130, 402]
    story.append(make_table(headers, rows, col_widths, mono_cols=[0]))

    story.append(PageBreak())
    return story

def create_toc_page():
    """Generates Table of Contents flowables."""
    story = []
    story.append(p("TABLE OF CONTENTS", 'CoverMeta'))
    story.append(p("Index of Chapters & Technical Topics", 'ChapterTitle'))
    story.append(hr())

    toc_rows = [
        ["Chapter 1", "Project Overview & Real-World Fintech Context", "Vision, Problem Statement, Business Value Matrix, Limitations"],
        ["Chapter 2", "Complete Tech Stack Deep Dive", "Technology Selection Matrix, FastAPI, React 18, PyArrow, SQLite WAL"],
        ["Chapter 3", "Project Folder Structure & Module Architecture", "Directory Tree, Layer Responsibilities, Separation of Concerns"],
        ["Chapter 4", "Har Important Source File ka Code Explanation", "Deep-Dive into 15+ Core Files: Imports, Functions, Inputs/Outputs, Logic"],
        ["Chapter 5", "Frontend Architecture (React 18 & Pure SVG UI)", "Mounting, Layout, CSS System, SvgCharts, 2-Stage Modal, RefreshKey"],
        ["Chapter 6", "Backend aur FastAPI Architecture", "Lifespan Startup, CORS, Pydantic v2 Models, Implemented Endpoints Table"],
        ["Chapter 7", "Database Architecture & Advanced SQL Analytics", "Schema Tables, Indexes, and Line-by-Line Breakdown of 7 Master SQL Queries"],
        ["Chapter 8", "CSV Upload aur Data Cleaning Pipeline", "6-Stage Ingestion Pipeline, Quarantine Governance, Parquet Export"],
        ["Chapter 9", "Transaction Analytics, Diurnal Curves & KPIs", "Mathematical Formulas, Indian UPI Diurnal Curves, DoD Growth, Moving Avg"],
        ["Chapter 10", "Rule-Based Anomaly Detection & Fraud Governance", "5 Mathematical Rules, Statistical Z-Score, Mean & Variance, Governance"],
        ["Chapter 11", "Frontend, Backend aur Database Integration", "End-to-End Ingestion Trace from User Click to Parquet & Dynamic UI Re-render"],
        ["Chapter 12", "Project ko Practically Use Kaise Karein", "Prerequisites, Terminal Commands, Local Servers Startup, UI Walkthrough"],
        ["Chapter 13", "Debugging aur Common Errors", "10 Common Development & Production Errors with Exact Diagnostic Commands"],
        ["Chapter 14", "Testing, Security, Limitations & Roadmap", "29 PyTest Tests Analysis, SQL Injection Prevention, Production Roadmap"],
        ["Chapter 15", "Master Interview & Viva Preparation (35+ Q&As)", "35+ Technical Viva Questions with Exact Model Answers in Hinglish"],
        ["Chapter 16", "Comprehensive Technical Glossary (25+ Terms)", "25+ Software Engineering & Fintech Terms Defined in Simple Hinglish"]
    ]

    headers = ["Chapter", "Title", "Key Topics Covered"]
    col_widths = [65, 205, 262]
    story.append(make_table(headers, toc_rows, col_widths, mono_cols=[0]))
    story.append(PageBreak())
    return story

def build_pdf():
    """Compiles the ReportLab PDF document using Platypus."""
    print("Building PDF document...")
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM
    )

    story = []
    # 1. Cover Page
    story.extend(create_cover_page())

    # 2. Table of Contents
    story.extend(create_toc_page())

    # 3. All 16 Chapters
    for num, title, mod in CHAPTER_MODULES:
        print(f"Adding Chapter {num}: {title}...")
        story.extend(mod.get_flowables())

    # Build PDF with NumberedCanvas for Running Header and Footers (Page X of Y)
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully compiled to: {PDF_PATH}")

if __name__ == "__main__":
    build_markdown()
    build_pdf()
    print("All deliverables generated successfully!")

