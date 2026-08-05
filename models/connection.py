"""
HiddenYatra — Database Connection Management & Pooling
Provides MySQL connection pool singleton and transaction-safe cursor context manager.
"""
import os
import re
import logging
import threading
from contextlib import contextmanager

import pymysql
import pymysql.converters
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB

from config import (
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD,
    DB_CHARSET, DB_POOL_SIZE, DB_POOL_MAX, DB_TIMEOUT
)

logger = logging.getLogger(__name__)


def _slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def slugify(text):
    """Convert text to URL-safe slug."""
    return _slugify(text)


def _escape_like(value):
    """Escape special LIKE wildcards in user input to prevent LIKE injection."""
    return value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


# ──────────────────────────────────────────────
# Connection Pool (thread-safe singleton)
# ──────────────────────────────────────────────
_pool = None
_pool_lock = threading.Lock()


def _get_pool():
    """Get or create the global connection pool (thread-safe)."""
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                from pymysql.constants import FIELD_TYPE
                conv = pymysql.converters.conversions.copy()
                conv[FIELD_TYPE.DECIMAL] = float
                conv[FIELD_TYPE.NEWDECIMAL] = float
                _pool = PooledDB(
                    creator=pymysql,
                    maxconnections=DB_POOL_MAX,
                    mincached=DB_POOL_SIZE,
                    maxcached=DB_POOL_SIZE,
                    blocking=True,
                    maxusage=0,
                    ping=1,
                    setsession=['SET NAMES utf8mb4', 'SET SESSION wait_timeout=28800'],
                    host=DB_HOST,
                    port=DB_PORT,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME,
                    charset=DB_CHARSET,
                    cursorclass=DictCursor,
                    connect_timeout=DB_TIMEOUT,
                    autocommit=False,
                    conv=conv,
                )
                logger.info("MySQL connection pool created (size=%d, max=%d)", DB_POOL_SIZE, DB_POOL_MAX)
    return _pool


def get_db():
    """Get a database connection from the pool."""
    return _get_pool().connection()


@contextmanager
def get_cursor(commit=False):
    """Context manager for safe cursor usage."""
    conn = get_db()
    try:
        cur = conn.cursor()
        yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def init_db():
    """Initialize MySQL database — run schema SQL if tables don't exist."""
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) AS cnt FROM information_schema.tables
            WHERE table_schema = %s AND table_name = 'states'
        """, (DB_NAME,))
        row = cur.fetchone()
        if row and row['cnt'] > 0:
            logger.info("MySQL database already initialized (tables exist).")
            cur.close()
            return

        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'scripts', 'migrations', 'mysql_schema.sql'
        )
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                sql = f.read()
            statements = [s.strip() for s in sql.split(';') if s.strip()]
            for stmt in statements:
                if stmt.upper().startswith(('CREATE DATABASE', 'USE ')):
                    continue
                try:
                    cur.execute(stmt)
                except pymysql.Error as e:
                    if e.args[0] not in (1050, 1061, 1062):
                        logger.warning("Schema statement warning: %s", e)
            conn.commit()
            logger.info("MySQL schema created successfully from %s", schema_path)
        else:
            logger.error("Schema file not found at %s — tables must be created manually.", schema_path)
        cur.close()
    except Exception as e:
        conn.rollback()
        logger.error("Failed to initialize database: %s", e)
        raise
    finally:
        conn.close()
