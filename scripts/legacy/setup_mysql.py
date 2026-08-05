"""Setup MySQL database for HiddenYatra."""
import pymysql
import os
import sys

DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'hiddenyatra'

print("Step 1: Connecting to MySQL...")
conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD)
cur = conn.cursor()
print(f"  Connected! Version: {conn.get_server_info()}")

print("Step 2: Creating database...")
cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
conn.commit()
print(f"  Database '{DB_NAME}' ready.")

print("Step 3: Importing schema...")
schema_path = os.path.join(os.path.dirname(__file__), 'scripts', 'migrations', 'mysql_schema.sql')
if os.path.exists(schema_path):
    with open(schema_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    cur.execute(f"USE {DB_NAME}")
    # Split by semicolons and execute each statement
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    success = 0
    errors = 0
    for stmt in statements:
        try:
            cur.execute(stmt)
            success += 1
        except pymysql.err.OperationalError as e:
            if e.args[0] == 1050:  # Table already exists
                pass
            else:
                print(f"  WARN: {e}")
                errors += 1
        except Exception as e:
            print(f"  WARN: {e}")
            errors += 1
    conn.commit()
    print(f"  Schema imported: {success} statements OK, {errors} warnings.")
else:
    print(f"  ERROR: Schema file not found at {schema_path}")

print("Step 4: Verifying tables...")
cur.execute(f"USE {DB_NAME}")
cur.execute("SHOW TABLES")
tables = [r[0] for r in cur.fetchall()]
print(f"  Tables ({len(tables)}): {', '.join(tables)}")

print("Step 5: Verifying foreign keys...")
cur.execute("""
    SELECT TABLE_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = %s AND REFERENCED_TABLE_NAME IS NOT NULL
""", (DB_NAME,))
fks = cur.fetchall()
print(f"  Foreign keys: {len(fks)}")
for fk in fks:
    print(f"    {fk[0]}.{fk[1]} -> {fk[2]}")

print("Step 6: Verifying indexes...")
cur.execute("""
    SELECT TABLE_NAME, INDEX_NAME, COLUMN_NAME
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = %s AND INDEX_NAME != 'PRIMARY'
    ORDER BY TABLE_NAME, INDEX_NAME
""", (DB_NAME,))
indexes = cur.fetchall()
print(f"  Non-primary indexes: {len(indexes)}")

cur.close()
conn.close()
print("\n=== MySQL setup COMPLETE ===")
