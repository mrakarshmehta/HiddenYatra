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
    cur.execute("""
        SELECT district_id, name, MIN(id) as keep_id, COUNT(*) as cnt
        FROM district_foods
        GROUP BY district_id, name
        HAVING cnt > 1
    """)
    dups = cur.fetchall()
    deleted = 0
    for d in dups:
        cur.execute("DELETE FROM district_foods WHERE district_id = %s AND name = %s AND id > %s",
                    (d['district_id'], d['name'], d['keep_id']))
        deleted += cur.rowcount

    conn.commit()
    print(f"Cleaned {deleted} duplicate rows from district_foods table!")

conn.close()
