"""Reviews routes — submit, edit, and manage place reviews."""
import logging
from flask import Blueprint, request, redirect, url_for, flash, session, jsonify

from models.database import (
    add_review, get_reviews_by_place, delete_review,
    get_place_by_id, count_reviews_by_session,
    get_review_by_id, update_review
)
from utils import csrf_required, get_session_id as _get_session_id

logger = logging.getLogger(__name__)
reviews_bp = Blueprint('reviews', __name__)

_MAX_AUTHOR_LEN = 100
_MAX_COMMENT_LEN = 2000


@reviews_bp.route('/review/<int:place_id>', methods=['POST'])
@csrf_required
def submit_review(place_id):
    place = get_place_by_id(place_id)
    if not place:
        flash('Place not found.', 'error')
        return redirect(url_for('main.index'))

    sid = _get_session_id()

    # Rate limit: max 3 reviews per session per place per day
    existing = count_reviews_by_session(sid, place_id)
    if existing >= 3:
        flash('You can only leave 3 reviews per place per day.', 'error')
        return redirect(url_for('places.place_detail', slug=place['slug']))

    author = request.form.get('author_name', '').strip()[:_MAX_AUTHOR_LEN] or 'Anonymous Traveler'
    rating = request.form.get('rating', '5')
    comment = request.form.get('comment', '').strip()[:_MAX_COMMENT_LEN]

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            rating = 5
    except (ValueError, TypeError):
        rating = 5

    add_review(place_id, sid, author, rating, comment)
    logger.info("Review submitted for place %d by session %s", place_id, sid[:8])
    flash('⭐ Your review has been posted!', 'success')
    return redirect(url_for('places.place_detail', slug=place['slug']))


@reviews_bp.route('/review/edit/<int:review_id>', methods=['POST'])
@csrf_required
def edit_review(review_id):
    """Edit a review — only by the same session that created it."""
    sid = _get_session_id()
    review = get_review_by_id(review_id)

    if not review:
        flash('Review not found.', 'error')
        return redirect(url_for('main.index'))

    # Ownership check: only the session that created the review can edit it
    if review.get('session_id') != sid:
        flash('You can only edit your own reviews.', 'error')
        place = get_place_by_id(review['place_id'])
        if place:
            return redirect(url_for('places.place_detail', slug=place['slug']))
        return redirect(url_for('main.index'))

    rating = request.form.get('rating', '5')
    comment = request.form.get('comment', '').strip()[:_MAX_COMMENT_LEN]

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            rating = 5
    except (ValueError, TypeError):
        rating = 5

    update_review(review_id, rating, comment)

    place = get_place_by_id(review['place_id'])
    flash('✏️ Your review has been updated!', 'success')
    if place:
        return redirect(url_for('places.place_detail', slug=place['slug']))
    return redirect(url_for('main.index'))


@reviews_bp.route('/review/delete/<int:review_id>', methods=['POST'])
@csrf_required
def delete_own_review(review_id):
    """Delete own review — session-based ownership."""
    sid = _get_session_id()
    review = get_review_by_id(review_id)

    if not review:
        flash('Review not found.', 'error')
        return redirect(url_for('main.index'))

    if review.get('session_id') != sid:
        flash('You can only delete your own reviews.', 'error')
        place = get_place_by_id(review['place_id'])
        if place:
            return redirect(url_for('places.place_detail', slug=place['slug']))
        return redirect(url_for('main.index'))

    place = get_place_by_id(review['place_id'])
    delete_review(review_id)
    logger.info("Review %d deleted by session %s", review_id, sid[:8])
    flash('🗑️ Your review has been deleted.', 'info')
    if place:
        return redirect(url_for('places.place_detail', slug=place['slug']))
    return redirect(url_for('main.index'))


@reviews_bp.route('/api/reviews/<int:place_id>')
def api_reviews(place_id):
    """Public API: get reviews for a place with pagination."""
    limit = min(request.args.get('limit', 20, type=int), 100)
    offset = max(request.args.get('offset', 0, type=int), 0)
    reviews = get_reviews_by_place(place_id, limit=limit, offset=offset)
    # Serialize datetime objects for JSON
    result = []
    for r in reviews:
        row = dict(r)
        for key in ('created_at',):
            if key in row and hasattr(row[key], 'isoformat'):
                row[key] = row[key].isoformat()
        result.append(row)
    return jsonify(result)


@reviews_bp.route('/admin/review/delete/<int:review_id>', methods=['POST'])
@csrf_required
def admin_delete_review(review_id):
    if not session.get('admin_logged_in'):
        flash('Unauthorized.', 'error')
        return redirect(url_for('admin.login'))
    delete_review(review_id)
    logger.info("Admin deleted review %d", review_id)
    flash('Review deleted.', 'info')
    return redirect(request.referrer or url_for('admin.dashboard'))

