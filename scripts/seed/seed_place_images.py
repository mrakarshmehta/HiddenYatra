"""
HiddenYatra — Seed High Quality Cover Images and Gallery Photos for All Places
Populates cover_image in `places` table and gallery photos in `photos` table.
"""
import pymysql
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# High-resolution Unsplash image mappings tailored for Bihar landmarks and categories
PLACE_IMAGES = {
    # Patna
    1: { # Golghar
        'cover': 'https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&w=1200&q=80',
        'gallery': [
            'https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&w=1000&q=80',
            'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1000&q=80'
        ]
    },
    2: { # Patna Sahib Gurudwara
        'cover': 'https://images.unsplash.com/photo-1605649487212-47bdab064df7?auto=format&fit=crop&w=1200&q=80',
        'gallery': [
            'https://images.unsplash.com/photo-1605649487212-47bdab064df7?auto=format&fit=crop&w=1000&q=80',
            'https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=1000&q=80'
        ]
    },
    3: { # Patna Museum
        'cover': 'https://images.unsplash.com/photo-1566127444979-b3d2b654e3d7?auto=format&fit=crop&w=1200&q=80',
        'gallery': [
            'https://images.unsplash.com/photo-1566127444979-b3d2b654e3d7?auto=format&fit=crop&w=1000&q=80'
        ]
    },
    4: { # Gandhi Maidan
        'cover': 'https://images.unsplash.com/photo-1519331379826-f10be5486c6f?auto=format&fit=crop&w=1200&q=80',
        'gallery': [
            'https://images.unsplash.com/photo-1519331379826-f10be5486c6f?auto=format&fit=crop&w=1000&q=80'
        ]
    },
    # Gaya / Bodh Gaya
    5: { # Mahabodhi Temple
        'cover': 'https://images.unsplash.com/photo-1599839575945-a9e5af0c3fa5?auto=format&fit=crop&w=1200&q=80',
        'gallery': [
            'https://images.unsplash.com/photo-1599839575945-a9e5af0c3fa5?auto=format&fit=crop&w=1000&q=80',
            'https://images.unsplash.com/photo-1609946782701-843498b8a3b0?auto=format&fit=crop&w=1000&q=80'
        ]
    },
    6: { # Vishnupad Temple
        'cover': 'https://images.unsplash.com/photo-1627894092073-7e78ee2ee624?auto=format&fit=crop&w=1200&q=80',
        'gallery': [
            'https://images.unsplash.com/photo-1627894092073-7e78ee2ee624?auto=format&fit=crop&w=1000&q=80'
        ]
    },
    7: { # Great Buddha Statue
        'cover': 'https://images.unsplash.com/photo-1609946782701-843498b8a3b0?auto=format&fit=crop&w=1200&q=80',
        'gallery': [
            'https://images.unsplash.com/photo-1609946782701-843498b8a3b0?auto=format&fit=crop&w=1000&q=80'
        ]
    },
    # Nalanda / Rajgir
    8: { # Nalanda University Ruins
        'cover': 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1200&q=80',
        'gallery': [
            'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1000&q=80',
            'https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&w=1000&q=80'
        ]
    },
    9: { # Rajgir
        'cover': 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80',
        'gallery': [
            'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1000&q=80'
        ]
    },
    # Vaishali
    10: { # Vaishali
        'cover': 'https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1200&q=80',
        'gallery': [
            'https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1000&q=80'
        ]
    },
    # Bhagalpur
    11: { # Vikramshila Gangetic Dolphin Sanctuary
        'cover': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80',
        'gallery': [
            'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80'
        ]
    },
    # Rohtas
    12: { # Rohtasgarh Fort
        'cover': 'https://images.unsplash.com/photo-1568849676085-51415703900f?auto=format&fit=crop&w=1200&q=80',
        'gallery': [
            'https://images.unsplash.com/photo-1568849676085-51415703900f?auto=format&fit=crop&w=1000&q=80'
        ]
    },
    13: { # Telhar Kund
        'cover': 'https://images.unsplash.com/photo-1432405972618-c60b0225786b?auto=format&fit=crop&w=1200&q=80',
        'gallery': [
            'https://images.unsplash.com/photo-1432405972618-c60b0225786b?auto=format&fit=crop&w=1000&q=80'
        ]
    },
    # Nawada
    14: { # Kakolat Waterfall
        'cover': 'https://images.unsplash.com/photo-1433086966358-54859d0ed716?auto=format&fit=crop&w=1200&q=80',
        'gallery': [
            'https://images.unsplash.com/photo-1433086966358-54859d0ed716?auto=format&fit=crop&w=1000&q=80'
        ]
    },
    # Sasaram
    15: { # Sher Shah Suri Tomb
        'cover': 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80',
        'gallery': [
            'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1000&q=80'
        ]
    },
}

# Default category images for remaining places
CATEGORY_DEFAULTS = {
    'temple': 'https://images.unsplash.com/photo-1627894092073-7e78ee2ee624?auto=format&fit=crop&w=1200&q=80',
    'historical': 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1200&q=80',
    'nature': 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80',
    'waterfall': 'https://images.unsplash.com/photo-1433086966358-54859d0ed716?auto=format&fit=crop&w=1200&q=80',
    'tourist_spot': 'https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&w=1200&q=80',
    'fort': 'https://images.unsplash.com/photo-1568849676085-51415703900f?auto=format&fit=crop&w=1200&q=80',
    'religious': 'https://images.unsplash.com/photo-1599839575945-a9e5af0c3fa5?auto=format&fit=crop&w=1200&q=80',
    'hidden_gem': 'https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1200&q=80',
}

def seed_images():
    conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
                            database=DB_NAME, charset='utf8mb4', autocommit=False)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("SELECT id, name, category FROM places")
    places = cur.fetchall()

    cover_updated = 0
    photos_inserted = 0

    for place in places:
        pid = place['id']
        cat = place.get('category', 'tourist_spot')
        
        # Determine cover image
        if pid in PLACE_IMAGES:
            cover = PLACE_IMAGES[pid]['cover']
            gallery = PLACE_IMAGES[pid].get('gallery', [cover])
        else:
            cover = CATEGORY_DEFAULTS.get(cat, CATEGORY_DEFAULTS['tourist_spot'])
            gallery = [cover]

        # Update cover_image in places
        cur.execute("UPDATE places SET cover_image = %s WHERE id = %s", (cover, pid))
        cover_updated += 1

        # Check if photos exist for this place
        cur.execute("SELECT COUNT(*) AS cnt FROM photos WHERE place_id = %s", (pid,))
        if cur.fetchone()['cnt'] == 0:
            for idx, g_img in enumerate(gallery):
                cur.execute(
                    "INSERT INTO photos (place_id, filename, caption, photo_type, sort_order) VALUES (%s, %s, %s, %s, %s)",
                    (pid, g_img, place['name'], 'official', idx)
                )
                photos_inserted += 1

    conn.commit()
    conn.close()

    print(f"✓ Updated cover images for {cover_updated} places")
    print(f"✓ Inserted {photos_inserted} gallery photos into photos table")

if __name__ == '__main__':
    seed_images()
