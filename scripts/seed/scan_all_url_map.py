"""
Scan EVERY rule registered in Flask app.url_map for 500 errors.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app

app = create_app()
app.testing = True
client = app.test_client()

print("=========================================================")
print("SCANNING EVERY FLASK URL_MAP RULE...")
print("=========================================================\n")

errors = []

# Populate test params for dynamic routes (<int:id>, <slug>, etc.)
sample_params = {
    'place_slug': 'golghar',
    'state_slug': 'bihar',
    'district_slug': 'buxar',
    'place_id': 1,
    'user_id': 1,
    'itinerary_id': 1,
    'submission_id': 1,
    'photo_id': 1,
    'district_id': 1,
    'block_id': 1,
    'id': 1,
}

for rule in app.url_map.iter_rules():
    if 'GET' not in rule.methods:
        continue
    
    # Construct test URL
    url = rule.rule
    for param in rule.arguments:
        val = sample_params.get(param, 1)
        url = url.replace(f'<{param}>', str(val)).replace(f'<int:{param}>', str(val)).replace(f'<string:{param}>', str(val))
    
    try:
        res = client.get(url)
        if res.status_code == 500:
            print(f"❌ 500 ERROR on {rule.endpoint} -> {url}")
            errors.append((rule.endpoint, url, "500 Status"))
        else:
            print(f"  {url} ({rule.endpoint}) -> {res.status_code}")
    except Exception as e:
        import traceback
        print(f"\n❌ EXCEPTION on {rule.endpoint} -> {url}:")
        traceback.print_exc()
        errors.append((rule.endpoint, url, str(e)))

# Now repeat for Admin authenticated
with client.session_transaction() as sess:
    sess['admin_logged_in'] = True

for rule in app.url_map.iter_rules():
    if 'GET' not in rule.methods or not rule.rule.startswith('/admin'):
        continue
    
    url = rule.rule
    for param in rule.arguments:
        val = sample_params.get(param, 1)
        url = url.replace(f'<{param}>', str(val)).replace(f'<int:{param}>', str(val)).replace(f'<string:{param}>', str(val))
    
    try:
        res = client.get(url)
        if res.status_code == 500:
            print(f"❌ 500 ERROR [Admin] on {rule.endpoint} -> {url}")
            errors.append((rule.endpoint, url, "500 Status [Admin]"))
        else:
            print(f"  [Admin] {url} ({rule.endpoint}) -> {res.status_code}")
    except Exception as e:
        import traceback
        print(f"\n❌ EXCEPTION [Admin] on {rule.endpoint} -> {url}:")
        traceback.print_exc()
        errors.append((rule.endpoint, url, str(e)))

print("\n=========================================================")
print(f"SCAN COMPLETE. Total 500 Errors Found: {len(errors)}")
print("=========================================================")
