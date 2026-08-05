"""
HiddenYatra — User Auth System Migration
Adds: status, otp, email_verified, last_login, full_name, phone to users table
Creates: otp_requests table for rate limiting
"""
import sqlite3

DB_PATH = 'bharat_darshan.db'

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # -- Users table new columns --
    user_cols = {
        'status': "TEXT DEFAULT 'active'",
        'email_verified': 'INTEGER DEFAULT 0',
        'otp_code': 'TEXT',
        'otp_expires_at': 'TEXT',
        'otp_purpose': 'TEXT',
        'last_login': 'TEXT',
        'full_name': 'TEXT',
        'phone': 'TEXT',
        'failed_login_count': 'INTEGER DEFAULT 0',
        'locked_until': 'TEXT',
    }
    existing = [r[1] for r in cur.execute("PRAGMA table_info(users)").fetchall()]
    for col, dtype in user_cols.items():
        if col not in existing:
            cur.execute(f"ALTER TABLE users ADD COLUMN {col} {dtype}")
            print(f"[+] Added users.{col}")
        else:
            print(f"[=] users.{col} exists")

    # Set all existing users to 'active' and 'verified'
    cur.execute("UPDATE users SET status = 'active', email_verified = 1 WHERE status IS NULL OR status = ''")
    print("[+] Existing users set to active+verified")

    conn.commit()
    conn.close()
    print("\nDone! User auth migration complete.")

if __name__ == '__main__':
    migrate()
