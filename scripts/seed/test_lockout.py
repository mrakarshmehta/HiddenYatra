"""Test account lockout after 5 failed login attempts."""
import os
import sys
import re
import pymysql

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app

app = create_app()
app.testing = True
client = app.test_client()

email = "e2e_qa_tester@example.com"

# First logout
with client:
    res = client.get('/login')
    csrf_token = re.search(r'name="_csrf_token" value="([^"]+)"', res.text).group(1)
    
    print("Submitting 5 wrong passwords...")
    for i in range(1, 6):
        res_fail = client.post('/login', data={'_csrf_token': csrf_token, 'email': email, 'password': f'WrongPass{i}'})
        print(f" Attempt {i}: Status {res_fail.status_code}")

    # Check DB
    conn = pymysql.connect(host='localhost', user='root', database='hiddenyatra', cursorclass=pymysql.cursors.DictCursor)
    with conn.cursor() as cur:
        cur.execute("SELECT failed_login_count, locked_until FROM users WHERE email=%s", (email,))
        row = cur.fetchone()
    conn.close()

    print("\nDatabase Account Lock State:")
    print("  Failed Login Count:", row.get('failed_login_count'))
    print("  Locked Until:", row.get('locked_until'))
    
    # Attempt 6th login (should be locked)
    res_lock = client.post('/login', data={'_csrf_token': csrf_token, 'email': email, 'password': 'WrongPass6'})
    print("\n6th Attempt Status (while locked):", res_lock.status_code)
