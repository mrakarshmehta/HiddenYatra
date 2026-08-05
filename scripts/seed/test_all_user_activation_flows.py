"""
End-to-End Test Suite for User Activation & Auth Workflow.
Verifies Tests 1-5 requested by user specifications.
"""
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

def get_db():
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DB', 'hiddenyatra'),
        cursorclass=pymysql.cursors.DictCursor
    )

uname = "wf_qa_test_user"
email = "wf_qa_test_user@example.com"
password = "WorkflowPassword123"

print("=========================================================")
print("RUNNING END-TO-END ACTIVATION WORKFLOW VERIFICATION SUITE")
print("=========================================================\n")

# Clean previous test user
conn = get_db()
with conn.cursor() as cur:
    cur.execute("DELETE FROM users WHERE username=%s OR email=%s", (uname, email))
conn.commit()
conn.close()

# ---------------------------------------------------------
# TEST 1: Signup -> OTP -> Verify -> DB Active & Verified -> Auto Login
# ---------------------------------------------------------
print("--- TEST 1: Signup -> OTP -> Verify -> Auto Login ---")
with client:
    res = client.get('/signup')
    with client.session_transaction() as sess:
        csrf_token = sess.get('_csrf_token')

    signup_res = client.post('/signup', data={
        '_csrf_token': csrf_token,
        'full_name': 'Workflow QA User',
        'username': uname,
        'email': email,
        'password': password,
        'confirm_password': password
    })
    
    # Check DB for pending user and OTP
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id, status, email_verified, otp_code FROM users WHERE username=%s", (uname,))
        user_row = cur.fetchone()
    conn.close()

    user_id = user_row['id']
    otp_code = user_row['otp_code']
    
    # Submit OTP verification
    with client.session_transaction() as sess:
        sess['pending_user_id'] = user_id
        sess['pending_email'] = email
        csrf_token = sess.get('_csrf_token')

    verify_res = client.post('/verify-email', data={'_csrf_token': csrf_token, 'otp': otp_code})
    
    # Check DB state after OTP verify
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT status, email_verified, otp_code FROM users WHERE id=%s", (user_id,))
        verified_row = cur.fetchone()
    conn.close()

    # Check session
    with client.session_transaction() as sess:
        session_user_id = sess.get('user_id')

    test1_pass = (
        verified_row['status'] == 'active' and
        verified_row['email_verified'] == 1 and
        verified_row['otp_code'] is None and
        session_user_id == user_id
    )
    
    print(f"  DB Status: '{verified_row['status']}'")
    print(f"  DB Email Verified: {verified_row['email_verified']}")
    print(f"  DB OTP Code: {verified_row['otp_code']}")
    print(f"  Session User ID: {session_user_id}")
    print(f"TEST 1 RESULT: {'PASS' if test1_pass else 'FAIL'}\n")

# ---------------------------------------------------------
# TEST 2: Login with Verified Account
# ---------------------------------------------------------
print("--- TEST 2: Login with Verified Account ---")
client_t2 = app.test_client()
with client_t2:
    client_t2.get('/login')
    with client_t2.session_transaction() as sess:
        csrf_token = sess.get('_csrf_token')
    
    login_res = client_t2.post('/login', data={
        '_csrf_token': csrf_token,
        'email': email,
        'password': password
    })
    
    with client_t2.session_transaction() as sess:
        logged_in_id = sess.get('user_id')

    test2_pass = (login_res.status_code == 302 and logged_in_id == user_id)
    print(f"  Login POST Status: {login_res.status_code}")
    print(f"  Logged In Session User ID: {logged_in_id}")
    print(f"TEST 2 RESULT: {'PASS' if test2_pass else 'FAIL'}\n")

# ---------------------------------------------------------
# TEST 3: Admin Panel Display & Action Buttons
# ---------------------------------------------------------
print("--- TEST 3: Admin Panel Display & Action Buttons ---")
client_t3 = app.test_client()
with client_t3:
    client_t3.get('/login')
    with client_t3.session_transaction() as sess:
        sess['admin_logged_in'] = True
        csrf_token = sess.get('_csrf_token')

    users_res = client_t3.get('/admin/users')
    
    status_active_present = "✅ Active" in users_res.text
    email_verified_present = "✅" in users_res.text
    
    # Check if activate button is hidden for active user
    user_activate_btn_pattern = f'action="/admin/users/{user_id}/status"[^>]*>\\s*<input[^>]*name="_csrf_token"[^>]*>\\s*<input[^>]*value="active"'
    activate_btn_found = bool(re.search(user_activate_btn_pattern, users_res.text))

    test3_pass = (status_active_present and email_verified_present and not activate_btn_found)
    print(f"  Admin Page Status 'Active' Shown: {status_active_present}")
    print(f"  Admin Page Verified 'Yes' Shown: {email_verified_present}")
    print(f"  Activate Button Hidden for Active User: {not activate_btn_found}")
    print(f"TEST 3 RESULT: {'PASS' if test3_pass else 'FAIL'}\n")

# ---------------------------------------------------------
# TEST 4: Suspend User -> Login Blocked
# ---------------------------------------------------------
print("--- TEST 4: Suspend User -> Login Blocked ---")
client_t4 = app.test_client()
with client_t4:
    client_t4.get('/login')
    with client_t4.session_transaction() as sess:
        sess['admin_logged_in'] = True
        csrf_token = sess.get('_csrf_token')

    suspend_res = client_t4.post(f'/admin/users/{user_id}/status', data={'_csrf_token': csrf_token, 'status': 'suspended'})
    
    # Verify DB status
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT status FROM users WHERE id=%s", (user_id,))
        suspended_row = cur.fetchone()
    conn.close()

    # User attempts login
    client_user_suspend = app.test_client()
    client_user_suspend.get('/login')
    with client_user_suspend.session_transaction() as sess:
        csrf_token = sess.get('_csrf_token')

    login_suspended_res = client_user_suspend.post('/login', data={
        '_csrf_token': csrf_token,
        'email': email,
        'password': password
    })
    
    with client_user_suspend.session_transaction() as sess:
        session_id_after_suspend_login = sess.get('user_id')

    test4_pass = (
        suspended_row['status'] == 'suspended' and
        login_suspended_res.status_code == 200 and
        session_id_after_suspend_login is None
    )
    print(f"  DB Status: '{suspended_row['status']}'")
    print(f"  Login POST Status: {login_suspended_res.status_code} (200 = blocked with flash message)")
    print(f"  Session User ID (should be None): {session_id_after_suspend_login}")
    print(f"TEST 4 RESULT: {'PASS' if test4_pass else 'FAIL'}\n")

# ---------------------------------------------------------
# TEST 5: Activate Suspended User -> Login Works Again
# ---------------------------------------------------------
print("--- TEST 5: Activate Suspended User -> Login Works Again ---")
client_t5 = app.test_client()
with client_t5:
    client_t5.get('/login')
    with client_t5.session_transaction() as sess:
        sess['admin_logged_in'] = True
        csrf_token = sess.get('_csrf_token')

    reactivate_res = client_t5.post(f'/admin/users/{user_id}/status', data={'_csrf_token': csrf_token, 'status': 'active'})
    
    # Verify DB status
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT status, email_verified FROM users WHERE id=%s", (user_id,))
        reactivated_row = cur.fetchone()
    conn.close()

    # User attempts login
    client_user_reactivated = app.test_client()
    client_user_reactivated.get('/login')
    with client_user_reactivated.session_transaction() as sess:
        csrf_token = sess.get('_csrf_token')

    login_reactivated_res = client_user_reactivated.post('/login', data={
        '_csrf_token': csrf_token,
        'email': email,
        'password': password
    })
    
    with client_user_reactivated.session_transaction() as sess:
        session_id_after_reactivate_login = sess.get('user_id')

    test5_pass = (
        reactivated_row['status'] == 'active' and
        reactivated_row['email_verified'] == 1 and
        login_reactivated_res.status_code == 302 and
        session_id_after_reactivate_login == user_id
    )
    print(f"  DB Status: '{reactivated_row['status']}'")
    print(f"  DB Email Verified: {reactivated_row['email_verified']}")
    print(f"  Login POST Status: {login_reactivated_res.status_code}")
    print(f"  Session User ID: {session_id_after_reactivate_login}")
    print(f"TEST 5 RESULT: {'PASS' if test5_pass else 'FAIL'}\n")

# Summary
print("=========================================================")
print("FINAL TEST RESULTS SUMMARY:")
print(f"  Test 1 (Signup -> OTP -> Verify -> Auto Login): {'PASS' if test1_pass else 'FAIL'}")
print(f"  Test 2 (Login Verified Account): {'PASS' if test2_pass else 'FAIL'}")
print(f"  Test 3 (Admin Panel Display & Buttons): {'PASS' if test3_pass else 'FAIL'}")
print(f"  Test 4 (Suspend User -> Login Blocked): {'PASS' if test4_pass else 'FAIL'}")
print(f"  Test 5 (Activate Suspended User -> Login Works): {'PASS' if test5_pass else 'FAIL'}")
print("=========================================================")
