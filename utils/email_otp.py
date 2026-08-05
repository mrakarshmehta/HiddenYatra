"""
HiddenYatra Email OTP Service
Sends OTP via SMTP for verification and password reset.
"""
import smtplib
import secrets
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from models.database import get_cursor

logger = logging.getLogger(__name__)


# ── CONFIG ──
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
SMTP_FROM = os.environ.get('SMTP_FROM', '') or SMTP_USER
OTP_EXPIRY_MINUTES = 10


def generate_otp():
    """Generate a 6-digit OTP using cryptographically secure random."""
    return str(secrets.randbelow(900000) + 100000)


def save_otp(user_id, otp_code, purpose='verify'):
    """Save OTP to user record with expiry."""
    expires = (datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)).strftime('%Y-%m-%d %H:%M:%S')
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE users SET otp_code = %s, otp_expires_at = %s, otp_purpose = %s WHERE id = %s",
            (otp_code, expires, purpose, user_id)
        )


def verify_otp(user_id, entered_otp, purpose='verify'):
    """Verify OTP for a user. Returns True/False."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT otp_code, otp_expires_at, otp_purpose FROM users WHERE id = %s",
            (user_id,)
        )
        row = cur.fetchone()

    if not row:
        return False

    stored_otp = row['otp_code']
    expires_at = row['otp_expires_at']
    stored_purpose = row['otp_purpose']

    if not stored_otp or not expires_at:
        return False

    # Check purpose matches
    if stored_purpose != purpose:
        return False

    # Check expiry
    try:
        if isinstance(expires_at, str):
            exp_time = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
        else:
            exp_time = expires_at
        if datetime.utcnow() > exp_time:
            return False
    except (ValueError, TypeError):
        return False

    # Check OTP matches (constant-time comparison)
    if not secrets.compare_digest(str(stored_otp), str(entered_otp)):
        return False

    # OTP valid — clear it
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE users SET otp_code = NULL, otp_expires_at = NULL, otp_purpose = NULL WHERE id = %s",
            (user_id,)
        )
    return True


def send_otp_email(to_email, otp_code, purpose='verify'):
    """Send OTP via email. Returns True if sent, False otherwise."""
    if not SMTP_USER or not SMTP_PASS:
        # Fallback: print OTP to console (dev mode)
        print(f"\n{'='*50}")
        print(f"📧 OTP for {to_email}: {otp_code} (purpose: {purpose})")
        print(f"{'='*50}\n")
        return True

    subject_map = {
        'verify': 'HiddenYatra — Verify Your Email',
        'reset': 'HiddenYatra — Reset Your Password',
    }
    body_map = {
        'verify': f"""
            <div style="font-family:sans-serif;max-width:500px;margin:0 auto;padding:30px;background:#0a0a12;color:#e5e5e5;border-radius:12px;">
                <div style="margin-bottom:16px;">
                    <span style="font-size:1.4rem;font-weight:700;color:#ffffff;">Hidden<strong style="color:#FF7A18;">Yatra</strong></span>
                </div>
                <h2 style="color:#00BFA6;margin-bottom:10px;">Welcome to HiddenYatra!</h2>
                <p>Your verification code is:</p>
                <div style="font-size:2.5rem;font-weight:800;letter-spacing:8px;text-align:center;padding:20px;background:#1a1a2e;border-radius:8px;color:#00BFA6;margin:20px 0;">
                    {otp_code}
                </div>
                <p>This code expires in <strong>{OTP_EXPIRY_MINUTES} minutes</strong>.</p>
                <p style="color:#888;font-size:0.85rem;">If you didn't create an account, ignore this email.</p>
            </div>
        """,
        'reset': f"""
            <div style="font-family:sans-serif;max-width:500px;margin:0 auto;padding:30px;background:#0a0a12;color:#e5e5e5;border-radius:12px;">
                <div style="margin-bottom:16px;">
                    <span style="font-size:1.4rem;font-weight:700;color:#ffffff;">Hidden<strong style="color:#FF7A18;">Yatra</strong></span>
                </div>
                <h2 style="color:#F59E0B;margin-bottom:10px;">Password Reset</h2>
                <p>Your password reset code is:</p>
                <div style="font-size:2.5rem;font-weight:800;letter-spacing:8px;text-align:center;padding:20px;background:#1a1a2e;border-radius:8px;color:#F59E0B;margin:20px 0;">
                    {otp_code}
                </div>
                <p>This code expires in <strong>{OTP_EXPIRY_MINUTES} minutes</strong>.</p>
                <p style="color:#888;font-size:0.85rem;">If you didn't request this, ignore this email.</p>
            </div>
        """,
    }

    subject = subject_map.get(purpose, 'HiddenYatra — Verification Code')
    html_body = body_map.get(purpose, body_map['verify'])

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f'HiddenYatra <{SMTP_FROM}>'
    msg['To'] = to_email
    msg.attach(MIMEText(f'Your HiddenYatra OTP is: {otp_code}', 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_FROM, to_email, msg.as_string())
        return True
    except Exception as e:
        logger.error('Failed to send OTP email to %s: %s', to_email, e)
        # Fallback: log OTP to console in dev only (NEVER in production)
        from config import IS_PRODUCTION
        if not IS_PRODUCTION:
            logger.info('OTP for %s: %s', to_email, otp_code)
        return False
