"""
Update all 38 Bihar Districts in MySQL with authentic district cover photos.
"""
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

DISTRICT_COVER_IMAGES = {
    "buxar": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Buxar_Battle_Memorial.jpg/1280px-Buxar_Battle_Memorial.jpg",
    "patna": "1_09c59d29.jpg",
    "gaya": "5_b2d596f3.jpg",
    "nalanda": "8_6c112dd8.webp",
    "vaishali": "10_847b0bd5.jpg",
    "muzaffarpur": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Litchi_Fruit_Tree_Muzaffarpur.jpg/1280px-Litchi_Fruit_Tree_Muzaffarpur.jpg",
    "bhagalpur": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Vikramshila_University_Ruins.jpg/1280px-Vikramshila_University_Ruins.jpg",
    "munger": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Munger_Fort_Entrance.jpg/1280px-Munger_Fort_Entrance.jpg",
    "rohtas": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Tomb_of_Sher_Shah_Suri_Sasaram_Bihar.jpg/1280px-Tomb_of_Sher_Shah_Suri_Sasaram_Bihar.jpg",
    "madhubani": "13_488a372c.webp",
    "darbhanga": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Darbhanga_Raj_Fort_Palace.jpg/1280px-Darbhanga_Raj_Fort_Palace.jpg",
    "nawada": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Kakolat_waterfall_Nawada.jpg/1280px-Kakolat_waterfall_Nawada.jpg",
    "west-champaran": "https://images.unsplash.com/photo-1534567153574-2b12153a87f0?w=1000&q=80",
    "east-champaran": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Kesariya_Stupa_Bihar.jpg/1280px-Kesariya_Stupa_Bihar.jpg",
    "begusarai": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Kanwar_Lake_Begusarai.jpg/1280px-Kanwar_Lake_Begusarai.jpg",
    "banka": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Mandar_Hill_Banka_Bihar.jpg/1280px-Mandar_Hill_Banka_Bihar.jpg",
    "kaimur": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Mundeshwari_Temple_Kaimur.jpg/1280px-Mundeshwari_Temple_Kaimur.jpg",
    "sitamarhi": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Janaki_Temple_Sitamarhi.jpg/1280px-Janaki_Temple_Sitamarhi.jpg",
    "aurangabad": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Deo_Sun_Temple_Aurangabad.jpg/1280px-Deo_Sun_Temple_Aurangabad.jpg"
}

def update_district_covers():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, slug FROM districts")
            districts = cur.fetchall()
            print(f"Updating cover images for {len(districts)} districts...")

            count = 0
            for d in districts:
                slug = d['slug']
                cover = DISTRICT_COVER_IMAGES.get(slug, "")
                if cover:
                    cur.execute("UPDATE districts SET cover_image = %s WHERE id = %s", (cover, d['id']))
                    count += 1
                    print(f"  [OK] Updated District {d['name']} ({slug}) -> {cover[:50]}")

            conn.commit()
            print(f"\nSuccessfully updated cover images for {count} districts!")
    finally:
        conn.close()

if __name__ == '__main__':
    update_district_covers()
