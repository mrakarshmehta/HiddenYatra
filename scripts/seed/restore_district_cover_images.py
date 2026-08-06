"""
Restores district cover image filenames from static/uploads/districts/ into MySQL database.
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

def restore_district_cover_images():
    upload_dir = os.path.join('static', 'uploads', 'districts')
    if not os.path.exists(upload_dir):
        print(f"Error: Directory {upload_dir} not found")
        return

    files = os.listdir(upload_dir)
    print(f"Found {len(files)} files in {upload_dir}")

    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, slug FROM districts")
            districts = cur.fetchall()

            updated_count = 0
            for d in districts:
                did = d['id']
                # Match district_{id}_*.png/jpg/webp
                matching_files = [f for f in files if f.startswith(f"district_{did}_")]
                if matching_files:
                    cover_filename = matching_files[0]
                    cur.execute(
                        "UPDATE districts SET cover_image = %s WHERE id = %s",
                        (cover_filename, did)
                    )
                    updated_count += 1
                    print(f"  [OK] District #{did} ({d['name']}) -> {cover_filename}")

            conn.commit()
            print(f"\nSuccessfully restored cover images for {updated_count} / {len(districts)} districts!")
    finally:
        conn.close()

if __name__ == '__main__':
    restore_district_cover_images()
