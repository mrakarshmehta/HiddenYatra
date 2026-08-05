"""
HiddenYatra Master Vision Migration
- Nearby Services table
- How to Reach fields on places
- Stay system enhancement
"""
import sqlite3

DB_PATH = 'bharat_darshan.db'

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # -- Nearby Services Table --
    cur.execute("""
        CREATE TABLE IF NOT EXISTS nearby_services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            district_id INTEGER,
            place_id INTEGER,
            name TEXT NOT NULL,
            service_type TEXT NOT NULL,
            address TEXT,
            phone TEXT,
            latitude REAL,
            longitude REAL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (district_id) REFERENCES districts(id),
            FOREIGN KEY (place_id) REFERENCES places(id)
        )
    """)
    print("[+] nearby_services table ready")

    # -- How to Reach fields on places --
    place_cols = {
        'nearest_railway': 'TEXT',
        'nearest_bus_stand': 'TEXT',
        'nearest_airport': 'TEXT',
        'road_connectivity': 'TEXT',
    }
    existing = [r[1] for r in cur.execute("PRAGMA table_info(places)").fetchall()]
    for col, dtype in place_cols.items():
        if col not in existing:
            cur.execute(f"ALTER TABLE places ADD COLUMN {col} {dtype}")
            print(f"[+] Added places.{col}")
        else:
            print(f"[=] places.{col} exists")

    # -- Stay system: budget_category on accommodations --
    acc_existing = [r[1] for r in cur.execute("PRAGMA table_info(accommodations)").fetchall()]
    if 'budget_category' not in acc_existing:
        cur.execute("ALTER TABLE accommodations ADD COLUMN budget_category TEXT DEFAULT 'mid'")
        print("[+] Added accommodations.budget_category")
    if 'facilities' not in acc_existing:
        cur.execute("ALTER TABLE accommodations ADD COLUMN facilities TEXT")
        print("[+] Added accommodations.facilities")
    if 'photos' not in acc_existing:
        cur.execute("ALTER TABLE accommodations ADD COLUMN photos TEXT")
        print("[+] Added accommodations.photos")

    conn.commit()
    conn.close()
    print("\nDone!")

if __name__ == '__main__':
    migrate()
