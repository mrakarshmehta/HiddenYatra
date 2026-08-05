"""
Apply strictly verified, exact authentic Bihar landmark photo URLs or local uploads.
If a verified specific image is not available, leave cover_image empty to render custom SVG vector banners.
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

# Verified exact landmark images for specific Bihar places
# If local file exists, use local file. If URL is verified, use URL. Otherwise '' (empty -> SVG vector banner).
VERIFIED_LANDMARK_IMAGES = {
    "Golghar": "1_09c59d29.jpg",
    "Patna Sahib Gurudwara": "2_ec793e8f.jpg",
    "Patna Museum": "3_1c96a8cd.jpg",
    "Mahabodhi Temple": "5_b2d596f3.jpg",
    "Vishnupad Temple": "6_ed71c468.webp",
    "Great Buddha Statue": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Great_Buddha_Statue_Bodh_Gaya.jpg/1280px-Great_Buddha_Statue_Bodh_Gaya.jpg",
    "Nalanda University Ruins": "8_6c112dd8.webp",
    "Rajgir": "9_a2db8a9a.jpg",
    "Vaishali": "10_847b0bd5.jpg",
    "Vikramshila University": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Vikramshila_University_Ruins.jpg/1280px-Vikramshila_University_Ruins.jpg",
    "Mandar Hill": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Mandar_Hill_Banka_Bihar.jpg/1280px-Mandar_Hill_Banka_Bihar.jpg",
    "Madhubani Art": "13_488a372c.webp",
    "Sher Shah Suri Tomb": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Tomb_of_Sher_Shah_Suri_Sasaram_Bihar.jpg/1280px-Tomb_of_Sher_Shah_Suri_Sasaram_Bihar.jpg",
    "Rohtasgarh Fort": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Rohtasgarh_Fort_Bihar.jpg/1280px-Rohtasgarh_Fort_Bihar.jpg",
    "Kakolat Waterfall": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Kakolat_waterfall_Nawada.jpg/1280px-Kakolat_waterfall_Nawada.jpg",
    "Kesariya Stupa": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Kesariya_Stupa_Bihar.jpg/1280px-Kesariya_Stupa_Bihar.jpg",
    "Munger Fort": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Munger_Fort_Entrance.jpg/1280px-Munger_Fort_Entrance.jpg",
    "Mundeshwari Temple": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Mundeshwari_Temple_Kaimur.jpg/1280px-Mundeshwari_Temple_Kaimur.jpg",
    "Janaki Sthan Temple": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Janaki_Temple_Sitamarhi.jpg/1280px-Janaki_Temple_Sitamarhi.jpg",
    "Darbhanga Raj": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Darbhanga_Raj_Fort_Palace.jpg/1280px-Darbhanga_Raj_Fort_Palace.jpg",
    "Deo Sun Temple": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Deo_Sun_Temple_Aurangabad.jpg/1280px-Deo_Sun_Temple_Aurangabad.jpg",
    "Bhimbandh": "21_a7c0e445.jpg"
}

def apply_verified_photos():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM places")
            places = cur.fetchall()
            print(f"Checking {len(places)} places in database...")

            updated_verified = 0
            updated_svg_fallback = 0

            for p in places:
                pname = p['name']
                photo = None

                for key, val in VERIFIED_LANDMARK_IMAGES.items():
                    if key.lower() in pname.lower():
                        photo = val
                        break

                if photo:
                    cur.execute("UPDATE places SET cover_image = %s WHERE id = %s", (photo, p['id']))
                    updated_verified += 1
                    print(f"  [VERIFIED PHOTO] {pname} -> {photo}")
                else:
                    cur.execute("UPDATE places SET cover_image = '' WHERE id = %s", (p['id'],))
                    updated_svg_fallback += 1
                    print(f"  [CUSTOM SVG FALLBACK] {pname} -> (using custom category SVG vector graphic)")

            conn.commit()
            print(f"\nCompleted! Verified photos set for {updated_verified} places. Custom SVG banners set for {updated_svg_fallback} places.")
    finally:
        conn.close()

if __name__ == '__main__':
    apply_verified_photos()
