"""Fix missing indexes from schema import."""
import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='', database='hiddenyatra')
cur = conn.cursor()

indexes = [
    ("idx_places_slug_deleted", "places", "(slug, deleted_at)"),
    ("idx_places_lat_lng", "places", "(latitude, longitude)"),
    ("idx_reviews_place_created", "reviews", "(place_id, created_at)"),
]

for name, table, cols in indexes:
    try:
        cur.execute(f"CREATE INDEX {name} ON {table} {cols}")
        print(f"  Created index {name}")
    except pymysql.err.OperationalError as e:
        if e.args[0] == 1061:  # Duplicate key name
            print(f"  Index {name} already exists")
        else:
            print(f"  WARN: {e}")

conn.commit()
cur.close()
conn.close()
print("--- INDEXES FIXED ---")
