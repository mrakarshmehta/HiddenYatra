"""
Automated Verification Script: verify_cover_images.py
Ensures 100% of districts and places have valid cover images and local disk files exist.
Exits with status 1 if any regression or missing cover image is detected.
"""
import os
import sys
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

def verify_cover_images():
    print("=" * 60)
    print("  AUTOMATED COVER IMAGE REGRESSION VERIFICATION")
    print("=" * 60)

    has_errors = False
    conn = pymysql.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cur:
            # 1. Verify Districts
            cur.execute("SELECT COUNT(*) AS total FROM districts")
            total_districts = cur.fetchone()['total']

            cur.execute("SELECT COUNT(*) AS with_cover FROM districts WHERE cover_image IS NOT NULL AND cover_image != ''")
            districts_with_cover = cur.fetchone()['with_cover']

            print(f"\n[DISTRICTS CHECK]")
            print(f"  * Total Districts:           {total_districts}")
            print(f"  * Districts with Cover Image: {districts_with_cover}")

            if total_districts < 38:
                print(f"  [ERROR] Total districts ({total_districts}) is less than expected 38!")
                has_errors = True
            elif districts_with_cover < total_districts:
                missing_cnt = total_districts - districts_with_cover
                print(f"  [ERROR] {missing_cnt} districts are missing cover images!")
                has_errors = True
            else:
                print(f"  [PASSED] All 38 districts have valid cover images (100% coverage).")

            # 2. Verify Places
            cur.execute("SELECT COUNT(*) AS total FROM places WHERE deleted_at IS NULL")
            total_places = cur.fetchone()['total']

            cur.execute("SELECT COUNT(*) AS with_cover FROM places WHERE deleted_at IS NULL AND cover_image IS NOT NULL AND cover_image != ''")
            places_with_cover = cur.fetchone()['with_cover']

            print(f"\n[PLACES CHECK]")
            print(f"  * Total Places:              {total_places}")
            print(f"  * Places with Cover Image:   {places_with_cover}")

            if places_with_cover < total_places:
                missing_cnt = total_places - places_with_cover
                print(f"  [WARNING/ERROR] {missing_cnt} places are missing cover images!")
                has_errors = True
            else:
                print(f"  [PASSED] All {total_places} places have valid cover images (100% coverage).")

            # 3. Verify Local Disk Files for Districts
            cur.execute("SELECT id, name, cover_image FROM districts WHERE cover_image != '' AND cover_image NOT LIKE 'http%'")
            local_district_covers = cur.fetchall()

            district_upload_dir = os.path.join('static', 'uploads', 'districts')
            missing_district_files = []
            for d in local_district_covers:
                fpath = os.path.join(district_upload_dir, d['cover_image'])
                if not os.path.exists(fpath):
                    missing_district_files.append((d['name'], d['cover_image']))

            print(f"\n[DISTRICT LOCAL DISK FILES CHECK]")
            if missing_district_files:
                print(f"  [ERROR] {len(missing_district_files)} district cover files missing on disk:")
                for name, fname in missing_district_files:
                    print(f"    - {name}: {fname}")
                has_errors = True
            else:
                print(f"  [PASSED] All {len(local_district_covers)} local district cover image files exist on disk.")

            # 4. Verify Local Disk Files for Places
            cur.execute("SELECT id, name, cover_image FROM places WHERE deleted_at IS NULL AND cover_image != '' AND cover_image NOT LIKE 'http%'")
            local_place_covers = cur.fetchall()

            place_upload_dir = os.path.join('static', 'uploads', 'places')
            missing_place_files = []
            for p in local_place_covers:
                fpath = os.path.join(place_upload_dir, p['cover_image'])
                if not os.path.exists(fpath):
                    missing_place_files.append((p['name'], p['cover_image']))

            print(f"\n[PLACE LOCAL DISK FILES CHECK]")
            if missing_place_files:
                print(f"  [ERROR] {len(missing_place_files)} place cover files missing on disk:")
                for name, fname in missing_place_files:
                    print(f"    - {name}: {fname}")
                has_errors = True
            else:
                print(f"  [PASSED] All {len(local_place_covers)} local place cover image files exist on disk.")

    finally:
        conn.close()

    print("\n" + "=" * 60)
    if has_errors:
        print("  VERIFICATION FAILED: REGRESSION DETECTED!")
        print("=" * 60)
        sys.exit(1)
    else:
        print("  VERIFICATION PASSED: ALL COVER IMAGES 100% HEALTHY!")
        print("=" * 60)
        sys.exit(0)

if __name__ == '__main__':
    verify_cover_images()
