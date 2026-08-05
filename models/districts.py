"""
HiddenYatra — States, Districts, and Blocks Database Operations
Manages hierarchy: State → District → Block.
"""
import logging
import pymysql

from models.connection import get_db, get_cursor, slugify

logger = logging.getLogger(__name__)


def get_all_states():
    with get_cursor() as cur:
        cur.execute("""
            SELECT s.*,
                   COUNT(DISTINCT p.id) AS place_count,
                   COUNT(DISTINCT d.id) AS district_count
            FROM states s
            LEFT JOIN places p ON p.state_id = s.id AND p.deleted_at IS NULL
            LEFT JOIN districts d ON d.state_id = s.id
            GROUP BY s.id
            ORDER BY s.sort_order, s.name
        """)
        return cur.fetchall()


def get_state_by_slug(slug):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM states WHERE slug = %s", (slug,))
        return cur.fetchone()


def get_state_by_id(state_id):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM states WHERE id = %s", (state_id,))
        return cur.fetchone()


def create_state(name, description='', image_url=''):
    slug = slugify(name)
    conn = get_db()
    try:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO states (name, slug, description, image_url) VALUES (%s, %s, %s, %s)",
                (name, slug, description, image_url)
            )
            conn.commit()
            state_id = cur.lastrowid
        except pymysql.IntegrityError:
            conn.rollback()
            cur.execute("SELECT id FROM states WHERE slug = %s", (slug,))
            row = cur.fetchone()
            state_id = row['id'] if row else None
            if state_id and description:
                try:
                    cur.execute("UPDATE states SET description = %s WHERE id = %s", (description, state_id))
                    conn.commit()
                except Exception:
                    conn.rollback()
                    logger.warning("Failed to update state description for id=%s", state_id)
        cur.close()
        return state_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_state_image(state_id, image_url):
    with get_cursor(commit=True) as cur:
        cur.execute("UPDATE states SET image_url = %s WHERE id = %s", (image_url, state_id))


def get_districts_by_state(state_id):
    with get_cursor() as cur:
        cur.execute("""
            SELECT d.*, COUNT(DISTINCT p.id) AS place_count,
                   COUNT(DISTINCT b.id) AS block_count
            FROM districts d
            LEFT JOIN places p ON p.district_id = d.id AND p.deleted_at IS NULL
            LEFT JOIN blocks b ON b.district_id = d.id
            WHERE d.state_id = %s AND d.is_visible = 1
            GROUP BY d.id
            ORDER BY d.sort_order ASC, d.name ASC
        """, (state_id,))
        return cur.fetchall()


def create_district(state_id, name, description='', famous_for=''):
    slug = slugify(name)
    conn = get_db()
    try:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO districts (state_id, name, slug, description, famous_for) VALUES (%s, %s, %s, %s, %s)",
                (state_id, name, slug, description, famous_for)
            )
            conn.commit()
            did = cur.lastrowid
        except pymysql.IntegrityError:
            conn.rollback()
            cur.execute(
                "SELECT id FROM districts WHERE state_id = %s AND slug = %s", (state_id, slug)
            )
            row = cur.fetchone()
            did = row['id'] if row else None
            if did and (description or famous_for):
                try:
                    cur.execute(
                        "UPDATE districts SET description = COALESCE(NULLIF(%s, ''), description), famous_for = COALESCE(NULLIF(%s, ''), famous_for) WHERE id = %s",
                        (description, famous_for, did)
                    )
                    conn.commit()
                except Exception:
                    conn.rollback()
                    logger.warning("Failed to update district description for id=%s", did)
        cur.close()
        return did
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_district_by_id(district_id):
    with get_cursor() as cur:
        cur.execute("""
            SELECT d.*, s.name AS state_name, s.slug AS state_slug
            FROM districts d
            JOIN states s ON s.id = d.state_id
            WHERE d.id = %s
        """, (district_id,))
        return cur.fetchone()


def get_district_by_slug(state_id, slug):
    with get_cursor() as cur:
        cur.execute("""
            SELECT d.*, s.name AS state_name, s.slug AS state_slug,
                   (SELECT COUNT(*) FROM blocks WHERE district_id = d.id) AS block_count,
                   (SELECT COUNT(*) FROM places WHERE district_id = d.id AND deleted_at IS NULL) AS place_count
            FROM districts d
            JOIN states s ON s.id = d.state_id
            WHERE d.state_id = %s AND d.slug = %s
        """, (state_id, slug))
        return cur.fetchone()


def get_all_districts_admin():
    with get_cursor() as cur:
        cur.execute("""
            SELECT d.*, s.name AS state_name, s.slug AS state_slug,
                   COUNT(DISTINCT p.id) AS place_count,
                   (SELECT COUNT(*) FROM blocks b WHERE b.district_id = d.id) AS block_count
            FROM districts d
            JOIN states s ON s.id = d.state_id
            LEFT JOIN places p ON p.district_id = d.id AND p.deleted_at IS NULL
            GROUP BY d.id
            ORDER BY d.sort_order ASC, d.name ASC
        """)
        return cur.fetchall()


def update_district(district_id, **kwargs):
    allowed = ['name', 'description', 'famous_for', 'cover_image', 'image_url',
               'is_featured', 'is_visible', 'sort_order']
    sets = []
    vals = []
    for k, v in kwargs.items():
        if k in allowed:
            sets.append(f"{k} = %s")
            vals.append(v)
    if not sets:
        return
    if 'name' in kwargs:
        sets.append("slug = %s")
        vals.append(slugify(kwargs['name']))
    vals.append(district_id)
    with get_cursor(commit=True) as cur:
        cur.execute(f"UPDATE districts SET {', '.join(sets)} WHERE id = %s", vals)


def delete_district(district_id):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM districts WHERE id = %s", (district_id,))
        row = cur.fetchone()
        if row:
            cur.execute("DELETE FROM districts WHERE id = %s", (district_id,))
            conn.commit()
        cur.close()
        return row
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def reorder_districts(id_list):
    if not id_list:
        return
    with get_cursor(commit=True) as cur:
        cases = ' '.join(f'WHEN id = %s THEN %s' for _ in id_list)
        params = []
        for i, did in enumerate(id_list):
            params.extend([did, i])
        params.extend(id_list)
        placeholders = ','.join(['%s'] * len(id_list))
        cur.execute(
            f"UPDATE districts SET sort_order = CASE {cases} END WHERE id IN ({placeholders})",
            params
        )


def get_districts_for_homepage(limit=12):
    with get_cursor() as cur:
        cur.execute("""
            SELECT d.*, s.name AS state_name, s.slug AS state_slug,
                   COUNT(DISTINCT p.id) AS place_count,
                   (SELECT COUNT(*) FROM blocks b WHERE b.district_id = d.id) AS block_count
            FROM districts d
            JOIN states s ON s.id = d.state_id
            LEFT JOIN places p ON p.district_id = d.id AND p.deleted_at IS NULL
            WHERE d.is_visible = 1
            GROUP BY d.id
            ORDER BY d.sort_order ASC, d.name ASC
            LIMIT %s
        """, (limit,))
        return cur.fetchall()


def get_featured_districts():
    with get_cursor() as cur:
        cur.execute("""
            SELECT d.*, s.name AS state_name, s.slug AS state_slug,
                   COUNT(DISTINCT p.id) AS place_count,
                   (SELECT COUNT(*) FROM blocks b WHERE b.district_id = d.id) AS block_count
            FROM districts d
            JOIN states s ON s.id = d.state_id
            LEFT JOIN places p ON p.district_id = d.id AND p.deleted_at IS NULL
            WHERE d.is_featured = 1 AND d.is_visible = 1
            GROUP BY d.id
            ORDER BY d.sort_order ASC
        """)
        return cur.fetchall()


def get_blocks_by_district(district_id):
    with get_cursor() as cur:
        cur.execute("""
            SELECT b.*, COUNT(p.id) AS place_count
            FROM blocks b
            LEFT JOIN places p ON p.block_id = b.id AND p.deleted_at IS NULL
            WHERE b.district_id = %s
            GROUP BY b.id
            ORDER BY b.name
        """, (district_id,))
        return cur.fetchall()


def get_blocks_grouped_by_district(state_id):
    from collections import defaultdict
    with get_cursor() as cur:
        cur.execute("""
            SELECT b.*, COUNT(p.id) AS place_count
            FROM blocks b
            JOIN districts d ON d.id = b.district_id
            LEFT JOIN places p ON p.block_id = b.id AND p.deleted_at IS NULL
            WHERE d.state_id = %s
            GROUP BY b.id
            ORDER BY b.name
        """, (state_id,))
        rows = cur.fetchall()
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['district_id']].append(row)
    return dict(grouped)


def create_block(district_id, name):
    slug = slugify(name)
    conn = get_db()
    try:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO blocks (district_id, name, slug) VALUES (%s, %s, %s)",
                (district_id, name, slug)
            )
            conn.commit()
            bid = cur.lastrowid
        except pymysql.IntegrityError:
            conn.rollback()
            cur.execute(
                "SELECT id FROM blocks WHERE district_id = %s AND slug = %s", (district_id, slug)
            )
            bid = cur.fetchone()['id']
        cur.close()
        return bid
    finally:
        conn.close()


def get_block_by_slug(district_id, slug):
    with get_cursor() as cur:
        cur.execute("""
            SELECT b.*, d.name AS district_name, d.slug AS district_slug,
                   s.name AS state_name, s.slug AS state_slug,
                   (SELECT COUNT(*) FROM places WHERE block_id = b.id AND deleted_at IS NULL) AS place_count
            FROM blocks b
            JOIN districts d ON d.id = b.district_id
            JOIN states s ON s.id = d.state_id
            WHERE b.district_id = %s AND b.slug = %s
        """, (district_id, slug))
        return cur.fetchone()
