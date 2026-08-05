"""Debug the 8 failing routes."""
import requests
import pymysql

BASE = "http://127.0.0.1:5000"

c = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='',
                    database='hiddenyatra', cursorclass=pymysql.cursors.DictCursor)
cur = c.cursor()

print("=== DEBUGGING FAILED ROUTES ===\n")

# 1. Browse page - check why no place cards
r = requests.get(f"{BASE}/browse")
print(f"Browse: HTTP {r.status_code}, length={len(r.text)}")
if "place-card" not in r.text:
    print("  No 'place-card' class found. Checking actual content...")
    # Check for other card patterns
    for pattern in ["card", "place_card", "placeCard", "place-item", "grid"]:
        count = r.text.count(pattern)
        if count:
            print(f"  Found '{pattern}': {count} times")

# 2. District page - find correct URL pattern
for url in ["/district/patna", "/state/bihar/patna", "/district/1", "/districts/patna"]:
    r = requests.get(f"{BASE}{url}")
    print(f"  {url}: HTTP {r.status_code}")

# 3. Mahabodhi - check slug
cur.execute("SELECT id, slug, name FROM places WHERE name LIKE '%Mahabodhi%'")
row = cur.fetchone()
print(f"\nMahabodhi in DB: {row}")

if row:
    slug = row['slug']
    r = requests.get(f"{BASE}/place/{slug}")
    print(f"  /place/{slug}: HTTP {r.status_code}")
    if r.status_code == 500:
        # Find the error in the HTML
        import re
        error = re.search(r"(TypeError|KeyError|AttributeError|OperationalError)[^<]+", r.text)
        if error:
            print(f"  ERROR: {error.group(0)[:200]}")
        else:
            print(f"  Response first 300 chars: {r.text[:300]}")

# 4. Check for Decimal issues in other queries
cur.execute("SELECT id, name, latitude, longitude FROM places WHERE id = %s", (row['id'],))
place = cur.fetchone()
print(f"\nPlace data types: lat={type(place['latitude'])}, lng={type(place['longitude'])}")

# 5. API routes - find correct prefix
for url in ["/api/states", "/api/v1/states", "/api/places", "/api/v1/places"]:
    r = requests.get(f"{BASE}{url}")
    print(f"  {url}: HTTP {r.status_code}")

# 6. Admin places
s = requests.Session()
r = s.get(f"{BASE}/admin/login")
import re
csrf = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', r.text)
if csrf:
    s.post(f"{BASE}/admin/login", data={"password": "admin@hidden123", "csrf_token": csrf.group(1)})

for url in ["/admin/places", "/admin/", "/admin/hero-media"]:
    r = s.get(f"{BASE}{url}")
    print(f"  {url}: HTTP {r.status_code}")
    if url == "/admin/hero-media":
        has_hero = "hero" in r.text.lower()
        print(f"    Contains 'hero': {has_hero}")
        # Check what text IS there
        title = re.search(r"<title>([^<]+)</title>", r.text)
        if title:
            print(f"    Page title: {title.group(1)}")

c.close()
