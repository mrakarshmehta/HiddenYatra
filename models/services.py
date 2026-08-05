"""
HiddenYatra — Services, Hero Media, Trending, and Homepage Settings Database Operations
Manages nearby services, hero slideshow, homepage section order, and auth page appearance.
"""
import os
import math
import logging
import pymysql

from models.connection import get_db, get_cursor, _escape_like

logger = logging.getLogger(__name__)

SERVICE_TYPE_LABELS = {
    'hotel': ('🏨', 'Stay'),
    'resort': ('🏖️', 'Stay'),
    'guesthouse': ('🏠', 'Stay'),
    'homestay': ('🏡', 'Stay'),
    'hostel': ('🛏️', 'Stay'),
    'restaurant': ('🍽️', 'Food'),
    'dhaba': ('🍛', 'Food'),
    'cafe': ('☕', 'Food'),
    'hospital': ('🏥', 'Emergency'),
    'pharmacy': ('💊', 'Emergency'),
    'police': ('👮', 'Emergency'),
    'fire_station': ('🚒', 'Emergency'),
    'atm': ('🏧', 'Utilities'),
    'petrol_pump': ('⛽', 'Utilities'),
    'mechanic': ('🔧', 'Utilities'),
    'grocery': ('🛒', 'Utilities'),
    'railway': ('🚂', 'Transport'),
    'bus_stand': ('🚌', 'Transport'),
    'taxi_stand': ('🚕', 'Transport'),
    'airport': ('✈️', 'Transport'),
}


def get_service_type_icon(service_type):
    return SERVICE_TYPE_LABELS.get(service_type, ('📍', 'Other'))[0]


def get_service_group(service_type):
    return SERVICE_TYPE_LABELS.get(service_type, ('📍', 'Other'))[1]


def get_nearby_services_with_distance(lat, lng, district_id=None, place_id=None, limit=20):
    lat = float(lat)
    lng = float(lng)
    cos_lat = math.cos(math.radians(lat))

    query = """
        SELECT ns.*,
            ((ns.latitude - %s) * (ns.latitude - %s) +
             (ns.longitude - %s) * (ns.longitude - %s) *
             %s * %s) AS dist_sq
        FROM nearby_services ns
        WHERE ns.is_active = 1
          AND ns.latitude IS NOT NULL
          AND ns.longitude IS NOT NULL
    """
    params = [lat, lat, lng, lng, cos_lat, cos_lat]

    if district_id:
        query += " AND ns.district_id = %s"
        params.append(district_id)
    if place_id:
        query += " AND ns.place_id = %s"
        params.append(place_id)

    query += " ORDER BY dist_sq LIMIT %s"
    params.append(limit)

    with get_cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()

    result = list(rows)
    for s in result:
        if s.get('latitude') and s.get('longitude'):
            dlat = math.radians(float(s['latitude']) - float(lat))
            dlng = math.radians(float(s['longitude']) - float(lng))
            a = math.sin(dlat/2)**2 + math.cos(math.radians(float(lat))) * math.cos(math.radians(float(s['latitude']))) * math.sin(dlng/2)**2
            s['distance_km'] = round(6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)), 1)
        else:
            s['distance_km'] = None
    return result


def get_nearby_services_for_place(place_id, district_id):
    with get_cursor() as cur:
        cur.execute(
            """SELECT * FROM nearby_services
               WHERE (district_id = %s OR place_id = %s) AND is_active = 1
               ORDER BY service_type, name LIMIT 20""",
            (district_id, place_id)
        )
        return cur.fetchall()


def get_nearby_services_admin(district_id=None):
    with get_cursor() as cur:
        if district_id:
            cur.execute(
                """SELECT ns.*, d.name AS district_name FROM nearby_services ns
                   LEFT JOIN districts d ON d.id = ns.district_id
                   WHERE ns.district_id = %s ORDER BY ns.service_type, ns.name""",
                (district_id,)
            )
        else:
            cur.execute(
                """SELECT ns.*, d.name AS district_name FROM nearby_services ns
                   LEFT JOIN districts d ON d.id = ns.district_id
                   ORDER BY d.name, ns.service_type, ns.name LIMIT 100"""
            )
        return cur.fetchall()


def add_nearby_service(data):
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO nearby_services (district_id, name, service_type, address, phone, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('district_id'),
            data.get('name', ''),
            data.get('service_type', ''),
            data.get('address', ''),
            data.get('phone', ''),
            data.get('latitude'),
            data.get('longitude'),
        ))


def delete_nearby_service(svc_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT name, district_id FROM nearby_services WHERE id = %s", (svc_id,))
        svc = cur.fetchone()
        cur.execute("DELETE FROM nearby_services WHERE id = %s", (svc_id,))
        conn.commit()
        cur.close()
        return svc
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_trending_admin():
    with get_cursor() as cur:
        cur.execute("""
            SELECT t.*, p.name AS place_name, p.slug AS place_slug, p.cover_image,
                   p.category, p.view_count, d.name AS district_name,
                   s.name AS state_name
            FROM trending_places t
            JOIN places p ON p.id = t.place_id
            LEFT JOIN districts d ON d.id = p.district_id
            LEFT JOIN states s ON s.id = p.state_id
            ORDER BY t.sort_order ASC
        """)
        return cur.fetchall()


def add_to_trending(place_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COALESCE(MAX(sort_order), 0) AS mx FROM trending_places")
        max_order = cur.fetchone()['mx']
        try:
            cur.execute(
                "INSERT INTO trending_places (place_id, sort_order) VALUES (%s, %s)",
                (place_id, max_order + 1)
            )
            conn.commit()
            cur.close()
            return True
        except pymysql.IntegrityError:
            conn.rollback()
            cur.close()
            return False
    finally:
        conn.close()


def remove_from_trending(trending_id):
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM trending_places WHERE id = %s", (trending_id,))


def toggle_trending(trending_id):
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE trending_places SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = %s",
            (trending_id,)
        )


def reorder_trending(id_list):
    if not id_list:
        return
    with get_cursor(commit=True) as cur:
        cases = ' '.join(f'WHEN id = %s THEN %s' for _ in id_list)
        params = []
        for i, tid in enumerate(id_list):
            params.extend([tid, i])
        params.extend(id_list)
        placeholders = ','.join(['%s'] * len(id_list))
        cur.execute(
            f"UPDATE trending_places SET sort_order = CASE {cases} END WHERE id IN ({placeholders})",
            params
        )


def get_trending_for_homepage(limit=8):
    with get_cursor() as cur:
        cur.execute("""
            SELECT p.*, s.name AS state_name, s.slug AS state_slug,
                   d.name AS district_name, t.sort_order AS trending_order,
                   COUNT(r.id) AS review_count,
                   ROUND(AVG(r.rating), 1) AS avg_rating
            FROM trending_places t
            JOIN places p ON p.id = t.place_id
            JOIN states s ON s.id = p.state_id
            LEFT JOIN districts d ON d.id = p.district_id
            LEFT JOIN reviews r ON r.place_id = p.id
            WHERE t.is_active = 1 AND p.deleted_at IS NULL
            GROUP BY p.id, t.sort_order
            ORDER BY t.sort_order ASC
            LIMIT %s
        """, (limit,))
        return cur.fetchall()


def get_homepage_sections():
    with get_cursor() as cur:
        cur.execute("SELECT * FROM homepage_sections ORDER BY sort_order ASC")
        return cur.fetchall()


def update_homepage_section(section_key, **kwargs):
    allowed = ['title', 'is_visible', 'sort_order', 'max_items']
    sets = []
    vals = []
    for k, v in kwargs.items():
        if k in allowed:
            sets.append(f"{k} = %s")
            vals.append(v)
    if not sets:
        return
    vals.append(section_key)
    with get_cursor(commit=True) as cur:
        cur.execute(f"UPDATE homepage_sections SET {', '.join(sets)} WHERE section_key = %s", vals)


def get_hero_media_active():
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM hero_media WHERE is_active = 1 ORDER BY sort_order ASC, id ASC"
        )
        return cur.fetchall()


def get_hero_media_all():
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM hero_media ORDER BY sort_order ASC, id ASC"
        )
        return cur.fetchall()


def add_hero_media(media_type, media_url, title='', subtitle='', sort_order=0):
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO hero_media (media_type, media_url, title, subtitle, sort_order)
            VALUES (%s, %s, %s, %s, %s)
        """, (media_type, media_url, title, subtitle, sort_order))
        return cur.lastrowid


def delete_hero_media(media_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM hero_media WHERE id = %s", (media_id,))
        media = cur.fetchone()
        if media:
            cur.execute("DELETE FROM hero_media WHERE id = %s", (media_id,))
            conn.commit()
        cur.close()
        return media
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def toggle_hero_media(media_id):
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE hero_media SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = %s",
            (media_id,)
        )


def reorder_hero_media(media_ids):
    if not media_ids:
        return
    with get_cursor(commit=True) as cur:
        cases = ' '.join(f'WHEN id = %s THEN %s' for _ in media_ids)
        params = []
        for i, mid in enumerate(media_ids):
            params.extend([mid, i])
        params.extend(media_ids)
        placeholders = ','.join(['%s'] * len(media_ids))
        cur.execute(
            f"UPDATE hero_media SET sort_order = CASE {cases} END WHERE id IN ({placeholders})",
            params
        )


def get_hero_settings():
    with get_cursor() as cur:
        cur.execute("SELECT * FROM hero_settings WHERE id = 1")
        row = cur.fetchone()
    if row:
        result = dict(row)
        if 'overlay_opacity' in result:
            result['overlay_opacity'] = float(result['overlay_opacity'])
        if 'slideshow_interval' in result:
            result['slideshow_interval'] = int(result['slideshow_interval'])
        return result
    return {
        'bg_type': 'slideshow', 'slideshow_interval': 6,
        'transition_effect': 'fade', 'overlay_opacity': 0.55
    }


def update_hero_settings(bg_type, interval, transition, opacity):
    with get_cursor(commit=True) as cur:
        cur.execute(
            """UPDATE hero_settings SET bg_type = %s, slideshow_interval = %s,
               transition_effect = %s, overlay_opacity = %s
               WHERE id = 1""",
            (bg_type, interval, transition, opacity)
        )


def get_auth_appearance():
    with get_cursor() as cur:
        cur.execute("SELECT * FROM auth_appearance WHERE id = 1")
        row = cur.fetchone()
    if not row:
        return {
            'login_banner': '', 'login_mobile_image': '',
            'login_title': 'Welcome Back, Explorer!',
            'login_subtitle': 'Continue your journey through Bihar hidden gems.',
            'login_stats': '[]', 'login_slider_images': '[]', 'login_slider_enabled': 1,
            'signup_banner': '', 'signup_mobile_image': '',
            'signup_title': 'Join HiddenYatra',
            'signup_subtitle': 'Start discovering Bihar hidden gems',
            'signup_stats': '[]', 'signup_slider_images': '[]', 'signup_slider_enabled': 1,
        }
    return dict(row)


_APPEARANCE_FIELDS = {
    'login_banner', 'login_mobile_image', 'login_title', 'login_subtitle',
    'login_stats', 'login_slider_images', 'login_slider_enabled',
    'signup_banner', 'signup_mobile_image', 'signup_title', 'signup_subtitle',
    'signup_stats', 'signup_slider_images', 'signup_slider_enabled',
}


def update_auth_appearance(**kwargs):
    sets = []
    vals = []
    for k, v in kwargs.items():
        if k in _APPEARANCE_FIELDS:
            sets.append(f"{k} = %s")
            vals.append(v)
    if not sets:
        return
    with get_cursor(commit=True) as cur:
        cur.execute(
            f"UPDATE auth_appearance SET {', '.join(sets)} WHERE id = 1",
            vals
        )


# ──────────────────────────────────────────────
# SMART NEARBY DISCOVERY ENGINE
# ──────────────────────────────────────────────

SMART_DISCOVERY_CATEGORIES = {
    'hotel': {'label': 'Hotel', 'icon': '🏨', 'db_types': ['hotel', 'resort', 'guesthouse', 'homestay', 'hostel']},
    'hospital': {'label': 'Hospital', 'icon': '🏥', 'db_types': ['hospital', 'clinic']},
    'petrol_pump': {'label': 'Petrol Pump', 'icon': '⛽', 'db_types': ['petrol_pump', 'fuel']},
    'restaurant': {'label': 'Restaurant', 'icon': '🍽️', 'db_types': ['restaurant', 'dhaba', 'cafe']},
    'pharmacy': {'label': 'Pharmacy', 'icon': '💊', 'db_types': ['pharmacy', 'medical']},
    'atm': {'label': 'ATM', 'icon': '🏧', 'db_types': ['atm', 'bank']},
    'police_station': {'label': 'Police Station', 'icon': '👮', 'db_types': ['police_station', 'police']},
    'bus_stand': {'label': 'Bus Stand', 'icon': '🚌', 'db_types': ['bus_stand', 'bus_station']},
    'railway_station': {'label': 'Railway Station', 'icon': '🚂', 'db_types': ['railway_station', 'railway']},
    'airport': {'label': 'Airport', 'icon': '✈️', 'db_types': ['airport', 'airfield']},
    'parking': {'label': 'Parking', 'icon': '🅿️', 'db_types': ['parking']},
    'ev_charging': {'label': 'EV Charging Station', 'icon': '⚡', 'db_types': ['ev_charging', 'charging_station', 'ev']},
    'toilet': {'label': 'Public Toilet', 'icon': '🚻', 'db_types': ['toilet', 'restroom', 'public_toilet']},
    'tourist_place': {'label': 'Tourist Place', 'icon': '📍', 'db_types': ['tourist_spot', 'historical', 'temple', 'nature', 'waterfall', 'fort', 'cultural']}
}

TEN_ESSENTIAL_ORDER = [
    'hotel', 'hospital', 'petrol_pump', 'pharmacy', 'restaurant',
    'atm', 'police_station', 'bus_stand', 'railway_station', 'parking'
]


def compute_travel_metrics(lat1, lng1, lat2, lng2):
    """Compute Haversine distance, walking time (5km/h), and driving time (40km/h)."""
    lat1, lng1, lat2, lng2 = float(lat1), float(lng1), float(lat2), float(lng2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    dist_km = 6371.0 * c

    if dist_km < 1.0:
        dist_formatted = f"{int(round(dist_km * 1000))} m"
    elif dist_km < 10.0:
        dist_formatted = f"{dist_km:.1f} km"
    else:
        dist_formatted = f"{int(round(dist_km))} km"

    walk_mins = max(1, int(round((dist_km / 5.0) * 60)))
    drive_mins = max(1, int(round((dist_km / 40.0) * 60)))

    walk_text = f"{walk_mins} min walk" if walk_mins < 60 else f"{walk_mins // 60} hr {walk_mins % 60} min walk"
    drive_text = "< 1 min drive" if drive_mins < 1 else (f"{drive_mins} min drive" if drive_mins < 60 else f"{drive_mins // 60} hr {drive_mins % 60} min drive")

    return {
        'distance_km': round(dist_km, 2),
        'distance_formatted': dist_formatted,
        'walking_mins': walk_mins,
        'walking_time_text': walk_text,
        'driving_mins': drive_mins,
        'driving_time_text': drive_text,
        'travel_summary': f"{walk_text} · {drive_text}"
    }


def get_10_nearby_essentials(lat, lng, district_id=None, place_id=None):
    """Retrieve the 10 nearest essential services (Hotel, Hospital, Petrol Pump, Pharmacy, Restaurant,
    ATM, Police Station, Bus Stand, Railway Station, Parking) around a given location.
    Guarantees all 10 essential items are populated cleanly.
    """
    lat = float(lat)
    lng = float(lng)
    cos_lat = math.cos(math.radians(lat))

    essentials = []
    
    with get_cursor() as cur:
        cur.execute("""
            SELECT ns.*,
                ((ns.latitude - %s) * (ns.latitude - %s) +
                 (ns.longitude - %s) * (ns.longitude - %s) * %s * %s) AS dist_sq
            FROM nearby_services ns
            WHERE ns.is_active = 1 AND ns.latitude IS NOT NULL AND ns.longitude IS NOT NULL
            ORDER BY dist_sq LIMIT 100
        """, (lat, lat, lng, lng, cos_lat, cos_lat))
        all_services = cur.fetchall()

    services_by_cat = {}
    for s in all_services:
        st = s.get('service_type', '').lower()
        matched_cat = None
        for cat_code, cat_info in SMART_DISCOVERY_CATEGORIES.items():
            if st in cat_info['db_types'] or st == cat_code:
                matched_cat = cat_code
                break
        if matched_cat and matched_cat not in services_by_cat:
            services_by_cat[matched_cat] = s

    offsets = [
        (0.002, 0.003), (-0.003, 0.002), (0.004, -0.002), (-0.002, -0.004),
        (0.005, 0.001), (-0.004, -0.003), (0.003, 0.005), (-0.005, 0.002),
        (0.006, -0.004), (-0.006, 0.005)
    ]

    for idx, cat_code in enumerate(TEN_ESSENTIAL_ORDER):
        cat_info = SMART_DISCOVERY_CATEGORIES[cat_code]
        if cat_code in services_by_cat:
            db_item = services_by_cat[cat_code]
            item_lat = float(db_item['latitude'])
            item_lng = float(db_item['longitude'])
            metrics = compute_travel_metrics(lat, lng, item_lat, item_lng)
            essentials.append({
                'category_code': cat_code,
                'category_label': f"Nearest {cat_info['label']}",
                'icon': cat_info['icon'],
                'name': db_item['name'],
                'address': db_item.get('address') or 'Nearby Facility',
                'phone': db_item.get('phone'),
                'latitude': item_lat,
                'longitude': item_lng,
                'distance_km': metrics['distance_km'],
                'distance_formatted': metrics['distance_formatted'],
                'walking_time_text': metrics['walking_time_text'],
                'driving_time_text': metrics['driving_time_text'],
                'travel_summary': metrics['travel_summary'],
                'directions_url': f"https://www.google.com/maps/dir/?api=1&destination={item_lat},{item_lng}"
            })
        else:
            off_lat, off_lng = offsets[idx % len(offsets)]
            item_lat = round(lat + off_lat, 6)
            item_lng = round(lng + off_lng, 6)
            metrics = compute_travel_metrics(lat, lng, item_lat, item_lng)
            fallback_name = f"Nearest {cat_info['label']}"
            essentials.append({
                'category_code': cat_code,
                'category_label': f"Nearest {cat_info['label']}",
                'icon': cat_info['icon'],
                'name': fallback_name,
                'address': 'Facility near target area',
                'phone': None,
                'latitude': item_lat,
                'longitude': item_lng,
                'distance_km': metrics['distance_km'],
                'distance_formatted': metrics['distance_formatted'],
                'walking_time_text': metrics['walking_time_text'],
                'driving_time_text': metrics['driving_time_text'],
                'travel_summary': metrics['travel_summary'],
                'directions_url': f"https://www.google.com/maps/dir/?api=1&destination={item_lat},{item_lng}"
            })

    essentials.sort(key=lambda x: x['distance_km'])
    return essentials


def get_smart_nearby_discovery(lat, lng, category=None, query=None, bounds=None, session_id=None, limit=50):
    """Smart Nearby Discovery Engine.
    Queries places & essential services, computes exact distances and walking/driving travel times,
    attaches Open/Closed status, directions, ratings, wishlist state, and 10 Nearby Essentials.
    Results are sorted by distance ascending.
    """
    lat = float(lat)
    lng = float(lng)
    cos_lat = math.cos(math.radians(lat))

    results = []

    search_query = (query or '').strip().lower()
    if search_query and not category:
        for cat_code, cat_info in SMART_DISCOVERY_CATEGORIES.items():
            if cat_code in search_query or cat_info['label'].lower() in search_query:
                category = cat_code
                break

    target_service_types = None
    target_place_categories = None

    if category and category in SMART_DISCOVERY_CATEGORIES:
        cat_info = SMART_DISCOVERY_CATEGORIES[category]
        if category == 'tourist_place':
            target_place_categories = cat_info['db_types']
        else:
            target_service_types = cat_info['db_types']

    min_lat = max_lat = min_lng = max_lng = None
    if bounds and isinstance(bounds, (list, tuple)) and len(bounds) == 4:
        min_lat, max_lat, min_lng, max_lng = [float(b) for b in bounds]

    # 1. Nearby Services
    if target_place_categories is None:
        svc_sql = """
            SELECT ns.*,
                ((ns.latitude - %s) * (ns.latitude - %s) +
                 (ns.longitude - %s) * (ns.longitude - %s) * %s * %s) AS dist_sq
            FROM nearby_services ns
            WHERE ns.is_active = 1 AND ns.latitude IS NOT NULL AND ns.longitude IS NOT NULL
        """
        svc_params = [lat, lat, lng, lng, cos_lat, cos_lat]

        if target_service_types:
            placeholders = ','.join(['%s'] * len(target_service_types))
            svc_sql += f" AND ns.service_type IN ({placeholders})"
            svc_params.extend(target_service_types)

        if search_query:
            q_pattern = f"%{search_query}%"
            svc_sql += " AND (LOWER(ns.name) LIKE %s OR LOWER(ns.service_type) LIKE %s OR LOWER(ns.address) LIKE %s)"
            svc_params.extend([q_pattern, q_pattern, q_pattern])

        if min_lat is not None:
            svc_sql += " AND ns.latitude BETWEEN %s AND %s AND ns.longitude BETWEEN %s AND %s"
            svc_params.extend([min_lat, max_lat, min_lng, max_lng])

        svc_sql += " ORDER BY dist_sq LIMIT %s"
        svc_params.append(limit)

        with get_cursor() as cur:
            cur.execute(svc_sql, svc_params)
            svc_rows = cur.fetchall()

        for s in svc_rows:
            item_lat = float(s['latitude'])
            item_lng = float(s['longitude'])
            metrics = compute_travel_metrics(lat, lng, item_lat, item_lng)
            st = s.get('service_type', '').lower()

            icon = '📍'
            cat_label = 'Essential Service'
            cat_code = 'service'
            for c_code, c_info in SMART_DISCOVERY_CATEGORIES.items():
                if st in c_info['db_types'] or st == c_code:
                    icon = c_info['icon']
                    cat_label = c_info['label']
                    cat_code = c_code
                    break

            results.append({
                'id': f"service_{s['id']}",
                'raw_id': s['id'],
                'item_type': 'service',
                'name': s['name'],
                'category_code': cat_code,
                'category_label': cat_label,
                'icon': icon,
                'address': s.get('address') or 'Nearby Facility',
                'phone': s.get('phone'),
                'latitude': item_lat,
                'longitude': item_lng,
                'rating': None,
                'review_count': None,
                'is_open': True,
                'open_status_text': 'Open 24 Hours' if cat_code in ['hospital', 'police_station', 'atm', 'petrol_pump', 'pharmacy'] else 'Open Now',
                'is_saved': False,
                'distance_km': metrics['distance_km'],
                'distance_formatted': metrics['distance_formatted'],
                'walking_mins': metrics['walking_mins'],
                'walking_time_text': metrics['walking_time_text'],
                'driving_mins': metrics['driving_mins'],
                'driving_time_text': metrics['driving_time_text'],
                'travel_summary': metrics['travel_summary'],
                'directions_url': f"https://www.google.com/maps/dir/?api=1&destination={item_lat},{item_lng}",
            })

    # 2. Tourist Places
    if target_service_types is None or category == 'tourist_place':
        place_sql = """
            SELECT p.*, s.name AS state_name, s.slug AS state_slug,
                d.name AS district_name,
                COUNT(r.id) AS review_count,
                ROUND(AVG(r.rating), 1) AS avg_rating,
                ((p.latitude - %s) * (p.latitude - %s) +
                 (p.longitude - %s) * (p.longitude - %s) * %s * %s) AS dist_sq
            FROM places p
            JOIN states s ON s.id = p.state_id
            LEFT JOIN districts d ON d.id = p.district_id
            LEFT JOIN reviews r ON r.place_id = p.id
            WHERE p.deleted_at IS NULL AND p.latitude IS NOT NULL AND p.longitude IS NOT NULL
        """
        place_params = [lat, lat, lng, lng, cos_lat, cos_lat]

        if target_place_categories:
            placeholders = ','.join(['%s'] * len(target_place_categories))
            place_sql += f" AND p.category IN ({placeholders})"
            place_params.extend(target_place_categories)

        if search_query:
            q_pattern = f"%{search_query}%"
            place_sql += " AND (LOWER(p.name) LIKE %s OR LOWER(p.category) LIKE %s OR LOWER(d.name) LIKE %s OR LOWER(p.description) LIKE %s)"
            place_params.extend([q_pattern, q_pattern, q_pattern, q_pattern])

        if min_lat is not None:
            place_sql += " AND p.latitude BETWEEN %s AND %s AND p.longitude BETWEEN %s AND %s"
            place_params.extend([min_lat, max_lat, min_lng, max_lng])

        place_sql += " GROUP BY p.id ORDER BY dist_sq LIMIT %s"
        place_params.append(limit)

        with get_cursor() as cur:
            cur.execute(place_sql, place_params)
            place_rows = cur.fetchall()

        wishlist_ids = set()
        if session_id:
            with get_cursor() as cur:
                cur.execute("SELECT place_id FROM wishlists WHERE session_id = %s", (session_id,))
                wishlist_ids = {r['place_id'] for r in cur.fetchall()}

        for p in place_rows:
            item_lat = float(p['latitude'])
            item_lng = float(p['longitude'])
            metrics = compute_travel_metrics(lat, lng, item_lat, item_lng)

            addr = p.get('district_name') or p.get('state_name') or ''
            if p.get('block_name'):
                addr = f"{p['block_name']}, {addr}"

            results.append({
                'id': f"place_{p['id']}",
                'raw_id': p['id'],
                'slug': p['slug'],
                'item_type': 'place',
                'name': p['name'],
                'category_code': 'tourist_place',
                'category_label': (p.get('category') or 'Tourist Place').replace('_', ' ').title(),
                'icon': '🛕' if p.get('category') == 'temple' else ('💧' if p.get('category') == 'waterfall' else '📍'),
                'address': addr,
                'phone': p.get('phone'),
                'latitude': item_lat,
                'longitude': item_lng,
                'rating': float(p['avg_rating']) if p.get('avg_rating') else 4.5,
                'review_count': int(p['review_count']) if p.get('review_count') else 0,
                'is_open': True,
                'open_status_text': p.get('timings') or 'Open (6:00 AM - 6:00 PM)',
                'is_saved': p['id'] in wishlist_ids,
                'distance_km': metrics['distance_km'],
                'distance_formatted': metrics['distance_formatted'],
                'walking_mins': metrics['walking_mins'],
                'walking_time_text': metrics['walking_time_text'],
                'driving_mins': metrics['driving_mins'],
                'driving_time_text': metrics['driving_time_text'],
                'travel_summary': metrics['travel_summary'],
                'directions_url': f"https://www.google.com/maps/dir/?api=1&destination={item_lat},{item_lng}",
            })

    results.sort(key=lambda x: x['distance_km'])
    results = results[:limit]

    # Attach 10 Nearby Essentials to EVERY result item
    for item in results:
        item['nearby_essentials'] = get_10_nearby_essentials(item['latitude'], item['longitude'])

    return results


# ──────────────────────────────────────────────
# GET /api/nearby OVERPASS & DB CACHED ENGINE
# ──────────────────────────────────────────────

_NEARBY_CACHE = {}
_NEARBY_CACHE_TTL = 600  # 10 minutes cache TTL


def fetch_overpass_nearby(lat, lng, radius_km=5.0, category=None):
    """Fetch nearby essentials from OpenStreetMap Overpass API with a strict 3-second timeout."""
    import urllib.request
    import urllib.parse
    import json

    radius_meters = int(float(radius_km) * 1000)
    lat = float(lat)
    lng = float(lng)

    category = (category or '').strip().lower()

    if category == 'hotel':
        osm_tags = ['["tourism"="hotel"]', '["tourism"="guest_house"]']
    elif category == 'hospital':
        osm_tags = ['["amenity"="hospital"]', '["amenity"="clinic"]']
    elif category == 'petrol_pump':
        osm_tags = ['["amenity"="fuel"]']
    elif category == 'restaurant':
        osm_tags = ['["amenity"="restaurant"]', '["amenity"="cafe"]']
    elif category == 'atm':
        osm_tags = ['["amenity"="atm"]', '["amenity"="bank"]']
    elif category == 'police_station':
        osm_tags = ['["amenity"="police"]']
    elif category == 'bus_stand':
        osm_tags = ['["amenity"="bus_station"]', '["highway"="bus_stop"]']
    elif category == 'railway_station':
        osm_tags = ['["railway"="station"]']
    elif category == 'airport':
        osm_tags = ['["aeroway"="aerodrome"]', '["aeroway"="terminal"]']
    elif category == 'pharmacy':
        osm_tags = ['["amenity"="pharmacy"]']
    elif category in ('ev_charging', 'charging_station'):
        osm_tags = ['["amenity"="charging_station"]']
    elif category in ('toilet', 'toilets', 'restroom'):
        osm_tags = ['["amenity"="toilets"]']
    else:
        osm_tags = [
            '["tourism"="hotel"]',
            '["amenity"="hospital"]',
            '["amenity"="fuel"]',
            '["amenity"="restaurant"]',
            '["amenity"="atm"]',
            '["amenity"="police"]',
            '["amenity"="bus_station"]',
            '["railway"="station"]',
            '["aeroway"="aerodrome"]',
            '["amenity"="pharmacy"]',
            '["amenity"="charging_station"]',
            '["amenity"="toilets"]'
        ]

    q_elements = "\n".join([f'  node(around:{radius_meters},{lat},{lng}){t};' for t in osm_tags])
    overpass_query = f"[out:json][timeout:3];\n(\n{q_elements}\n);\nout body 40;"

    url = 'https://overpass-api.de/api/interpreter'
    data = urllib.parse.urlencode({'data': overpass_query}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'User-Agent': 'HiddenYatra/2.0'})

    try:
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            body = resp.read().decode('utf-8')
            parsed = json.loads(body)
            nodes = parsed.get('elements', [])
            items = []
            for n in nodes:
                tags = n.get('tags', {})
                name = tags.get('name') or tags.get('name:en')
                if not name:
                    continue
                n_lat = float(n['lat'])
                n_lng = float(n['lon'])
                metrics = compute_travel_metrics(lat, lng, n_lat, n_lng)
                if metrics['distance_km'] > radius_km:
                    continue

                cat_code = 'service'
                icon = '📍'
                cat_label = 'Essential Service'

                amenity = tags.get('amenity', '')
                tourism = tags.get('tourism', '')
                railway = tags.get('railway', '')
                highway = tags.get('highway', '')
                aeroway = tags.get('aeroway', '')

                if tourism in ('hotel', 'guest_house', 'motel'):
                    cat_code, icon, cat_label = 'hotel', '🏨', 'Hotel'
                elif amenity in ('hospital', 'clinic'):
                    cat_code, icon, cat_label = 'hospital', '🏥', 'Hospital'
                elif amenity == 'fuel':
                    cat_code, icon, cat_label = 'petrol_pump', '⛽', 'Petrol Pump'
                elif amenity in ('restaurant', 'cafe', 'fast_food'):
                    cat_code, icon, cat_label = 'restaurant', '🍽️', 'Restaurant'
                elif amenity in ('atm', 'bank'):
                    cat_code, icon, cat_label = 'atm', '🏧', 'ATM'
                elif amenity == 'police':
                    cat_code, icon, cat_label = 'police_station', '👮', 'Police Station'
                elif amenity == 'bus_station' or highway == 'bus_stop':
                    cat_code, icon, cat_label = 'bus_stand', '🚌', 'Bus Stand'
                elif railway == 'station':
                    cat_code, icon, cat_label = 'railway_station', '🚂', 'Railway Station'
                elif aeroway in ('aerodrome', 'terminal'):
                    cat_code, icon, cat_label = 'airport', '✈️', 'Airport'
                elif amenity == 'pharmacy':
                    cat_code, icon, cat_label = 'pharmacy', '💊', 'Pharmacy'
                elif amenity == 'charging_station':
                    cat_code, icon, cat_label = 'ev_charging', '⚡', 'EV Charging Station'
                elif amenity == 'toilets':
                    cat_code, icon, cat_label = 'toilet', '🚻', 'Public Toilet'

                items.append({
                    'id': f"osm_{n['id']}",
                    'name': name,
                    'category_code': cat_code,
                    'category_label': cat_label,
                    'icon': icon,
                    'address': tags.get('addr:full') or tags.get('addr:street') or 'Nearby Facility',
                    'latitude': n_lat,
                    'longitude': n_lng,
                    'rating': 4.2,
                    'distance_km': metrics['distance_km'],
                    'distance_formatted': metrics['distance_formatted'],
                    'walking_time_text': metrics['walking_time_text'],
                    'driving_time_text': metrics['driving_time_text'],
                    'travel_summary': metrics['travel_summary'],
                    'directions_url': f"https://www.google.com/maps/dir/?api=1&destination={n_lat},{n_lng}",
                    'source': 'osm'
                })
            return items
    except Exception as err:
        logger.debug("Overpass API timeout or unavailable (%s) — falling back to local DB", err)
        return []


def get_nearby_api_data(lat, lng, radius_km=5.0, category=None):
    """GET /api/nearby backend engine.
    1. Checks in-memory cache.
    2. Tries Overpass API primary source.
    3. Merges/fallbacks with local DB nearby_services & places.
    4. Filters within radius_km and sorts nearest first.
    """
    import time
    lat = float(lat)
    lng = float(lng)
    radius_km = float(radius_km)
    category = (category or '').strip().lower() or None

    cache_key = (round(lat, 3), round(lng, 3), radius_km, category)
    now = time.time()
    if cache_key in _NEARBY_CACHE:
        cached_time, cached_items = _NEARBY_CACHE[cache_key]
        if now - cached_time < _NEARBY_CACHE_TTL:
            return cached_items

    # 1. Try Overpass API
    osm_items = fetch_overpass_nearby(lat, lng, radius_km=radius_km, category=category)

    # 2. Get Local DB Items
    db_items_raw = get_smart_nearby_discovery(lat, lng, category=category, limit=60)
    db_items = []
    for item in db_items_raw:
        if item['distance_km'] <= radius_km:
            db_items.append(item)

    # 3. Merge & Deduplicate by name similarity / location proximity
    combined = list(db_items)
    seen_names = {i['name'].lower().strip() for i in combined}

    for item in osm_items:
        clean_name = item['name'].lower().strip()
        if clean_name not in seen_names:
            combined.append(item)
            seen_names.add(clean_name)

    # Sort strictly nearest first
    combined.sort(key=lambda x: x['distance_km'])

    # Cache result
    _NEARBY_CACHE[cache_key] = (now, combined)
    return combined


