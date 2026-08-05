"""
HiddenYatra — Seed Comprehensive 10 Essential Services
Seeds records for all 10 essential types across Bihar districts:
- hotel
- hospital
- petrol_pump
- pharmacy
- restaurant
- atm
- police_station
- bus_stand
- railway_station
- parking
"""
import pymysql, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
                        database=DB_NAME, charset='utf8mb4', autocommit=False)
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("SELECT id, name FROM districts")
dist_map = {d['name'].lower(): d['id'] for d in cur.fetchall()}

essential_services = [
    # --- PATNA (Patna district) ---
    {'district': 'patna', 'name': 'Patna Central Pharmacy (Jan Aushadhi)', 'service_type': 'pharmacy', 'address': 'Fraser Road, Patna', 'phone': '0612-2234900', 'latitude': 25.6090, 'longitude': 85.1385},
    {'district': 'patna', 'name': 'Apollo Pharmacy - Boring Road', 'service_type': 'pharmacy', 'address': 'Boring Road, Patna', 'phone': '0612-2541122', 'latitude': 25.6125, 'longitude': 85.1315},
    {'district': 'patna', 'name': 'Mithapur Inter-State Bus Terminal (ISBT)', 'service_type': 'bus_stand', 'address': 'Mithapur, Patna', 'phone': '0612-2354400', 'latitude': 25.5920, 'longitude': 85.1310},
    {'district': 'patna', 'name': 'Bankipur Bus Stand', 'service_type': 'bus_stand', 'address': 'Gandhi Maidan, Patna', 'phone': '0612-2224500', 'latitude': 25.6145, 'longitude': 85.1440},
    {'district': 'patna', 'name': 'Patna Junction Multi-Level Parking', 'service_type': 'parking', 'address': 'Station Road, Patna', 'phone': None, 'latitude': 25.6010, 'longitude': 85.1410},
    {'district': 'patna', 'name': 'Gandhi Maidan Public Parking Lot', 'service_type': 'parking', 'address': 'North Gandhi Maidan, Patna', 'phone': None, 'latitude': 25.6150, 'longitude': 85.1425},
    {'district': 'patna', 'name': 'HP Fuel Station - Fraser Road', 'service_type': 'petrol_pump', 'address': 'Fraser Road, Patna', 'phone': None, 'latitude': 25.6075, 'longitude': 85.1375},
    {'district': 'patna', 'name': 'ICICI Bank ATM - Station Road', 'service_type': 'atm', 'address': 'Station Road, Patna', 'phone': None, 'latitude': 25.6008, 'longitude': 85.1408},

    # --- GAYA / BODH GAYA (Gaya district) ---
    {'district': 'gaya', 'name': 'Bodh Gaya City Pharmacy & Medicos', 'service_type': 'pharmacy', 'address': 'Near Temple Gate, Bodh Gaya', 'phone': '0631-2200111', 'latitude': 24.6960, 'longitude': 84.9910},
    {'district': 'gaya', 'name': 'Gaya Central Bus Stand', 'service_type': 'bus_stand', 'address': 'Government Bus Stand, Gaya', 'phone': '0631-2221200', 'latitude': 24.7930, 'longitude': 85.0010},
    {'district': 'gaya', 'name': 'Bodh Gaya Mahabodhi Visitor Parking', 'service_type': 'parking', 'address': 'Bodh Gaya Bypass Road', 'phone': None, 'latitude': 24.6940, 'longitude': 84.9880},
    {'district': 'gaya', 'name': 'IndianOil Petrol Pump - Bodh Gaya', 'service_type': 'petrol_pump', 'address': 'Main Road, Bodh Gaya', 'phone': None, 'latitude': 24.6980, 'longitude': 84.9920},
    {'district': 'gaya', 'name': 'Punjab National Bank ATM - Gaya Station', 'service_type': 'atm', 'address': 'Station Road, Gaya', 'phone': None, 'latitude': 24.7918, 'longitude': 84.9995},

    # --- NALANDA / RAJGIR (Nalanda district) ---
    {'district': 'nalanda', 'name': 'Rajgir Tourist Pharmacy', 'service_type': 'pharmacy', 'address': 'Main Market, Rajgir', 'phone': '06112-255888', 'latitude': 25.0285, 'longitude': 85.4195},
    {'district': 'nalanda', 'name': 'Rajgir Bus Stand', 'service_type': 'bus_stand', 'address': 'Bus Stand Road, Rajgir', 'phone': '06112-255300', 'latitude': 25.0290, 'longitude': 85.4210},
    {'district': 'nalanda', 'name': 'Rajgir Ropeway & Viswa Shanti Stupa Parking', 'service_type': 'parking', 'address': 'Ropeway Station, Rajgir', 'phone': None, 'latitude': 25.0120, 'longitude': 85.4380},
    {'district': 'nalanda', 'name': 'Bharat Petroleum - Rajgir Bypass', 'service_type': 'petrol_pump', 'address': 'Bypass Road, Rajgir', 'phone': None, 'latitude': 25.0240, 'longitude': 85.4150},
    {'district': 'nalanda', 'name': 'SBI ATM - Rajgir Market', 'service_type': 'atm', 'address': 'Main Market, Rajgir', 'phone': None, 'latitude': 25.0275, 'longitude': 85.4185},
    {'district': 'nalanda', 'name': 'Green Hotel & Restaurant', 'service_type': 'restaurant', 'address': 'Near Bus Stand, Rajgir', 'phone': '06112-255999', 'latitude': 25.0282, 'longitude': 85.4202},

    # --- ROHTAS / SASARAM (Rohtas district) ---
    {'district': 'rohtas', 'name': 'Sasaram Junction Railway Station', 'service_type': 'railway_station', 'address': 'GT Road, Sasaram', 'phone': None, 'latitude': 24.9520, 'longitude': 84.0150},
    {'district': 'rohtas', 'name': 'Sasaram District Hospital', 'service_type': 'hospital', 'address': 'Hospital Road, Sasaram', 'phone': '06184-222300', 'latitude': 24.9550, 'longitude': 84.0200},
    {'district': 'rohtas', 'name': 'Sher Shah Tourist Hotel', 'service_type': 'hotel', 'address': 'GT Road, Sasaram', 'phone': '06184-223456', 'latitude': 24.9530, 'longitude': 84.0180},
    {'district': 'rohtas', 'name': 'Sasaram Bus Stand', 'service_type': 'bus_stand', 'address': 'GT Road, Sasaram', 'phone': None, 'latitude': 24.9510, 'longitude': 84.0140},
    {'district': 'rohtas', 'name': 'Sasaram Town Police Station', 'service_type': 'police_station', 'address': 'GT Road, Sasaram', 'phone': '100', 'latitude': 24.9540, 'longitude': 84.0170},
    {'district': 'rohtas', 'name': 'HP Petrol Pump - Sasaram', 'service_type': 'petrol_pump', 'address': 'GT Road, Sasaram', 'phone': None, 'latitude': 24.9500, 'longitude': 84.0120},
    {'district': 'rohtas', 'name': 'Apollo Pharmacy - Sasaram', 'service_type': 'pharmacy', 'address': 'GT Road, Sasaram', 'phone': None, 'latitude': 24.9535, 'longitude': 84.0175},
    {'district': 'rohtas', 'name': 'Tomb Visitor Parking', 'service_type': 'parking', 'address': 'Sher Shah Tomb Road, Sasaram', 'phone': None, 'latitude': 24.9560, 'longitude': 84.0160},
    {'district': 'rohtas', 'name': 'SBI ATM - Sasaram GT Road', 'service_type': 'atm', 'address': 'GT Road, Sasaram', 'phone': None, 'latitude': 24.9525, 'longitude': 84.0155},
    {'district': 'rohtas', 'name': 'Grand Trunk Restaurant', 'service_type': 'restaurant', 'address': 'GT Road, Sasaram', 'phone': None, 'latitude': 24.9532, 'longitude': 84.0182},
]

inserted = 0
for s in essential_services:
    dist_id = dist_map.get(s['district'])
    # Check if already exists by name
    cur.execute("SELECT id FROM nearby_services WHERE name = %s", (s['name'],))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO nearby_services (district_id, name, service_type, address, phone, latitude, longitude, is_active) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, 1)",
            (dist_id, s['name'], s['service_type'], s.get('address',''),
             s.get('phone'), s.get('latitude'), s.get('longitude'))
        )
        inserted += 1

conn.commit()
print(f"✓ Seeded {inserted} additional essential service records")

cur.execute("SELECT service_type, COUNT(*) as cnt FROM nearby_services WHERE is_active = 1 GROUP BY service_type ORDER BY cnt DESC")
print("Updated service types in DB:")
for r in cur.fetchall():
    print(f"  {r['service_type']}: {r['cnt']}")

conn.close()
