"""
HiddenYatra — Admin & Moderation Database Operations
Handles community submissions moderation, user photos approval, audit logs, and dashboard statistics.
"""
import os
import logging
from models.connection import get_db, get_cursor, _slugify
from config import SUBMISSION_UPLOAD

logger = logging.getLogger(__name__)


def submit_place(data):
    conn = get_db()
    try:
        cur = conn.cursor()
        submitter = ''
        if data.get('user_id'):
            cur.execute("SELECT display_name, username FROM users WHERE id = %s",
                        (data['user_id'],))
            user = cur.fetchone()
            if user:
                submitter = user['display_name'] or user['username']

        cur.execute("""
            INSERT INTO user_submissions
            (user_id, session_id, place_name, district_name, description,
             category, latitude, longitude, photos, submitter_name,
             best_time_to_visit, entry_fee, crowd_level, safety_level,
             short_description, local_tips, nearby_food, nearby_stay)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('user_id'),
            data.get('session_id', ''),
            data.get('place_name', ''),
            data.get('district_name', ''),
            data.get('description', ''),
            data.get('category', 'tourist_spot'),
            data.get('latitude'),
            data.get('longitude'),
            data.get('photos', ''),
            data.get('submitter_name', submitter or 'Anonymous'),
            data.get('best_time_to_visit', ''),
            data.get('entry_fee', ''),
            data.get('crowd_level', ''),
            data.get('safety_level', ''),
            data.get('short_description', ''),
            data.get('local_tips', ''),
            data.get('nearby_food', ''),
            data.get('nearby_stay', ''),
        ))
        conn.commit()
        sub_id = cur.lastrowid
        cur.close()
        return sub_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_user_submissions(session_id=None, user_id=None):
    with get_cursor() as cur:
        if user_id:
            cur.execute(
                "SELECT * FROM user_submissions WHERE user_id = %s ORDER BY created_at DESC",
                (user_id,)
            )
        else:
            cur.execute(
                "SELECT * FROM user_submissions WHERE session_id = %s ORDER BY created_at DESC",
                (session_id or '',)
            )
        return cur.fetchall()


def get_pending_submissions():
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM user_submissions WHERE status = 'pending' ORDER BY created_at DESC"
        )
        return cur.fetchall()


def get_all_submissions():
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM user_submissions ORDER BY created_at DESC"
        )
        return cur.fetchall()


def get_submission_by_id(sub_id):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM user_submissions WHERE id = %s", (sub_id,))
        return cur.fetchone()


def count_pending_submissions():
    with get_cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM user_submissions WHERE status = 'pending'"
        )
        return cur.fetchone()['cnt']


def delete_submission(sub_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT place_name, photos FROM user_submissions WHERE id = %s", (sub_id,))
        sub = cur.fetchone()
        cur.execute("DELETE FROM user_submissions WHERE id = %s", (sub_id,))
        conn.commit()
        cur.close()
        return sub
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def approve_submission(sub_id, admin_notes=''):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM user_submissions WHERE id = %s", (sub_id,))
        sub = cur.fetchone()
        if not sub:
            cur.close()
            return

        cur.execute(
            "UPDATE user_submissions SET status = 'approved', admin_notes = %s WHERE id = %s",
            (admin_notes, sub_id)
        )
        cur.execute("SELECT id FROM states WHERE slug = 'bihar'")
        bihar = cur.fetchone()
        state_id = bihar['id'] if bihar else 1
        district_id = None
        if sub.get('district_name'):
            cur.execute(
                "SELECT id FROM districts WHERE name = %s AND state_id = %s",
                (sub['district_name'], state_id)
            )
            dist = cur.fetchone()
            if dist:
                district_id = dist['id']

        slug = _slugify(sub['place_name'])
        cur.execute("SELECT id FROM places WHERE slug = %s", (slug,))
        existing = cur.fetchone()
        if not existing:
            cur.execute("""
                INSERT INTO places (state_id, district_id, name, slug, description, category,
                                    latitude, longitude, best_time_to_visit, entry_fee, travel_tips)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                state_id, district_id, sub['place_name'], slug,
                sub.get('description', ''), sub.get('category', 'tourist_spot'),
                sub.get('latitude'), sub.get('longitude'),
                sub.get('best_time_to_visit', ''),
                sub.get('entry_fee', ''),
                sub.get('local_tips', '')
            ))

        log_admin_action('approve', 'submission', sub_id, f"Approved place submission: {sub['place_name']}")
        conn.commit()
        cur.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def reject_submission(sub_id, admin_notes=''):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT photos FROM user_submissions WHERE id = %s", (sub_id,))
        sub = cur.fetchone()
        if sub and sub.get('photos'):
            for fn in sub['photos'].split(','):
                fn = fn.strip()
                if fn:
                    fpath = os.path.join(SUBMISSION_UPLOAD, fn)
                    if os.path.exists(fpath):
                        os.remove(fpath)
        cur.execute(
            "UPDATE user_submissions SET status = 'rejected', admin_notes = %s WHERE id = %s",
            (admin_notes, sub_id)
        )
        conn.commit()
        cur.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def find_duplicates_for_submission(sub_id):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM user_submissions WHERE id = %s", (sub_id,))
        sub = cur.fetchone()
        if not sub:
            return [], []

        name = sub['place_name'].strip()
        q = f"%{name}%"

        cur.execute(
            "SELECT id, name, slug, category FROM places WHERE deleted_at IS NULL AND name LIKE %s",
            (q,)
        )
        dup_places = cur.fetchall()

        cur.execute(
            "SELECT id, place_name, status, submitter_name FROM user_submissions WHERE id != %s AND place_name LIKE %s",
            (sub_id, q)
        )
        dup_subs = cur.fetchall()

        return dup_places, dup_subs


def get_filtered_submissions(status=None, has_duplicates=False):
    with get_cursor() as cur:
        query = "SELECT * FROM user_submissions"
        params = []
        if status:
            query += " WHERE status = %s"
            params.append(status)
        query += " ORDER BY created_at DESC"
        cur.execute(query, params)
        result = list(cur.fetchall())

    if has_duplicates:
        filtered = []
        for sub in result:
            dup_places, dup_subs = find_duplicates_for_submission(sub['id'])
            if dup_places or dup_subs:
                sub_dict = dict(sub)
                sub_dict['duplicate_places'] = dup_places
                sub_dict['duplicate_subs'] = dup_subs
                filtered.append(sub_dict)
        return filtered
    return result


def merge_submissions(keep_id, merge_id, merged_data=None):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM user_submissions WHERE id = %s", (keep_id,))
        keep = cur.fetchone()
        cur.execute("SELECT * FROM user_submissions WHERE id = %s", (merge_id,))
        merge = cur.fetchone()
        if not keep or not merge:
            cur.close()
            return False

        photos1 = keep.get('photos', '') or ''
        photos2 = merge.get('photos', '') or ''
        all_photos = ','.join(filter(None, [photos1, photos2]))

        final_name = merged_data.get('place_name', keep['place_name']) if merged_data else keep['place_name']
        final_desc = merged_data.get('description', keep.get('description', '')) if merged_data else (keep.get('description', '') + '\n\n' + merge.get('description', '')).strip()

        cur.execute("""
            UPDATE user_submissions SET
                place_name = %s, description = %s, photos = %s,
                submitter_name = %s
            WHERE id = %s
        """, (
            final_name, final_desc, all_photos,
            ((keep.get('submitter_name', '') or '') + ', ' + (merge.get('submitter_name', '') or '')).strip(', '),
            keep_id
        ))
        cur.execute(
            "UPDATE user_submissions SET status = 'merged', merged_into = %s WHERE id = %s",
            (keep_id, merge_id)
        )
        log_admin_action('merge', 'submission', keep_id,
                         f'Merged submission #{merge_id} into #{keep_id}')
        conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
        logger.error("Failed to merge submissions %d -> %d: %s", merge_id, keep_id, e)
        return False
    finally:
        conn.close()
    return True


def update_submission(sub_id, data):
    with get_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE user_submissions SET
                place_name = %s, district_name = %s, description = %s,
                category = %s, latitude = %s, longitude = %s,
                best_time_to_visit = %s, entry_fee = %s
            WHERE id = %s
        """, (
            data.get('place_name', ''), data.get('district_name', ''),
            data.get('description', ''), data.get('category', 'tourist_spot'),
            data.get('latitude'), data.get('longitude'),
            data.get('best_time_to_visit', ''), data.get('entry_fee', ''),
            sub_id
        ))


def replace_place_with_submission(place_id, sub_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM user_submissions WHERE id = %s", (sub_id,))
        sub = cur.fetchone()
        cur.execute("SELECT * FROM places WHERE id = %s", (place_id,))
        place = cur.fetchone()
        if not sub or not place:
            cur.close()
            return False

        cur.execute("""
            UPDATE places SET
                description = %s, category = %s, latitude = %s, longitude = %s,
                best_time_to_visit = %s, entry_fee = %s, travel_tips = %s
            WHERE id = %s
        """, (
            sub.get('description', ''), sub.get('category', 'tourist_spot'),
            sub.get('latitude'), sub.get('longitude'),
            sub.get('best_time_to_visit', ''), sub.get('entry_fee', ''),
            sub.get('local_tips', ''), place_id
        ))
        cur.execute(
            "UPDATE user_submissions SET status = 'approved', admin_notes = 'Replaced existing place data' WHERE id = %s",
            (sub_id,)
        )
        log_admin_action('replace', 'place', place_id,
                         f'Replaced with submission #{sub_id}')
        conn.commit()
        cur.close()
    except Exception:
        conn.rollback()
    finally:
        conn.close()
    return True


def log_admin_action(action, target_type, target_id, details=''):
    try:
        with get_cursor(commit=True) as cur:
            cur.execute("""
                INSERT INTO admin_logs (action, target_type, target_id, details)
                VALUES (%s, %s, %s, %s)
            """, (action, target_type, target_id, details))
    except Exception:
        pass


def get_admin_logs(limit=50):
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM admin_logs ORDER BY created_at DESC LIMIT %s", (limit,)
        )
        return cur.fetchall()


def add_user_photo(place_id, session_id, uploader_name, filename, caption=''):
    with get_cursor(commit=True) as cur:
        cur.execute(
            """INSERT INTO user_photos (place_id, session_id, uploader_name, filename, caption)
               VALUES (%s, %s, %s, %s, %s)""",
            (place_id, session_id, uploader_name, filename, caption)
        )


def get_approved_user_photos(place_id):
    with get_cursor() as cur:
        cur.execute(
            """SELECT * FROM user_photos WHERE place_id = %s AND status = 'approved'
               ORDER BY created_at DESC""",
            (place_id,)
        )
        return cur.fetchall()


def get_pending_user_photos():
    with get_cursor() as cur:
        cur.execute(
            """SELECT up.*, p.name AS place_name, p.slug AS place_slug
               FROM user_photos up
               JOIN places p ON up.place_id = p.id
               WHERE up.status = 'pending'
               ORDER BY up.created_at DESC"""
        )
        return cur.fetchall()


def get_all_user_photos_admin():
    with get_cursor() as cur:
        cur.execute(
            """SELECT up.*, p.name AS place_name, p.slug AS place_slug
               FROM user_photos up
               JOIN places p ON p.id = up.place_id
               ORDER BY up.created_at DESC"""
        )
        return cur.fetchall()


def approve_user_photo(photo_id):
    with get_cursor(commit=True) as cur:
        cur.execute(
            """UPDATE user_photos SET status = 'approved', reviewed_by = 'admin',
               reviewed_at = NOW() WHERE id = %s""",
            (photo_id,)
        )


def reject_user_photo(photo_id):
    with get_cursor(commit=True) as cur:
        cur.execute(
            """UPDATE user_photos SET status = 'rejected', reviewed_by = 'admin',
               reviewed_at = NOW() WHERE id = %s""",
            (photo_id,)
        )


def delete_user_photo(photo_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM user_photos WHERE id = %s", (photo_id,))
        photo = cur.fetchone()
        if photo:
            cur.execute("DELETE FROM user_photos WHERE id = %s", (photo_id,))
            conn.commit()
        cur.close()
        return photo
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def count_pending_user_photos():
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM user_photos WHERE status = 'pending'")
        return cur.fetchone()['cnt']


def get_user_photos_by_status(status=None):
    """Get user photos filtered by status for admin management."""
    with get_cursor() as cur:
        query = """SELECT up.*, p.name AS place_name, p.slug AS place_slug
                   FROM user_photos up
                   JOIN places p ON up.place_id = p.id"""
        params = []
        if status:
            query += " WHERE up.status = %s"
            params.append(status)
        query += " ORDER BY up.created_at DESC"
        cur.execute(query, params)
        return cur.fetchall()


def get_admin_districts_list():
    """Get simple id and name list of districts for admin dropdowns."""
    with get_cursor() as cur:
        cur.execute("SELECT id, name FROM districts ORDER BY name")
        return cur.fetchall()



_stats_cache = {'data': None, 'ts': 0}
_STATS_CACHE_TTL = 30  # seconds


def get_stats():
    import time as _t
    now = _t.time()
    if _stats_cache['data'] and (now - _stats_cache['ts']) < _STATS_CACHE_TTL:
        return dict(_stats_cache['data'])

    with get_cursor() as cur:
        cur.execute("""
            SELECT
                (SELECT COUNT(*) FROM states) AS states,
                (SELECT COUNT(*) FROM districts) AS districts,
                (SELECT COUNT(*) FROM places WHERE deleted_at IS NULL) AS places,
                (SELECT COUNT(*) FROM places WHERE deleted_at IS NOT NULL) AS deleted_places,
                (SELECT COUNT(*) FROM photos) AS photos,
                (SELECT COUNT(*) FROM reviews) AS reviews,
                (SELECT COUNT(*) FROM users) AS users,
                (SELECT COUNT(*) FROM user_submissions WHERE status = 'pending') AS pending_submissions
        """)
        result = dict(cur.fetchone())

    _stats_cache['data'] = result
    _stats_cache['ts'] = now
    return dict(result)


def get_dashboard_analytics():
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT name, slug, view_count, district_id FROM places WHERE deleted_at IS NULL ORDER BY view_count DESC LIMIT 5"
        )
        top_viewed = cur.fetchall()
        cur.execute("""
            SELECT d.name, d.slug, SUM(p.view_count) AS total_views, COUNT(p.id) AS place_count
            FROM districts d LEFT JOIN places p ON p.district_id = d.id AND p.deleted_at IS NULL
            GROUP BY d.id ORDER BY total_views DESC LIMIT 5
        """)
        top_districts = cur.fetchall()
        cur.execute(
            "SELECT name, slug, created_at FROM places WHERE deleted_at IS NULL ORDER BY created_at DESC LIMIT 5"
        )
        recent_places = cur.fetchall()
        cur.execute("SELECT COUNT(*) AS cnt FROM blocks")
        blocks_count = cur.fetchone()['cnt']
        try:
            cur.execute("SELECT COUNT(*) AS cnt FROM wishlists")
            wishlist_count = cur.fetchone()['cnt']
        except Exception:
            wishlist_count = 0
        cur.execute("SELECT COUNT(*) AS cnt FROM places WHERE deleted_at IS NULL")
        total_places = cur.fetchone()['cnt']
        cur.close()
        return {
            'top_viewed': top_viewed,
            'top_districts': top_districts,
            'recent_places': recent_places,
            'blocks_count': blocks_count,
            'wishlist_count': wishlist_count,
            'total_places': total_places,
        }
    finally:
        conn.close()


def get_place_edit_history(place_id, limit=20):
    with get_cursor() as cur:
        cur.execute("""
            SELECT * FROM admin_logs
            WHERE target_type = 'place' AND target_id = %s
            ORDER BY created_at DESC LIMIT %s
        """, (place_id, limit))
        return cur.fetchall()


def get_sitemap_districts():
    with get_cursor() as cur:
        cur.execute(
            "SELECT d.slug AS d_slug, s.slug AS s_slug "
            "FROM districts d JOIN states s ON s.id = d.state_id "
            "WHERE d.is_visible = 1"
        )
        return cur.fetchall()
