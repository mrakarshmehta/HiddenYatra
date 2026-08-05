"""
Seed the database with sample Indian tourist places.
Run once: python seed_data.py
"""
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import (
    init_db, create_state, create_district, create_place,
    add_specialty, get_db
)


def seed():
    """Populate the database with real Indian places."""
    init_db()

    # Check if already seeded
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM places").fetchone()[0]
    conn.close()
    if count > 0:
        print(f"Database already has {count} places. Skipping seed.")
        return

    print("Seeding database with sample data...")

    # ── States ───────────────────────────────────
    states = {
        "Rajasthan": create_state("Rajasthan", "The Land of Kings — known for majestic forts, vibrant culture, and vast deserts."),
        "Kerala": create_state("Kerala", "God's Own Country — lush backwaters, spice gardens, and Ayurveda traditions."),
        "Uttar Pradesh": create_state("Uttar Pradesh", "Home to the Taj Mahal and the spiritual heart of India."),
        "Maharashtra": create_state("Maharashtra", "The land of Marathas — from the bustling Mumbai to serene Western Ghats."),
        "Goa": create_state("Goa", "India's beach paradise — golden sands, Portuguese heritage, and vibrant nightlife."),
        "Tamil Nadu": create_state("Tamil Nadu", "Land of temples — ancient Dravidian architecture and rich cultural heritage."),
        "Karnataka": create_state("Karnataka", "From the tech hub Bengaluru to the ruins of Hampi."),
        "Himachal Pradesh": create_state("Himachal Pradesh", "The abode of snow — stunning hill stations and adventure sports."),
        "West Bengal": create_state("West Bengal", "City of Joy Kolkata, Sundarbans mangroves, and rich literary heritage."),
        "Jammu & Kashmir": create_state("Jammu & Kashmir", "Paradise on Earth — Dal Lake, Mughal gardens, and snow-capped peaks."),
        "Uttarakhand": create_state("Uttarakhand", "Dev Bhoomi — Land of the Gods with sacred rivers and Himalayan beauty."),
        "Gujarat": create_state("Gujarat", "The land of legends — from the Gir lions to the Rann of Kutch."),
    }

    # ── Districts ────────────────────────────────
    districts = {
        "Jaipur": create_district(states["Rajasthan"], "Jaipur"),
        "Jodhpur": create_district(states["Rajasthan"], "Jodhpur"),
        "Udaipur": create_district(states["Rajasthan"], "Udaipur"),
        "Agra": create_district(states["Uttar Pradesh"], "Agra"),
        "Varanasi": create_district(states["Uttar Pradesh"], "Varanasi"),
        "Alappuzha": create_district(states["Kerala"], "Alappuzha"),
        "Munnar": create_district(states["Kerala"], "Idukki"),
        "Mumbai": create_district(states["Maharashtra"], "Mumbai"),
        "Pune": create_district(states["Maharashtra"], "Pune"),
        "North Goa": create_district(states["Goa"], "North Goa"),
        "South Goa": create_district(states["Goa"], "South Goa"),
        "Madurai": create_district(states["Tamil Nadu"], "Madurai"),
        "Bellary": create_district(states["Karnataka"], "Bellary"),
        "Manali": create_district(states["Himachal Pradesh"], "Kullu"),
        "Shimla": create_district(states["Himachal Pradesh"], "Shimla"),
        "Kolkata": create_district(states["West Bengal"], "Kolkata"),
        "Srinagar": create_district(states["Jammu & Kashmir"], "Srinagar"),
        "Dehradun": create_district(states["Uttarakhand"], "Dehradun"),
        "Kutch": create_district(states["Gujarat"], "Kutch"),
    }

    # ── Places ───────────────────────────────────
    places_data = [
        {
            "name": "Taj Mahal",
            "state_id": states["Uttar Pradesh"],
            "district_id": districts["Agra"],
            "description": "An ivory-white marble mausoleum on the right bank of the Yamuna river. Built by Mughal emperor Shah Jahan in memory of his wife Mumtaz Mahal, the Taj Mahal is widely regarded as the finest example of Mughal architecture and a jewel of Muslim art in India. It was designated as a UNESCO World Heritage Site in 1983.",
            "category": "historical",
            "latitude": 27.1751,
            "longitude": 78.0421,
            "is_featured": True,
            "specialties": [
                {"name": "Petha", "description": "A translucent soft candy made from ash gourd, a signature Agra sweet.", "category": "sweet", "where_to_find": "Panchhi Petha, Agra"},
                {"name": "Mughlai Paratha", "description": "Stuffed paratha with minced meat and egg, a rich Mughlai delicacy.", "category": "food", "where_to_find": "Joney Boy Dhaba"},
            ]
        },
        {
            "name": "Hawa Mahal",
            "state_id": states["Rajasthan"],
            "district_id": districts["Jaipur"],
            "description": "The Palace of Winds is a stunning five-story pink sandstone structure with 953 small windows called jharokhas, designed to allow royal women to observe street life without being seen. Built in 1799 by Maharaja Sawai Pratap Singh, this honeycombed masterpiece is Jaipur's most iconic landmark.",
            "category": "historical",
            "latitude": 26.9239,
            "longitude": 75.8267,
            "is_featured": True,
            "specialties": [
                {"name": "Dal Baati Churma", "description": "Rajasthan's iconic trio — baked wheat balls with lentils and sweet crumbled bread.", "category": "food", "where_to_find": "Laxmi Mishthan Bhandar (LMB)"},
                {"name": "Ghevar", "description": "A disc-shaped sweet cake made with flour, soaked in sugar syrup.", "category": "sweet", "where_to_find": "Rawat Mishthan Bhandar"},
            ]
        },
        {
            "name": "Backwaters of Alleppey",
            "state_id": states["Kerala"],
            "district_id": districts["Alappuzha"],
            "description": "A network of brackish lagoons and lakes lying parallel to the Arabian Sea coast. The serene houseboat cruises through palm-fringed canals offer a unique glimpse into Kerala's village life. Named by National Geographic as one of the 'must-see' destinations in the world.",
            "category": "nature",
            "latitude": 9.4981,
            "longitude": 76.3388,
            "is_featured": True,
            "specialties": [
                {"name": "Karimeen Pollichathu", "description": "Pearl spot fish marinated in spices, wrapped in banana leaf, and pan-fried.", "category": "food", "where_to_find": "Thaff Houseboat Kitchen"},
                {"name": "Appam with Stew", "description": "Lacy rice pancakes served with coconut milk vegetable stew.", "category": "food", "where_to_find": "Kream Korner, Alleppey"},
            ]
        },
        {
            "name": "Gateway of India",
            "state_id": states["Maharashtra"],
            "district_id": districts["Mumbai"],
            "description": "An arch-monument built in the 20th century to commemorate the landing of King George V and Queen Mary at Apollo Bunder. This grand basalt structure overlooks the Arabian Sea and is one of Mumbai's most photographed landmarks, visited by thousands of tourists daily.",
            "category": "historical",
            "latitude": 18.9220,
            "longitude": 72.8347,
            "is_featured": True,
            "specialties": [
                {"name": "Vada Pav", "description": "Mumbai's iconic street food — spiced potato fritter in a bun with chutneys.", "category": "food", "where_to_find": "Ashok Vada Pav, Kirti College"},
                {"name": "Pav Bhaji", "description": "Buttery mashed vegetable curry served with soft bread rolls.", "category": "food", "where_to_find": "Sardar Pav Bhaji, Tardeo"},
            ]
        },
        {
            "name": "Hampi",
            "state_id": states["Karnataka"],
            "district_id": districts["Bellary"],
            "description": "The ruins of the Vijayanagara Empire, a UNESCO World Heritage Site. Spread across boulder-strewn hills, Hampi's temples, royal enclosures, and market streets tell the story of one of the largest and richest cities in medieval India. The Vitthala Temple with its iconic stone chariot is a marvel of architecture.",
            "category": "historical",
            "latitude": 15.3350,
            "longitude": 76.4600,
            "is_featured": True,
            "specialties": [
                {"name": "Jolada Rotti", "description": "Sorghum flatbread, a staple of North Karnataka cuisine.", "category": "food", "where_to_find": "Mango Tree Restaurant, Hampi"},
            ]
        },
        {
            "name": "Varanasi Ghats",
            "state_id": states["Uttar Pradesh"],
            "district_id": districts["Varanasi"],
            "description": "The sacred ghats along the Ganges river in one of the world's oldest continuously inhabited cities. The mesmerizing Ganga Aarti ceremony at Dashashwamedh Ghat draws thousands of devotees at sunset. Mark Twain wrote: 'Varanasi is older than history, older than tradition, older than legend.'",
            "category": "temple",
            "latitude": 25.3176,
            "longitude": 83.0106,
            "is_featured": True,
            "specialties": [
                {"name": "Banarasi Paan", "description": "Betel leaf preparation with areca nut, lime, and sweet fillings — a famous Varanasi tradition.", "category": "food", "where_to_find": "Keshav Tambul, Lanka"},
                {"name": "Kachori Sabzi", "description": "Crispy fried bread stuffed with lentils, served with spicy potato curry.", "category": "food", "where_to_find": "Ram Bhandar, near Kashi Vishwanath"},
            ]
        },
        {
            "name": "Calangute Beach",
            "state_id": states["Goa"],
            "district_id": districts["North Goa"],
            "description": "Known as the 'Queen of Beaches', Calangute is Goa's largest and most popular beach. Stretching along the Arabian Sea, it offers golden sands, water sports, beach shacks, and a vibrant nightlife scene. The perfect blend of sun, sand, and Goan hospitality.",
            "category": "beach",
            "latitude": 15.5449,
            "longitude": 73.7553,
            "is_featured": True,
            "specialties": [
                {"name": "Fish Curry Rice", "description": "The quintessential Goan meal — spicy coconut fish curry with steamed rice.", "category": "food", "where_to_find": "Brittos, Baga Beach"},
                {"name": "Bebinca", "description": "A traditional Goan layered pudding dessert of Portuguese origin.", "category": "sweet", "where_to_find": "Cafe Bodega, Sunaparanta"},
            ]
        },
        {
            "name": "Meenakshi Amman Temple",
            "state_id": states["Tamil Nadu"],
            "district_id": districts["Madurai"],
            "description": "A historic Hindu temple located on the southern bank of the Vaigai River. This temple is dedicated to Parvati (Meenakshi) and Shiva (Sundareshwar). Its towering gopurams (gateway towers) covered with thousands of colorful sculptures are an extraordinary example of Dravidian architecture.",
            "category": "temple",
            "latitude": 9.9195,
            "longitude": 78.1193,
            "is_featured": True,
            "specialties": [
                {"name": "Jigarthanda", "description": "A cold, sweet drink made with milk, almond gum, sarsaparilla syrup, and ice cream.", "category": "drink", "where_to_find": "Famous Jigarthanda, Madurai"},
            ]
        },
        {
            "name": "Mehrangarh Fort",
            "state_id": states["Rajasthan"],
            "district_id": districts["Jodhpur"],
            "description": "One of the largest forts in India, perched 400 feet above the blue city of Jodhpur on a cliff. Founded in 1459 by Rao Jodha, the fort houses magnificent palaces, courtyards, and a museum with an extensive collection of royal artifacts. Its massive walls and sweeping views make it an awe-inspiring experience.",
            "category": "historical",
            "latitude": 26.2984,
            "longitude": 73.0183,
            "is_featured": False,
            "specialties": [
                {"name": "Mirchi Vada", "description": "Large green chilli stuffed with spiced potato, battered and fried.", "category": "food", "where_to_find": "Shahi Samosa, Jodhpur"},
                {"name": "Makhaniya Lassi", "description": "Rich, creamy buttermilk drink topped with malai, a Jodhpur specialty.", "category": "drink", "where_to_find": "Mishrilal Hotel, Sardar Market"},
            ]
        },
        {
            "name": "Munnar Tea Gardens",
            "state_id": states["Kerala"],
            "district_id": districts["Munnar"],
            "description": "Rolling hills carpeted with emerald-green tea plantations at an altitude of 1,600 meters. Munnar's misty mornings, cool climate, and breathtaking views of the Western Ghats make it Kerala's most sought-after hill station. The Eravikulam National Park nearby is home to the endangered Nilgiri Tahr.",
            "category": "nature",
            "latitude": 10.0889,
            "longitude": 77.0595,
            "is_featured": False,
            "specialties": [
                {"name": "Munnar Tea", "description": "World-famous high-grown tea with a unique flavor from the Western Ghats.", "category": "drink", "where_to_find": "Kanan Devan Tea Museum"},
            ]
        },
        {
            "name": "Dal Lake",
            "state_id": states["Jammu & Kashmir"],
            "district_id": districts["Srinagar"],
            "description": "The jewel in the crown of Kashmir — a stunning lake surrounded by Mughal gardens, houseboats, and the Zabarwan mountains. Shikara rides at sunset, floating markets, and the reflection of snow-capped peaks make Dal Lake one of India's most romantic and photographed destinations.",
            "category": "lake",
            "latitude": 34.0837,
            "longitude": 74.8378,
            "is_featured": True,
            "specialties": [
                {"name": "Rogan Josh", "description": "Aromatic lamb curry slow-cooked with Kashmiri spices and yogurt.", "category": "food", "where_to_find": "Mughal Darbar, Srinagar"},
                {"name": "Kahwa", "description": "Traditional Kashmiri green tea with saffron, cardamom, cinnamon, and almonds.", "category": "drink", "where_to_find": "Any Shikara or houseboat"},
            ]
        },
        {
            "name": "Rishikesh",
            "state_id": states["Uttarakhand"],
            "district_id": districts["Dehradun"],
            "description": "The Yoga Capital of the World, situated at the foothills of the Himalayas along the Ganges. Known for its ashrams, adventure sports (river rafting, bungee jumping), the iconic Laxman Jhula suspension bridge, and the Beatles' ashram. A spiritual and adventure destination rolled into one.",
            "category": "adventure",
            "latitude": 30.0869,
            "longitude": 78.2676,
            "is_featured": False,
            "specialties": [
                {"name": "Chotiwala Thali", "description": "A legendary pure vegetarian thali served at the iconic Chotiwala restaurant since 1958.", "category": "food", "where_to_find": "Chotiwala Restaurant, Ram Jhula"},
            ]
        },
        {
            "name": "City Palace, Udaipur",
            "state_id": states["Rajasthan"],
            "district_id": districts["Udaipur"],
            "description": "A majestic complex of palaces overlooking Lake Pichola, built over nearly 400 years by successive Mewar rulers. The palace blends Rajasthani and Mughal architectural styles, with ornate balconies, towers, and courtyards. Udaipur's romantic lakeside setting earned it the title 'Venice of the East'.",
            "category": "historical",
            "latitude": 24.5764,
            "longitude": 73.6815,
            "is_featured": False,
            "specialties": [
                {"name": "Daal Baati Churma", "description": "The Mewari version of this Rajasthani classic, served with pure ghee.", "category": "food", "where_to_find": "Natraj Restaurant, Udaipur"},
            ]
        },
        {
            "name": "Victoria Memorial",
            "state_id": states["West Bengal"],
            "district_id": districts["Kolkata"],
            "description": "A grand white marble memorial built between 1906-1921, dedicated to Queen Victoria. Now a museum housing a vast collection of artifacts from the British Raj. Surrounded by lush gardens, its stunning architecture blends British and Mughal elements. It is one of Kolkata's most iconic monuments.",
            "category": "historical",
            "latitude": 22.5448,
            "longitude": 88.3426,
            "is_featured": False,
            "specialties": [
                {"name": "Rasgulla", "description": "Spongy white cheese balls soaked in sugar syrup — Bengal's gift to dessert lovers.", "category": "sweet", "where_to_find": "K.C. Das, Esplanade"},
                {"name": "Kathi Roll", "description": "Paratha wrapped around spiced kebab filling — Kolkata's signature street food.", "category": "food", "where_to_find": "Nizam's, New Market"},
            ]
        },
        {
            "name": "Rann of Kutch",
            "state_id": states["Gujarat"],
            "district_id": districts["Kutch"],
            "description": "The Great Rann of Kutch is a vast white salt desert that transforms into a surreal moonscape under the full moon. During the Rann Utsav festival (Nov-Feb), the area comes alive with cultural performances, handicraft exhibitions, and camel rides across the gleaming white expanse.",
            "category": "nature",
            "latitude": 23.7337,
            "longitude": 69.8597,
            "is_featured": False,
            "specialties": [
                {"name": "Dabeli", "description": "Spiced potato filling in a bun with pomegranate, peanuts, and chutneys — Kutchi street food.", "category": "food", "where_to_find": "Luv Kush Dabeli, Mandvi"},
            ]
        },
        {
            "name": "Shimla Ridge",
            "state_id": states["Himachal Pradesh"],
            "district_id": districts["Shimla"],
            "description": "The Ridge is a large open space in the heart of Shimla, offering stunning views of the surrounding mountains. It serves as the center of cultural activities and is home to the iconic Christ Church and the Scandal Point. A walk along the Ridge at sunset is an unforgettable experience.",
            "category": "mountain",
            "latitude": 31.1048,
            "longitude": 77.1734,
            "is_featured": False,
            "specialties": [
                {"name": "Siddu", "description": "Steamed wheat bread stuffed with poppy seeds or walnut paste, served with ghee.", "category": "food", "where_to_find": "Wake & Bake Cafe, Mall Road"},
            ]
        },
        {
            "name": "Manali - Solang Valley",
            "state_id": states["Himachal Pradesh"],
            "district_id": districts["Manali"],
            "description": "A picturesque valley located 13 km from Manali, famous for adventure sports including paragliding, zorbing, skiing, and rope-way rides. Surrounded by snow-capped peaks and dense deodar forests, Solang Valley is a year-round destination for thrill-seekers and nature lovers alike.",
            "category": "adventure",
            "latitude": 32.3154,
            "longitude": 77.1574,
            "is_featured": False,
            "specialties": [
                {"name": "Trout Fish", "description": "Freshwater trout from Himalayan streams, grilled or pan-fried with local spices.", "category": "food", "where_to_find": "Johnson's Cafe, Manali"},
            ]
        },
    ]

    for pd in places_data:
        specs = pd.pop("specialties", [])
        place_id = create_place(pd)
        for spec in specs:
            add_specialty(place_id, spec)
        print(f"  + {pd['name']}")

    print(f"\nDone! Seeded {len(places_data)} places across {len(states)} states!")


if __name__ == "__main__":
    seed()
