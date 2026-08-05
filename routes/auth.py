"""Auth routes — Registration with OTP, Login with status, Forgot Password."""
import re
import time as _time
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from models.database import (
    register_user, login_user, get_user_by_id, get_user_by_email,
    activate_user, update_user_password,
    get_wishlist, get_visited_places, get_user_submissions
)
from utils.email_otp import generate_otp, save_otp, verify_otp, send_otp_email
from utils import csrf_required, login_required, get_session_id as _get_session_id

auth_bp = Blueprint('auth', __name__)


# ── Rate limiters ──
_login_attempts = {}
_signup_attempts = {}
_otp_attempts = {}
_MAX_RATE_STORE_SIZE = 500  # Prevent unbounded growth


def _rate_check(store, ip, max_attempts=5, window=60):
    """Returns True if rate limited."""
    now = _time.time()
    attempts = store.get(ip, [])
    attempts = [t for t in attempts if now - t < window]
    store[ip] = attempts
    # Prevent unbounded growth
    if len(store) > _MAX_RATE_STORE_SIZE:
        store.clear()
        return False
    if len(attempts) >= max_attempts:
        return True
    return False


def _rate_record(store, ip):
    now = _time.time()
    attempts = store.get(ip, [])
    attempts.append(now)
    store[ip] = attempts


def _validate_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)


def _validate_username(username):
    return re.match(r'^[a-zA-Z0-9_]{3,20}$', username)


def _validate_password(password):
    """Check password strength. Returns error message or None."""
    if len(password) < 8:
        return 'Password must be at least 8 characters.'
    if not re.search(r'[A-Za-z]', password):
        return 'Password must contain at least one letter.'
    if not re.search(r'[0-9]', password):
        return 'Password must contain at least one number.'
    return None


# ═══════════════════════════════════════════
# SIGNUP
# ═══════════════════════════════════════════
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('user_id'):
        return redirect(url_for('auth.profile'))

    if request.method == 'POST':
        token = request.form.get('_csrf_token', '')
        if not token or token != session.get('_csrf_token'):
            flash('Invalid request. Please try again.', 'error')
            return render_template('auth/signup.html', form_data={})

        ip = request.remote_addr
        if _rate_check(_signup_attempts, ip, max_attempts=3, window=300):
            flash('Too many signup attempts. Please wait 5 minutes.', 'error')
            return render_template('auth/signup.html')

        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        # Validate
        errors = []
        if not full_name:
            errors.append('Full name is required.')
        if not username or not _validate_username(username):
            errors.append('Username must be 3-20 characters (letters, numbers, underscores).')
        if not email or not _validate_email(email):
            errors.append('Please enter a valid email address.')
        pw_err = _validate_password(password)
        if pw_err:
            errors.append(pw_err)
        if password != confirm:
            errors.append('Passwords do not match.')

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('auth/signup.html',
                                   form_data={'full_name': full_name, 'username': username, 'email': email})

        # Register with pending status
        user_id = register_user(
            username=username,
            email=email,
            password=password,
            display_name=full_name,
            full_name=full_name,
            status='pending'
        )

        if not user_id:
            flash('Username or email already exists. Please try a different one.', 'error')
            return render_template('auth/signup.html',
                                   form_data={'full_name': full_name, 'username': username, 'email': email})

        _rate_record(_signup_attempts, ip)

        # Generate and send OTP
        otp = generate_otp()
        save_otp(user_id, otp, purpose='verify')
        send_otp_email(email, otp, purpose='verify')

        # Store user_id in session for verification
        session['pending_user_id'] = user_id
        session['pending_email'] = email
        flash('📧 We sent a verification code to your email. Please check your inbox.', 'info')
        return redirect(url_for('auth.verify_email'))

    return render_template('auth/signup.html', form_data={})


# ═══════════════════════════════════════════
# EMAIL VERIFICATION (OTP)
# ═══════════════════════════════════════════
@auth_bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    pending_id = session.get('pending_user_id')
    pending_email = session.get('pending_email')

    if not pending_id:
        flash('No pending verification. Please sign up first.', 'error')
        return redirect(url_for('auth.signup'))

    if request.method == 'POST':
        token = request.form.get('_csrf_token', '')
        if not token or token != session.get('_csrf_token'):
            flash('Invalid request. Please try again.', 'error')
            return render_template('auth/verify_email.html', email=pending_email)

        ip = request.remote_addr
        if _rate_check(_otp_attempts, ip, max_attempts=5, window=60):
            flash('Too many attempts. Please wait 1 minute.', 'error')
            return render_template('auth/verify_email.html', email=pending_email)

        entered_otp = request.form.get('otp', '').strip()
        if not entered_otp or len(entered_otp) != 6:
            flash('Please enter a valid 6-digit code.', 'error')
            return render_template('auth/verify_email.html', email=pending_email)

        _rate_record(_otp_attempts, ip)

        if verify_otp(pending_id, entered_otp, purpose='verify'):
            activate_user(pending_id)
            user = get_user_by_id(pending_id)

            # Auto-login
            session.pop('pending_user_id', None)
            session.pop('pending_email', None)
            session.permanent = True
            session['user_id'] = user['id']
            session['user_name'] = user['display_name']
            session['user_emoji'] = user.get('avatar_emoji', '🧳')

            flash(f'🎉 Email verified! Welcome to HiddenYatra, {user["display_name"]}!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid or expired code. Please try again.', 'error')

    return render_template('auth/verify_email.html', email=pending_email)


@auth_bp.route('/resend-otp', methods=['POST'])
@csrf_required
def resend_otp():
    """Resend verification OTP."""
    pending_id = session.get('pending_user_id')
    pending_email = session.get('pending_email')

    if not pending_id or not pending_email:
        flash('No pending verification.', 'error')
        return redirect(url_for('auth.signup'))

    ip = request.remote_addr
    if _rate_check(_otp_attempts, ip, max_attempts=3, window=120):
        flash('Please wait 2 minutes before requesting a new code.', 'error')
        return redirect(url_for('auth.verify_email'))

    _rate_record(_otp_attempts, ip)

    otp = generate_otp()
    save_otp(pending_id, otp, purpose='verify')
    send_otp_email(pending_email, otp, purpose='verify')
    flash('📧 New verification code sent!', 'success')
    return redirect(url_for('auth.verify_email'))


# ═══════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('auth.profile'))

    if request.method == 'POST':
        token = request.form.get('_csrf_token', '')
        if not token or token != session.get('_csrf_token'):
            flash('Invalid request. Please try again.', 'error')
            return render_template('auth/login.html')

        ip = request.remote_addr
        if _rate_check(_login_attempts, ip):
            flash('Too many login attempts. Please wait 1 minute.', 'error')
            return render_template('auth/login.html')

        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('auth/login.html')

        result = login_user(email, password)

        if result == 'pending':
            # User exists but not verified — let them verify
            user = get_user_by_email(email)
            if user:
                session['pending_user_id'] = user['id']
                session['pending_email'] = email
                otp = generate_otp()
                save_otp(user['id'], otp, purpose='verify')
                send_otp_email(email, otp, purpose='verify')
            flash('Your email is not verified. We sent a new verification code.', 'info')
            return redirect(url_for('auth.verify_email'))

        if result == 'suspended':
            flash('Your account has been temporarily suspended. Contact support.', 'error')
            return render_template('auth/login.html')

        if result == 'banned':
            flash('Your account has been banned.', 'error')
            return render_template('auth/login.html')

        if result == 'locked':
            flash('Your account is temporarily locked due to too many failed login attempts. Please try again in 15 minutes.', 'error')
            return render_template('auth/login.html')

        if isinstance(result, dict):
            # Successful login
            session.pop('admin_logged_in', None)
            session.permanent = True
            session['user_id'] = result['id']
            session['user_name'] = result['display_name']
            session['user_emoji'] = result.get('avatar_emoji', '🧳')
            _login_attempts.pop(ip, None)
            flash(f'Welcome back, {result["display_name"]}! 🧭', 'success')
            return redirect(url_for('main.index'))

        # Invalid credentials
        _rate_record(_login_attempts, ip)
        flash('Invalid email or password.', 'error')

    return render_template('auth/login.html')


# ═══════════════════════════════════════════
# FORGOT PASSWORD
# ═══════════════════════════════════════════
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        token = request.form.get('_csrf_token', '')
        if not token or token != session.get('_csrf_token'):
            flash('Invalid request. Please try again.', 'error')
            return render_template('auth/forgot_password.html')

        ip = request.remote_addr
        if _rate_check(_otp_attempts, ip, max_attempts=3, window=120):
            flash('Please wait 2 minutes before requesting again.', 'error')
            return render_template('auth/forgot_password.html')

        email = request.form.get('email', '').strip().lower()
        # Always show same message (prevent email enumeration)
        flash('If an account exists with that email, we sent a reset code.', 'info')

        user = get_user_by_email(email)
        if user and user.get('status') != 'banned':
            _rate_record(_otp_attempts, ip)
            otp = generate_otp()
            save_otp(user['id'], otp, purpose='reset')
            send_otp_email(email, otp, purpose='reset')
            session['reset_user_id'] = user['id']
            session['reset_email'] = email

        # Always redirect to reset page — prevents email enumeration
        # via redirect behavior difference
        return redirect(url_for('auth.reset_password'))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    reset_id = session.get('reset_user_id')
    reset_email = session.get('reset_email')

    if not reset_id:
        flash('Please start from forgot password.', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        token = request.form.get('_csrf_token', '')
        if not token or token != session.get('_csrf_token'):
            flash('Invalid request. Please try again.', 'error')
            return render_template('auth/reset_password.html', email=reset_email)

        ip = request.remote_addr
        if _rate_check(_otp_attempts, ip):
            flash('Too many attempts. Please wait.', 'error')
            return render_template('auth/reset_password.html', email=reset_email)

        entered_otp = request.form.get('otp', '').strip()
        new_password = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')

        if not entered_otp or len(entered_otp) != 6:
            flash('Please enter a valid 6-digit code.', 'error')
            return render_template('auth/reset_password.html', email=reset_email)

        pw_err = _validate_password(new_password)
        if pw_err:
            flash(pw_err, 'error')
            return render_template('auth/reset_password.html', email=reset_email)

        if new_password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('auth/reset_password.html', email=reset_email)

        _rate_record(_otp_attempts, ip)

        if verify_otp(reset_id, entered_otp, purpose='reset'):
            update_user_password(reset_id, new_password)
            session.pop('reset_user_id', None)
            session.pop('reset_email', None)
            flash('🔐 Password reset successful! Please login with your new password.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid or expired code.', 'error')

    return render_template('auth/reset_password.html', email=reset_email)


# ═══════════════════════════════════════════
# LOGOUT
# ═══════════════════════════════════════════
@auth_bp.route('/logout', methods=['POST'])
@csrf_required
def logout():
    # Clear entire session to prevent session fixation attacks.
    # A new session (with new CSRF token) is created on next request.
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.index'))


# ═══════════════════════════════════════════
# PROFILE
# ═══════════════════════════════════════════
@auth_bp.route('/profile')
@login_required
def profile():
    sid = _get_session_id()
    user = None
    if session.get('user_id'):
        user = get_user_by_id(session['user_id'])

    favorites = get_wishlist(sid)
    visited = get_visited_places(sid)
    submissions = get_user_submissions(session_id=sid, user_id=session.get('user_id'))

    return render_template('auth/profile.html',
                           user=user,
                           favorites=favorites,
                           visited=visited,
                           submissions=submissions)
