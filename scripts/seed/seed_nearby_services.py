"""Seed nearby essential services for key Bihar districts and places."""
import pymysql, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
                        database=DB_NAME, charset='utf8mb4', autocommit=False)
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("SELECT COUNT(*) AS cnt FROM nearby_services")
if cur.fetchone()['cnt'] > 0:
    print("Nearby services already seeded, skipping")
    exit(0)

# Get district IDs
cur.execute("SELECT id, name FROM districts LIMIT 10")
districts = {d['name']: d['id'] for d in cur.fetchall()}

# Get place IDs
cur.execute("SELECT id, name, district_id FROM places LIMIT 10")
places = {p['name']: p for p in cur.fetchall()}

services = [
    # Patna district services
    {'district_id': 1, 'name': 'Patna Junction Railway Station', 'service_type': 'railway_station', 'address': 'Station Road, Patna', 'phone': '0612-2203430', 'latitude': 25.6005, 'longitude': 85.1405},
    {'district_id': 1, 'name': 'Jay Prakash Narayan Airport', 'service_type': 'airport', 'address': 'Shaheed Pir Ali Khan Marg, Patna', 'phone': '0612-2222051', 'latitude': 25.5913, 'longitude': 85.0879},
    {'district_id': 1, 'name': 'Patna Medical College & Hospital', 'service_type': 'hospital', 'address': 'Ashok Rajpath, Patna', 'phone': '0612-2300343', 'latitude': 25.6156, 'longitude': 85.1628},
    {'district_id': 1, 'name': 'IGIMS Hospital', 'service_type': 'hospital', 'address': 'Raja Bazar, Patna', 'phone': '0612-2297631', 'latitude': 25.6230, 'longitude': 85.1498},
    {'district_id': 1, 'name': 'State Bank of India ATM - Gandhi Maidan', 'service_type': 'atm', 'address': 'Gandhi Maidan Road, Patna', 'phone': None, 'latitude': 25.6135, 'longitude': 85.1430},
    {'district_id': 1, 'name': 'HDFC Bank ATM - Boring Road', 'service_type': 'atm', 'address': 'Boring Road, Patna', 'phone': None, 'latitude': 25.6120, 'longitude': 85.1305},
    {'district_id': 1, 'name': 'Indian Oil Petrol Pump - Patna', 'service_type': 'petrol_pump', 'address': 'Bailey Road, Patna', 'phone': None, 'latitude': 25.6178, 'longitude': 85.1380},
    {'district_id': 1, 'name': 'Kotwali Police Station', 'service_type': 'police_station', 'address': 'Patna City, Bihar', 'phone': '100', 'latitude': 25.6080, 'longitude': 85.1710},
    {'district_id': 1, 'name': 'Hotel Maurya Patna', 'service_type': 'hotel', 'address': 'South Gandhi Maidan, Patna', 'phone': '0612-2203040', 'latitude': 25.6095, 'longitude': 85.1370},
    {'district_id': 1, 'name': 'Hotel Chanakya', 'service_type': 'hotel', 'address': 'Beer Chand Patel Road, Patna', 'phone': '0612-2222141', 'latitude': 25.6160, 'longitude': 85.1430},
    {'district_id': 1, 'name': 'Tandoor Hut', 'service_type': 'restaurant', 'address': 'Boring Road, Patna', 'phone': '0612-2580123', 'latitude': 25.6110, 'longitude': 85.1310},
    {'district_id': 1, 'name': 'Bansi Vilas', 'service_type': 'restaurant', 'address': 'Kadam Kuan, Patna', 'phone': '0612-2677890', 'latitude': 25.6070, 'longitude': 85.1360},

    # Gaya district services
    {'district_id': 3, 'name': 'Gaya Junction Railway Station', 'service_type': 'railway_station', 'address': 'Station Road, Gaya', 'phone': '0631-2220200', 'latitude': 24.7914, 'longitude': 84.9990},
    {'district_id': 3, 'name': 'Gaya International Airport', 'service_type': 'airport', 'address': 'Bodh Gaya Road, Gaya', 'phone': '0631-2200201', 'latitude': 24.7443, 'longitude': 84.9512},
    {'district_id': 3, 'name': 'Anugrah Narayan Magadh Medical College', 'service_type': 'hospital', 'address': 'Gaya, Bihar', 'phone': '0631-2220015', 'latitude': 24.7960, 'longitude': 85.0040},
    {'district_id': 3, 'name': 'Royal Residency Hotel', 'service_type': 'hotel', 'address': 'Bodh Gaya Road, Gaya', 'phone': '0631-2200567', 'latitude': 24.6982, 'longitude': 84.9892},
    {'district_id': 3, 'name': 'Mohammad Sujat Restaurant', 'service_type': 'restaurant', 'address': 'Bodh Gaya, Bihar', 'phone': None, 'latitude': 24.6970, 'longitude': 84.9905},
    {'district_id': 3, 'name': 'Bodh Gaya Police Station', 'service_type': 'police_station', 'address': 'Bodh Gaya, Bihar', 'phone': '100', 'latitude': 24.6955, 'longitude': 84.9870},
    {'district_id': 3, 'name': 'SBI ATM - Bodh Gaya', 'service_type': 'atm', 'address': 'Main Road, Bodh Gaya', 'phone': None, 'latitude': 24.6963, 'longitude': 84.9890},

    # Nalanda district services
    {'district_id': 4, 'name': 'Rajgir Railway Station', 'service_type': 'railway_station', 'address': 'Rajgir, Nalanda', 'phone': None, 'latitude': 25.0300, 'longitude': 85.4200},
    {'district_id': 4, 'name': 'Hotel Tathagat Vihar', 'service_type': 'hotel', 'address': 'Rajgir, Nalanda', 'phone': '06112-255511', 'latitude': 25.0270, 'longitude': 85.4190},
    {'district_id': 4, 'name': 'Indo Hokke Hotel', 'service_type': 'hotel', 'address': 'Rajgir, Nalanda', 'phone': '06112-255245', 'latitude': 25.0250, 'longitude': 85.4170},
    {'district_id': 4, 'name': 'Nalanda District Hospital', 'service_type': 'hospital', 'address': 'Bihar Sharif, Nalanda', 'phone': '06112-232555', 'latitude': 25.2010, 'longitude': 85.5205},
    {'district_id': 4, 'name': 'Rajgir Police Station', 'service_type': 'police_station', 'address': 'Rajgir, Nalanda', 'phone': '100', 'latitude': 25.0280, 'longitude': 85.4180},
]

# Emergency contacts (state-level)
emergency_services = [
    {'district_id': None, 'name': 'Bihar Police Helpline', 'service_type': 'emergency', 'address': 'Bihar', 'phone': '100'},
    {'district_id': None, 'name': 'Ambulance', 'service_type': 'emergency', 'address': 'Bihar', 'phone': '108'},
    {'district_id': None, 'name': 'Bihar Tourism Helpline', 'service_type': 'emergency', 'address': 'Bihar', 'phone': '1800-345-6225'},
    {'district_id': None, 'name': 'Women Helpline', 'service_type': 'emergency', 'address': 'Bihar', 'phone': '181'},
    {'district_id': None, 'name': 'Fire Department', 'service_type': 'emergency', 'address': 'Bihar', 'phone': '101'},
]

all_services = services + emergency_services
for s in all_services:
    cur.execute(
        "INSERT INTO nearby_services (district_id, name, service_type, address, phone, latitude, longitude) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (s.get('district_id'), s['name'], s['service_type'], s.get('address',''),
         s.get('phone'), s.get('latitude'), s.get('longitude'))
    )

conn.commit()
print(f"✓ Seeded {len(all_services)} nearby services")

cur.execute("SELECT service_type, COUNT(*) as cnt FROM nearby_services GROUP BY service_type ORDER BY cnt DESC")
for r in cur.fetchall():
    print(f"  {r['service_type']}: {r['cnt']}")

conn.close()
