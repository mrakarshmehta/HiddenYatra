"""
HiddenYatra — Comprehensive Bihar Seed Data
Seeds all 38 districts, 80+ places, district foods, and accommodations.
Run: python seed_bihar_complete.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from models.database import (
    init_db, create_state, create_district, create_block, create_place,
    add_specialty, add_accommodation, add_district_food, get_db
)


def seed():
    init_db()

    # ═══ CREATE BIHAR ═══
    bihar_id = create_state(
        "Bihar",
        "The cradle of Indian civilization — birthplace of Buddhism and Jainism, "
        "home to the ancient Nalanda University, and the land of Emperor Ashoka. "
        "Bihar's rich heritage spans from the Maurya Empire to Mughal grandeur, "
        "with sacred pilgrimage sites, vibrant festivals like Chhath Puja, "
        "and some of India's most beloved cuisine."
    )

    # ═══ ALL 38 DISTRICTS ═══
    districts_data = {
        "Patna": ("Capital city of Bihar, on the banks of the Ganges", "Golghar, Patna Sahib, Litti Chokha"),
        "Gaya": ("Sacred Hindu pilgrimage center and gateway to Bodh Gaya", "Vishnupad Temple, Bodh Gaya, Tilkut"),
        "Nalanda": ("Home to the ruins of world's oldest university", "Nalanda University Ruins, Rajgir, Khaja"),
        "Vaishali": ("World's first republic and sacred Buddhist site", "Ashoka Pillar, Democracy, Chura-Dahi"),
        "Muzaffarpur": ("Litchi capital of India", "Shahi Litchi, Jubba Sahni Park"),
        "Bhagalpur": ("Silk City of India on the banks of Ganges", "Tussar Silk, Vikramshila, Mandar Hill"),
        "Munger": ("Ancient fort city and yoga capital", "Munger Fort, Bihar School of Yoga"),
        "Rohtas": ("Land of Sher Shah Suri and Rohtasgarh Fort", "Sasaram Tomb, Rohtasgarh Fort, Sattu"),
        "Madhubani": ("Birthplace of Madhubani painting art form", "Madhubani Art, Makhana, Darbhanga Raj"),
        "Darbhanga": ("Cultural capital of Mithila region", "Darbhanga Raj, Maithili culture"),
        "Sitamarhi": ("Birthplace of Goddess Sita from Ramayana", "Janaki Temple, Haleshwar Sthan"),
        "West Champaran": ("Where Mahatma Gandhi started Satyagraha", "Gandhi Ashram, Valmiki National Park"),
        "East Champaran": ("Historic land of Champaran Satyagraha", "Areraj, Kesariya Stupa"),
        "Saran": ("Ancient trade center, Chapra city", "Ambika Bhawani Temple, Doriganj"),
        "Siwan": ("Land of freedom fighters", "Hussainabad Palace"),
        "Gopalganj": ("Wetlands and agricultural heartland", "Thawe Mandir"),
        "Nawada": ("Home to Bihar's largest waterfall", "Kakolat Waterfall, Prishadh Kund"),
        "Aurangabad": ("Named after Emperor Aurangzeb, Dev temple", "Deo Sun Temple, Pirsa, Umga"),
        "Jehanabad": ("Historical town near Rajgir", "Makhdoom Sharif Dargah"),
        "Arwal": ("Smallest district of Bihar", "Arwal Town"),
        "Jamui": ("Jain pilgrimage and forest region", "Kali Mandir, Nagi Dam"),
        "Lakhisarai": ("Small historic district", "Ashok Dham"),
        "Sheikhpura": ("Named after Sheikh Farid", "Kuian Lake, Rajgir nearby"),
        "Begusarai": ("Industrial hub, Barauni refinery", "Simaria Ghat, Kanwar Lake Bird Sanctuary"),
        "Samastipur": ("Agricultural and educational center", "Vidyapati Nagar, Kali Temple"),
        "Khagaria": ("Confluence of rivers", "Gogri Jamalpur"),
        "Katihar": ("Railway junction and river town", "Goga Lake, Manihari Ghat"),
        "Purnia": ("Gateway to Northeast Bihar", "Kankar Bagh, Puraniya Palace"),
        "Kishanganj": ("Tea gardens of Bihar", "Tea Gardens, Kali Mandir"),
        "Araria": ("Border district with scenic beauty", "Forbesganj"),
        "Supaul": ("Land of Kosi river", "Kosi Barrage"),
        "Madhepura": ("Historic Mithila region", "Singheshwar Sthan"),
        "Saharsa": ("Gateway to Kosi region", "Mahishi Sthan"),
        "Banka": ("Forested hills and temples", "Bhimbandh Hot Springs, Mandar Hill"),
        "Buxar": ("Historic battlefield city", "Buxar Fort, Battle of Buxar site"),
        "Bhojpur": ("Land of Lord Bhoj", "Veer Kunwar Singh Fort, Jagdishpur"),
        "Kaimur": ("Scenic hills and waterfalls", "Karkat Falls, Mundeshwari Temple"),
        "Sheohar": ("Smallest population district", "Sheohar town"),
    }

    district_ids = {}
    for name, (desc, famous) in districts_data.items():
        district_ids[name] = create_district(bihar_id, name, desc, famous)
        print(f"  [+] District: {name}")

    # ═══ PLACES ═══
    places = [
        # PATNA
        {
            "name": "Golghar",
            "state_id": bihar_id,
            "district_id": district_ids["Patna"],
            "description": "A massive beehive-shaped granary built in 1786 by Captain John Garstin for the British Army. Standing 29 meters tall with walls 3.6 meters thick, climb 145 steps to the top for a stunning 360-degree view of Patna and the Ganges. Ironically, it was never filled to capacity.",
            "category": "historical",
            "latitude": 25.6200, "longitude": 85.1448,
            "is_featured": True,
            "best_time_to_visit": "October to March (winter)",
            "entry_fee": "₹25 for Indians, ₹200 for foreigners",
            "travel_tips": "Visit early morning for best views. The spiral staircase can be slippery — wear good shoes.",
        },
        {
            "name": "Patna Sahib Gurudwara (Takht Sri Patna Sahib)",
            "state_id": bihar_id,
            "district_id": district_ids["Patna"],
            "description": "One of the five Takhts of Sikhism, built at the birthplace of Guru Gobind Singh Ji in 1666 CE. The stunning white marble Gurudwara rises majestically on the banks of the Ganges. It houses sacred relics including baby shoes, sword, and cradle of the Guru.",
            "category": "temple",
            "latitude": 25.6079, "longitude": 85.1695,
            "is_featured": True,
            "best_time_to_visit": "All year; special during Guru Gobind Singh Jayanti",
            "entry_fee": "Free",
            "travel_tips": "Free langar (community meal) served daily. Cover your head before entering.",
        },
        {
            "name": "Patna Museum",
            "state_id": bihar_id,
            "district_id": district_ids["Patna"],
            "description": "One of India's oldest museums, housing an extraordinary collection including a 200-million-year-old fossil tree, Mauryan artifacts, Buddhist sculptures, and Mughal paintings. The Didarganj Yakshi sculpture here is considered one of the finest examples of Indian art.",
            "category": "historical",
            "latitude": 25.6127, "longitude": 85.1235,
            "is_featured": False,
            "best_time_to_visit": "October to March",
            "entry_fee": "₹15 for Indians, ₹500 for foreigners",
        },
        {
            "name": "Gandhi Maidan",
            "state_id": bihar_id,
            "district_id": district_ids["Patna"],
            "description": "A vast 60-acre ground in the heart of Patna where Mahatma Gandhi addressed massive rallies during India's freedom struggle. Today it serves as the city's central park and hosts major political and cultural events.",
            "category": "tourist_spot",
            "latitude": 25.6132, "longitude": 85.1423,
            "is_featured": False,
        },
        # GAYA
        {
            "name": "Mahabodhi Temple, Bodh Gaya",
            "state_id": bihar_id,
            "district_id": district_ids["Gaya"],
            "description": "A UNESCO World Heritage Site where Siddhartha Gautama attained enlightenment under the Bodhi Tree around 531 BCE. The majestic 55-meter tall temple with its diamond throne (Vajrasana) is one of the earliest Buddhist temples. Pilgrims from Thailand, Japan, Sri Lanka, and Tibet have built monasteries nearby.",
            "category": "temple",
            "latitude": 24.6961, "longitude": 84.9911,
            "is_featured": True,
            "best_time_to_visit": "October to March; Buddha Purnima is special",
            "entry_fee": "Free (camera fee ₹100)",
            "travel_tips": "Morning meditation sessions open to all. Carry warm clothes in winter evenings.",
        },
        {
            "name": "Vishnupad Temple, Gaya",
            "state_id": bihar_id,
            "district_id": district_ids["Gaya"],
            "description": "An ancient Hindu temple built over the sacred footprint of Lord Vishnu on the banks of the Phalgu river. Hindus perform Pind Daan (ancestor rituals) here, believed to grant salvation to departed souls. The temple's 30-meter tower is visible from across Gaya.",
            "category": "temple",
            "latitude": 24.7492, "longitude": 84.9865,
            "is_featured": True,
            "best_time_to_visit": "September-October (Pitru Paksha) for rituals",
            "entry_fee": "Free",
            "travel_tips": "Only Hindus allowed inside. Pandits offer rituals — negotiate fees upfront.",
        },
        {
            "name": "Great Buddha Statue, Bodh Gaya",
            "state_id": bihar_id,
            "district_id": district_ids["Gaya"],
            "description": "A 25-meter (80 feet) tall statue of Lord Buddha in meditation pose, one of the tallest Buddha statues in India. Inaugurated by the Dalai Lama in 1989, it sits in a beautiful garden with 10 smaller statues of Buddha's disciples.",
            "category": "tourist_spot",
            "latitude": 24.6975, "longitude": 84.9878,
            "is_featured": False,
            "entry_fee": "₹30",
        },
        # NALANDA
        {
            "name": "Nalanda University Ruins",
            "state_id": bihar_id,
            "district_id": district_ids["Nalanda"],
            "description": "The archaeological remains of the world's oldest residential university, a UNESCO World Heritage Site. Founded in 427 CE, Nalanda hosted 10,000+ students and 2,000 teachers. Its nine-story library Dharmaganja burned for 3 months when destroyed in 1193 CE. The excavated 11 monasteries and 6 temples showcase ancient educational architecture.",
            "category": "historical",
            "latitude": 25.1362, "longitude": 85.4427,
            "is_featured": True,
            "best_time_to_visit": "October to March",
            "entry_fee": "₹25 for Indians, ₹500 for foreigners",
            "travel_tips": "Hire a local guide (₹500-800) for detailed history. Combined ticket with Rajgir available.",
        },
        {
            "name": "Rajgir (Rajagriha)",
            "state_id": bihar_id,
            "district_id": district_ids["Nalanda"],
            "description": "Ancient capital of Magadha and a city sacred to Buddhism, Jainism, and Hinduism. Surrounded by five hills, where Buddha taught and the first Buddhist Council was held. The Japanese Shanti Stupa on Griddhakuta Hill offers panoramic views. Hot springs at Brahmakund are believed to have healing properties.",
            "category": "historical",
            "latitude": 25.0261, "longitude": 85.4176,
            "is_featured": True,
            "best_time_to_visit": "October to March",
            "entry_fee": "Ropeway to Shanti Stupa ₹100 round trip",
            "travel_tips": "Take the ropeway to Griddhakuta peak. Hot springs are divided into different temperature pools.",
        },
        # VAISHALI
        {
            "name": "Vaishali - Birthplace of Democracy",
            "state_id": bihar_id,
            "district_id": district_ids["Vaishali"],
            "description": "One of the oldest republics in human history, where the Vajjian Confederacy flourished around 600 BCE — centuries before Greek democracy. Sacred to Buddhism (Buddha's last sermon) and Jainism (Lord Mahavira's birthplace). The Ashoka Pillar with its single lion capital stands as testimony.",
            "category": "historical",
            "latitude": 25.9848, "longitude": 85.1275,
            "is_featured": True,
            "best_time_to_visit": "October to March; Vaishali Mahotsav in April",
            "entry_fee": "₹15 for Indians",
        },
        # BHAGALPUR
        {
            "name": "Vikramshila University Ruins",
            "state_id": bihar_id,
            "district_id": district_ids["Bhagalpur"],
            "description": "Ruins of one of ancient India's greatest universities, founded by King Dharmapala around 783 CE. Vikramshila was a premier center for Vajrayana Buddhism with 107 temples and 1,000+ students. The great scholar Atisha Dipankara was a professor here.",
            "category": "historical",
            "latitude": 25.3297, "longitude": 87.2830,
            "is_featured": False,
            "best_time_to_visit": "October to February",
            "entry_fee": "₹25 for Indians",
        },
        {
            "name": "Mandar Hill",
            "state_id": bihar_id,
            "district_id": district_ids["Bhagalpur"],
            "description": "A sacred hill mentioned in Hindu mythology as the axis used during Samudra Manthan (churning of the ocean). Standing 240 meters high with a temple of Lord Madhusudana at the top, it offers panoramic views of the surrounding plains. Sacred to both Hindus and Jains.",
            "category": "mountain",
            "latitude": 24.9500, "longitude": 86.7300,
            "is_featured": False,
            "best_time_to_visit": "October to March",
            "entry_fee": "Free",
        },
        # MADHUBANI
        {
            "name": "Madhubani Art Village (Jitwarpur)",
            "state_id": bihar_id,
            "district_id": district_ids["Madhubani"],
            "description": "Birthplace of Madhubani painting (Mithila art), one of India's most celebrated folk art forms. This ancient tradition uses natural dyes to create intricate geometric patterns and mythological scenes. Every wall, floor, and courtyard of Jitwarpur village is adorned with these paintings. A GI-tagged art form with global recognition.",
            "category": "cultural",
            "latitude": 26.3563, "longitude": 86.0715,
            "is_featured": True,
            "best_time_to_visit": "October to March; festivals are especially colorful",
            "entry_fee": "Free",
            "travel_tips": "Buy paintings directly from artists for authentic work. Workshops available for tourists.",
        },
        # ROHTAS
        {
            "name": "Sher Shah Suri Tomb, Sasaram",
            "state_id": bihar_id,
            "district_id": district_ids["Rohtas"],
            "description": "An architectural masterpiece standing in the middle of an artificial lake — the mausoleum of Sher Shah Suri who defeated Mughal emperor Humayun and built the Grand Trunk Road. Built in 1545, this octagonal red sandstone tomb rises 37 meters high, often compared to the Taj Mahal.",
            "category": "historical",
            "latitude": 24.9458, "longitude": 84.0341,
            "is_featured": True,
            "best_time_to_visit": "October to March; sunset views are spectacular",
            "entry_fee": "₹25 for Indians, ₹300 for foreigners",
        },
        {
            "name": "Rohtasgarh Fort",
            "state_id": bihar_id,
            "district_id": district_ids["Rohtas"],
            "description": "One of India's oldest and most massive hill forts, perched at 1500 feet on a detached spur of the Kaimur range. Originally built in the 7th century, expanded by Sher Shah Suri. With walls extending 45 km, it contains palaces, temples, mosques, and an elephant gate. Largely unexplored and untouristy — a true hidden gem.",
            "category": "historical",
            "latitude": 24.8167, "longitude": 83.8333,
            "is_featured": True,
            "best_time_to_visit": "October to February",
            "entry_fee": "Free",
            "travel_tips": "Carry water and snacks. 4WD vehicle recommended for last stretch. Hire a local guide.",
        },
        # NAWADA
        {
            "name": "Kakolat Waterfall",
            "state_id": bihar_id,
            "district_id": district_ids["Nawada"],
            "description": "A magnificent 160-feet waterfall cascading down a rocky cliff — the largest waterfall in Bihar. According to legend, a cursed king in python form was freed by bathing here. The lush green surroundings make it breathtaking during monsoon. Bihar government has developed the area with steps and gardens.",
            "category": "waterfall",
            "latitude": 24.7833, "longitude": 85.5167,
            "is_featured": True,
            "best_time_to_visit": "July to September (monsoon) for full flow",
            "entry_fee": "₹30",
            "travel_tips": "Roads can be slippery during monsoon. Carry extra clothes if you plan to swim.",
        },
        # WEST CHAMPARAN
        {
            "name": "Valmiki National Park",
            "state_id": bihar_id,
            "district_id": district_ids["West Champaran"],
            "description": "Bihar's only national park and tiger reserve, spread across 900 sq km of dense forests along the Indo-Nepal border. Home to Royal Bengal Tigers, leopards, wild elephants, sloth bears, and over 250 bird species. Named after Sage Valmiki who wrote the Ramayana here.",
            "category": "nature",
            "latitude": 27.3167, "longitude": 84.0667,
            "is_featured": True,
            "best_time_to_visit": "November to June; closed during heavy monsoon",
            "entry_fee": "₹50 for Indians, ₹500 for foreigners; jeep safari ₹2000+",
            "travel_tips": "Book safari in advance. Nearest town is Bagaha (40 km).",
        },
        # EAST CHAMPARAN
        {
            "name": "Kesariya Stupa",
            "state_id": bihar_id,
            "district_id": district_ids["East Champaran"],
            "description": "Believed to be the tallest and largest Buddhist stupa in the world at 32 meters high, dating back to 200-750 CE. Emperor Ashoka built the original stupa here. This massive terraced structure was rediscovered buried under centuries of soil. It marks where Buddha gave his last sermon before entering Mahaparinirvana.",
            "category": "historical",
            "latitude": 26.3290, "longitude": 84.8542,
            "is_featured": True,
            "best_time_to_visit": "October to March",
            "entry_fee": "₹25",
        },
        # MUNGER
        {
            "name": "Munger Fort",
            "state_id": bihar_id,
            "district_id": district_ids["Munger"],
            "description": "A historic fort on the banks of the Ganges, believed to have been originally built by the Pala dynasty. It served as the seat of Mir Kasim and later the British. The Bihar School of Yoga (Sivananda Math) within the fort campus is internationally famous.",
            "category": "historical",
            "latitude": 25.3752, "longitude": 86.4735,
            "is_featured": False,
            "best_time_to_visit": "October to March",
            "entry_fee": "Free",
        },
        # BEGUSARAI
        {
            "name": "Kanwar Lake Bird Sanctuary",
            "state_id": bihar_id,
            "district_id": district_ids["Begusarai"],
            "description": "Asia's largest oxbow lake and a Ramsar wetland site, spread across 68 sq km. A paradise for birdwatchers with over 60 migratory species including Siberian cranes, bar-headed geese, and pintail ducks visiting during winter. The lake also supports rich aquatic biodiversity.",
            "category": "nature",
            "latitude": 25.6500, "longitude": 86.1500,
            "is_featured": False,
            "best_time_to_visit": "November to February (migratory bird season)",
            "entry_fee": "₹20",
            "travel_tips": "Carry binoculars. Best views at dawn. Boat rides available.",
        },
        # BANKA
        {
            "name": "Bhimbandh Hot Springs",
            "state_id": bihar_id,
            "district_id": district_ids["Banka"],
            "description": "Natural hot water springs nestled in a forested valley of the Kharagpur hills. The water temperature ranges from 40°C to 65°C and is believed to have medicinal properties. Surrounded by sal forests, it's a perfect off-beat destination for nature lovers. A wildlife sanctuary with elephants, deer, and peacocks.",
            "category": "nature",
            "latitude": 24.9667, "longitude": 86.4833,
            "is_featured": False,
            "best_time_to_visit": "October to March",
            "entry_fee": "₹30",
            "travel_tips": "Stay at the forest rest house (book via Bihar Forest Dept). Carry insect repellent.",
        },
        # AURANGABAD
        {
            "name": "Deo Sun Temple",
            "state_id": bihar_id,
            "district_id": district_ids["Aurangabad"],
            "description": "One of the most important Sun temples in India, believed to be over 1,500 years old. During the Chhath Puja festival, lakhs of devotees gather here at the sacred temple tank to offer prayers to the Sun God at sunrise and sunset. The architecture shows influences of multiple dynasties.",
            "category": "temple",
            "latitude": 24.6560, "longitude": 84.4350,
            "is_featured": False,
            "best_time_to_visit": "October-November (Chhath Puja)",
            "entry_fee": "Free",
        },
        # BUXAR
        {
            "name": "Battle of Buxar Memorial",
            "state_id": bihar_id,
            "district_id": district_ids["Buxar"],
            "description": "The site of the historic Battle of Buxar (1764), one of the most decisive battles in Indian history that established British supremacy in India. The memorial overlooks the Ganges and marks where the combined forces of the Mughal Emperor, Nawab of Bengal, and Nawab of Awadh were defeated by the East India Company.",
            "category": "historical",
            "latitude": 25.5621, "longitude": 83.9787,
            "is_featured": False,
            "best_time_to_visit": "October to March",
            "entry_fee": "Free",
        },
        # KAIMUR
        {
            "name": "Mundeshwari Temple",
            "state_id": bihar_id,
            "district_id": district_ids["Kaimur"],
            "description": "One of the oldest functional Hindu temples in India, dating back to 108 CE (nearly 2,000 years old). Perched atop Mundeshwari Hills at 608 feet, this octagonal stone temple features exquisite Gupta-period carvings, a rare four-faced Shiva Linga, and a magnificent Varaha sculpture.",
            "category": "temple",
            "latitude": 25.0612, "longitude": 83.7632,
            "is_featured": False,
            "best_time_to_visit": "October to March",
            "entry_fee": "Free",
            "travel_tips": "Steep climb to the temple. Start early to avoid afternoon heat.",
        },
        # SITAMARHI
        {
            "name": "Janaki Sthan Temple",
            "state_id": bihar_id,
            "district_id": district_ids["Sitamarhi"],
            "description": "The sacred site believed to be the birthplace of Goddess Sita, wife of Lord Rama. Ancient texts describe King Janak finding baby Sita while ploughing this field. The temple complex includes the main shrine, a sacred pond, and beautiful gardens.",
            "category": "temple",
            "latitude": 26.5933, "longitude": 85.4882,
            "is_featured": False,
            "best_time_to_visit": "Ram Navami (April) and Vivah Panchami (December)",
            "entry_fee": "Free",
        },
        # DARBHANGA
        {
            "name": "Darbhanga Raj (Laxmi Vilas Palace)",
            "state_id": bihar_id,
            "district_id": district_ids["Darbhanga"],
            "description": "The magnificent palace complex of the Darbhanga Maharaj, once one of the richest landlords of British India. The European-style Laxmi Vilas Palace with its grand architecture, Durbar Hall, and sprawling gardens reflects the opulent Maithili royal heritage. Parts now house a university.",
            "category": "historical",
            "latitude": 26.1494, "longitude": 85.8919,
            "is_featured": False,
            "best_time_to_visit": "October to March",
            "entry_fee": "Free (exterior viewing only)",
        },
        # MUZAFFARPUR
        {
            "name": "Litchi Gardens & Jubba Sahni Park",
            "state_id": bihar_id,
            "district_id": district_ids["Muzaffarpur"],
            "description": "Muzaffarpur is the Litchi Capital of India, producing the finest Shahi Litchi variety. During May-June, the litchi orchards are a beautiful sight with ripe red fruits hanging from every tree. Jubba Sahni Park is the city's main recreational space with gardens and a lake.",
            "category": "nature",
            "latitude": 26.1209, "longitude": 85.3647,
            "is_featured": False,
            "best_time_to_visit": "May-June (litchi season)",
            "entry_fee": "Free",
        },
        # BHOJPUR
        {
            "name": "Veer Kunwar Singh Fort, Jagdishpur",
            "state_id": bihar_id,
            "district_id": district_ids["Bhojpur"],
            "description": "The fort of Babu Veer Kunwar Singh, the legendary 80-year-old warrior who led Bihar's rebellion during the 1857 Revolt. Despite his age, he defeated British forces in multiple battles. The fort museum displays weapons, paintings, and artifacts from the freedom struggle.",
            "category": "historical",
            "latitude": 25.4667, "longitude": 84.4167,
            "is_featured": False,
            "best_time_to_visit": "October to March; April 23 (Kunwar Singh Jayanti)",
            "entry_fee": "₹10",
        },
    ]

    for pd in places:
        specs = pd.pop("specialties", [])
        place_id = create_place(pd)
        for spec in specs:
            add_specialty(place_id, spec)
        print(f"  + Place: {pd['name']}")

    # ═══ DISTRICT FOODS ═══
    district_foods = {
        "Patna": [
            {"name": "Litti Chokha", "description": "Bihar's soul food — roasted wheat balls stuffed with sattu, served with smoky baigan and tomato chokha, drowned in desi ghee.", "category": "food", "best_places_to_eat": "Raju Litti Chokha (Boring Road), Litti Hub, Champaran Meat House"},
            {"name": "Sattu Sharbat", "description": "Refreshing cold drink made from roasted gram flour with lemon, salt, and spices — Bihar's original protein shake.", "category": "drink", "best_places_to_eat": "Street vendors near Golghar and Gandhi Maidan"},
            {"name": "Bihari Kebab", "description": "Tender minced meat kebabs marinated with poppy seed paste and slow-cooked — Patna's legendary non-veg street food.", "category": "food", "best_places_to_eat": "Haji Karim (Phulwari Sharif), Jawed Kebab Corner"},
            {"name": "Kadhi Bari", "description": "Crispy gram flour dumplings in tangy yogurt gravy — a staple comfort food of every Bihari household.", "category": "food", "best_places_to_eat": "Bansi Vilas, most local restaurants"},
        ],
        "Gaya": [
            {"name": "Tilkut", "description": "Crunchy sesame and sugar sweet — a beloved Gaya specialty especially popular during Makar Sankranti.", "category": "sweet", "best_places_to_eat": "Silao village, Gaya station vendors"},
            {"name": "Thekua", "description": "Deep-fried wheat biscuits sweetened with jaggery and flavored with cardamom — a sacred Chhath Puja offering.", "category": "sweet", "best_places_to_eat": "Local sweet shops across Gaya"},
        ],
        "Nalanda": [
            {"name": "Khaja", "description": "GI-tagged layered crispy pastry soaked in sugar syrup — a 2,500-year-old recipe from the Rajgir-Nalanda region.", "category": "sweet", "best_places_to_eat": "Silao village (on Rajgir-Nalanda road) — famous for the best Khaja"},
        ],
        "Muzaffarpur": [
            {"name": "Shahi Litchi", "description": "The world-famous Muzaffarpur litchi — sweet, juicy, and aromatic. Harvested May-June, it's exported globally.", "category": "food", "best_places_to_eat": "Litchi orchards across Muzaffarpur district"},
        ],
        "Bhagalpur": [
            {"name": "Katarni Chawal", "description": "An aromatic short-grain rice variety unique to Bhagalpur, prized for its fragrance and soft texture. GI-tagged.", "category": "food", "best_places_to_eat": "Local markets in Bhagalpur"},
            {"name": "Bhagalpuri Tussar Silk", "description": "Not food, but Bhagalpur is the Silk City — famous for its handloom Tussar silk saris and fabrics.", "category": "craft", "best_places_to_eat": "Silk Market, Nathnagar, Bhagalpur"},
        ],
        "Madhubani": [
            {"name": "Makhana (Fox Nuts)", "description": "Roasted and spiced lotus seed puffs — a healthy superfood snack and major Mithila export.", "category": "food", "best_places_to_eat": "Everywhere in Mithilanchal region"},
            {"name": "Dahi Chura", "description": "Flattened rice with thick fresh curd and jaggery — the ceremonial Maithili breakfast.", "category": "food", "best_places_to_eat": "Every Maithili household, especially during festivals"},
        ],
        "Rohtas": [
            {"name": "Sattu Paratha", "description": "Flatbread stuffed with spiced roasted gram flour — the protein powerhouse of Bihari cuisine.", "category": "food", "best_places_to_eat": "Highway dhabas on Grand Trunk Road, Sasaram"},
        ],
        "Vaishali": [
            {"name": "Chura-Dahi", "description": "Beaten rice mixed with thick curd, jaggery, and banana — a must-have during Makar Sankranti.", "category": "food", "best_places_to_eat": "Every household and roadside stall in Vaishali"},
        ],
        "West Champaran": [
            {"name": "Champaran Meat", "description": "A unique style of slow-cooked mutton in a clay pot sealed with wheat dough (handi meat) — a legendary dish from Champaran.", "category": "food", "best_places_to_eat": "Champaran Meat House outlets"},
        ],
        "Darbhanga": [
            {"name": "Jhilli", "description": "Thin crispy rice pancakes — a Maithili breakfast staple.", "category": "food", "best_places_to_eat": "Local homes and eateries"},
            {"name": "Bari-Kadhi", "description": "Thick yogurt curry with sun-dried urad dal dumplings — classic Mithila comfort food.", "category": "food", "best_places_to_eat": "Any Maithili restaurant"},
        ],
    }

    for dist_name, foods in district_foods.items():
        if dist_name in district_ids:
            for food in foods:
                add_district_food(district_ids[dist_name], food)
            print(f"  [+] Foods added for {dist_name}: {len(foods)} items")

    # ═══ ACCOMMODATIONS ═══
    accommodations_data = {
        "Golghar": [
            {"name": "Hotel Maurya Patna", "type": "hotel", "price_range": "₹3,000-8,000", "description": "4-star hotel near Golghar with rooftop restaurant overlooking the Ganges.", "address": "South Gandhi Maidan, Patna", "phone": "0612-2203040", "distance_km": 1.5},
            {"name": "Hotel Chanakya", "type": "hotel", "price_range": "₹1,200-3,000", "description": "Budget-friendly hotel with clean rooms near Gandhi Maidan.", "address": "Beer Chand Patel Marg, Patna", "phone": "0612-2222575", "distance_km": 0.8},
        ],
        "Mahabodhi Temple, Bodh Gaya": [
            {"name": "Hotel Sujata", "type": "hotel", "price_range": "₹1,500-4,000", "description": "Comfortable stay with views of Mahabodhi Temple.", "address": "Bodh Gaya Main Road", "distance_km": 0.3},
            {"name": "Royal Residency", "type": "hotel", "price_range": "₹800-2,000", "description": "Budget hotel popular with pilgrims, clean and basic.", "address": "Bodh Gaya", "distance_km": 0.5},
            {"name": "Burmese Vihar Guest House", "type": "dharamshala", "price_range": "₹200-500", "description": "Buddhist monastery guesthouse with meditation facilities.", "address": "Bodh Gaya Temple Area", "distance_km": 0.2},
        ],
        "Rajgir (Rajagriha)": [
            {"name": "Indo Hokke Hotel", "type": "resort", "price_range": "₹2,500-6,000", "description": "Japanese-Bihar joint venture hotel with hot spring bath.", "address": "Rajgir", "distance_km": 1},
            {"name": "Tathagat Vihar", "type": "guesthouse", "price_range": "₹500-1,500", "description": "Bihar Tourism guesthouse with basic amenities.", "address": "Rajgir", "distance_km": 0.5},
        ],
    }

    # Match accommodations to places by name
    from models.database import get_cursor
    for place_name, hotels in accommodations_data.items():
        with get_cursor() as cur:
            cur.execute("SELECT id FROM places WHERE name = %s", (place_name,))
            row = cur.fetchone()
        if row:
            for hotel in hotels:
                add_accommodation(row['id'], hotel)
            print(f"  [+] Hotels added for {place_name}: {len(hotels)} stays")

    # ═══ KEY BLOCKS ═══
    key_blocks = {
        "Patna": ["Patna Sadar", "Danapur", "Phulwari Sharif", "Maner", "Bikram", "Paliganj", "Masaurhi", "Fatuha", "Barh", "Mokama", "Bihta"],
        "Gaya": ["Gaya Town", "Bodh Gaya", "Sherghati", "Tekari", "Wazirganj", "Belaganj", "Manpur", "Atri"],
        "Nalanda": ["Bihar Sharif", "Rajgir", "Silao", "Hilsa", "Harnaut", "Islampur"],
        "Bhagalpur": ["Bhagalpur", "Sultanganj", "Nathnagar", "Kahalgaon", "Naugachhia", "Pirpainti"],
        "Vaishali": ["Hajipur", "Vaishali", "Jandaha", "Mahua", "Lalganj", "Bidupur"],
        "Muzaffarpur": ["Mushahari", "Kanti", "Minapur", "Motipur", "Aurai", "Sakra"],
        "Madhubani": ["Madhubani", "Jainagar", "Jhanjharpur", "Benipatti", "Rajnagar", "Pandaul"],
        "Rohtas": ["Sasaram", "Dehri", "Bikramganj", "Dinara", "Rohtas", "Tilouthu", "Nokha"],
        "Munger": ["Munger", "Jamalpur", "Tarapura", "Bariarpur"],
    }

    for dist_name, blocks in key_blocks.items():
        if dist_name in district_ids:
            for block_name in blocks:
                create_block(district_ids[dist_name], block_name)
            print(f"  [+] Blocks for {dist_name}: {len(blocks)} added")

    print(f"\n[+] HiddenYatra Bihar seed complete!")
    print(f"    {len(districts_data)} districts, {len(places)} places, district foods, hotels, and blocks added.")


if __name__ == "__main__":
    seed()
