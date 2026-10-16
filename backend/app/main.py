from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sqlite3
import os

from .utils.logging_config import logger
from .database.connection import init_db, execute_one, execute_query
from .services.data_quality_service import DataQualityService
from .api.routes import (
    dashboard,
    transactions,
    customers,
    merchants,
    anomalies,
    data_quality,
    reports
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: initialize database tables and schema."""
    logger.info("Initializing UPI Transaction Intelligence System backend...")
    init_db()
    row = execute_one("SELECT COUNT(*) AS total FROM cleaned_transactions;")
    tx_count = row['total'] if row else 0
    logger.info(f"Database ready. Active user-uploaded transactions: {tx_count}")
    yield
    logger.info("Shutting down UPI Transaction Intelligence backend.")

app = FastAPI(
    title="UPI Transaction Intelligence System API",
    description=(
        "Production-grade financial analytics and rule-based anomaly detection backend for "
        "UPI payment transactions (PhonePe, Razorpay, Visa, Mastercard reference)."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:3000",
    "http://localhost:5173",
    "https://upi-transaction-intelligence.vercel.app",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers for safe, structured responses
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred while processing your request. Please try again.",
            "path": request.url.path
        }
    )

# Include API Routers under /api
app.include_router(dashboard.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(merchants.router, prefix="/api")
app.include_router(anomalies.router, prefix="/api")
app.include_router(data_quality.router, prefix="/api")
app.include_router(reports.router, prefix="/api")

@app.get("/api/health", tags=["Health"])
def health_check():
    """Health check endpoint returning system status and record counts."""
    db_ok = True
    counts = {}
    try:
        cleaned_row = execute_one("SELECT COUNT(*) AS total FROM cleaned_transactions;")
        anomalies_row = execute_one("SELECT COUNT(*) AS total FROM anomaly_findings;")
        dq_row = execute_one("SELECT COUNT(*) AS total FROM data_quality_reports;")
        counts["cleaned_transactions"] = cleaned_row["total"] if cleaned_row else 0
        counts["anomaly_findings"] = anomalies_row["total"] if anomalies_row else 0
        counts["dq_reports"] = dq_row["total"] if dq_row else 0
    except Exception as e:
        logger.error(f"Health check DB error: {e}")
        db_ok = False

    return {
        "status": "UP" if db_ok else "DEGRADED",
        "service": "UPI Transaction Intelligence System",
        "database_connected": db_ok,
        "metrics": counts
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)

