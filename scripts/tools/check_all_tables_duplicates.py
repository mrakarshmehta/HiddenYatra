import pymysql
import os

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'hiddenyatra'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

conn = pymysql.connect(**DB_CONFIG)
with conn.cursor() as cur:
    print("--- Places Duplicates ---")
    cur.execute("SELECT name, COUNT(*) as cnt FROM places WHERE deleted_at IS NULL GROUP BY name HAVING cnt > 1")
    print(cur.fetchall())

    print("\n--- Districts Duplicates ---")
    cur.execute("SELECT name, COUNT(*) as cnt FROM districts GROUP BY name HAVING cnt > 1")
    print(cur.fetchall())

    print("\n--- Accommodations Duplicates ---")
    cur.execute("SELECT place_id, name, COUNT(*) as cnt FROM accommodations GROUP BY place_id, name HAVING cnt > 1")
    print(cur.fetchall())

    print("\n--- District Foods Duplicates ---")
    cur.execute("SELECT district_id, name, COUNT(*) as cnt FROM district_foods GROUP BY district_id, name HAVING cnt > 1")
    print(cur.fetchall())

conn.close()
