"""
HiddenYatra — SQLite to MySQL Data Migration Script.
Copies all data from bharat_darshan.db → MySQL hiddenyatra database.
Run AFTER mysql_schema.sql has been executed.

Usage:
    python scripts/migrations/migrate_sqlite_to_mysql.py
"""
import os
import sys
import sqlite3
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env'))

import pymysql
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_CHARSET

# ── Paths ──
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SQLITE_DB = os.path.join(PROJECT_ROOT, 'bharat_darshan.db')

# Tables in dependency order (parents first)
TABLES = [
    'states',
    'districts',
    'blocks',
    'places',
    'photos',
    'specialties',
    'accommodations',
    'users',
    'wishlists',
    'reviews',
    'itineraries',
    'itinerary_items',
    'user_submissions',
    'visited_places',
    'district_foods',
    'nearby_services',
    'admin_logs',
    'hero_media',
    'hero_settings',
    'trending_places',
    'homepage_sections',
    'auth_appearance',
    'user_photos',
]


def get_sqlite_conn():
    """Get SQLite connection."""
    if not os.path.exists(SQLITE_DB):
        print(f"ERROR: SQLite database not found at {SQLITE_DB}")
        sys.exit(1)
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    return conn


def get_mysql_conn():
    """Get MySQL connection."""
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset=DB_CHARSET,
        autocommit=False,
    )


def get_sqlite_table_columns(sqlite_conn, table_name):
    """Get column names for a SQLite table."""
    cur = sqlite_conn.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cur.fetchall()]


def get_mysql_table_columns(mysql_conn, table_name):
    """Get column names for a MySQL table."""
    cur = mysql_conn.cursor()
    cur.execute(f"SHOW COLUMNS FROM {table_name}")
    cols = [row[0] for row in cur.fetchall()]
    cur.close()
    return cols


def migrate_table(sqlite_conn, mysql_conn, table_name):
    """Migrate a single table from SQLite to MySQL."""
    # Get common columns (present in both databases)
    try:
        sqlite_cols = get_sqlite_table_columns(sqlite_conn, table_name)
    except Exception:
        print(f"  SKIP: Table '{table_name}' not found in SQLite.")
        return 0

    try:
        mysql_cols = get_mysql_table_columns(mysql_conn, table_name)
    except Exception:
        print(f"  SKIP: Table '{table_name}' not found in MySQL.")
        return 0

    common_cols = [c for c in sqlite_cols if c in mysql_cols]
    if not common_cols:
        print(f"  SKIP: No common columns for '{table_name}'.")
        return 0

    # Read all rows from SQLite
    col_list = ', '.join(common_cols)
    sqlite_rows = sqlite_conn.execute(f"SELECT {col_list} FROM {table_name}").fetchall()

    if not sqlite_rows:
        print(f"  EMPTY: '{table_name}' has no data.")
        return 0

    # Build MySQL INSERT
    placeholders = ', '.join(['%s'] * len(common_cols))
    insert_sql = f"INSERT INTO {table_name} ({col_list}) VALUES ({placeholders})"

    cur = mysql_conn.cursor()
    count = 0
    errors = 0

    for row in sqlite_rows:
        values = []
        for i, col in enumerate(common_cols):
            val = row[col]
            # Convert SQLite booleans
            if val is True:
                val = 1
            elif val is False:
                val = 0
            values.append(val)

        try:
            cur.execute(insert_sql, values)
            count += 1
        except pymysql.IntegrityError as e:
            # Duplicate key — skip
            errors += 1
        except pymysql.Error as e:
            print(f"    ERROR on row: {e}")
            errors += 1

    mysql_conn.commit()
    cur.close()

    if errors:
        print(f"  OK: {count} rows migrated, {errors} skipped (duplicates/errors)")
    else:
        print(f"  OK: {count} rows migrated")
    return count


def main():
    """Run the full migration."""
    print("=" * 60)
    print("HiddenYatra — SQLite → MySQL Migration")
    print("=" * 60)
    print(f"Source: {SQLITE_DB}")
    print(f"Target: mysql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    print()

    sqlite_conn = get_sqlite_conn()
    mysql_conn = get_mysql_conn()

    # Disable FK checks during migration
    cur = mysql_conn.cursor()
    cur.execute("SET FOREIGN_KEY_CHECKS = 0")
    mysql_conn.commit()
    cur.close()

    total_rows = 0
    for table in TABLES:
        print(f"Migrating: {table}")
        count = migrate_table(sqlite_conn, mysql_conn, table)
        total_rows += count

    # Re-enable FK checks
    cur = mysql_conn.cursor()
    cur.execute("SET FOREIGN_KEY_CHECKS = 1")
    mysql_conn.commit()
    cur.close()

    sqlite_conn.close()
    mysql_conn.close()

    print()
    print("=" * 60)
    print(f"Migration complete! Total rows migrated: {total_rows}")
    print("=" * 60)


if __name__ == '__main__':
    main()
