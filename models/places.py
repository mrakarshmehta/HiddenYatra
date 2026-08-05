"""
HiddenYatra — Places, Photos, Specialties, Accommodations & Search Database Operations
"""
import os
import math
import logging
from datetime import datetime

from models.connection import get_db, get_cursor, slugify, _escape_like
from config import UPLOAD_FOLDER

logger = logging.getLogger(__name__)


def get_all_places(limit=50, offset=0, category=None, state_id=None, featured_only=False):
    with get_cursor() as cur:
        query = """
            SELECT p.*, s.name AS state_name, s.slug AS state_slug,
                   d.name AS district_name,
                   (SELECT COUNT(*) FROM photos ph WHERE ph.place_id = p.id) AS photo_count
            FROM places p
            JOIN states s ON s.id = p.state_id
            LEFT JOIN districts d ON d.id = p.district_id
            WHERE 1=1 AND p.deleted_at IS NULL
        """
        params = []
        if category:
            query += " AND p.category = %s"
            params.append(category)
        if state_id:
            query += " AND p.state_id = %s"
            params.append(state_id)
        if featured_only:
            query += " AND p.is_featured = 1"

        query += " ORDER BY p.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cur.execute(query, params)
        return cur.fetchall()


def get_featured_places(limit=8):
    with get_cursor() as cur:
        cur.execute("""
            SELECT p.*, s.name AS state_name, s.slug AS state_slug,
                   d.name AS district_name,
                   COUNT(r.id) AS review_count,
                   ROUND(AVG(r.rating), 1) AS avg_rating
            FROM places p
            JOIN states s ON s.id = p.state_id
            LEFT JOIN districts d ON d.id = p.district_id
            LEFT JOIN reviews r ON r.place_id = p.id
            WHERE p.is_featured = 1 AND p.deleted_at IS NULL
            GROUP BY p.id
            ORDER BY p.created_at DESC
            LIMIT %s
        """, (limit,))
        return cur.fetchall()


def get_recent_places(limit=6):
    return get_all_places(limit=limit)


def get_trending_places(limit=8):
    with get_cursor() as cur:
        cur.execute("""
            SELECT p.*, s.name AS state_name, s.slug AS state_slug,
                   d.name AS district_name,
                   COUNT(r.id) AS review_count,
                   ROUND(AVG(r.rating), 1) AS avg_rating
            FROM places p
            JOIN states s ON s.id = p.state_id
            LEFT JOIN districts d ON d.id = p.district_id
            LEFT JOIN reviews r ON r.place_id = p.id
            WHERE p.deleted_at IS NULL
            GROUP BY p.id
            ORDER BY (p.view_count + review_count * 10) DESC
            LIMIT %s
        """, (limit,))
        return cur.fetchall()


def get_place_by_slug(slug):
    with get_cursor() as cur:
        cur.execute("""
            SELECT p.*, s.name AS state_name, s.slug AS state_slug,
                   d.name AS district_name, b.name AS block_name
            FROM places p
            JOIN states s ON s.id = p.state_id
            LEFT JOIN districts d ON d.id = p.district_id
            LEFT JOIN blocks b ON b.id = p.block_id
            WHERE p.slug = %s AND p.deleted_at IS NULL
        """, (slug,))
        return cur.fetchone()


def get_place_by_id(place_id):
    with get_cursor() as cur:
        cur.execute("""
            SELECT p.*, s.name AS state_name, s.slug AS state_slug,
                   d.name AS district_name, b.name AS block_name
            FROM places p
            JOIN states s ON s.id = p.state_id
            LEFT JOIN districts d ON d.id = p.district_id
            LEFT JOIN blocks b ON b.id = p.block_id
            WHERE p.id = %s
        """, (place_id,))
        return cur.fetchone()


def get_places_by_state(state_id, limit=50):
    return get_all_places(limit=limit, state_id=state_id)


def get_places_by_district(district_id, limit=50, offset=0):
    with get_cursor() as cur:
        cur.execute("""
            SELECT p.*, s.name AS state_name, s.slug AS state_slug,
                   d.name AS district_name, b.name AS block_name
            FROM places p
            JOIN states s ON s.id = p.state_id
            LEFT JOIN districts d ON d.id = p.district_id
            LEFT JOIN blocks b ON b.id = p.block_id
            WHERE p.district_id = %s AND p.deleted_at IS NULL
            ORDER BY p.is_featured DESC, p.name
            LIMIT %s OFFSET %s
        """, (district_id, limit, offset))
        return cur.fetchall()


def count_places_in_district(district_id):
    with get_cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM places WHERE district_id = %s AND deleted_at IS NULL",
            (district_id,)
        )
        return cur.fetchone()['cnt']


def get_places_by_block(block_id, limit=50, offset=0):
    with get_cursor() as cur:
        cur.execute("""
            SELECT p.*, s.name AS state_name, s.slug AS state_slug,
                   d.name AS district_name, b.name AS block_name
            FROM places p
            JOIN states s ON s.id = p.state_id
            LEFT JOIN districts d ON d.id = p.district_id
            LEFT JOIN blocks b ON b.id = p.block_id
            WHERE p.block_id = %s AND p.deleted_at IS NULL
            ORDER BY p.is_featured DESC, p.name
            LIMIT %s OFFSET %s
        """, (block_id, limit, offset))
        return cur.fetchall()


def count_places_in_block(block_id):
    with get_cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM places WHERE block_id = %s AND deleted_at IS NULL",
            (block_id,)
        )
        return cur.fetchone()['cnt']


def increment_view_count(place_id):
    with get_cursor(commit=True) as cur:
        cur.execute("UPDATE places SET view_count = view_count + 1 WHERE id = %s", (place_id,))


def create_place(data):
    conn = get_db()
    try:
        cur = conn.cursor()
        slug = slugify(data['name'])
        cur.execute("SELECT id FROM places WHERE slug = %s", (slug,))
        existing = cur.fetchone()
        if existing:
            slug = f"{slug}-{int(datetime.now().timestamp())}"

        cur.execute("""
            INSERT INTO places (state_id, district_id, block_id, name, slug, description,
                               category, latitude, longitude, maps_link, cover_image, is_featured,
                               best_time_to_visit, entry_fee, travel_tips)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['state_id'], data.get('district_id'), data.get('block_id'),
            data['name'], slug, data.get('description', ''),
            data.get('category', 'tourist_spot'),
            data.get('latitude'), data.get('longitude'),
            data.get('maps_link', ''), data.get('cover_image', ''),
            1 if data.get('is_featured') else 0,
            data.get('best_time_to_visit', ''),
            data.get('entry_fee', ''),
            data.get('travel_tips', ''),
        ))
        conn.commit()
        place_id = cur.lastrowid
        cur.close()
        return place_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_place(place_id, data):
    with get_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE places SET
                state_id = %s, district_id = %s, block_id = %s,
                name = %s, description = %s, category = %s,
                latitude = %s, longitude = %s, maps_link = %s,
                cover_image = %s, is_featured = %s,
                best_time_to_visit = %s, entry_fee = %s, travel_tips = %s
            WHERE id = %s
        """, (
            data['state_id'], data.get('district_id'), data.get('block_id'),
            data['name'], data.get('description', ''),
            data.get('category', 'tourist_spot'),
            data.get('latitude'), data.get('longitude'),
            data.get('maps_link', ''), data.get('cover_image', ''),
            1 if data.get('is_featured') else 0,
            data.get('best_time_to_visit', ''),
            data.get('entry_fee', ''),
            data.get('travel_tips', ''),
            place_id
        ))


def update_place_extra_fields(place_id, data):
    with get_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE places SET
                best_time_to_visit = %s,
                entry_fee = %s,
                travel_tips = %s,
                is_hidden_gem = %s,
                history = %s,
                local_tips = %s,
                safety_tips = %s,
                best_season = %s,
                best_time_of_day = %s,
                crowd_level = %s,
                parking_info = %s,
                family_friendly = %s,
                nearest_railway = %s,
                nearest_bus_stand = %s,
                nearest_airport = %s,
                road_connectivity = %s
            WHERE id = %s
        """, (
            data.get('best_time_to_visit', ''),
            data.get('entry_fee', ''),
            data.get('travel_tips', ''),
            1 if data.get('is_hidden_gem') else 0,
            data.get('history', ''),
            data.get('local_tips', ''),
            data.get('safety_tips', ''),
            data.get('best_season', ''),
            data.get('best_time_of_day', ''),
            data.get('crowd_level', ''),
            data.get('parking_info', ''),
            1 if data.get('family_friendly') else 0,
            data.get('nearest_railway', ''),
            data.get('nearest_bus_stand', ''),
            data.get('nearest_airport', ''),
            data.get('road_connectivity', ''),
            place_id
        ))


def quick_edit_place(place_id, name, description, category, is_featured):
    with get_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE places SET name = %s, description = %s, category = %s,
            is_featured = %s WHERE id = %s
        """, (name, description, category, is_featured, place_id))


def set_place_cover(place_id, filename):
    with get_cursor(commit=True) as cur:
        cur.execute("UPDATE places SET cover_image = %s WHERE id = %s", (filename, place_id))


def clear_place_cover_if_match(place_id, filename):
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE places SET cover_image = '' WHERE id = %s AND cover_image = %s",
            (place_id, filename)
        )


def delete_place(place_id):
    soft_delete_place(place_id, 'admin')


def soft_delete_place(place_id, deleted_by='admin'):
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE places SET deleted_at = NOW(), deleted_by = %s WHERE id = %s",
            (deleted_by, place_id)
        )


def restore_place(place_id):
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE places SET deleted_at = NULL, deleted_by = NULL WHERE id = %s",
            (place_id,)
        )


def permanent_delete_place(place_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT filename FROM photos WHERE place_id = %s", (place_id,))
        photos = cur.fetchall()
        for ph in photos:
            fpath = os.path.join(UPLOAD_FOLDER, ph['filename'])
            if os.path.exists(fpath):
                os.remove(fpath)
        cur.execute("DELETE FROM photos WHERE place_id = %s", (place_id,))
        cur.execute("DELETE FROM reviews WHERE place_id = %s", (place_id,))
        cur.execute("DELETE FROM specialties WHERE place_id = %s", (place_id,))
        cur.execute("DELETE FROM accommodations WHERE place_id = %s", (place_id,))
        cur.execute("DELETE FROM wishlists WHERE place_id = %s", (place_id,))
        cur.execute("DELETE FROM places WHERE id = %s", (place_id,))
        conn.commit()
        cur.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_deleted_places():
    with get_cursor() as cur:
        cur.execute("""
            SELECT p.*, s.name AS state_name, d.name AS district_name
            FROM places p
            JOIN states s ON s.id = p.state_id
            LEFT JOIN districts d ON d.id = p.district_id
            WHERE p.deleted_at IS NOT NULL
            ORDER BY p.deleted_at DESC
        """)
        return cur.fetchall()


def count_places():
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM places WHERE deleted_at IS NULL")
        return cur.fetchone()['cnt']


def count_deleted_places():
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM places WHERE deleted_at IS NOT NULL")
        return cur.fetchone()['cnt']


def get_photos_by_place(place_id):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM photos WHERE place_id = %s ORDER BY sort_order, id", (place_id,))
        return cur.fetchall()


def add_photo(place_id, filename, caption='', sort_order=0):
    with get_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO photos (place_id, filename, caption, sort_order) VALUES (%s, %s, %s, %s)",
            (place_id, filename, caption, sort_order)
        )
        return cur.lastrowid


def delete_photo(photo_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT filename FROM photos WHERE id = %s", (photo_id,))
        row = cur.fetchone()
        cur.execute("DELETE FROM photos WHERE id = %s", (photo_id,))
        conn.commit()
        cur.close()
        return row
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_specialties_by_place(place_id):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM specialties WHERE place_id = %s ORDER BY id", (place_id,))
        return cur.fetchall()


def add_specialty(place_id, data):
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO specialties (place_id, name, description, category,
                                    where_to_find, location_hint, latitude, longitude, distance_km)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            place_id, data['name'], data.get('description', ''),
            data.get('category', 'food'), data.get('where_to_find', ''),
            data.get('location_hint', ''),
            data.get('latitude'), data.get('longitude'),
            data.get('distance_km', 0)
        ))
        return cur.lastrowid


def delete_specialty(specialty_id):
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM specialties WHERE id = %s", (specialty_id,))


def delete_specialties_by_place(place_id):
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM specialties WHERE place_id = %s", (place_id,))


def get_accommodations_by_place(place_id):
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM accommodations WHERE place_id = %s ORDER BY distance_km, name",
            (place_id,)
        )
        return cur.fetchall()


def add_accommodation(place_id, data):
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO accommodations (place_id, name, type, price_range, description,
                                        address, phone, website, rating, latitude, longitude, distance_km)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            place_id, data['name'], data.get('type', 'hotel'),
            data.get('price_range', ''), data.get('description', ''),
            data.get('address', ''), data.get('phone', ''),
            data.get('website', ''), data.get('rating', 0),
            data.get('latitude'), data.get('longitude'),
            data.get('distance_km', 0)
        ))
        return cur.lastrowid


def delete_accommodations_by_place(place_id):
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM accommodations WHERE place_id = %s", (place_id,))


def get_district_foods(district_id):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM district_foods WHERE district_id = %s ORDER BY name", (district_id,))
        return cur.fetchall()


def get_all_district_foods_by_state(state_id):
    with get_cursor() as cur:
        cur.execute("""
            SELECT df.*, d.name AS district_name, d.slug AS district_slug
            FROM district_foods df
            JOIN districts d ON d.id = df.district_id
            WHERE d.state_id = %s
            ORDER BY d.name, df.name
        """, (state_id,))
        return cur.fetchall()


def add_district_food(district_id, data):
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO district_foods (district_id, name, description, category, image_url, best_places_to_eat)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            district_id, data['name'], data.get('description', ''),
            data.get('category', 'food'), data.get('image_url', ''),
            data.get('best_places_to_eat', '')
        ))
        return cur.lastrowid


def delete_district_food(food_id):
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM district_foods WHERE id = %s", (food_id,))


def get_nearby_places(place_id, limit=4):
    """Get nearby places in the same district or state."""
    with get_cursor() as cur:
        cur.execute("SELECT district_id, state_id FROM places WHERE id = %s", (place_id,))
        p = cur.fetchone()
        if not p:
            return []

        cur.execute("""
            SELECT p.*, s.name AS state_name, s.slug AS state_slug,
                   d.name AS district_name,
                   (SELECT COUNT(*) FROM reviews r WHERE r.place_id = p.id) AS review_count,
                   (SELECT ROUND(AVG(r.rating), 1) FROM reviews r WHERE r.place_id = p.id) AS avg_rating
            FROM places p
            JOIN states s ON s.id = p.state_id
            LEFT JOIN districts d ON d.id = p.district_id
            WHERE p.id != %s AND p.deleted_at IS NULL
                  AND (p.district_id = %s OR p.state_id = %s)
            ORDER BY CASE WHEN p.district_id = %s THEN 0 ELSE 1 END, p.view_count DESC
            LIMIT %s
        """, (place_id, p['district_id'], p['state_id'], p['district_id'], limit))
        return cur.fetchall()



def search_places(query, limit=20):
    with get_cursor() as cur:
        q = f"%{_escape_like(query)}%"
        cur.execute("""
            SELECT p.*, s.name AS state_name, s.slug AS state_slug,
                   d.name AS district_name,
                   (SELECT COUNT(*) FROM reviews r WHERE r.place_id = p.id) AS review_count,
                   (SELECT ROUND(AVG(r.rating), 1) FROM reviews r WHERE r.place_id = p.id) AS avg_rating
            FROM places p
            JOIN states s ON s.id = p.state_id
            LEFT JOIN districts d ON d.id = p.district_id
            WHERE p.deleted_at IS NULL
                  AND (p.name LIKE %s OR p.description LIKE %s
                  OR s.name LIKE %s OR d.name LIKE %s
                  OR p.category LIKE %s)
            ORDER BY
                CASE WHEN p.name LIKE %s THEN 0 ELSE 1 END,
                p.is_featured DESC,
                p.view_count DESC,
                p.created_at DESC
            LIMIT %s
        """, (q, q, q, q, q, q, limit))
        return cur.fetchall()


def search_all(query, limit=20):
    conn = get_db()
    try:
        cur = conn.cursor()
        q = f"%{_escape_like(query)}%"

        cur.execute("""
            SELECT s.*, COUNT(p.id) AS place_count
            FROM states s LEFT JOIN places p ON p.state_id = s.id
            WHERE s.name LIKE %s
            GROUP BY s.id ORDER BY s.name
        """, (q,))
        states = cur.fetchall()

        cur.execute("""
            SELECT d.*, s.name AS state_name, s.slug AS state_slug,
                   COUNT(DISTINCT b.id) AS block_count,
                   COUNT(DISTINCT pl.id) AS place_count
            FROM districts d
            JOIN states s ON s.id = d.state_id
            LEFT JOIN blocks b ON b.district_id = d.id
            LEFT JOIN places pl ON pl.district_id = d.id AND pl.deleted_at IS NULL
            WHERE d.name LIKE %s
            GROUP BY d.id
            ORDER BY d.name LIMIT %s
        """, (q, limit))
        districts = cur.fetchall()

        cur.execute("""
            SELECT b.*, d.name AS district_name, d.slug AS district_slug,
                   s.name AS state_name, s.slug AS state_slug,
                   COUNT(pl.id) AS place_count
            FROM blocks b
            JOIN districts d ON d.id = b.district_id
            JOIN states s ON s.id = d.state_id
            LEFT JOIN places pl ON pl.block_id = b.id AND pl.deleted_at IS NULL
            WHERE b.name LIKE %s
            GROUP BY b.id
            ORDER BY b.name LIMIT %s
        """, (q, limit))
        blocks = cur.fetchall()

        cur.execute("""
            SELECT p.*, s.name AS state_name, s.slug AS state_slug,
                   d.name AS district_name,
                   (SELECT COUNT(*) FROM reviews r WHERE r.place_id = p.id) AS review_count,
                   (SELECT ROUND(AVG(r.rating), 1) FROM reviews r WHERE r.place_id = p.id) AS avg_rating
            FROM places p
            JOIN states s ON s.id = p.state_id
            LEFT JOIN districts d ON d.id = p.district_id
            WHERE p.deleted_at IS NULL
                  AND (p.name LIKE %s OR p.description LIKE %s
                  OR s.name LIKE %s OR d.name LIKE %s
                  OR p.category LIKE %s)
            ORDER BY
                CASE WHEN p.name LIKE %s THEN 0 ELSE 1 END,
                p.is_featured DESC,
                p.view_count DESC,
                p.created_at DESC
            LIMIT %s
        """, (q, q, q, q, q, q, limit))
        places = cur.fetchall()

        cur.execute("""
            SELECT df.*, d.name AS district_name, d.slug AS district_slug,
                   s.slug AS state_slug, s.name AS state_name
            FROM district_foods df
            JOIN districts d ON d.id = df.district_id
            JOIN states s ON s.id = d.state_id
            WHERE df.name LIKE %s OR df.description LIKE %s
            ORDER BY df.name LIMIT %s
        """, (q, q, limit))
        foods = cur.fetchall()
        cur.close()

        return {
            'states': states,
            'districts': districts,
            'blocks': blocks,
            'places': places,
            'foods': foods,
        }
    finally:
        conn.close()


def search_places_simple(query, limit=10):
    """Simple search query returning basic place details for admin selectors."""
    q = f"%{_escape_like(query)}%"
    with get_cursor() as cur:
        cur.execute("""
            SELECT p.id, p.name, p.slug, d.name AS district_name
            FROM places p
            LEFT JOIN districts d ON p.district_id = d.id
            WHERE p.deleted_at IS NULL AND p.name LIKE %s
            ORDER BY p.name LIMIT %s
        """, (q, limit))
        return cur.fetchall()


def smart_search(query, limit=10):
    import re as _re
    clean = _re.sub(r'(?i)(i am going to|going to|visiting|visit|explore|show me)\s*', '', query).strip()
    if not clean:
        clean = query.strip()

    conn = get_db()
    try:
        cur = conn.cursor()
        q = f"%{_escape_like(clean)}%"

        cur.execute("""
            SELECT p.*, s.name AS state_name, s.slug AS state_slug,
                d.name AS district_name
            FROM places p
            JOIN states s ON s.id = p.state_id
            LEFT JOIN districts d ON d.id = p.district_id
            WHERE p.deleted_at IS NULL
              AND (p.name LIKE %s OR d.name LIKE %s OR p.description LIKE %s)
            ORDER BY
                CASE WHEN d.name LIKE %s THEN 0
                     WHEN p.name LIKE %s THEN 1
                     ELSE 2 END,
                p.is_featured DESC
            LIMIT %s
        """, (q, q, q, q, q, limit))
        places = cur.fetchall()

        cur.execute("""
            SELECT df.*, d.name AS district_name
            FROM district_foods df
            JOIN districts d ON d.id = df.district_id
            WHERE d.name LIKE %s OR df.name LIKE %s
            LIMIT %s
        """, (q, q, limit))
        foods = cur.fetchall()

        cur.execute("""
            SELECT a.*, p.name AS place_name
            FROM accommodations a
            JOIN places p ON p.id = a.place_id
            LEFT JOIN districts d ON d.id = p.district_id
            WHERE d.name LIKE %s OR p.name LIKE %s
            LIMIT %s
        """, (q, q, limit))
        hotels = cur.fetchall()

        cur.close()
        return {
            'query': clean,
            'places': places,
            'foods': foods,
            'hotels': hotels,
        }
    finally:
        conn.close()


nl_search = smart_search


def get_nearby_places(lat, lng, radius_km=50, limit=10, exclude_id=None, district_id=None):
    lat = float(lat)
    lng = float(lng)
    cos_lat = math.cos(math.radians(lat))
    lat_range = radius_km / 111.0
    lng_range = radius_km / (111.0 * max(0.01, cos_lat))

    query = """
        SELECT p.*, s.name AS state_name, s.slug AS state_slug,
            d.name AS district_name,
            ((p.latitude - %s) * (p.latitude - %s) +
             (p.longitude - %s) * (p.longitude - %s) * %s * %s) AS dist_sq
        FROM places p
        JOIN states s ON s.id = p.state_id
        LEFT JOIN districts d ON d.id = p.district_id
        WHERE p.latitude BETWEEN %s AND %s
          AND p.longitude BETWEEN %s AND %s
          AND p.latitude IS NOT NULL
          AND p.deleted_at IS NULL
    """
    params = [lat, lat, lng, lng, cos_lat, cos_lat,
              float(lat) - lat_range, float(lat) + lat_range,
              float(lng) - lng_range, float(lng) + lng_range]

    if exclude_id:
        query += " AND p.id != %s"
        params.append(exclude_id)

    if district_id:
        query += " ORDER BY (CASE WHEN p.district_id = %s THEN 0 ELSE 1 END), dist_sq LIMIT %s"
        params.extend([district_id, limit])
    else:
        query += " ORDER BY dist_sq LIMIT %s"
        params.append(limit)

    with get_cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()

    result = list(rows)
    for p in result:
        if p.get('latitude') and p.get('longitude'):
            dlat = math.radians(float(p['latitude']) - float(lat))
            dlng = math.radians(float(p['longitude']) - float(lng))
            a = math.sin(dlat/2)**2 + math.cos(math.radians(float(lat))) * math.cos(math.radians(float(p['latitude']))) * math.sin(dlng/2)**2
            p['distance_km'] = round(6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)), 1)
        else:
            p['distance_km'] = None
    return result


def get_places_for_map(category=None, state_id=None):
    with get_cursor() as cur:
        query = """
            SELECT p.id, p.name, p.slug, p.category, p.state_id,
                   p.latitude, p.longitude,
                   p.cover_image, p.is_featured, p.is_hidden_gem, p.best_time_to_visit,
                   p.best_season, p.maps_link,
                   s.name AS state_name, s.slug AS state_slug,
                   d.id AS district_id, d.name AS district_name,
                   COALESCE(ROUND(AVG(r.rating), 1), 4.5) AS avg_rating,
                   COUNT(r.id) AS review_count
            FROM places p
            JOIN states s ON s.id = p.state_id
            LEFT JOIN districts d ON d.id = p.district_id
            LEFT JOIN reviews r ON r.place_id = p.id
            WHERE p.latitude IS NOT NULL AND p.longitude IS NOT NULL
                  AND p.deleted_at IS NULL
        """
        params = []
        if category:
            query += " AND p.category = %s"
            params.append(category)
        if state_id:
            query += " AND p.state_id = %s"
            params.append(state_id)
        query += " GROUP BY p.id ORDER BY p.is_featured DESC, p.name"
        cur.execute(query, params)
        return cur.fetchall()
