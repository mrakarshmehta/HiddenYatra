"""Test signup flow via HTTP requests (UTF-8 encoding output)."""
import requests
import re
import sys

# Force UTF-8 output for Windows console
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://127.0.0.1:5000'
s = requests.Session()

# Step 1: GET signup page
r = s.get(f'{BASE}/signup')
print(f"GET /signup: {r.status_code}")

# Extract CSRF token
csrf_match = re.search(r'name="_csrf_token" value="([^"]+)"', r.text)
token = csrf_match.group(1) if csrf_match else ''
print(f"CSRF token found: {bool(token)}")

# Step 2: POST signup
data = {
    '_csrf_token': token,
    'full_name': 'QA Test User',
    'username': 'qatest2026',
    'email': 'testqa@example.com',
    'password': 'TestPass123',
    'confirm_password': 'TestPass123',
}
r2 = s.post(f'{BASE}/signup', data=data, allow_redirects=False)
print(f"POST /signup Status: {r2.status_code}")
print(f"Location header: {r2.headers.get('Location', 'NONE')}")

if r2.status_code == 302:
    redirect_url = r2.headers['Location']
    print(f"SUCCESS - Redirected to: {redirect_url}")
    r3 = s.get(f'{BASE}{redirect_url}' if redirect_url.startswith('/') else redirect_url)
    print(f"Redirected Page Status: {r3.status_code}")
    print(f"Redirected Page URL: {r3.url}")
else:
    print(f"Response Page Content Snippet:\n{r2.text[:500]}")
