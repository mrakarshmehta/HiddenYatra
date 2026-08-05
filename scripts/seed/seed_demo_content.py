"""
HiddenYatra — Seed demo content for hackathon presentation.
Adds hero images, sample reviews, and place specialties to MySQL.
Run once: python scripts/seed/seed_demo_content.py
"""
import pymysql
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

conn = pymysql.connect(
    host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
    database=DB_NAME, charset='utf8mb4', autocommit=False
)
cur = conn.cursor(pymysql.cursors.DictCursor)

print("═══════════════════════════════════════")
print("  HiddenYatra — Seeding Demo Content")
print("═══════════════════════════════════════")

# ═══ 1. HERO MEDIA ═══
# Schema: id, filename, media_type, title, is_active, sort_order, uploaded_at
hero_images = [
    ('hero/hero_1.png', 'image', 'Mahabodhi Temple, Bodh Gaya', True, 1),
    ('hero/hero_2.png', 'image', 'Nalanda University Ruins', True, 2),
    ('hero/hero_3.png', 'image', 'Rajgir Hills', True, 3),
    ('hero/hero_4.png', 'image', 'Ganges River, Patna', True, 4),
    ('hero/hero_5.png', 'image', 'Rohtasgarh Fort', True, 5),
]

cur.execute("SELECT COUNT(*) AS cnt FROM hero_media")
if cur.fetchone()['cnt'] == 0:
    for filename, media_type, title, is_active, sort_order in hero_images:
        cur.execute(
            "INSERT INTO hero_media (filename, media_type, title, is_active, sort_order) "
            "VALUES (%s, %s, %s, %s, %s)",
            (filename, media_type, title, is_active, sort_order)
        )
    conn.commit()
    print(f"  ✓ Hero media: {len(hero_images)} images seeded")
else:
    print("  ℹ Hero media already has content, skipping")

# ═══ 2. SAMPLE REVIEWS ═══
# Schema: id, place_id, session_id, author_name, rating, comment, created_at
cur.execute("SELECT id, name FROM places ORDER BY id LIMIT 15")
places = cur.fetchall()

cur.execute("SELECT COUNT(*) AS cnt FROM reviews")
if cur.fetchone()['cnt'] == 0:
    review_data = [
        (5, "Rahul S.", "Absolutely stunning place! The history and architecture are breathtaking. A must-visit for anyone traveling to Bihar."),
        (4, "Priya M.", "Great experience overall. The surroundings are peaceful and well-maintained. Would recommend visiting early morning."),
        (5, "Amit K.", "One of the best heritage sites I've visited in India. The spiritual atmosphere is incredible."),
        (4, "Sneha D.", "Beautiful location with rich historical significance. The local guides are very knowledgeable."),
        (3, "Vikash T.", "Decent place to visit. Could use better facilities and signage. The main attraction is worth seeing though."),
        (5, "Ananya R.", "Exceeded my expectations! The sunset view from here is absolutely magical. Don't miss this gem."),
        (4, "Deepak J.", "A hidden gem in Bihar. Not very crowded which makes it even more special. Great for photography."),
        (5, "Kavita P.", "This place has so much history. Every corner tells a story. Spent hours exploring and still wanted more."),
        (4, "Rajesh B.", "Well-preserved historical site. The local food nearby is also excellent. Plan at least half a day here."),
        (3, "Neha S.", "Good place for a quick visit. The main structure is impressive but the area needs better upkeep."),
        (5, "Suresh V.", "Incredible experience! The serenity of this place is unmatched. Perfect for meditation and reflection."),
        (4, "Meera G.", "Rich cultural heritage and beautiful architecture. The evening light makes it look even more spectacular."),
        (5, "Arjun N.", "A truly remarkable place. The craftsmanship of the ancient builders is awe-inspiring."),
        (4, "Pooja L.", "Peaceful and beautiful. Great for families. The kids loved exploring the grounds."),
        (5, "Sanjay W.", "Bihar has so many hidden treasures and this is one of the finest. Highly recommended!"),
        (4, "Ritu A.", "The historical significance of this place cannot be overstated. A pilgrimage for history lovers."),
        (3, "Manish C.", "Interesting place but could benefit from better tourist infrastructure. The core site is beautiful."),
        (5, "Shruti H.", "Mind-blowing architecture and spiritual vibes. One of the highlights of my Bihar trip."),
        (4, "Vivek F.", "Loved the tranquility here. Away from the hustle of the city. Perfect weekend getaway."),
        (5, "Nisha E.", "This place changed my perspective on Bihar tourism. So much beauty waiting to be discovered!"),
    ]

    session_ids = [f"demo_reviewer_{i}" for i in range(1, 11)]
    review_count = 0

    for i, place in enumerate(places):
        num_reviews = min(2, len(review_data) - review_count)
        if num_reviews <= 0:
            break
        for j in range(num_reviews):
            idx = review_count % len(review_data)
            rating, author, comment = review_data[idx]
            sid = session_ids[review_count % len(session_ids)]
            cur.execute(
                "INSERT INTO reviews (place_id, session_id, author_name, rating, comment) "
                "VALUES (%s, %s, %s, %s, %s)",
                (place['id'], sid, author, rating, comment)
            )
            review_count += 1

    conn.commit()
    print(f"  ✓ Reviews: {review_count} sample reviews seeded across {min(len(places), review_count//2)} places")
else:
    print("  ℹ Reviews already exist, skipping")

# ═══ 3. PLACE SPECIALTIES ═══
# Schema: id, place_id, name, description, category, where_to_find, ...
cur.execute("SELECT COUNT(*) AS cnt FROM specialties")
if cur.fetchone()['cnt'] == 0:
    cur.execute("SELECT id, name, category FROM places LIMIT 20")
    spec_places = cur.fetchall()

    specialty_map = {
        'temple': [
            ('Ancient Architecture', 'Intricate stone carvings and centuries-old design', 'attraction'),
            ('Spiritual Significance', 'Major pilgrimage site for devotees', 'attraction'),
            ('Religious Ceremonies', 'Daily aarti and special festival celebrations', 'attraction'),
        ],
        'historical': [
            ('UNESCO Heritage', 'Recognized for outstanding universal value', 'attraction'),
            ('Archaeological Importance', 'Excavated ruins dating back millennia', 'attraction'),
            ('Ancient History', 'Witness to major historical events', 'attraction'),
        ],
        'nature': [
            ('Scenic Beauty', 'Breathtaking natural landscapes', 'attraction'),
            ('Wildlife Spotting', 'Home to diverse flora and fauna', 'attraction'),
            ('Trekking Trails', 'Well-marked paths through natural terrain', 'attraction'),
        ],
        'waterfall': [
            ('Natural Beauty', 'Cascading waters amid lush greenery', 'attraction'),
            ('Swimming Spot', 'Safe natural pool at the base', 'attraction'),
            ('Monsoon Special', 'Most spectacular during rainy season', 'attraction'),
        ],
        'tourist_spot': [
            ('Local Culture', 'Experience authentic Bihar traditions', 'attraction'),
            ('Photography', 'Stunning photo opportunities', 'attraction'),
            ('Family Friendly', 'Safe and enjoyable for all ages', 'attraction'),
        ],
    }

    spec_count = 0
    for place in spec_places:
        cat = place.get('category', 'tourist_spot') or 'tourist_spot'
        specs = specialty_map.get(cat, specialty_map['tourist_spot'])
        for name, desc, cat_type in specs:
            cur.execute(
                "INSERT INTO specialties (place_id, name, description, category) VALUES (%s, %s, %s, %s)",
                (place['id'], name, desc, cat_type)
            )
            spec_count += 1

    conn.commit()
    print(f"  ✓ Specialties: {spec_count} seeded across {len(spec_places)} places")
else:
    print("  ℹ Specialties already exist, skipping")

# ═══ VERIFY ═══
print("\n  Verification:")
for t in ['hero_media', 'reviews', 'specialties']:
    cur.execute(f"SELECT COUNT(*) AS cnt FROM {t}")
    print(f"    {t}: {cur.fetchone()['cnt']} rows")

cur.close()
conn.close()
print("\n✓ Demo content seeding complete!")
