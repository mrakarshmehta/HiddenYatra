"""
HiddenYatra — Wishlist & Visited Places Database Operations
Session-based wishlist bookmarking and visited place tracking.
"""
import logging
import pymysql
from models.connection import get_cursor

logger = logging.getLogger(__name__)


def add_to_wishlist(session_id, place_id):
    """Add a place to wishlist (ignore duplicates)."""
    try:
        with get_cursor(commit=True) as cur:
            cur.execute(
                "INSERT INTO wishlists (session_id, place_id) VALUES (%s, %s)",
                (session_id, place_id)
            )
    except pymysql.IntegrityError:
        pass


def remove_from_wishlist(session_id, place_id):
    """Remove a place from wishlist."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            "DELETE FROM wishlists WHERE session_id = %s AND place_id = %s",
            (session_id, place_id)
        )


def is_wishlisted(session_id, place_id):
    """Check if a place is wishlisted by a session."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT 1 AS w FROM wishlists WHERE session_id = %s AND place_id = %s",
            (session_id, place_id)
        )
        return cur.fetchone() is not None


def get_wishlist(session_id):
    """Get all wishlisted places for a session."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT p.*, s.name AS state_name, s.slug AS state_slug,
                   d.name AS district_name, w.created_at AS wishlisted_at
            FROM wishlists w
            JOIN places p ON p.id = w.place_id
            JOIN states s ON s.id = p.state_id
            LEFT JOIN districts d ON d.id = p.district_id
            WHERE w.session_id = %s AND p.deleted_at IS NULL
            ORDER BY w.created_at DESC
        """, (session_id,))
        return cur.fetchall()


def get_wishlist_count(session_id):
    """Get total wishlist count for a session."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM wishlists WHERE session_id = %s", (session_id,)
        )
        return cur.fetchone()['cnt']


def get_place_wishlist_count(place_id):
    """Get total times a place has been wishlisted."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM wishlists WHERE place_id = %s", (place_id,)
        )
        return cur.fetchone()['cnt']


def mark_visited(session_id, place_id):
    """Mark a place as visited."""
    try:
        with get_cursor(commit=True) as cur:
            cur.execute(
                "INSERT INTO visited_places (session_id, place_id) VALUES (%s, %s)",
                (session_id, place_id)
            )
    except pymysql.IntegrityError:
        pass


def unmark_visited(session_id, place_id):
    """Unmark a place as visited."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            "DELETE FROM visited_places WHERE session_id = %s AND place_id = %s",
            (session_id, place_id)
        )


def is_visited(session_id, place_id):
    """Check if a place is marked as visited."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT 1 AS v FROM visited_places WHERE session_id = %s AND place_id = %s",
            (session_id, place_id)
        )
        return cur.fetchone() is not None


def get_visited_places(session_id):
    """Get all visited places for a session."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT p.*, s.name AS state_name, s.slug AS state_slug,
                   d.name AS district_name, v.visited_at
            FROM visited_places v
            JOIN places p ON p.id = v.place_id
            JOIN states s ON s.id = p.state_id
            LEFT JOIN districts d ON d.id = p.district_id
            WHERE v.session_id = %s AND p.deleted_at IS NULL
            ORDER BY v.visited_at DESC
        """, (session_id,))
        return cur.fetchall()


def get_visited_count(session_id):
    """Get total visited count for a session."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM visited_places WHERE session_id = %s", (session_id,)
        )
        return cur.fetchone()['cnt']
