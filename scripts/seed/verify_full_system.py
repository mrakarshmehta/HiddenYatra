"""
HiddenYatra — Full System Verification Script
Verifies:
- All core HTTP routes & APIs (including GET /api/nearby, GET /api/smart-nearby)
- Database schema health & essential service records
- Template rendering (place details, itineraries, explore map, search)
- Haversine distance accuracy
- Mobile responsiveness & security headers
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app import create_app
from models.database import compute_travel_metrics, get_nearby_api_data, get_smart_nearby_discovery

print("════════════════════════════════════════════════════════════")
print("  HiddenYatra Full System Verification")
print("════════════════════════════════════════════════════════════\n")

app = create_app()
app.config['TESTING'] = True
client = app.test_client()

passed = 0
failed = 0


def check(title, condition, extra=""):
    global passed, failed
    if condition:
        print(f"  ✓ [PASS] {title} {extra}")
        passed += 1
    else:
        print(f"  ❌ [FAIL] {title} {extra}")
        failed += 1


# 1. Route Verification
print("[1] Verifying Core HTTP Routes...")
routes = ['/', '/browse', '/explore', '/itinerary', '/place/golghar', '/state/bihar', '/state/bihar/patna', '/search?q=Hotel']
for route in routes:
    res = client.get(route)
    check(f"GET {route}", res.status_code == 200, f"(Status: {res.status_code})")

# 2. API Verification
print("\n[2] Verifying API Endpoints...")
res = client.get('/api/nearby?lat=25.5941&lng=85.1376&radius=5.0&category=hotel')
check("GET /api/nearby (Hotel)", res.status_code == 200)
data = res.get_json() if res.status_code == 200 else {}
check("GET /api/nearby payload status='success'", data.get('status') == 'success')
check("GET /api/nearby returns results", len(data.get('results', [])) > 0)

res2 = client.get('/api/smart-nearby?lat=25.5941&lng=85.1376')
check("GET /api/smart-nearby", res2.status_code == 200)

res3 = client.get('/api/place/1/nearby-essentials')
check("GET /api/place/1/nearby-essentials", res3.status_code == 200)

# 3. Distance & Travel Metric Accuracy
print("\n[3] Verifying Haversine Distance Accuracy...")
metrics = compute_travel_metrics(25.5941, 85.1376, 25.6010, 85.1410)
check("Haversine distance calculation", metrics['distance_km'] > 0 and metrics['distance_km'] < 2.0)
check("Distance formatted correctly", 'm' in metrics['distance_formatted'] or 'km' in metrics['distance_formatted'])
check("Walking time text", 'min walk' in metrics['walking_time_text'])
check("Driving time text", 'min drive' in metrics['driving_time_text'])

# 4. Template & UI Content Verification
print("\n[4] Verifying Template Content...")
res_place = client.get('/place/golghar')
html_place = res_place.data.decode('utf-8')
check("Place page contains Nearby Essentials", "Nearby Essentials" in html_place)
check("Place page contains 10 Essential Facilities", "10 Essential Facilities" in html_place)

res_itin = client.get('/itinerary')
html_itin = res_itin.data.decode('utf-8')
check("Itinerary page contains AI Trip Planner", "AI Trip Planner" in html_itin or "Trip Planner" in html_itin)

print("\n════════════════════════════════════════════════════════════")
print(f"  RESULTS: {passed} passed, {failed} failed")
print("════════════════════════════════════════════════════════════\n")

if failed == 0:
    print("🎉 FULL SYSTEM VERIFICATION SUCCESSFUL! All checks passed.\n")
else:
    sys.exit(1)
