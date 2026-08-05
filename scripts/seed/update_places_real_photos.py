"""
Seed/Update all MySQL places with working high-res Unsplash travel photos by category/name.
"""
import pymysql
import os
import sys

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'hiddenyatra'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# Mapping keywords / categories to curated HD Unsplash travel photos
CATEGORY_PHOTOS = {
    'waterfall': 'https://images.unsplash.com/photo-1432405972618-c60b0225b8f9?w=1000&q=80',
    'temple': 'https://images.unsplash.com/photo-1609947017136-9daf32a15c8c?w=1000&q=80',
    'religious': 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=1000&q=80',
    'fort': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=1000&q=80',
    'historical': 'https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?w=1000&q=80',
    'nature': 'https://images.unsplash.com/photo-1506461883276-594a12b11cf3?w=1000&q=80',
    'hill_station': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1000&q=80',
    'mountain': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1000&q=80',
    'park': 'https://images.unsplash.com/photo-1506461883276-594a12b11cf3?w=1000&q=80',
    'lake': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1000&q=80',
    'wildlife': 'https://images.unsplash.com/photo-1534567153574-2b12153a87f0?w=1000&q=80',
    'default': 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=1000&q=80'
}

def update_photos():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, category, cover_image FROM places")
            places = cur.fetchall()
            print(f"Found {len(places)} places in database.")

            updated_count = 0
            for p in places:
                name_lower = p['name'].lower()
                cat_lower = (p['category'] or 'default').lower()

                # Choose best photo URL based on name/category
                if 'waterfall' in name_lower or 'kund' in name_lower or cat_lower == 'waterfall':
                    photo_url = CATEGORY_PHOTOS['waterfall']
                elif 'temple' in name_lower or 'mandir' in name_lower or cat_lower in ('temple', 'religious'):
                    photo_url = CATEGORY_PHOTOS['temple']
                elif 'fort' in name_lower or ' किला' in name_lower or cat_lower == 'fort':
                    photo_url = CATEGORY_PHOTOS['fort']
                elif 'hill' in name_lower or 'peak' in name_lower or cat_lower == 'hill_station':
                    photo_url = CATEGORY_PHOTOS['hill_station']
                elif 'lake' in name_lower or 'talao' in name_lower or cat_lower == 'lake':
                    photo_url = CATEGORY_PHOTOS['lake']
                elif 'wildlife' in name_lower or 'sanctuary' in name_lower or cat_lower == 'wildlife':
                    photo_url = CATEGORY_PHOTOS['wildlife']
                elif 'ruins' in name_lower or 'tomb' in name_lower or cat_lower == 'historical':
                    photo_url = CATEGORY_PHOTOS['historical']
                else:
                    photo_url = CATEGORY_PHOTOS.get(cat_lower, CATEGORY_PHOTOS['default'])

                cur.execute("UPDATE places SET cover_image = %s WHERE id = %s", (photo_url, p['id']))
                updated_count += 1

            conn.commit()
            print(f"Successfully updated {updated_count} places with high-res travel photos!")
    finally:
        conn.close()

if __name__ == '__main__':
    update_photos()
