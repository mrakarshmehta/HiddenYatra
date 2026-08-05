"""
Seed accommodations (hotels) and state images.
Run: python seed_hotels.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import (
    init_db, get_db, add_accommodation, update_state_image
)


def seed_hotels():
    init_db()
    conn = get_db()

    # Check if accommodations already seeded
    try:
        count = conn.execute("SELECT COUNT(*) FROM accommodations").fetchone()[0]
        if count > 0:
            print(f"Already have {count} accommodations. Skipping hotel seed.")
            conn.close()
            return
    except Exception:
        pass

    # Get all places as dict {name: id}
    places = {}
    for row in conn.execute("SELECT id, name FROM places").fetchall():
        places[row[0]] = row[1]  # id -> name
    # Also build name -> id
    name_to_id = {}
    for row in conn.execute("SELECT id, name FROM places").fetchall():
        name_to_id[row[1]] = row[0]
    conn.close()

    print("Seeding accommodation data...")

    # ══════════════════════════════════════════════════
    # BIHAR HOTELS (detailed, 2-3 per place)
    # ══════════════════════════════════════════════════
    bihar_hotels = {
        "Mahabodhi Temple, Bodh Gaya": [
            {
                "name": "Royal Residency",
                "type": "hotel",
                "price_range": "Rs 2,500 - 5,000/night",
                "description": "A comfortable mid-range hotel just 500m from the Mahabodhi Temple. Clean rooms with AC, Wi-Fi, and a rooftop restaurant serving vegetarian and non-veg cuisines.",
                "address": "Bodh Gaya Main Road, near Mahabodhi Temple",
                "phone": "+91 631 220 0456",
                "latitude": 24.6980,
                "longitude": 84.9870,
                "distance_km": 0.5,
            },
            {
                "name": "Sujata Heritage Hotel",
                "type": "hotel",
                "price_range": "Rs 3,500 - 8,000/night",
                "description": "Premium hotel with a Buddhist-inspired interior, landscaped garden, conference hall, and multi-cuisine restaurant. Popular with international pilgrims and tourists.",
                "address": "Sujata Bypass Road, Bodh Gaya",
                "phone": "+91 631 220 1234",
                "latitude": 24.6935,
                "longitude": 84.9950,
                "distance_km": 1.2,
            },
            {
                "name": "Mahabodhi Dharamshala",
                "type": "dharamshala",
                "price_range": "Rs 200 - 800/night",
                "description": "Budget pilgrim accommodation run by the temple trust. Simple, clean rooms with common facilities. Walking distance to the temple. Booking through temple office.",
                "address": "Mahabodhi Temple Complex, Bodh Gaya",
                "phone": "+91 631 220 0735",
                "latitude": 24.6958,
                "longitude": 84.9905,
                "distance_km": 0.2,
            },
        ],
        "Nalanda University Ruins": [
            {
                "name": "Nalanda Regency",
                "type": "hotel",
                "price_range": "Rs 1,800 - 4,000/night",
                "description": "Comfortable hotel near the archaeological site. Features AC rooms, restaurant, and guided tour arrangements. Good base for exploring Nalanda and Rajgir.",
                "address": "Near Nalanda Archaeological Museum",
                "phone": "+91 6112 281 234",
                "latitude": 25.1350,
                "longitude": 85.4410,
                "distance_km": 0.8,
            },
            {
                "name": "Tathagat Guest House (BSTDC)",
                "type": "guesthouse",
                "price_range": "Rs 800 - 2,000/night",
                "description": "Government-run tourist lodge by Bihar State Tourism. Clean rooms at budget prices with a canteen. Ideal for backpackers and history enthusiasts.",
                "address": "BSTDC Complex, Nalanda",
                "phone": "+91 6112 281 500",
                "latitude": 25.1370,
                "longitude": 85.4440,
                "distance_km": 1.0,
            },
        ],
        "Patna Sahib Gurudwara (Takht Sri Patna Sahib)": [
            {
                "name": "Hotel Maurya Patna",
                "type": "hotel",
                "price_range": "Rs 4,000 - 12,000/night",
                "description": "Patna's premier luxury hotel. Features elegant rooms, swimming pool, multiple restaurants (Indian, Chinese, Continental), fitness center, and banquet halls.",
                "address": "South Gandhi Maidan, Patna",
                "phone": "+91 612 220 3040",
                "website": "https://www.hotelmaurya.com",
                "latitude": 25.6107,
                "longitude": 85.1295,
                "distance_km": 3.5,
            },
            {
                "name": "Lemon Tree Premier, Patna",
                "type": "hotel",
                "price_range": "Rs 3,500 - 8,000/night",
                "description": "Modern business hotel with well-appointed rooms, a rooftop pool, multi-cuisine restaurant, and conference facilities. Located centrally with easy access to all Patna landmarks.",
                "address": "Exhibition Road, Patna",
                "phone": "+91 612 662 3333",
                "website": "https://www.lemontreehotels.com",
                "latitude": 25.6120,
                "longitude": 85.1340,
                "distance_km": 4.0,
            },
            {
                "name": "Gurudwara Sarai (Free Accommodation)",
                "type": "dharamshala",
                "price_range": "Free (donations welcome)",
                "description": "The Gurudwara provides free accommodation (sarai) for all visitors irrespective of religion. Simple, clean rooms with langar (free community meals). Advance booking recommended during festivals.",
                "address": "Takht Sri Patna Sahib Complex",
                "phone": "+91 612 264 5390",
                "latitude": 25.6079,
                "longitude": 85.1695,
                "distance_km": 0.0,
            },
        ],
        "Rajgir (Rajagriha)": [
            {
                "name": "Indo Hokke Hotel",
                "type": "resort",
                "price_range": "Rs 3,000 - 7,000/night",
                "description": "Japanese-managed resort with natural hot spring baths, tatami-style rooms, and a serene zen garden. The only hotel in India with authentic Japanese onsen facilities.",
                "address": "Rajgir, Nalanda District",
                "phone": "+91 6112 255 245",
                "latitude": 25.0280,
                "longitude": 85.4200,
                "distance_km": 1.5,
            },
            {
                "name": "Rajgir Residency (BSTDC)",
                "type": "guesthouse",
                "price_range": "Rs 1,000 - 3,000/night",
                "description": "Bihar Tourism's well-maintained property near the hot springs. AC rooms, restaurant, and parking. Great location for exploring Rajgir's Buddhist and Jain heritage sites.",
                "address": "Near Hot Springs, Rajgir",
                "phone": "+91 6112 255 350",
                "latitude": 25.0250,
                "longitude": 85.4160,
                "distance_km": 0.8,
            },
        ],
        "Vaishali - Birthplace of Democracy": [
            {
                "name": "BSTDC Tourist Bungalow, Vaishali",
                "type": "guesthouse",
                "price_range": "Rs 600 - 1,500/night",
                "description": "Government tourist bungalow near the Ashoka Pillar. Basic but clean rooms with attached bathrooms. The only proper accommodation in Vaishali town.",
                "address": "Near Vaishali Museum",
                "phone": "+91 621 234 5678",
                "latitude": 25.9860,
                "longitude": 85.1290,
                "distance_km": 0.5,
            },
        ],
        "Vikramshila University Ruins": [
            {
                "name": "Hotel Mayur, Bhagalpur",
                "type": "hotel",
                "price_range": "Rs 1,200 - 3,500/night",
                "description": "Best option in Bhagalpur city, about 40km from Vikramshila ruins. AC rooms, restaurant, and travel desk to arrange site visits.",
                "address": "Khalifabagh, Bhagalpur",
                "phone": "+91 641 242 1234",
                "latitude": 25.2425,
                "longitude": 86.9842,
                "distance_km": 40.0,
            },
        ],
        "Madhubani - Art Village": [
            {
                "name": "Hotel Sangam, Madhubani",
                "type": "hotel",
                "price_range": "Rs 800 - 2,000/night",
                "description": "Basic but clean hotel in Madhubani town. Good base for visiting Jitwarpur art village (8km away). The walls of the hotel are decorated with Madhubani paintings.",
                "address": "Station Road, Madhubani",
                "phone": "+91 6276 222 334",
                "latitude": 26.3540,
                "longitude": 86.0750,
                "distance_km": 0.5,
            },
            {
                "name": "Mithila Homestay",
                "type": "homestay",
                "price_range": "Rs 500 - 1,200/night",
                "description": "Stay with a local Maithili family in a traditional home decorated with original Madhubani art. Experience authentic Maithili cuisine and watch artists create paintings live.",
                "address": "Jitwarpur Village, near Madhubani",
                "phone": "+91 98350 12345",
                "latitude": 26.3580,
                "longitude": 86.0680,
                "distance_km": 2.0,
            },
        ],
        "Sher Shah Suri Tomb, Sasaram": [
            {
                "name": "Hotel Highway Inn",
                "type": "motel",
                "price_range": "Rs 800 - 1,800/night",
                "description": "Located on the Grand Trunk Road (NH-2), this highway motel offers clean rooms, parking, and a dhaba-style restaurant. Convenient stop for GT Road travelers visiting the tomb.",
                "address": "GT Road (NH-2), Sasaram",
                "phone": "+91 6184 222 567",
                "latitude": 24.9480,
                "longitude": 84.0310,
                "distance_km": 1.5,
            },
        ],
        "Golghar, Patna": [
            {
                "name": "Panache Hotel, Patna",
                "type": "hotel",
                "price_range": "Rs 2,500 - 6,000/night",
                "description": "Modern boutique hotel near Gandhi Maidan and Golghar. Stylish rooms with city views, rooftop dining, and close proximity to Patna's major attractions.",
                "address": "Fraser Road, Patna",
                "phone": "+91 612 222 0088",
                "latitude": 25.6150,
                "longitude": 85.1400,
                "distance_km": 1.5,
            },
            {
                "name": "Hotel Republic",
                "type": "hotel",
                "price_range": "Rs 1,800 - 4,500/night",
                "description": "Well-rated business hotel with modern amenities, restaurant, conference room, and 24-hour room service. Walking distance from Golghar.",
                "address": "Exhibition Road, near Golghar, Patna",
                "phone": "+91 612 235 6789",
                "latitude": 25.6180,
                "longitude": 85.1430,
                "distance_km": 0.8,
            },
        ],
        "Mundeshwari Temple": [
            {
                "name": "Forest Rest House, Kaimur",
                "type": "guesthouse",
                "price_range": "Rs 300 - 800/night",
                "description": "Forest department guest house at the base of Mundeshwari Hills. Basic rooms surrounded by Kaimur forest. Prior booking required through forest department.",
                "address": "Mundeshwari Hills, Kaimur Range",
                "phone": "+91 6184 250 100",
                "latitude": 25.0620,
                "longitude": 83.7640,
                "distance_km": 1.0,
            },
        ],
    }

    # ══════════════════════════════════════════════════
    # OTHER STATES HOTELS (1-2 per place)
    # ══════════════════════════════════════════════════
    other_hotels = {
        "Taj Mahal": [
            {
                "name": "The Oberoi Amarvilas",
                "type": "resort",
                "price_range": "Rs 25,000 - 80,000/night",
                "description": "Luxury 5-star resort with uninterrupted Taj Mahal views from every room. Mughal-inspired architecture, spa, pool, and fine dining.",
                "address": "Taj East Gate Road, Agra",
                "website": "https://www.oberoihotels.com",
                "latitude": 27.1720, "longitude": 78.0450, "distance_km": 0.6,
            },
        ],
        "Hawa Mahal": [
            {
                "name": "Hotel Pearl Palace",
                "type": "hotel",
                "price_range": "Rs 1,500 - 4,000/night",
                "description": "Award-winning heritage boutique hotel with rooftop restaurant overlooking Jaipur. Rated #1 budget hotel in India by TripAdvisor multiple times.",
                "address": "Hari Kishan Somani Marg, Jaipur",
                "latitude": 26.9180, "longitude": 75.8200, "distance_km": 1.0,
            },
        ],
        "Backwaters of Alleppey": [
            {
                "name": "Kerala Houseboat Stay",
                "type": "resort",
                "price_range": "Rs 6,000 - 15,000/night",
                "description": "Overnight stay on a traditional Kettuvallam (houseboat) cruising through the backwaters. Includes meals cooked onboard with fresh local seafood.",
                "address": "Alleppey Boat Jetty",
                "latitude": 9.4990, "longitude": 76.3400, "distance_km": 0.5,
            },
        ],
        "Gateway of India": [
            {
                "name": "The Taj Mahal Palace",
                "type": "hotel",
                "price_range": "Rs 18,000 - 1,00,000/night",
                "description": "India's most iconic luxury hotel, a heritage landmark overlooking the Gateway of India since 1903. Opulent rooms, 11 restaurants and bars, and legendary service.",
                "address": "Apollo Bunder, Colaba, Mumbai",
                "website": "https://www.tajhotels.com",
                "latitude": 18.9217, "longitude": 72.8332, "distance_km": 0.1,
            },
        ],
        "Calangute Beach": [
            {
                "name": "Resort Rio, Goa",
                "type": "resort",
                "price_range": "Rs 5,000 - 12,000/night",
                "description": "5-star resort with multiple pools, spa, casino, and direct beach access. Family-friendly with kids' activities and water park.",
                "address": "Calangute-Arpora Road, North Goa",
                "latitude": 15.5470, "longitude": 73.7600, "distance_km": 1.0,
            },
        ],
        "Hampi": [
            {
                "name": "Evolve Back, Hampi",
                "type": "resort",
                "price_range": "Rs 12,000 - 35,000/night",
                "description": "Ultra-luxury resort inspired by Vijayanagara architecture, set among boulder landscapes. Private pools, heritage walks, and fine dining.",
                "address": "Kamalapur, near Hampi",
                "latitude": 15.3280, "longitude": 76.4700, "distance_km": 3.0,
            },
        ],
        "Varanasi Ghats": [
            {
                "name": "BrijRama Palace",
                "type": "hotel",
                "price_range": "Rs 8,000 - 25,000/night",
                "description": "Heritage hotel in a restored 18th-century palace right on the Darbhanga Ghat. Watch the Ganga Aarti from your balcony.",
                "address": "Darbhanga Ghat, Varanasi",
                "latitude": 25.3100, "longitude": 83.0130, "distance_km": 0.5,
            },
        ],
        "Dal Lake": [
            {
                "name": "Sukoon Houseboat",
                "type": "homestay",
                "price_range": "Rs 8,000 - 18,000/night",
                "description": "Award-winning luxury houseboat on Dal Lake. Hand-carved cedar interiors, butler service, and Kashmiri wazwan cuisine. A TripAdvisor Travellers' Choice winner.",
                "address": "Dal Lake, Boulevard Road, Srinagar",
                "latitude": 34.0900, "longitude": 74.8400, "distance_km": 0.0,
            },
        ],
    }

    # Add Bihar hotels
    for place_name, hotels in bihar_hotels.items():
        pid = name_to_id.get(place_name)
        if not pid:
            print(f"  ! Place not found: {place_name}")
            continue
        for h in hotels:
            add_accommodation(pid, h)
        print(f"  + {place_name}: {len(hotels)} hotels")

    # Add other hotels
    for place_name, hotels in other_hotels.items():
        pid = name_to_id.get(place_name)
        if not pid:
            print(f"  ! Place not found: {place_name}")
            continue
        for h in hotels:
            add_accommodation(pid, h)
        print(f"  + {place_name}: {len(hotels)} hotels")

    print("\nDone! Accommodation data seeded.")


def seed_state_images():
    """Add representative image URLs for all states."""
    print("\nUpdating state images...")
    conn = get_db()
    states = conn.execute("SELECT id, name FROM states").fetchall()
    conn.close()

    # Unsplash images -- free, no auth needed with width param
    state_images = {
        "Bihar": "https://images.unsplash.com/photo-1600100397608-e18b4a498a73?w=800&q=80",
        "Rajasthan": "https://images.unsplash.com/photo-1599661046289-e31897846e41?w=800&q=80",
        "Kerala": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800&q=80",
        "Uttar Pradesh": "https://images.unsplash.com/photo-1564507592924-0bb5a26b4547?w=800&q=80",
        "Maharashtra": "https://images.unsplash.com/photo-1567157577867-05ccb1388e13?w=800&q=80",
        "Goa": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800&q=80",
        "Tamil Nadu": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=800&q=80",
        "Karnataka": "https://images.unsplash.com/photo-1600100397608-e18b4a498a73?w=800&q=80",
        "Himachal Pradesh": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=800&q=80",
        "West Bengal": "https://images.unsplash.com/photo-1558431382-27e303142255?w=800&q=80",
        "Jammu & Kashmir": "https://images.unsplash.com/photo-1597074866923-dc0589150458?w=800&q=80",
        "Uttarakhand": "https://images.unsplash.com/photo-1585136917228-c5a65eb8a40e?w=800&q=80",
        "Gujarat": "https://images.unsplash.com/photo-1609947017136-9daf32a15c28?w=800&q=80",
    }

    for row in states:
        sid, sname = row[0], row[1]
        url = state_images.get(sname)
        if url:
            update_state_image(sid, url)
            print(f"  + {sname}")
        else:
            print(f"  - No image for: {sname}")

    print("Done! State images updated.")


if __name__ == "__main__":
    seed_hotels()
    seed_state_images()
