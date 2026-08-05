"""Print flash messages from signup POST response."""
import requests
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://127.0.0.1:5000'
s = requests.Session()

r = s.get(f'{BASE}/signup')
token = re.search(r'name="_csrf_token" value="([^"]+)"', r.text).group(1)

data = {
    '_csrf_token': token,
    'full_name': 'QA Test User',
    'username': 'qatest2026',
    'email': 'testqa@example.com',
    'password': 'TestPass123',
    'confirm_password': 'TestPass123',
}
r2 = s.post(f'{BASE}/signup', data=data)
print(f"Status: {r2.status_code}")
print(f"Final URL: {r2.url}")

# Find flash messages or errors
flashes = re.findall(r'<div class="flash-message[^"]*">(.*?)</div>', r2.text, re.DOTALL)
print("Flashes:", [f.strip() for f in flashes])

# Find form input hints/errors
hints = re.findall(r'<div class="input-hint[^"]*">(.*?)</div>', r2.text, re.DOTALL)
print("Hints:", [h.strip() for h in hints])
