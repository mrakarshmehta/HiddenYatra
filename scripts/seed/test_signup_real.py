"""Test full signup + OTP flow with unique credentials."""
import requests
import re
import sys
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://127.0.0.1:5000'
s = requests.Session()

uname = "qa_user_777"
email = "qa_user_777@example.com"

# Clean up before testing
conn = pymysql.connect(host='localhost', user='root', database='hiddenyatra', cursorclass=pymysql.cursors.DictCursor)
with conn.cursor() as cur:
    cur.execute("DELETE FROM users WHERE username=%s OR email=%s", (uname, email))
conn.commit()
conn.close()

# 1. GET signup page
r = s.get(f'{BASE}/signup')
token = re.search(r'name="_csrf_token" value="([^"]+)"', r.text).group(1)

# 2. POST signup form
data = {
    '_csrf_token': token,
    'full_name': 'QA Automated Test',
    'username': uname,
    'email': email,
    'password': 'Password123',
    'confirm_password': 'Password123',
}
r2 = s.post(f'{BASE}/signup', data=data, allow_redirects=False)
print(f"1. POST /signup status: {r2.status_code}")
print(f"   Redirect Location: {r2.headers.get('Location')}")

if r2.status_code == 302 and r2.headers.get('Location') == '/verify-email':
    print("   ✅ SIGNUP SUCCESS: Redirected to /verify-email")

# 3. Inspect DB for newly registered pending user
conn = pymysql.connect(host='localhost', user='root', database='hiddenyatra', cursorclass=pymysql.cursors.DictCursor)
with conn.cursor() as cur:
    cur.execute("SELECT id, username, email, status, email_verified, otp_code, otp_expires_at, otp_purpose FROM users WHERE username=%s", (uname,))
    user = cur.fetchone()
    print("2. DATABASE RECORD AFTER SIGNUP:")
    print("  ", user)

conn.close()
