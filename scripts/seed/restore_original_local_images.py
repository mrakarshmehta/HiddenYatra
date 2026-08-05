"""
Restore original local uploaded images from static/uploads/places/ back into MySQL database places table.
"""
import os
import pymysql

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'hiddenyatra'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static', 'uploads', 'places')

def restore_local_photos():
    if not os.path.exists(UPLOADS_DIR):
        print("Uploads directory not found.")
        return

    files = [f for f in os.listdir(UPLOADS_DIR) if f != '.gitkeep']
    print(f"Found {len(files)} local uploaded files in static/uploads/places/:")
    for f in files:
        print("  -", f)

    # Group files by place_id (filename format: {place_id}_{hash}.{ext})
    place_files = {}
    for f in files:
        parts = f.split('_')
        if parts[0].isdigit():
            pid = int(parts[0])
            if pid not in place_files:
                place_files[pid] = f

    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            restored = 0
            for pid, filename in place_files.items():
                cur.execute("UPDATE places SET cover_image = %s WHERE id = %s", (filename, pid))
                restored += cur.rowcount
                print(f"[OK] Restored Place ID {pid} -> {filename}")

            conn.commit()
            print(f"\nSuccessfully restored {restored} original local uploaded images into MySQL database!")
    finally:
        conn.close()

if __name__ == '__main__':
    restore_local_photos()
