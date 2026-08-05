"""
HiddenYatra — User Authentication & Account Database Operations
Handles password hashing (PBKDF2-HMAC-SHA256), account lockout, user registrations, and lookups.
"""
import hashlib
import secrets
import logging
from datetime import datetime
import pymysql

from models.connection import get_db, get_cursor, _escape_like

logger = logging.getLogger(__name__)

_PBKDF2_ITERATIONS = 260000  # OWASP 2023 recommendation


def hash_password(password):
    """Hash password with PBKDF2-HMAC-SHA256."""
    salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        'sha256', password.encode(), salt.encode(), _PBKDF2_ITERATIONS
    ).hex()
    return f"pbkdf2${salt}${pw_hash}"


def verify_password(password, stored_hash):
    """Verify password. Supports both new PBKDF2 and legacy SHA-256 hashes."""
    try:
        if stored_hash.startswith('pbkdf2$'):
            _, salt, pw_hash = stored_hash.split('$', 2)
            computed = hashlib.pbkdf2_hmac(
                'sha256', password.encode(), salt.encode(), _PBKDF2_ITERATIONS
            ).hex()
            return secrets.compare_digest(computed, pw_hash)
        else:
            salt, pw_hash = stored_hash.split('$', 1)
            computed = hashlib.sha256((salt + password).encode()).hexdigest()
            return secrets.compare_digest(computed, pw_hash)
    except (ValueError, AttributeError):
        return False


def upgrade_password_hash(user_id, password):
    """Re-hash password with PBKDF2 if still using legacy SHA-256."""
    new_hash = hash_password(password)
    with get_cursor(commit=True) as cur:
        cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id))


def register_user(username, email, password, display_name='', full_name='', status='pending'):
    """Register a new user. Returns user_id or None if duplicate."""
    pw_hash = hash_password(password)
    try:
        with get_cursor(commit=True) as cur:
            cur.execute(
                """INSERT INTO users (username, email, password_hash, display_name, full_name, status, email_verified)
                   VALUES (%s, %s, %s, %s, %s, %s, 0)""",
                (username.strip(), email.strip().lower(), pw_hash,
                 display_name or username, full_name.strip(), status)
            )
            return cur.lastrowid
    except pymysql.IntegrityError:
        return None


def login_user(email, password):
    """Authenticate user. Returns user dict, 'pending', 'suspended', 'banned', 'locked', or None."""
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email.strip().lower(),))
        user = cur.fetchone()

        if not user:
            cur.close()
            return None

        if user.get('locked_until'):
            locked = user['locked_until']
            if isinstance(locked, str):
                try:
                    locked = datetime.strptime(locked, '%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    locked = None
            if locked and datetime.utcnow() < locked:
                cur.close()
                return 'locked'
            cur.execute(
                "UPDATE users SET failed_login_count = 0, locked_until = NULL WHERE id = %s",
                (user['id'],)
            )
            conn.commit()

        if not verify_password(password, user['password_hash']):
            new_count = (user.get('failed_login_count') or 0) + 1
            if new_count >= 5:
                cur.execute(
                    "UPDATE users SET failed_login_count = %s, locked_until = DATE_ADD(NOW(), INTERVAL 15 MINUTE) WHERE id = %s",
                    (new_count, user['id'])
                )
            else:
                cur.execute(
                    "UPDATE users SET failed_login_count = %s WHERE id = %s",
                    (new_count, user['id'])
                )
            conn.commit()
            cur.close()
            return None

        if not user['password_hash'].startswith('pbkdf2$'):
            upgrade_password_hash(user['id'], password)

        status = user.get('status', 'active')
        if status in ('pending', 'suspended', 'banned'):
            cur.close()
            return status

        cur.execute(
            "UPDATE users SET last_login = NOW(), failed_login_count = 0, locked_until = NULL WHERE id = %s",
            (user['id'],)
        )
        conn.commit()
        cur.close()

        return user
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_user_by_id(user_id):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cur.fetchone()


def get_user_by_email(email):
    """Get user by email (case-insensitive)."""
    with get_cursor() as cur:
        cur.execute("SELECT * FROM users WHERE email = %s", (email.strip().lower(),))
        return cur.fetchone()


def activate_user(user_id):
    """Mark user as active and email_verified."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE users SET status = 'active', email_verified = 1 WHERE id = %s",
            (user_id,)
        )


def update_user_status(user_id, status):
    """Update user status: active, suspended, banned."""
    with get_cursor(commit=True) as cur:
        if status == 'active':
            cur.execute("UPDATE users SET status = %s, email_verified = 1 WHERE id = %s", (status, user_id))
        else:
            cur.execute("UPDATE users SET status = %s WHERE id = %s", (status, user_id))


def update_user_password(user_id, new_password):
    """Set new password for user."""
    pw_hash = hash_password(new_password)
    with get_cursor(commit=True) as cur:
        cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (pw_hash, user_id))


def search_users(query):
    """Search users by name, username, or email."""
    q = f"%{_escape_like(query)}%"
    with get_cursor() as cur:
        cur.execute(
            """SELECT id, username, email, display_name, full_name, status, email_verified,
                      last_login, created_at
               FROM users WHERE username LIKE %s OR email LIKE %s OR display_name LIKE %s OR full_name LIKE %s
               ORDER BY created_at DESC LIMIT 50""",
            (q, q, q, q)
        )
        return cur.fetchall()


def count_users():
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM users")
        return cur.fetchone()['cnt']


def get_all_users():
    """Get all registered users for admin panel."""
    with get_cursor() as cur:
        cur.execute(
            """SELECT id, username, email, display_name, full_name, avatar_emoji,
                      status, is_admin, email_verified, last_login, created_at
               FROM users ORDER BY created_at DESC"""
        )
        return cur.fetchall()


def delete_user(user_id):
    """Delete a user by ID."""
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))

