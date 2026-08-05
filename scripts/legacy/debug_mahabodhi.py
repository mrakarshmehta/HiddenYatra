"""Quick check: why Golghar works but Mahabodhi crashes."""
import pymysql

c = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='',
                    database='hiddenyatra', cursorclass=pymysql.cursors.DictCursor)
cur = c.cursor()

# Check data types returned by MySQL directly (no pool conv)
cur.execute("SELECT id, name, latitude, longitude, district_id FROM places WHERE slug IN ('golghar', 'mahabodhi-temple-bodh-gaya')")
for r in cur.fetchall():
    print(f"{r['name']}: lat={r['latitude']} ({type(r['latitude']).__name__}), "
          f"lng={r['longitude']} ({type(r['longitude']).__name__}), "
          f"district_id={r['district_id']}")

# Check if Golghar has nearby places query that would also crash
import math
for slug in ['golghar', 'mahabodhi-temple-bodh-gaya']:
    cur.execute("SELECT latitude, longitude FROM places WHERE slug = %s", (slug,))
    p = cur.fetchone()
    lat = p['latitude']
    lng = p['longitude']
    print(f"\n{slug}: lat={lat} ({type(lat).__name__}), lng={lng} ({type(lng).__name__})")
    
    # Simulate the nearby_places query
    try:
        cos_lat = math.cos(math.radians(float(lat)))
        lat_range = 50 / 111.0
        lng_range = 50 / (111.0 * max(0.01, cos_lat))
        params = [lat, lat, lng, lng, cos_lat, cos_lat,
                  float(lat) - lat_range, float(lat) + lat_range,
                  float(lng) - lng_range, float(lng) + lng_range]
        print(f"  Param types: {[type(p).__name__ for p in params]}")
        
        # Test mogrify
        query = "SELECT 1 WHERE %s = %s AND %s = %s AND %s = %s AND %s < %s AND %s < %s"
        cur.execute(query, params)
        print(f"  Query OK!")
    except Exception as e:
        print(f"  ERROR: {e}")

c.close()
