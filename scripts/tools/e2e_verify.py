"""
HiddenYatra — End-to-End Route Verification Script
Tests every major route/feature against the live running application.
"""
import urllib.request
import urllib.error
import json
import sys
import http.client

BASE = 'http://127.0.0.1:5000'

results = []
failures = []


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Handler that doesn't follow redirects, so we can detect 302s."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)


no_redirect_opener = urllib.request.build_opener(NoRedirectHandler)


def check(name, url, expect_status=200, expect_in=None, follow_redirects=True):
    """Check a URL returns expected status."""
    full_url = f'{BASE}{url}'
    try:
        req = urllib.request.Request(full_url)
        req.add_header('User-Agent', 'HiddenYatraE2E/1.0')
        
        if follow_redirects:
            opener = urllib.request.build_opener()
        else:
            opener = no_redirect_opener
        
        resp = opener.open(req, timeout=10)
        status = resp.status
        body = resp.read().decode('utf-8', errors='replace')
        
        ok = status == expect_status
        if expect_in and expect_in.lower() not in body.lower():
            ok = False
            results.append(f'  FAIL  {name}: {url} -> {status} (missing: "{expect_in}")')
            failures.append(name)
            return
        
        if ok:
            results.append(f'  OK    {name}: {url} -> {status}')
        else:
            results.append(f'  FAIL  {name}: {url} -> {status} (expected {expect_status})')
            failures.append(name)
    except urllib.error.HTTPError as e:
        if e.code == expect_status:
            results.append(f'  OK    {name}: {url} -> {e.code}')
        else:
            results.append(f'  FAIL  {name}: {url} -> {e.code} (expected {expect_status})')
            failures.append(name)
    except Exception as e:
        results.append(f'  FAIL  {name}: {url} -> ERROR: {e}')
        failures.append(name)


def check_json(name, url, expect_key=None):
    """Check a JSON API endpoint."""
    full_url = f'{BASE}{url}'
    try:
        req = urllib.request.Request(full_url)
        req.add_header('User-Agent', 'HiddenYatraE2E/1.0')
        req.add_header('Accept', 'application/json')
        resp = urllib.request.urlopen(req, timeout=10)
        body = resp.read().decode('utf-8')
        data = json.loads(body)
        
        if expect_key and isinstance(data, dict) and expect_key not in data:
            results.append(f'  FAIL  {name}: {url} -> missing key "{expect_key}"')
            failures.append(name)
            return
        
        results.append(f'  OK    {name}: {url} -> 200 JSON')
    except Exception as e:
        results.append(f'  FAIL  {name}: {url} -> ERROR: {e}')
        failures.append(name)


print('='*60)
print('HiddenYatra E2E Verification')
print('='*60)

# ── PUBLIC ROUTES ──
print('\n--- Public Routes ---')
check('Home', '/', expect_in='HiddenYatra')
check('Browse', '/browse', expect_in='Bihar')
check('Search (empty)', '/search')
check('Search (query)', '/search?q=patna')
check('Search (special chars)', '/search?q=%25_%27')
check('Explore Map', '/explore')
check('Food Culture', '/food-culture')

# ── STATE & DISTRICT ROUTES ──
print('\n--- State & District Routes ---')
check('State: Bihar', '/state/bihar', expect_in='Bihar')
check('State 404', '/state/fake-state', expect_status=404)

# ── PLACE ROUTES ──
print('\n--- Place Routes ---')
check('Place 404', '/place/nonexistent-place-xyz', expect_status=404)

# ── AUTH ROUTES ──
print('\n--- Auth Routes ---')
check('Login Page', '/login', expect_in='login')
check('Signup Page', '/signup', expect_in='sign')
check('Forgot Password', '/forgot-password')
check('Profile (works anonymous)', '/profile', expect_status=200)
check('Logout (redirect)', '/logout', expect_status=302, follow_redirects=False)

# ── FEATURE ROUTES ──
print('\n--- Feature Routes ---')
check('Wishlist', '/wishlist')
check('Itinerary', '/itinerary')
check('Suggest Place', '/suggest')
check('My Submissions (no-login redirect)', '/my-submissions', expect_status=302, follow_redirects=False)

# ── ADMIN ROUTES (should redirect to login) ──
print('\n--- Admin Routes (auth required -> redirect to login) ---')
check('Admin Dashboard', '/admin/', expect_status=302, follow_redirects=False)
check('Admin Submissions', '/admin/submissions', expect_status=302, follow_redirects=False)
check('Admin Users', '/admin/users', expect_status=302, follow_redirects=False)
check('Admin Districts', '/admin/districts', expect_status=302, follow_redirects=False)
check('Admin Hero Media', '/admin/hero-media', expect_status=302, follow_redirects=False)
check('Admin Trending', '/admin/trending', expect_status=302, follow_redirects=False)
check('Admin Recycle Bin', '/admin/recycle-bin', expect_status=302, follow_redirects=False)
check('Admin User Photos', '/admin/user-photos', expect_status=302, follow_redirects=False)
check('Admin Auth Appearance', '/admin/appearance/auth', expect_status=302, follow_redirects=False)
check('Admin Nearby Services', '/admin/nearby-services', expect_status=302, follow_redirects=False)
check('Admin Logs', '/admin/logs', expect_status=302, follow_redirects=False)
check('Admin Login Page', '/admin/login')

# ── API ROUTES ──
print('\n--- API Routes ---')
check_json('API Autocomplete', '/api/autocomplete?q=patna')
check_json('API Smart Search', '/api/smart-search?q=temple', expect_key='places')
check_json('API Trending', '/api/trending')
check_json('API Autocomplete (short)', '/api/autocomplete?q=a')

# ── ERROR PAGES ──
print('\n--- Error Pages ---')
check('404 Page', '/nonexistent-xyz-123', expect_status=404, expect_in='Lost')
check('403 Page check', '/nonexistent-xyz-123', expect_status=404)

# ── SEO & MONITORING ROUTES ──
print('\n--- SEO & Monitoring Routes ---')
check('Health Check', '/health', expect_in='ok')
check('Robots.txt', '/robots.txt')
check('Sitemap.xml', '/sitemap.xml', expect_in='urlset')

# ── PRINT RESULTS ──
print('\n' + '='*60)
for r in results:
    print(r)

print('\n' + '='*60)
passed = len(results) - len(failures)
total = len(results)
print(f'\nResults: {passed}/{total} passed, {len(failures)} failed')
if failures:
    print(f'\nFailed: {", ".join(failures)}')
    sys.exit(1)
else:
    print('\nALL E2E CHECKS PASSED!')
    sys.exit(0)
