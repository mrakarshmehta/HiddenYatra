# HiddenYatra utils package

from functools import wraps
from flask import session, request, jsonify, abort
import uuid


def csrf_required(f):
    """Decorator to validate CSRF token on POST requests."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'POST':
            token = (request.headers.get('X-CSRF-Token')
                     or request.form.get('_csrf_token', ''))
            if not token or token != session.get('_csrf_token'):
                if (request.is_json
                        or request.headers.get('X-Requested-With') == 'XMLHttpRequest'):
                    return jsonify({'error': 'Invalid or missing CSRF token'}), 403
                abort(403)
        return f(*args, **kwargs)
    return decorated


def get_session_id():
    """Get or create a persistent anonymous session ID.
    Shared across all modules that need session-based tracking
    (wishlist, reviews, itinerary, visited, etc.).
    """
    if 'user_sid' not in session:
        session['user_sid'] = uuid.uuid4().hex
    return session['user_sid']


def login_required(f):
    """Decorator to require user login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Login required'}), 401
            from flask import flash, redirect, url_for
            flash('Please login to continue.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated
