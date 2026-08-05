"""
HiddenYatra — Reviews & Ratings Database Operations
Handles review submission, editing, deletion, ratings, and pagination.
"""
import logging
from models.connection import get_cursor

logger = logging.getLogger(__name__)


def add_review(place_id, session_id, author_name, rating, comment=''):
    """Add a review for a place."""
    with get_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO reviews (place_id, session_id, author_name, rating, comment)
            VALUES (%s, %s, %s, %s, %s)
        """, (place_id, session_id, author_name, rating, comment))
        return cur.lastrowid


def get_reviews_by_place(place_id, limit=20, offset=0):
    """Get reviews for a place with pagination."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT * FROM reviews WHERE place_id = %s
            ORDER BY created_at DESC LIMIT %s OFFSET %s
        """, (place_id, limit, offset))
        return cur.fetchall()


def get_review_by_id(review_id):
    """Get a single review by ID."""
    with get_cursor() as cur:
        cur.execute("SELECT * FROM reviews WHERE id = %s", (review_id,))
        return cur.fetchone()


def update_review(review_id, rating, comment):
    """Update an existing review."""
    with get_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE reviews SET rating = %s, comment = %s
            WHERE id = %s
        """, (rating, comment, review_id))


def delete_review(review_id):
    """Delete a review by ID."""
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM reviews WHERE id = %s", (review_id,))


def get_avg_rating(place_id):
    """Get average rating and review count for a place."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT ROUND(AVG(rating), 1) AS avg_rating,
                   COUNT(*) AS review_count
            FROM reviews WHERE place_id = %s
        """, (place_id,))
        return cur.fetchone() or {'avg_rating': None, 'review_count': 0}


def count_reviews_by_session(session_id, place_id):
    """Count reviews created by a session for a place in the last 24h (rate limit)."""
    with get_cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) AS cnt FROM reviews
            WHERE session_id = %s AND place_id = %s
              AND created_at >= NOW() - INTERVAL 1 DAY
        """, (session_id, place_id))
        return cur.fetchone()['cnt']
