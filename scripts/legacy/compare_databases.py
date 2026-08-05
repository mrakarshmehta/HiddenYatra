"""Compare recovered SQLite database with current MySQL database."""
import sqlite3
import pymysql

# Connect to recovered SQLite
sqlite_conn = sqlite3.connect(r"D:\HiddenYatra\bharat_darshan_recovered.db")
sqlite_conn.row_factory = sqlite3.Row
sqlite_cur = sqlite_conn.cursor()

# Connect to MySQL
mysql_conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='',
                             database='hiddenyatra', cursorclass=pymysql.cursors.DictCursor)
mysql_cur = mysql_conn.cursor()

print("=" * 75)
print("  SQLite vs MySQL — TABLE-BY-TABLE COMPARISON")
print("  Source: bharat_darshan_recovered.db (from HiddenYatra(1).zip)")
print("=" * 75)
print()

# Get all SQLite tables
sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
sqlite_tables = [r[0] for r in sqlite_cur.fetchall()]

# Get all MySQL tables
mysql_cur.execute("SHOW TABLES")
mysql_tables = sorted([list(r.values())[0] for r in mysql_cur.fetchall()])

all_tables = sorted(set(sqlite_tables + mysql_tables))

print(f"{'Table':<25} {'SQLite':>8} {'MySQL':>8} {'Delta':>8} {'Status':>15}")
print("-" * 75)

total_sqlite = 0
total_mysql = 0
missing_tables = []
tables_with_missing_data = []

for table in all_tables:
    # SQLite count
    try:
        sqlite_cur.execute(f"SELECT COUNT(*) FROM [{table}]")
        s_count = sqlite_cur.fetchone()[0]
    except Exception:
        s_count = -1  # table doesn't exist in SQLite

    # MySQL count
    try:
        mysql_cur.execute(f"SELECT COUNT(*) AS cnt FROM {table}")
        m_count = mysql_cur.fetchone()['cnt']
    except Exception:
        m_count = -1  # table doesn't exist in MySQL

    if s_count == -1:
        status = "MySQL only"
        delta = f"+{m_count}"
    elif m_count == -1:
        status = "SQLITE ONLY!"
        delta = f"-{s_count}"
        missing_tables.append((table, s_count))
    elif s_count == m_count:
        status = "MATCH"
        delta = "0"
    elif m_count > s_count:
        status = "MySQL has more"
        delta = f"+{m_count - s_count}"
    else:
        status = "MISSING DATA!"
        delta = f"-{s_count - m_count}"
        tables_with_missing_data.append((table, s_count, m_count))

    s_str = str(s_count) if s_count >= 0 else "N/A"
    m_str = str(m_count) if m_count >= 0 else "N/A"
    
    if s_count >= 0:
        total_sqlite += s_count
    if m_count >= 0:
        total_mysql += m_count
    
    print(f"  {table:<23} {s_str:>8} {m_str:>8} {delta:>8} {status:>15}")

print("-" * 75)
print(f"  {'TOTAL':<23} {total_sqlite:>8} {total_mysql:>8} {total_mysql - total_sqlite:>+8}")
print()

# Show sample data from tables with missing data
if tables_with_missing_data:
    print("=" * 75)
    print("  TABLES WITH MISSING DATA — DETAILS")
    print("=" * 75)
    for table, s_count, m_count in tables_with_missing_data:
        print(f"\n  {table}: {s_count} in SQLite, {m_count} in MySQL ({s_count - m_count} missing)")
        try:
            sqlite_cur.execute(f"SELECT * FROM [{table}] LIMIT 5")
            cols = [desc[0] for desc in sqlite_cur.description]
            rows = sqlite_cur.fetchall()
            print(f"  Columns: {', '.join(cols)}")
            for row in rows:
                # Show first few relevant columns
                summary = {}
                for c in cols[:5]:
                    val = row[cols.index(c)]
                    if val is not None:
                        summary[c] = str(val)[:50]
                print(f"    {summary}")
        except Exception as e:
            print(f"  Error reading: {e}")

if missing_tables:
    print()
    print("=" * 75)
    print("  TABLES IN SQLITE BUT NOT IN MySQL")
    print("=" * 75)
    for table, count in missing_tables:
        print(f"  {table}: {count} rows")
        try:
            sqlite_cur.execute(f"SELECT * FROM [{table}] LIMIT 3")
            cols = [desc[0] for desc in sqlite_cur.description]
            print(f"  Columns: {', '.join(cols)}")
        except Exception as e:
            print(f"  Error: {e}")

print()
print("=" * 75)
print("  VERDICT")
print("=" * 75)
if not tables_with_missing_data and not missing_tables:
    print("  ALL DATA MATCHES OR MySQL HAS MORE")
else:
    missing_total = sum(s - m for _, s, m in tables_with_missing_data) + sum(c for _, c in missing_tables)
    print(f"  {missing_total} RECORDS NEED TO BE MIGRATED FROM SQLite TO MySQL")
print("=" * 75)

sqlite_conn.close()
mysql_conn.close()
