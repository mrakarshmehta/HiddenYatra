"""
E2E QA Verification Script for HiddenYatra Auth System.
Tests all flows and records exact runtime behavior, database states, and status codes.
"""
import os
import sys
import re
import pymysql
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app

print("=========================================================")
print("RUNNING COMPLETE E2E AUTHENTICATION QA VERIFICATION")
print("=========================================================\n")

app = create_app()
app.testing = True
client = app.test_client()

# Utility DB cleaner
def get_db():
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DB', 'hiddenyatra'),
        cursorclass=pymysql.cursors.DictCursor
    )

# ---------------------------------------------------------
# STEP 1: App Startup & MySQL Connection
# ---------------------------------------------------------
print("--- STEP 1: App Startup & DB Connection ---")
try:
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT 1 AS ok")
        res = cur.fetchone()
    conn.close()
    print("✓ MySQL Connection: SUCCESS")
    print("✓ Flask App Initialization: SUCCESS\n")
except Exception as e:
    print(f"❌ MySQL Connection: FAILED ({e})\n")

# ---------------------------------------------------------
# STEP 2: Signup Flow
# ---------------------------------------------------------
print("--- STEP 2: Signup Flow ---")
test_user = "e2e_qa_tester"
test_email = "e2e_qa_tester@example.com"
test_pass = "SecurePass123"

# Clean previous test user
conn = get_db()
with conn.cursor() as cur:
    cur.execute("DELETE FROM users WHERE username=%s OR email=%s", (test_user, test_email))
conn.commit()
conn.close()

with client:
    # 2.1 GET Signup page
    res = client.get('/signup')
    csrf_token = re.search(r'name="_csrf_token" value="([^"]+)"', res.text).group(1)
    
    # 2.2 POST Signup (Valid)
    signup_data = {
        '_csrf_token': csrf_token,
        'full_name': 'E2E QA Tester',
        'username': test_user,
        'email': test_email,
        'password': test_pass,
        'confirm_password': test_pass
    }
    signup_res = client.post('/signup', data=signup_data)
    print(f"Signup POST Status: {signup_res.status_code}")
    print(f"Redirect Location: {signup_res.headers.get('Location')}")
    
    # 2.3 Verify DB record
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE username=%s", (test_user,))
        db_user = cur.fetchone()
    conn.close()
    
    print("\nDatabase Record After Signup:")
    print("  User ID:", db_user.get('id') if db_user else None)
    print("  Username:", db_user.get('username') if db_user else None)
    print("  Status:", db_user.get('status') if db_user else None)
    print("  Email Verified:", db_user.get('email_verified') if db_user else None)
    print("  Password Hash Prefix:", db_user.get('password_hash')[:20] if db_user else None)
    print("  OTP Code Stored:", db_user.get('otp_code') if db_user else None)
    print("  OTP Purpose:", db_user.get('otp_purpose') if db_user else None)
    print("  OTP Expires At:", db_user.get('otp_expires_at') if db_user else None)
    print()

# ---------------------------------------------------------
# STEP 3: OTP Delivery Inspection
# ---------------------------------------------------------
print("--- STEP 3: OTP Delivery Inspection ---")
smtp_user = os.environ.get('SMTP_USER', '')
smtp_pass = os.environ.get('SMTP_PASS', '')
smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
smtp_port = os.environ.get('SMTP_PORT', '587')

print(f"SMTP_HOST: '{smtp_host}'")
print(f"SMTP_PORT: '{smtp_port}'")
print(f"SMTP_USER: '{smtp_user}'")
print(f"SMTP_PASS: '{'*' * len(smtp_pass) if smtp_pass else ''}'")

if not smtp_user or not smtp_pass:
    print("\nRESULT: ❌ EMAIL DELIVERY FAIL")
    print("REASON: SMTP credentials (SMTP_USER/SMTP_PASS) are missing in environment/.env.")
    print("BEHAVIOR: OTP EMAIL IS NOT BEING SENT. IT IS ONLY PRINTED TO THE CONSOLE.\n")
else:
    print("\nRESULT: ✅ SMTP Configured\n")

# ---------------------------------------------------------
# STEP 4: Email Verification Flow
# ---------------------------------------------------------
print("--- STEP 4: Email Verification Flow ---")
otp_code = db_user.get('otp_code')
user_id = db_user.get('id')

with client:
    # Set pending session
    with client.session_transaction() as sess:
        sess['pending_user_id'] = user_id
        sess['pending_email'] = test_email
        sess['_csrf_token'] = csrf_token

    # 4.1 Wrong OTP Test
    wrong_res = client.post('/verify-email', data={'_csrf_token': csrf_token, 'otp': '000000'})
    print("Wrong OTP Submit Status:", wrong_res.status_code)
    
    # 4.2 Correct OTP Test
    verify_res = client.post('/verify-email', data={'_csrf_token': csrf_token, 'otp': otp_code})
    print("Correct OTP Submit Status:", verify_res.status_code)
    print("Redirect Location:", verify_res.headers.get('Location'))

    # Check DB status after verification
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT status, email_verified, otp_code FROM users WHERE id=%s", (user_id,))
        verified_user = cur.fetchone()
    conn.close()

    print("\nDatabase Record After Verification:")
    print("  Status:", verified_user.get('status'))
    print("  Email Verified:", verified_user.get('email_verified'))
    print("  OTP Code (should be None):", verified_user.get('otp_code'))
    print()

# ---------------------------------------------------------
# STEP 5: Login Flow
# ---------------------------------------------------------
print("--- STEP 5: Login Flow ---")
with client:
    # 5.1 Wrong Password Test
    r_wrong = client.post('/login', data={'_csrf_token': csrf_token, 'email': test_email, 'password': 'WrongPassword123'})
    print("Wrong Password Submit Status:", r_wrong.status_code)
    
    # Check failed login count in DB
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT failed_login_count, locked_until FROM users WHERE id=%s", (user_id,))
        failed_row = cur.fetchone()
    conn.close()
    print(f"  Failed Login Count in DB: {failed_row['failed_login_count']}")

    # 5.2 Correct Login Test
    r_correct = client.post('/login', data={'_csrf_token': csrf_token, 'email': test_email, 'password': test_pass})
    print("Correct Password Submit Status:", r_correct.status_code)
    print("Redirect Location:", r_correct.headers.get('Location'))
    
    # Check session
    with client.session_transaction() as sess:
        print("  Logged In User ID in Session:", sess.get('user_id'))
        print("  Logged In User Name in Session:", sess.get('user_name'))
    print()

# ---------------------------------------------------------
# STEP 6: Forgot Password & Reset Password Flow
# ---------------------------------------------------------
print("--- STEP 6: Forgot & Reset Password Flow ---")
with client:
    # 6.1 Forgot Password Request
    fp_res = client.post('/forgot-password', data={'_csrf_token': csrf_token, 'email': test_email})
    print("Forgot Password Submit Status:", fp_res.status_code)
    print("Redirect Location:", fp_res.headers.get('Location'))

    # Fetch Reset OTP from DB
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT otp_code, otp_purpose FROM users WHERE id=%s", (user_id,))
        reset_row = cur.fetchone()
    conn.close()
    
    reset_otp = reset_row.get('otp_code')
    print(f"  Reset OTP stored in DB: '{reset_otp}' (purpose: '{reset_row.get('otp_purpose')}')")

    # Set reset session
    with client.session_transaction() as sess:
        sess['reset_user_id'] = user_id
        sess['reset_email'] = test_email
        sess['_csrf_token'] = csrf_token

    new_pass = "NewSecurePass456"
    
    # 6.2 Reset Password Submit
    rp_res = client.post('/reset-password', data={
        '_csrf_token': csrf_token,
        'otp': reset_otp,
        'new_password': new_pass,
        'confirm_password': new_pass
    })
    print("Reset Password Submit Status:", rp_res.status_code)
    print("Redirect Location:", rp_res.headers.get('Location'))

    # 6.3 Verify login with NEW password
    r_new_login = client.post('/login', data={'_csrf_token': csrf_token, 'email': test_email, 'password': new_pass})
    print("Login with NEW Password Status:", r_new_login.status_code)
    print("Redirect Location:", r_new_login.headers.get('Location'))

    # 6.4 Verify login with OLD password fails
    r_old_login = client.post('/login', data={'_csrf_token': csrf_token, 'email': test_email, 'password': test_pass})
    print("Login with OLD Password Status (should return 200 with error flash):", r_old_login.status_code)
    print()

print("=========================================================")
print("E2E QA VERIFICATION COMPLETE")
print("=========================================================")
