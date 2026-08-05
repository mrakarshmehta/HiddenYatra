"""Migrate Haldia Dam place and its photos from SQLite to MySQL."""
import sqlite3
import pymysql

s = sqlite3.connect(r"D:\HiddenYatra\bharat_darshan_recovered.db")
s.row_factory = sqlite3.Row
sc = s.cursor()

m = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='',
                    database='hiddenyatra', cursorclass=pymysql.cursors.DictCursor)
mc = m.cursor()

# Get Haldia Dam from SQLite
sc.execute("SELECT * FROM places WHERE name = ?", ("Haldia Dam",))
row = sc.fetchone()
cols = [d[0] for d in sc.description]

# Get MySQL column info
mc.execute("DESCRIBE places")
mysql_cols = {r['Field']: r for r in mc.fetchall()}

# Map district_id
sc.execute("SELECT name FROM districts WHERE id = ?", (row['district_id'],))
dist = sc.fetchone()
dist_name = dist['name'] if dist else None
print(f"District: {dist_name}")

new_dist_id = None
if dist_name:
    mc.execute("SELECT id FROM districts WHERE name = %s", (dist_name,))
    r = mc.fetchone()
    new_dist_id = r['id'] if r else None
print(f"MySQL district_id: {new_dist_id}")

# Map state_id
sc.execute("SELECT name FROM states WHERE id = ?", (row['state_id'],))
st = sc.fetchone()
mc.execute("SELECT id FROM states WHERE name = %s", (st['name'],))
new_state_id = mc.fetchone()['id']

# Build insert - skip id, block_id (NULL), state_id, district_id (remapped)
skip_cols = {'id', 'block_id', 'state_id', 'district_id'}
common = [c for c in cols if c in mysql_cols and c not in skip_cols]

values = [new_state_id, new_dist_id]
for c in common:
    v = row[c]
    info = mysql_cols.get(c, {})
    if v is None and info.get('Null') == 'NO':
        t = info.get('Type', '')
        v = 0 if 'int' in t else (0.0 if 'decimal' in t or 'float' in t else '')
    values.append(v)

col_names = ['state_id', 'district_id'] + [c for c in common]
col_str = ', '.join([f'`{c}`' for c in col_names])
ph = ', '.join(['%s'] * len(col_names))

mc.execute(f"INSERT INTO places ({col_str}) VALUES ({ph})", tuple(values))
m.commit()
print("Haldia Dam migrated!")

# Get new Haldia Dam ID
mc.execute("SELECT id FROM places WHERE name = %s", ("Haldia Dam",))
new_hd_id = mc.fetchone()['id']
print(f"New Haldia Dam ID: {new_hd_id}")

# Migrate the 6 missing photos for Haldia Dam
sc.execute("SELECT * FROM photos WHERE place_id = 30")
photo_rows = sc.fetchall()
pcols = [d[0] for d in sc.description]

mc.execute("DESCRIBE photos")
photo_mysql = {r['Field']: r for r in mc.fetchall()}
pcommon = [c for c in pcols if c in photo_mysql and c != 'id']

for pr in photo_rows:
    vals = []
    for c in pcommon:
        v = pr[c]
        if c == 'place_id':
            v = new_hd_id
        info = photo_mysql.get(c, {})
        if v is None and info.get('Null') == 'NO':
            t = info.get('Type', '')
            v = 0 if 'int' in t else ''
        vals.append(v)
    
    ph = ', '.join(['%s'] * len(pcommon))
    cn = ', '.join([f'`{c}`' for c in pcommon])
    mc.execute(f"INSERT INTO photos ({cn}) VALUES ({ph})", tuple(vals))

m.commit()
print(f"Migrated {len(photo_rows)} photos for Haldia Dam")

# FINAL COUNT
print()
print("=== FINAL VERIFICATION ===")
for tbl in ['places', 'photos', 'users', 'reviews', 'wishlists',
            'hero_media', 'admin_logs', 'blocks', 'accommodations',
            'district_foods', 'districts', 'states']:
    sc.execute(f"SELECT COUNT(*) FROM [{tbl}]")
    sc_cnt = sc.fetchone()[0]
    mc.execute(f"SELECT COUNT(*) AS cnt FROM {tbl}")
    mc_cnt = mc.fetchone()['cnt']
    status = "OK" if mc_cnt >= sc_cnt else "MISSING"
    print(f"  {tbl:<20} SQLite={sc_cnt:>4}  MySQL={mc_cnt:>4}  {status}")

s.close()
m.close()
print("\nALL DATA MIGRATED!")
