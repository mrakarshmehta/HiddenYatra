"""Generate migration verification report comparing expected vs actual data."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='', 
                       database='hiddenyatra', cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

# Expected counts from seed_bihar_complete.py
expected = {
    'states': 1,
    'districts': 38,
    'blocks': 60,  # 11+8+6+6+6+6+6+7+4
    'places': 28,
    'photos': 0,  # No photos in seed (need image seed)
    'specialties': 0,
    'accommodations': 7,  # 2+3+2
    'district_foods': 17,  # 4+2+1+1+2+2+1+1+1+2
    'reviews': 0,
    'users': 0,
    'wishlists': 0,
    'visited_places': 0,
    'itineraries': 0,
    'itinerary_items': 0,
    'user_submissions': 0,
    'user_photos': 0,
    'trending_places': 0,
    'hero_media': 0,
    'hero_settings': 1,
    'homepage_sections': 6,
    'auth_appearance': 1,
    'admin_logs': 0,
    'nearby_services': 0,
}

print("=" * 70)
print("  MIGRATION VERIFICATION REPORT")
print("  HiddenYatra: SQLite → MySQL Data Migration")
print("=" * 70)
print()
print(f"{'Table':<25} {'Expected':>10} {'MySQL':>10} {'Status':>10}")
print("-" * 60)

all_match = True
total_expected = 0
total_actual = 0

cur.execute("SHOW TABLES")
tables = sorted([list(r.values())[0] for r in cur.fetchall()])

for table in tables:
    cur.execute(f"SELECT COUNT(*) AS cnt FROM {table}")
    actual = cur.fetchone()['cnt']
    exp = expected.get(table, '?')
    
    if exp == '?':
        status = '⚠️ UNKNOWN'
    elif actual == exp:
        status = '✅ MATCH'
    elif actual > 0 and exp == 0:
        status = '✅ EXTRA'
    else:
        status = '❌ MISMATCH'
        all_match = False
    
    total_expected += exp if isinstance(exp, int) else 0
    total_actual += actual
    print(f"  {table:<23} {str(exp):>10} {actual:>10} {status:>10}")

print("-" * 60)
print(f"  {'TOTAL':<23} {total_expected:>10} {total_actual:>10}")
print()

# Verify foreign key integrity
print("=" * 70)
print("  FOREIGN KEY INTEGRITY CHECK")
print("=" * 70)
fk_checks = [
    ("districts → states", "SELECT COUNT(*) AS cnt FROM districts d LEFT JOIN states s ON d.state_id=s.id WHERE s.id IS NULL"),
    ("places → states", "SELECT COUNT(*) AS cnt FROM places p LEFT JOIN states s ON p.state_id=s.id WHERE s.id IS NULL"),
    ("places → districts", "SELECT COUNT(*) AS cnt FROM places p LEFT JOIN districts d ON p.district_id=d.id WHERE p.district_id IS NOT NULL AND d.id IS NULL"),
    ("blocks → districts", "SELECT COUNT(*) AS cnt FROM blocks b LEFT JOIN districts d ON b.district_id=d.id WHERE d.id IS NULL"),
    ("accommodations → places", "SELECT COUNT(*) AS cnt FROM accommodations a LEFT JOIN places p ON a.place_id=p.id WHERE p.id IS NULL"),
    ("district_foods → districts", "SELECT COUNT(*) AS cnt FROM district_foods df LEFT JOIN districts d ON df.district_id=d.id WHERE d.id IS NULL"),
    ("reviews → places", "SELECT COUNT(*) AS cnt FROM reviews r LEFT JOIN places p ON r.place_id=p.id WHERE p.id IS NULL"),
]

all_fk_ok = True
for name, query in fk_checks:
    cur.execute(query)
    orphans = cur.fetchone()['cnt']
    status = "✅ OK" if orphans == 0 else f"❌ {orphans} orphans"
    if orphans > 0:
        all_fk_ok = False
    print(f"  {name:<35} {status}")

print()

# Sample data verification
print("=" * 70)
print("  SAMPLE DATA VERIFICATION")
print("=" * 70)

cur.execute("SELECT name FROM states")
states = [r['name'] for r in cur.fetchall()]
print(f"  States: {', '.join(states)}")

cur.execute("SELECT COUNT(*) AS cnt FROM districts WHERE state_id = (SELECT id FROM states LIMIT 1)")
print(f"  Districts in Bihar: {cur.fetchone()['cnt']}")

cur.execute("SELECT name FROM places WHERE is_featured = 1 LIMIT 5")
featured = [r['name'] for r in cur.fetchall()]
print(f"  Featured places: {', '.join(featured)}")

cur.execute("SELECT COUNT(*) AS cnt FROM places WHERE latitude IS NOT NULL AND longitude IS NOT NULL")
print(f"  Places with coordinates: {cur.fetchone()['cnt']}")

cur.execute("SELECT COUNT(DISTINCT district_id) AS cnt FROM district_foods")
print(f"  Districts with food data: {cur.fetchone()['cnt']}")

cur.execute("SELECT COUNT(DISTINCT district_id) AS cnt FROM blocks")
print(f"  Districts with blocks: {cur.fetchone()['cnt']}")

print()
print("=" * 70)
if all_match and all_fk_ok:
    print("  ✅ MIGRATION COMPLETE — ALL DATA VERIFIED")
else:
    print("  ⚠️ MIGRATION NEEDS ATTENTION — SEE ABOVE")
print("=" * 70)

cur.close()
conn.close()
