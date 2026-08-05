"""
Seed Bihar with detailed block-level hierarchy data.
Adds blocks to existing Bihar districts and creates new ones.
Run: python seed_bihar_hierarchy.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import (
    init_db, get_db, create_state, create_district, create_block, create_place,
    add_specialty
)


def seed_hierarchy():
    init_db()
    conn = get_db()

    # Check if Bihar exists
    bihar = conn.execute("SELECT id FROM states WHERE slug = 'bihar'").fetchone()
    if not bihar:
        print("Bihar not found. Run seed_bihar.py first.")
        conn.close()
        return

    bihar_id = bihar[0]

    # Get existing districts
    existing = {}
    for row in conn.execute("SELECT id, slug FROM districts WHERE state_id = ?", (bihar_id,)).fetchall():
        existing[row[1]] = row[0]

    conn.close()

    # ── NAWADA DISTRICT ────────────────────────────
    if 'nawada' not in existing:
        nawada_id = create_district(bihar_id, "Nawada")
    else:
        nawada_id = existing['nawada']

    nawada_blocks = [
        "Nawada", "Hisua", "Pakribarawan", "Roh", "Gobindpur",
        "Sirdala", "Warisaliganj", "Kashi Chak", "Rajauli",
        "Akbarpur", "Narhat", "Nardiganj", "Meskaur", "Kawakol"
    ]
    for name in nawada_blocks:
        create_block(nawada_id, name)
    print(f"  ✓ Nawada: {len(nawada_blocks)} blocks added")

    # Add a tourist place in Nawada
    place_data = {
        "name": "Kakolat Waterfall",
        "state_id": bihar_id,
        "district_id": nawada_id,
        "description": (
            "A magnificent 160-feet (49-meter) waterfall cascading down a rocky cliff in the Kakolat hills, "
            "about 33 km from Nawada town. Kakolat is the largest waterfall in Bihar and one of the most "
            "popular picnic destinations in the state. According to local legend, a king cursed to become a "
            "python was freed when he bathed in these falls. The lush green surroundings and the thundering "
            "cascade make it a breathtaking sight, especially during the monsoon season (July-September). "
            "The Bihar government has developed the area with steps, gardens, and changing rooms for visitors."
        ),
        "category": "waterfall",
        "latitude": 24.7833,
        "longitude": 85.5167,
        "is_featured": True,
    }
    try:
        pid = create_place(place_data)
        add_specialty(pid, {
            "name": "Tilkut",
            "description": "Crunchy sesame and sugar sweet, a beloved specialty of the Nawada-Gaya region.",
            "category": "sweet",
            "where_to_find": "Sweet shops in Nawada town"
        })
        print(f"  ✓ Added Kakolat Waterfall in Nawada")
    except Exception:
        print(f"  → Kakolat Waterfall already exists, skipping")

    # ── PATNA DISTRICT ─────────────────────────────
    patna_id = existing.get('patna')
    if patna_id:
        patna_blocks = [
            "Patna Sadar", "Danapur", "Phulwari Sharif", "Sampatchak",
            "Maner", "Naubatpur", "Bikram", "Paliganj", "Masaurhi",
            "Daniawan", "Khusrupur", "Fatuha", "Bakhtiarpur",
            "Barh", "Belchhi", "Mokama", "Pandarak", "Athmalgola",
            "Dulhin Bazar", "Punpun", "Bihta"
        ]
        for name in patna_blocks:
            create_block(patna_id, name)
        print(f"  ✓ Patna: {len(patna_blocks)} blocks added")

    # ── GAYA DISTRICT ──────────────────────────────
    gaya_id = existing.get('gaya')
    if gaya_id:
        gaya_blocks = [
            "Gaya Town", "Bodh Gaya", "Sherghati", "Tekari",
            "Paraiya", "Wazirganj", "Belaganj", "Khizarsarai",
            "Manpur", "Barachatti", "Fatehpur", "Konch",
            "Imamganj", "Atri", "Tankuppa", "Dumaria",
            "Mohanpur", "Gurua", "Amas", "Banke Bazar",
            "Dobhi", "Guraru", "Muhra"
        ]
        for name in gaya_blocks:
            create_block(gaya_id, name)
        print(f"  ✓ Gaya: {len(gaya_blocks)} blocks added")

    # ── NALANDA DISTRICT ───────────────────────────
    nalanda_id = existing.get('nalanda')
    if nalanda_id:
        nalanda_blocks = [
            "Bihar Sharif", "Rajgir", "Silao", "Noorsarai",
            "Hilsa", "Harnaut", "Parwalpur", "Asthawan",
            "Sarmera", "Islampur", "Ben", "Karai Parsurai",
            "Bind", "Tharthari", "Giriak", "Ekangarsarai",
            "Katrisarai", "Rahui", "Chandi", "Nagarnausa"
        ]
        for name in nalanda_blocks:
            create_block(nalanda_id, name)
        print(f"  ✓ Nalanda: {len(nalanda_blocks)} blocks added")

    # ── BHAGALPUR DISTRICT ─────────────────────────
    bhagalpur_id = existing.get('bhagalpur')
    if bhagalpur_id:
        bhagalpur_blocks = [
            "Bhagalpur", "Sultanganj", "Nathnagar", "Sabour",
            "Kahalgaon", "Naugachhia", "Narayanpur", "Jagdishpur",
            "Shahkund", "Pirpainti", "Sanhaula", "Gopalpur",
            "Ismailpur", "Kharik", "Bihpur", "Rangra Chowk"
        ]
        for name in bhagalpur_blocks:
            create_block(bhagalpur_id, name)
        print(f"  ✓ Bhagalpur: {len(bhagalpur_blocks)} blocks added")

    # ── VAISHALI DISTRICT ──────────────────────────
    vaishali_id = existing.get('vaishali')
    if vaishali_id:
        vaishali_blocks = [
            "Hajipur", "Vaishali", "Jandaha", "Mahua",
            "Lalganj", "Patepur", "Bidupur", "Raghopur",
            "Bhagwanpur", "Sahdei Buzurg", "Desri",
            "Rajapakar", "Mahnar", "Goraul", "Chehrakala"
        ]
        for name in vaishali_blocks:
            create_block(vaishali_id, name)
        print(f"  ✓ Vaishali: {len(vaishali_blocks)} blocks added")

    # ── MUZAFFARPUR DISTRICT ───────────────────────
    muzzafarpur_id = existing.get('muzaffarpur')
    if muzzafarpur_id:
        muzaffarpur_blocks = [
            "Mushahari", "Kanti", "Minapur", "Motipur",
            "Sahebganj", "Bochahan", "Gaighat", "Marwan",
            "Kurhani", "Aurai", "Paroo", "Sakra",
            "Bandra", "Muraul", "Katra"
        ]
        for name in muzaffarpur_blocks:
            create_block(muzzafarpur_id, name)
        print(f"  ✓ Muzaffarpur: {len(muzaffarpur_blocks)} blocks added")

    # ── MADHUBANI DISTRICT ─────────────────────────
    madhubani_id = existing.get('madhubani')
    if madhubani_id:
        madhubani_blocks = [
            "Madhubani", "Jainagar", "Jhanjharpur", "Benipatti",
            "Phulparas", "Ladania", "Bisfi", "Pandaul",
            "Rajnagar", "Ghoghardiha", "Babubarhi", "Khajauli",
            "Laukahi", "Harlakhi", "Laukaha", "Madhwapur",
            "Kaluahi", "Rahika", "Basopatti", "Andhratharhi"
        ]
        for name in madhubani_blocks:
            create_block(madhubani_id, name)
        print(f"  ✓ Madhubani: {len(madhubani_blocks)} blocks added")

    # ── ROHTAS DISTRICT ────────────────────────────
    rohtas_id = existing.get('rohtas')
    if rohtas_id:
        rohtas_blocks = [
            "Sasaram", "Dehri", "Bikramganj", "Dinara",
            "Kochas", "Rohtas", "Sanjhauli", "Tilouthu",
            "Karakat", "Akorhigola", "Nasriganj", "Dawath",
            "Suryapura", "Chenari", "Sheosagar", "Rajpur",
            "Kargahar", "Nokha", "Nauhatta"
        ]
        for name in rohtas_blocks:
            create_block(rohtas_id, name)
        print(f"  ✓ Rohtas: {len(rohtas_blocks)} blocks added")

    # ── MUNGER DISTRICT ────────────────────────────
    munger_id = existing.get('munger')
    if munger_id:
        munger_blocks = [
            "Munger", "Jamalpur", "Tarapura", "Bariarpur",
            "Asarganj", "Dharhara", "Tetia Bambar", "Sangrampur",
            "Haveli Kharagpur"
        ]
        for name in munger_blocks:
            create_block(munger_id, name)
        print(f"  ✓ Munger: {len(munger_blocks)} blocks added")

    # ── RAJGIR (If exists as separate district) ────
    rajgir_id = existing.get('rajgir')
    if rajgir_id:
        rajgir_blocks = ["Rajgir", "Giriak"]
        for name in rajgir_blocks:
            create_block(rajgir_id, name)
        print(f"  ✓ Rajgir: {len(rajgir_blocks)} blocks added")

    print(f"\n✅ Bihar hierarchy seed complete! Blocks added for all key districts.")


if __name__ == "__main__":
    seed_hierarchy()
