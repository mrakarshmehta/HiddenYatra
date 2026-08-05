# HiddenYatra — Architecture Documentation

## Overview

HiddenYatra is a Flask-based travel discovery platform for Bihar, India. It helps users explore hidden gems, local food, and cultural heritage across Bihar's districts.

## Tech Stack

| Component | Technology |
|---|---|
| **Backend** | Python 3.11+ / Flask 2.x |
| **Database** | MySQL 8.x (InnoDB, utf8mb4) |
| **Connection Pool** | DBUtils PooledDB |
| **Template Engine** | Jinja2 (auto-escaping enabled) |
| **WSGI Server** | Waitress (dev) / Gunicorn (production) |
| **Image Processing** | Pillow (PIL) |
| **Maps** | Leaflet.js + OpenStreetMap tiles |
| **CSS** | Vanilla CSS (custom design system) |
| **JavaScript** | Vanilla JS (no framework) |

## Directory Structure

```
HiddenYatra/
├── app.py                  # Flask app factory + error handlers + SEO routes
├── config.py               # Configuration (DB, uploads, secrets, validation)
├── .env                    # Environment variables (not committed)
├── models/
│   ├── __init__.py
│   └── database.py         # Complete data access layer (~2800 lines)
├── routes/
│   ├── admin.py            # Admin panel (CRUD, moderation, hero, districts)
│   ├── api.py              # JSON API endpoints
│   ├── auth.py             # User authentication (login, signup, OTP)
│   ├── community.py        # User place submissions
│   ├── itinerary.py        # Trip planning
│   ├── main.py             # Public pages (home, browse, search, explore)
│   ├── places.py           # Place detail pages
│   ├── reviews.py          # Review CRUD
│   ├── user_photos.py      # User photo uploads
│   └── wishlist.py         # Session-based wishlists
├── utils/
│   ├── __init__.py         # CSRF, login_required, get_session_id
│   └── email_otp.py        # SMTP OTP service
├── templates/              # 24 Jinja2 templates
│   ├── base.html
│   ├── index.html
│   ├── admin/              # Admin panel templates
│   └── auth/               # Login/signup templates
├── static/
│   ├── css/                # 5 CSS files (~106KB total)
│   ├── js/                 # 5 JS files (~25KB total)
│   ├── uploads/            # User-uploaded content
│   ├── hero/               # Hero media
│   └── robots.txt
├── scripts/
│   ├── migrations/         # MySQL schema + migration scripts
│   ├── seed/               # Data seeding scripts
│   └── legacy/             # Old frontend (preserved, not used)
├── tests/
│   ├── test_routes.py      # Route & blueprint tests
│   ├── test_database.py    # Database layer tests
│   └── test_security.py    # Security control tests
└── docs/                   # This documentation
```

## Request Lifecycle

```
Client Request
    │
    ▼
Flask WSGI App (app.py)
    │
    ├── before_request: CSRF token generation
    │
    ├── Blueprint Router
    │   ├── main_bp        → Public pages
    │   ├── places_bp      → Place detail
    │   ├── admin_bp       → Admin panel (auth + CSRF check)
    │   ├── api_bp         → JSON API
    │   ├── wishlist_bp    → Wishlist CRUD
    │   ├── reviews_bp     → Review CRUD
    │   ├── itinerary_bp   → Trip planning
    │   ├── auth_bp        → Authentication
    │   ├── community_bp   → Submissions
    │   └── user_photos_bp → Photo uploads
    │
    ├── models/database.py → MySQL via PooledDB
    │
    ├── templates/*.html   → Jinja2 rendering
    │
    └── after_request: Security headers + cache headers
```

## Blueprint Map

| Blueprint | Prefix | Routes | Purpose |
|---|---|---|---|
| `main_bp` | `/` | 8 | Home, browse, search, explore, food, state/district/block detail |
| `places_bp` | `/place` | 1 | Place detail page |
| `admin_bp` | `/admin` | 35+ | Full admin panel |
| `api_bp` | `/api` | 6 | JSON API |
| `wishlist_bp` | `/wishlist` | 3 | Wishlist CRUD |
| `reviews_bp` | `/review` | 5 | Review CRUD + admin delete |
| `itinerary_bp` | `/itinerary` | 7 | Trip planning |
| `auth_bp` | `/` | 8 | Login, signup, OTP, profile |
| `community_bp` | `/suggest` | 4 | Place submissions |
| `user_photos_bp` | `/photos` | 1 | Photo uploads |

## Data Access Pattern

All database access is centralized in `models/database.py`. No route file directly executes SQL.

```python
# Read pattern — auto-closing cursor
with get_cursor() as cur:
    cur.execute("SELECT * FROM places WHERE id = %s", (place_id,))
    return cur.fetchone()

# Write pattern — auto-commit + rollback
with get_cursor(commit=True) as cur:
    cur.execute("INSERT INTO reviews ...", params)
```

## Authentication

| Type | Method | Details |
|---|---|---|
| **Admin** | Session + shared password | `session['admin_logged_in']` |
| **User** | Session + email/password | PBKDF2 hashing, OTP verification |
| **Session ID** | Auto-generated | `session['_session_id']` for anonymous features |

## Security Controls

- **CSRF**: Global token generation, validated on all POST requests
- **CSP**: Content-Security-Policy header on all responses
- **XSS**: Jinja2 auto-escaping, nosniff header
- **SQLi**: Parameterized queries only, LIKE wildcard escaping
- **Clickjacking**: X-Frame-Options SAMEORIGIN
- **Upload**: Magic byte validation, size limits, PIL processing
- **Rate Limiting**: In-memory per-IP rate limiting on login/signup/OTP
- **Account Lockout**: 5 failed attempts → 15-minute lock
