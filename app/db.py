import os
import logging
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ai_tools_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
CLOUD_SQL_CONNECTION_NAME = os.getenv("CLOUD_SQL_CONNECTION_NAME", "")
DB_SSLMODE = os.getenv("DB_SSLMODE", "prefer")


def get_connection():
    """Create and return a new database connection.

    Uses Cloud SQL Unix socket when CLOUD_SQL_CONNECTION_NAME is set,
    otherwise uses direct host/port connection settings.
    """
    if CLOUD_SQL_CONNECTION_NAME:
        return psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=f"/cloudsql/{CLOUD_SQL_CONNECTION_NAME}",
        )

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode=DB_SSLMODE,
    )


@contextmanager
def get_cursor():
    """Context manager that yields a RealDictCursor."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            yield cursor
    finally:
        conn.close()


def execute_query(sql: str) -> list[dict]:
    """
    Execute a read-only SQL query and return results as a list of dicts.

    Args:
        sql: The SQL statement to execute.

    Returns:
        A list of row dictionaries.

    Raises:
        ValueError: If the SQL statement is not a SELECT query.
        psycopg2.Error: On database errors.
    """
    normalized = sql.strip().upper()
    if not normalized.startswith("SELECT"):
        raise ValueError("Only SELECT queries are permitted.")

    with get_cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
