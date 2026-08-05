"""
HiddenYatra — Main Flask application entry point.
"""
import os
import json as _json
import secrets as _secrets
import logging
from decimal import Decimal
from datetime import datetime, date

from flask import Flask, render_template, request
from flask.json.provider import DefaultJSONProvider
from dotenv import load_dotenv

load_dotenv()

from config import SECRET_KEY, UPLOAD_FOLDER, MAX_CONTENT_LENGTH, APP_NAME, IS_PRODUCTION
from models.database import init_db, get_category_label, PLACE_CATEGORIES, get_auth_appearance

# ── Logging ──
logging.basicConfig(
    level=logging.INFO if IS_PRODUCTION else logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger('hiddenyatra')


class HiddenYatraJSONProvider(DefaultJSONProvider):
    """Custom JSON provider that handles MySQL Decimal and datetime types."""

    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        return super().default(o)


def create_app():
    app = Flask(__name__)
    app.json_provider_class = HiddenYatraJSONProvider
    app.json = HiddenYatraJSONProvider(app)
    app.secret_key = SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # ═══ SESSION SECURITY ═══
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 14400  # 4 hours
    app.config['SESSION_COOKIE_SECURE'] = IS_PRODUCTION

    # Ensure upload directories exist
    for folder in [UPLOAD_FOLDER]:
        os.makedirs(folder, exist_ok=True)

    # Initialize database
    init_db()

    # ═══ CSRF TOKEN GENERATION ═══
    @app.before_request
    def _ensure_csrf():
        from flask import session as s
        if '_csrf_token' not in s:
            s['_csrf_token'] = _secrets.token_hex(32)

    @app.template_global('csrf_token')
    def csrf_token():
        from flask import session as s
        return s.get('_csrf_token', '')

    @app.template_global('csrf_input')
    def csrf_input():
        from flask import session as s
        from markupsafe import Markup, escape
        token = escape(s.get('_csrf_token', ''))
        return Markup(f'<input type="hidden" name="_csrf_token" value="{token}">')

    # ═══ SECURITY HEADERS ═══
    @app.after_request
    def _security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(self), camera=(), microphone=()'
        # CSP - allow inline styles/scripts (required for Jinja templates)
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://unpkg.com https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://unpkg.com https://fonts.googleapis.com; "
            "img-src 'self' data: https: blob:; "
            "font-src 'self' https://fonts.gstatic.com; "
            "connect-src 'self' https://*.tile.openstreetmap.org https://*.basemaps.cartocdn.com https://unpkg.com; "
            "frame-src 'none'; "
            "object-src 'none';"
        )
        # Static asset caching
        if request.path.startswith('/static/'):
            if any(request.path.endswith(ext) for ext in ('.css', '.js')):
                response.headers['Cache-Control'] = 'public, max-age=3600'  # 1 hour
            elif any(request.path.endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg', '.ico')):
                response.headers['Cache-Control'] = 'public, max-age=86400'  # 1 day
        return response

    # ═══ TEMPLATE CONTEXT ═══
    # Cache auth_appearance to avoid a DB call on every single request.
    _auth_appearance_cache = {'data': None, 'ts': 0}
    _CACHE_TTL = 30  # seconds

    @app.context_processor
    def inject_globals():
        import time
        now = time.time()
        # Only re-fetch from DB every 30 seconds
        if _auth_appearance_cache['data'] is None or (now - _auth_appearance_cache['ts']) > _CACHE_TTL:
            appearance = get_auth_appearance()
            if isinstance(appearance, dict):
                json_list_mapping = {
                    'login_slider_images': 'login_slider_list',
                    'signup_slider_images': 'signup_slider_list',
                    'login_stats': 'login_stats_list',
                    'signup_stats': 'signup_stats_list',
                }
                for key, list_key in json_list_mapping.items():
                    try:
                        appearance[list_key] = _json.loads(appearance.get(key, '[]'))
                    except (TypeError, _json.JSONDecodeError):
                        appearance[list_key] = []
            _auth_appearance_cache['data'] = appearance
            _auth_appearance_cache['ts'] = now

        return {
            'app_name': APP_NAME,
            'categories': PLACE_CATEGORIES,
            'auth_appearance': _auth_appearance_cache['data'],
        }

    # ═══ TEMPLATE FILTERS ═══
    @app.template_filter('category_label')
    def category_label_filter(code):
        return get_category_label(code)

    @app.template_filter('truncate_words')
    def truncate_words_filter(text, count=25):
        words = (text or '').split()
        if len(words) <= count:
            return text
        return ' '.join(words[:count]) + '...'

    # ═══ BLUEPRINTS ═══
    from routes.main import main_bp
    from routes.places import places_bp
    from routes.admin import admin_bp
    from routes.api import api_bp
    from routes.wishlist import wishlist_bp
    from routes.reviews import reviews_bp
    from routes.itinerary import itinerary_bp
    from routes.auth import auth_bp
    from routes.community import community_bp
    from routes.user_photos import user_photos_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(places_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(wishlist_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(itinerary_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(user_photos_bp)

    # ═══ ERROR HANDLERS ═══
    @app.errorhandler(403)
    def forbidden(e):
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from flask import jsonify
            return jsonify({'error': 'Forbidden'}), 403
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        if request.is_json:
            from flask import jsonify
            return jsonify({'error': 'Not found'}), 404
        return render_template('404.html'), 404

    @app.errorhandler(413)
    def too_large(e):
        if request.is_json:
            from flask import jsonify
            return jsonify({'error': 'File too large. Maximum 16 MB.'}), 413
        return render_template('413.html'), 413

    @app.errorhandler(429)
    def rate_limited(e):
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from flask import jsonify
            return jsonify({'error': 'Too many requests. Please try again later.'}), 429
        return render_template('429.html'), 429

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception('Internal server error: %s', e)
        if request.is_json:
            from flask import jsonify
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('500.html'), 500

    # ═══ HEALTH CHECK ═══
    @app.route('/health')
    def health():
        from flask import jsonify
        status = {'status': 'ok', 'app': APP_NAME}
        try:
            from models.database import get_db
            conn = get_db()
            cur = conn.cursor()
            cur.execute('SELECT 1')
            cur.close()
            conn.close()
            status['database'] = 'connected'
        except Exception as e:
            logger.error('Health check DB error: %s', e)
            status['status'] = 'degraded'
            status['database'] = 'error'
            return jsonify(status), 503
        return jsonify(status), 200

    # ═══ SEO ROUTES ═══
    @app.route('/robots.txt')
    def robots():
        from flask import send_from_directory
        return send_from_directory(app.static_folder, 'robots.txt')


    @app.route('/sitemap.xml')
    def sitemap():
        from flask import Response
        from datetime import datetime, timezone
        from models.database import get_all_states, get_all_places, get_sitemap_districts
        pages = []
        host = request.host_url.rstrip('/')
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')

        # Static pages
        for path in ['/', '/browse', '/explore', '/food-culture', '/search']:
            pages.append(
                f'<url><loc>{host}{path}</loc>'
                f'<lastmod>{today}</lastmod>'
                f'<changefreq>weekly</changefreq>'
                f'<priority>0.8</priority></url>'
            )

        # States
        for s in get_all_states():
            pages.append(
                f'<url><loc>{host}/state/{s["slug"]}</loc>'
                f'<changefreq>monthly</changefreq>'
                f'<priority>0.7</priority></url>'
            )

        # Districts
        for d in get_sitemap_districts():
            pages.append(
                f'<url><loc>{host}/state/{d["s_slug"]}/{d["d_slug"]}</loc>'
                f'<changefreq>monthly</changefreq>'
                f'<priority>0.6</priority></url>'
            )

        # Places
        for p in get_all_places(limit=500):
            lastmod = ''
            if p.get('updated_at'):
                try:
                    lastmod = f'<lastmod>{p["updated_at"].strftime("%Y-%m-%d")}</lastmod>'
                except (AttributeError, ValueError):
                    lastmod = f'<lastmod>{today}</lastmod>'
            pages.append(
                f'<url><loc>{host}/place/{p["slug"]}</loc>'
                f'{lastmod}'
                f'<changefreq>weekly</changefreq>'
                f'<priority>0.5</priority></url>'
            )

        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        xml += '\n'.join(pages)
        xml += '\n</urlset>'
        return Response(xml, mimetype='application/xml')

    return app


if __name__ == '__main__':
    app = create_app()
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug, host='0.0.0.0', port=5000)
