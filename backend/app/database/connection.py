import sqlite3
import os
from contextlib import contextmanager
from typing import Generator, List, Dict, Any, Optional
from ..utils.logging_config import logger

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
DB_PATH = os.path.join(DB_DIR, "upi_transactions.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

def ensure_db_dir():
    """Ensure data directory exists."""
    os.makedirs(DB_DIR, exist_ok=True)
    os.makedirs(os.path.join(DB_DIR, "processed"), exist_ok=True)

@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Yield a SQLite connection configured for dict-like row access."""
    ensure_db_dir()
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys and WAL mode for better concurrency
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database tables, indexes, and views from schema.sql."""
    ensure_db_dir()
    logger.info(f"Initializing database at: {DB_PATH}")
    with get_db_connection() as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_script = f.read()
        conn.executescript(schema_script)
        conn.commit()
    logger.info("Database schema initialized successfully.")

def clear_all_data():
    """Truncate data tables and remove parquet file while preserving schema and configuration."""
    with get_db_connection() as conn:
        conn.execute("DELETE FROM quarantined_transactions;")
        conn.execute("DELETE FROM anomaly_findings;")
        conn.execute("DELETE FROM data_quality_reports;")
        conn.execute("DELETE FROM cleaned_transactions;")
        conn.execute("DELETE FROM raw_transactions;")
        conn.commit()
    
    parquet_path = os.path.join(DB_DIR, "processed", "cleaned_transactions.parquet")
    if os.path.exists(parquet_path):
        try:
            os.remove(parquet_path)
        except Exception:
            pass

def execute_query(query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Execute a read query and return list of row dictionaries."""
    params = params or {}
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def execute_one(query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Execute a read query returning a single row dict or None."""
    params = params or {}
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

def execute_commit(query: str, params: Optional[Dict[str, Any]] = None) -> int:
    """Execute an INSERT/UPDATE/DELETE query and return affected row count."""
    params = params or {}
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount

def execute_batch(query: str, param_list: List[Dict[str, Any]]) -> int:
    """Execute an executemany operation within a transaction."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany(query, param_list)
        conn.commit()
        return cursor.rowcount

