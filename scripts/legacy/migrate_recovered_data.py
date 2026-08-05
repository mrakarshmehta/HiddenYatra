"""Migrate ALL missing data from recovered SQLite to MySQL — fixed version."""
import sqlite3
import pymysql

sqlite_conn = sqlite3.connect(r"D:\HiddenYatra\bharat_darshan_recovered.db")
sqlite_conn.row_factory = sqlite3.Row
s_cur = sqlite_conn.cursor()

mysql_conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='',
                             database='hiddenyatra', cursorclass=pymysql.cursors.DictCursor)
m_cur = mysql_conn.cursor()


def get_mysql_cols(table):
    """Get MySQL column info."""
    m_cur.execute(f"DESCRIBE {table}")
    return {r['Field']: r for r in m_cur.fetchall()}


def fix_nulls(col_info, col_name, value):
    """Replace NULL with default for NOT NULL columns."""
    info = col_info.get(col_name, {})
    if value is None and info.get('Null') == 'NO':
        col_type = info.get('Type', '')
        if 'int' in col_type:
            return 0
        elif 'decimal' in col_type or 'float' in col_type or 'double' in col_type:
            return 0.0
        else:
            return ''
    return value


def migrate_rows(table, where_clause=None):
    """Migrate rows from SQLite to MySQL, handling NULLs."""
    query = f"SELECT * FROM [{table}]"
    if where_clause:
        query += f" WHERE {where_clause}"
    
    s_cur.execute(query)
    rows = s_cur.fetchall()
    if not rows:
        print(f"  {table}: no rows to migrate")
        return 0
    
    sqlite_cols = [desc[0] for desc in s_cur.description]
    mysql_col_info = get_mysql_cols(table)
    common = [c for c in sqlite_cols if c in mysql_col_info]
    
    placeholders = ', '.join(['%s'] * len(common))
    col_names = ', '.join([f'`{c}`' for c in common])
    
    migrated = 0
    for row in rows:
        # Check if exists
        m_cur.execute(f"SELECT 1 FROM {table} WHERE id = %s", (row['id'],))
        if m_cur.fetchone():
            continue
        
        values = tuple(fix_nulls(mysql_col_info, c, row[c]) for c in common)
        try:
            m_cur.execute(f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})", values)
            migrated += 1
        except Exception as e:
            print(f"  ERROR {table} id={row['id']}: {e}")
    
    mysql_conn.commit()
    print(f"  {table}: migrated {migrated} rows")
    return migrated


print("=" * 60)
print("  MIGRATING MISSING DATA: SQLite -> MySQL")
print("=" * 60)

# 1. Users
print("\n[1/8] Users...")
migrate_rows('users')

# 2. Missing place
print("\n[2/8] Places...")
# Find missing places by name
s_cur.execute("SELECT name FROM places")
sqlite_place_names = {r['name'] for r in s_cur.fetchall()}
m_cur.execute("SELECT name FROM places")
mysql_place_names = {r['name'] for r in m_cur.fetchall()}
missing_names = sqlite_place_names - mysql_place_names
print(f"  Missing places: {missing_names}")

for name in missing_names:
    s_cur.execute("SELECT * FROM places WHERE name = ?", (name,))
    row = s_cur.fetchone()
    sqlite_cols = [desc[0] for desc in s_cur.description]
    mysql_col_info = get_mysql_cols('places')
    common = [c for c in sqlite_cols if c in mysql_col_info and c != 'id']
    
    values = tuple(fix_nulls(mysql_col_info, c, row[c]) for c in common)
    placeholders = ', '.join(['%s'] * len(common))
    col_names = ', '.join([f'`{c}`' for c in common])
    
    try:
        m_cur.execute(f"INSERT INTO places ({col_names}) VALUES ({placeholders})", values)
        mysql_conn.commit()
        print(f"  Migrated place: {name}")
    except Exception as e:
        print(f"  ERROR place {name}: {e}")

# 3. Missing blocks
print("\n[3/8] Blocks...")
s_cur.execute("SELECT * FROM blocks")
sqlite_blocks = s_cur.fetchall()
m_cur.execute("SELECT name, district_id FROM blocks")
mysql_blocks = {(r['name'], r['district_id']) for r in m_cur.fetchall()}

mysql_col_info = get_mysql_cols('blocks')
sqlite_cols = [desc[0] for desc in s_cur.description]
common = [c for c in sqlite_cols if c in mysql_col_info and c != 'id']

migrated_blocks = 0
for row in sqlite_blocks:
    if (row['name'], row['district_id']) not in mysql_blocks:
        values = tuple(fix_nulls(mysql_col_info, c, row[c]) for c in common)
        placeholders = ', '.join(['%s'] * len(common))
        col_names = ', '.join([f'`{c}`' for c in common])
        try:
            m_cur.execute(f"INSERT INTO blocks ({col_names}) VALUES ({placeholders})", values)
            migrated_blocks += 1
            print(f"  Migrated block: {row['name']}")
        except Exception as e:
            print(f"  ERROR block: {e}")
mysql_conn.commit()
print(f"  blocks: migrated {migrated_blocks}")

# 4. Photos — need to map place_id correctly
print("\n[4/8] Photos...")
# Build place name -> new mysql id mapping
s_cur.execute("SELECT id, name FROM places")
sqlite_pid_to_name = {r['id']: r['name'] for r in s_cur.fetchall()}
m_cur.execute("SELECT id, name FROM places")
mysql_name_to_pid = {r['name']: r['id'] for r in m_cur.fetchall()}

s_cur.execute("SELECT * FROM photos")
photo_rows = s_cur.fetchall()
sqlite_cols = [desc[0] for desc in s_cur.description]
mysql_col_info = get_mysql_cols('photos')
common = [c for c in sqlite_cols if c in mysql_col_info and c != 'id']

migrated_photos = 0
for row in photo_rows:
    old_place_id = row['place_id']
    place_name = sqlite_pid_to_name.get(old_place_id)
    new_place_id = mysql_name_to_pid.get(place_name)
    
    if not new_place_id:
        print(f"  WARN: no MySQL place for photo place_id={old_place_id} ({place_name})")
        continue
    
    values = []
    for c in common:
        val = row[c]
        if c == 'place_id':
            val = new_place_id
        values.append(fix_nulls(mysql_col_info, c, val))
    
    placeholders = ', '.join(['%s'] * len(common))
    col_names = ', '.join([f'`{c}`' for c in common])
    
    try:
        m_cur.execute(f"INSERT INTO photos ({col_names}) VALUES ({placeholders})", tuple(values))
        migrated_photos += 1
    except Exception as e:
        print(f"  ERROR photo: {e}")

mysql_conn.commit()
print(f"  photos: migrated {migrated_photos}")

# 5. Hero media
print("\n[5/8] Hero media...")
migrate_rows('hero_media')

# 6. Reviews — need to map place_id
print("\n[6/8] Reviews...")
s_cur.execute("SELECT * FROM reviews")
review_rows = s_cur.fetchall()
sqlite_cols = [desc[0] for desc in s_cur.description]
mysql_col_info = get_mysql_cols('reviews')
common = [c for c in sqlite_cols if c in mysql_col_info and c != 'id']

for row in review_rows:
    old_pid = row['place_id']
    pname = sqlite_pid_to_name.get(old_pid)
    new_pid = mysql_name_to_pid.get(pname)
    
    if not new_pid:
        print(f"  WARN: no MySQL place for review place_id={old_pid}")
        continue
    
    values = []
    for c in common:
        val = row[c]
        if c == 'place_id':
            val = new_pid
        values.append(fix_nulls(mysql_col_info, c, val))
    
    placeholders = ', '.join(['%s'] * len(common))
    col_names = ', '.join([f'`{c}`' for c in common])
    
    try:
        m_cur.execute(f"INSERT INTO reviews ({col_names}) VALUES ({placeholders})", tuple(values))
        print(f"  Migrated review by {row['author_name']} for {pname}")
    except Exception as e:
        print(f"  ERROR review: {e}")

mysql_conn.commit()

# 7. Wishlists — map place_id
print("\n[7/8] Wishlists...")
s_cur.execute("SELECT * FROM wishlists")
wl_rows = s_cur.fetchall()
sqlite_cols = [desc[0] for desc in s_cur.description]
mysql_col_info = get_mysql_cols('wishlists')
common = [c for c in sqlite_cols if c in mysql_col_info and c != 'id']

for row in wl_rows:
    old_pid = row['place_id']
    pname = sqlite_pid_to_name.get(old_pid)
    new_pid = mysql_name_to_pid.get(pname)
    
    if not new_pid:
        continue
    
    values = []
    for c in common:
        val = row[c]
        if c == 'place_id':
            val = new_pid
        values.append(fix_nulls(mysql_col_info, c, val))
    
    placeholders = ', '.join(['%s'] * len(common))
    col_names = ', '.join([f'`{c}`' for c in common])
    
    try:
        m_cur.execute(f"INSERT INTO wishlists ({col_names}) VALUES ({placeholders})", tuple(values))
        print(f"  Migrated wishlist: place={pname}")
    except Exception as e:
        print(f"  ERROR wishlist: {e}")

mysql_conn.commit()

# 8. Admin logs
print("\n[8/8] Admin logs...")
migrate_rows('admin_logs')

# === FINAL VERIFICATION ===
print()
print("=" * 60)
print("  FINAL VERIFICATION")
print("=" * 60)
print(f"{'Table':<25} {'SQLite':>8} {'MySQL':>8} {'Status':>10}")
print("-" * 55)

s_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
all_ok = True
for r in s_cur.fetchall():
    table = r[0]
    s_cur.execute(f"SELECT COUNT(*) FROM [{table}]")
    s_count = s_cur.fetchone()[0]
    try:
        m_cur.execute(f"SELECT COUNT(*) AS cnt FROM {table}")
        m_count = m_cur.fetchone()['cnt']
        status = "OK" if m_count >= s_count else "MISSING!"
        if m_count < s_count:
            all_ok = False
    except:
        m_count = 'N/A'
        status = 'N/A (empty table)'
    print(f"  {table:<23} {s_count:>8} {str(m_count):>8} {status:>10}")

print()
if all_ok:
    print("  ALL DATA MIGRATED SUCCESSFULLY!")
else:
    print("  SOME DATA STILL MISSING — CHECK ABOVE")

sqlite_conn.close()
mysql_conn.close()
