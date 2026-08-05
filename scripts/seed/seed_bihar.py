"""
Add detailed Bihar data to the database.
Run: python seed_bihar.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import (
    init_db, create_state, create_district, create_place,
    add_specialty, get_db
)

def seed_bihar():
    init_db()

    # Create Bihar state with rich description
    bihar_id = create_state(
        "Bihar",
        "The cradle of Indian civilization -- birthplace of Buddhism and Jainism, "
        "home to the ancient Nalanda University, and the land of Emperor Ashoka. "
        "Bihar's rich heritage spans from the Maurya Empire to Mughal grandeur, "
        "with sacred pilgrimage sites, vibrant festivals like Chhath Puja, "
        "and some of India's most beloved cuisine."
    )

    # Districts
    d_patna    = create_district(bihar_id, "Patna")
    d_gaya     = create_district(bihar_id, "Gaya")
    d_nalanda  = create_district(bihar_id, "Nalanda")
    d_vaishali = create_district(bihar_id, "Vaishali")
    d_muzzafarpur = create_district(bihar_id, "Muzaffarpur")
    d_bhagalpur = create_district(bihar_id, "Bhagalpur")
    d_rajgir   = create_district(bihar_id, "Rajgir")
    d_munger   = create_district(bihar_id, "Munger")
    d_sasaram  = create_district(bihar_id, "Rohtas")
    d_madhubani = create_district(bihar_id, "Madhubani")

    places = [
        # ── PATNA ──────────────────────────────────
        {
            "name": "Mahabodhi Temple, Bodh Gaya",
            "state_id": bihar_id,
            "district_id": d_gaya,
            "description": (
                "A UNESCO World Heritage Site and one of the four holy sites related to the life of Lord Buddha. "
                "This is the very place where Siddhartha Gautama attained enlightenment under the sacred Bodhi Tree "
                "around 531 BCE, becoming the Buddha. The majestic 55-meter tall temple, with its diamond throne "
                "(Vajrasana), is one of the earliest and most significant Buddhist temples built entirely in brick. "
                "Pilgrims from across the world -- Thailand, Japan, Sri Lanka, Tibet, Myanmar -- have built their own "
                "monasteries around the temple, creating a stunning multicultural religious complex. The annual Buddha "
                "Purnima celebrations here draw hundreds of thousands of devotees."
            ),
            "category": "temple",
            "latitude": 24.6961,
            "longitude": 84.9911,
            "is_featured": True,
            "specialties": [
                {"name": "Tilkut", "description": "A crunchy sesame and sugar sweet, a beloved Gaya specialty especially popular during Makar Sankranti.", "category": "sweet", "where_to_find": "Silao village, near Bodh Gaya"},
                {"name": "Thekua", "description": "Deep-fried wheat biscuits sweetened with jaggery and flavored with cardamom -- a sacred Chhath Puja offering.", "category": "sweet", "where_to_find": "Local sweet shops across Gaya"},
            ]
        },
        {
            "name": "Nalanda University Ruins",
            "state_id": bihar_id,
            "district_id": d_nalanda,
            "description": (
                "The archaeological remains of the world's oldest residential university, a UNESCO World Heritage Site. "
                "Founded in 427 CE, Nalanda was a thriving center of learning for over 800 years, hosting 10,000+ students "
                "and 2,000 teachers from all across Asia. The university had a nine-story library called Dharmaganja "
                "(Treasury of Truth) that was said to be so vast it burned for three months when destroyed by invaders in 1193 CE. "
                "Scholars like Xuanzang and Yijing from China traveled thousands of miles to study here. The excavated ruins "
                "reveal 11 monasteries and 6 temples arranged systematically, showcasing the pinnacle of ancient Indian "
                "educational architecture. The new Nalanda University was reopened nearby in 2014 to revive this legacy."
            ),
            "category": "historical",
            "latitude": 25.1362,
            "longitude": 85.4427,
            "is_featured": True,
            "specialties": [
                {"name": "Khaja", "description": "Layered crispy pastry soaked in sugar syrup, originally offered to the Buddha -- a 2,500-year-old recipe from Rajgir-Nalanda region.", "category": "sweet", "where_to_find": "Silao (famous for Khaja), between Nalanda and Rajgir"},
            ]
        },
        {
            "name": "Patna Sahib Gurudwara (Takht Sri Patna Sahib)",
            "state_id": bihar_id,
            "district_id": d_patna,
            "description": (
                "One of the five Takhts (seats of authority) of Sikhism, built at the birthplace of Guru Gobind Singh Ji, "
                "the tenth Sikh Guru, in 1666 CE. The stunning white marble Gurudwara rises majestically on the banks of "
                "the Ganges river. It houses sacred relics including the Guru's baby shoes, a sword, and a 'pangura' (cradle). "
                "During Guru Gobind Singh's Prakash Utsav (birthday celebrations), millions of Sikh devotees from around the "
                "world visit this holy shrine. The architecture combines Sikh, Mughal, and Rajput styles, and the langar "
                "(community kitchen) serves free meals to thousands of visitors daily."
            ),
            "category": "temple",
            "latitude": 25.6079,
            "longitude": 85.1695,
            "is_featured": True,
            "specialties": [
                {"name": "Litti Chokha", "description": "Bihar's soul food -- roasted wheat balls stuffed with sattu (roasted gram flour), served with mashed vegetables (chokha) of brinjal, tomato, and potato. Best enjoyed with ghee and achaar.", "category": "food", "where_to_find": "Raju Litti Chokha, Boring Road, Patna"},
                {"name": "Kadhi Bari", "description": "Crispy gram flour dumplings (bari) in tangy yogurt gravy -- a staple comfort food of every Bihari household.", "category": "food", "where_to_find": "Bansi Vilas, Patna"},
            ]
        },
        {
            "name": "Rajgir (Rajagriha)",
            "state_id": bihar_id,
            "district_id": d_rajgir,
            "description": (
                "The ancient capital of the Magadha kingdom and a city sacred to Buddhism, Jainism, and Hinduism alike. "
                "Surrounded by five hills (Panch Pahar), Rajgir is where Buddha spent many years teaching and where the "
                "first Buddhist Council was held at Saptaparni Cave after his death. King Bimbisara ruled from here and "
                "built the famous Cyclopean Wall. The Japanese Shanti Stupa (Peace Pagoda) on Griddhakuta Hill offers "
                "panoramic views of the valley. The natural hot springs at Brahmakund are believed to have healing properties "
                "and have been sacred since Vedic times. The ruins of Ajatashatru's fort and the Venuvana monastery where "
                "Buddha stayed make this an unparalleled archaeological treasure."
            ),
            "category": "historical",
            "latitude": 25.0261,
            "longitude": 85.4176,
            "is_featured": True,
            "specialties": [
                {"name": "Khaja", "description": "The original Silao Khaja from nearby Silao village -- flaky, layered pastry dipped in sugar syrup. A GI-tagged delicacy.", "category": "sweet", "where_to_find": "Silao village sweet shops (on Rajgir-Nalanda road)"},
                {"name": "Pedakiya", "description": "Milk-based sweet fudge balls flavored with cardamom and saffron.", "category": "sweet", "where_to_find": "Local halwai shops, Rajgir market"},
            ]
        },
        {
            "name": "Vaishali - Birthplace of Democracy",
            "state_id": bihar_id,
            "district_id": d_vaishali,
            "description": (
                "One of the oldest republics in human history, Vaishali is where the world's first democratic system "
                "(the Vajjian Confederacy/Licchavi Republic) flourished around 600 BCE -- centuries before Greek democracy. "
                "It is sacred to both Buddhism (Buddha delivered his last sermon here) and Jainism (birthplace of Lord "
                "Mahavira, the 24th Tirthankara). The Ashoka Pillar with its single lion capital stands as testimony to "
                "Emperor Ashoka's reverence for this land. The Kolhua archaeological complex contains the sacred relic "
                "stupa and an ancient coronation tank (Abhishek Pushkarini). The annual Vaishali Mahotsav festival "
                "celebrates its democratic heritage with cultural programs and Buddhist ceremonies."
            ),
            "category": "historical",
            "latitude": 25.9848,
            "longitude": 85.1275,
            "is_featured": True,
            "specialties": [
                {"name": "Chura-Dahi (Flattened Rice with Curd)", "description": "A simple but iconic Bihari breakfast -- beaten rice mixed with thick curd, jaggery, and sometimes banana. A must-have during Makar Sankranti.", "category": "food", "where_to_find": "Every household and roadside stall in Vaishali"},
            ]
        },
        {
            "name": "Vikramshila University Ruins",
            "state_id": bihar_id,
            "district_id": d_bhagalpur,
            "description": (
                "The ruins of one of ancient India's two greatest universities (along with Nalanda), founded by King "
                "Dharmapala of the Pala dynasty around 783 CE. Vikramshila was a premier center for Vajrayana Buddhism "
                "and Tantric studies, with 107 temples, 6 colleges, and over 1,000 students. The great scholar Atisha "
                "Dipankara, who revived Buddhism in Tibet, was a professor here. The site, on a hill overlooking the "
                "Ganges at Antichak village, has yielded stunning terracotta plaques, bronze statues, and a massive "
                "central temple with intricate carvings. It represents Bihar's unparalleled contribution to global education."
            ),
            "category": "historical",
            "latitude": 25.3297,
            "longitude": 87.2830,
            "is_featured": False,
            "specialties": [
                {"name": "Katarni Chawal", "description": "An aromatic short-grain rice variety unique to Bhagalpur, prized for its fragrance and soft texture. A GI-tagged Bihari specialty.", "category": "food", "where_to_find": "Local markets, Bhagalpur"},
                {"name": "Manga-Jhol (Mango Curry)", "description": "Tangy raw mango curry cooked in mustard paste -- a Bhagalpur summer delicacy.", "category": "food", "where_to_find": "Home kitchens and local dhabas"},
            ]
        },
        {
            "name": "Madhubani - Art Village",
            "state_id": bihar_id,
            "district_id": d_madhubani,
            "description": (
                "The birthplace of Madhubani painting (Mithila art), one of India's most celebrated folk art forms. "
                "This ancient art tradition, dating back to the time of the Ramayana (King Janak is said to have "
                "commissioned paintings for Sita's wedding), uses natural dyes and pigments to create intricate geometric "
                "patterns and mythological scenes. The entire village of Jitwarpur is adorned with these paintings on every "
                "wall, floor, and courtyard. Madhubani art received a GI tag and has gained international recognition, "
                "with works displayed in galleries worldwide. Walking through Jitwarpur is like walking through a living art gallery."
            ),
            "category": "cultural",
            "latitude": 26.3563,
            "longitude": 86.0715,
            "is_featured": True,
            "specialties": [
                {"name": "Madhubani Paintings", "description": "Vibrant folk art on handmade paper and fabric using natural colors -- from wall murals to postcards, every piece is unique.", "category": "craft", "where_to_find": "Jitwarpur village artisan homes and cooperatives"},
                {"name": "Makhana (Fox Nuts)", "description": "Roasted and spiced lotus seed puffs -- a healthy superfood snack that's a major Mithila export.", "category": "food", "where_to_find": "Everywhere in Mithilanchal region"},
                {"name": "Dahi Chura", "description": "Flattened rice with thick fresh curd and jaggery -- the ceremonial Maithili breakfast.", "category": "food", "where_to_find": "Every Maithili household, especially during festivals"},
            ]
        },
        {
            "name": "Sher Shah Suri Tomb, Sasaram",
            "state_id": bihar_id,
            "district_id": d_sasaram,
            "description": (
                "An architectural masterpiece standing in the middle of an artificial lake -- the mausoleum of Sher Shah Suri, "
                "the brilliant Afghan ruler who defeated Mughal emperor Humayun and built the Grand Trunk Road from Kabul to "
                "Kolkata. Built in 1545 in Indo-Afghan style, this octagonal red sandstone tomb rises 37 meters high with a "
                "magnificent dome. It is considered one of the finest examples of medieval Indian architecture, often compared "
                "to the Taj Mahal in its grandeur. The tomb's reflection in the surrounding lake creates a breathtaking visual "
                "spectacle, especially at sunset."
            ),
            "category": "historical",
            "latitude": 24.9458,
            "longitude": 84.0341,
            "is_featured": False,
            "specialties": [
                {"name": "Sattu Paratha", "description": "Flatbread stuffed with spiced roasted gram flour (sattu) -- the protein powerhouse of Bihari cuisine. Best with raw onion and green chili.", "category": "food", "where_to_find": "Highway dhabas on Grand Trunk Road, Sasaram"},
            ]
        },
        {
            "name": "Golghar, Patna",
            "state_id": bihar_id,
            "district_id": d_patna,
            "description": (
                "A massive beehive-shaped granary built in 1786 by Captain John Garstin for the British Army to store grain "
                "after the devastating famine of 1770. Standing 29 meters tall with walls 3.6 meters thick at the base, this "
                "architectural marvel has a unique design -- two staircases spiral around the outside and workers carrying grain "
                "would enter from one side and exit from the other without collision. Climb the 145 steps to the top for a "
                "stunning 360-degree panoramic view of Patna city and the Ganges river. Ironically, the granary was never "
                "filled to capacity as the walls could not support the full weight. Today it's Patna's most iconic landmark."
            ),
            "category": "historical",
            "latitude": 25.6200,
            "longitude": 85.1448,
            "is_featured": True,
            "specialties": [
                {"name": "Sattu Sharbat", "description": "Refreshing cold drink made from roasted gram flour, lemon, salt, and spices -- Bihar's original protein shake, perfect for hot summers.", "category": "drink", "where_to_find": "Street vendors near Golghar and Gandhi Maidan"},
                {"name": "Litti Chokha", "description": "Bihar's most famous dish -- smoky coal-roasted wheat balls stuffed with sattu, served with baigan (brinjal) and tomato chokha, drowned in desi ghee.", "category": "food", "where_to_find": "Litti Hub and Champaran Meat House, Patna"},
                {"name": "Bihari Kebab", "description": "Tender minced meat kebabs marinated with poppy seed paste and slow-cooked on skewers -- Patna's legendary non-veg street food.", "category": "food", "where_to_find": "Haji Karim, Phulwari Sharif, Patna"},
            ]
        },
        {
            "name": "Mundeshwari Temple",
            "state_id": bihar_id,
            "district_id": d_sasaram,
            "description": (
                "Considered one of the oldest functional Hindu temples in India, the Mundeshwari Devi Temple dates back to "
                "108 CE based on its inscriptions, making it nearly 2,000 years old. Perched atop the Mundeshwari Hills at "
                "an elevation of 608 feet in the Kaimur Range, this octagonal stone temple is dedicated to Lord Shiva and "
                "Shakti. The temple features exquisite Gupta-period carvings, including a rare Chaturmukha (four-faced) "
                "Shiv Linga and a magnificent Varaha (boar incarnation of Vishnu) sculpture. The ASI maintains this temple "
                "as one of Bihar's most important archaeological monuments."
            ),
            "category": "temple",
            "latitude": 25.0612,
            "longitude": 83.7632,
            "is_featured": False,
            "specialties": [
                {"name": "Pua-Pitha", "description": "Deep-fried rice flour pancakes sweetened with jaggery -- a traditional temple offering and festive treat.", "category": "sweet", "where_to_find": "Temple prasad stalls and village homes"},
            ]
        },
    ]

    for pd in places:
        specs = pd.pop("specialties", [])
        place_id = create_place(pd)
        for spec in specs:
            add_specialty(place_id, spec)
        print(f"  + {pd['name']}")

    print(f"\nDone! Added {len(places)} Bihar places with detailed descriptions and specialties!")


if __name__ == "__main__":
    seed_bihar()
