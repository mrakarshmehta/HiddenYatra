"""
Script to scan ALL registered routes in HiddenYatra and detect any 500 Internal Server Error.
Captures exact exception tracebacks.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app

app = create_app()
app.testing = True  # Propagate exceptions
client = app.test_client()

print("=========================================================")
print("SCANNING ALL REGISTERED ROUTES FOR 500 ERRORS...")
print("=========================================================\n")

errors_found = []

# List of sample URLs across all blueprints
test_urls = [
    '/',
    '/browse',
    '/explore',
    '/food-culture',
    '/search',
    '/search?q=patna',
    '/place/golghar',
    '/state/bihar',
    '/state/bihar/buxar',
    '/itinerary',
    '/wishlist',
    '/suggest',
    '/suggest-place',
    '/login',
    '/signup',
    '/forgot-password',
    '/reset-password',
    '/verify-email',
    '/profile',
    '/robots.txt',
    '/sitemap.xml',
    '/health',
    '/api/autocomplete?q=Gol',
    '/api/smart-search?q=Patna',
    '/api/search/nl?q=waterfalls',
    '/community',
]

# Admin URLs (with admin session)
admin_urls = [
    '/admin/',
    '/admin/places',
    '/admin/districts',
    '/admin/users',
    '/admin/submissions',
    '/admin/trending',
    '/admin/hero-media',
]

# 1. Test Public / User Routes
for url in test_urls:
    try:
        res = client.get(url)
        if res.status_code == 500:
            print(f"❌ 500 ERROR FOUND on: {url}")
            errors_found.append((url, "500 Status Code"))
        else:
            print(f"  {url} -> {res.status_code}")
    except Exception as e:
        import traceback
        print(f"\n❌ EXCEPTION TRIPPED on GET {url}:")
        traceback.print_exc()
        errors_found.append((url, str(e)))

# 2. Test Admin Routes
with client.session_transaction() as sess:
    sess['admin_logged_in'] = True

for url in admin_urls:
    try:
        res = client.get(url)
        if res.status_code == 500:
            print(f"❌ 500 ERROR FOUND on: {url}")
            errors_found.append((url, "500 Status Code"))
        else:
            print(f"  [Admin] {url} -> {res.status_code}")
    except Exception as e:
        import traceback
        print(f"\n❌ EXCEPTION TRIPPED on GET {url}:")
        traceback.print_exc()
        errors_found.append((url, str(e)))

print("\n=========================================================")
print(f"SCAN COMPLETE. Total 500 Errors Found: {len(errors_found)}")
print("=========================================================")
