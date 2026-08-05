const CITIES_DATA = [
  {
    id: "delhi",
    name: "Delhi",
    country: "India",
    emoji: "🇮🇳",
    tagline: "A Symphony of History and Modernity",
    description: "India's capital territory is a massive metropolitan area in the country's north. In Old Delhi, a neighborhood dating to the 1600s, stands the imposing Mughal-era Red Fort, a symbol of India, and the sprawling Jama Masjid mosque.",
    image: "https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=800&q=80",
    quickFacts: {
      population: "33 million (Metro)",
      language: "Hindi, English, Punjabi",
      currency: "Indian Rupee (₹)",
      bestTime: "October to March",
      timezone: "IST (UTC+5:30)"
    },
    landmarks: [
      { name: "Qutub Minar", description: "A 73-meter tall minaret built by Qutb-ud-din Aibak in 1193, representing the triumph of Indo-Islamic architecture and a UNESCO World Heritage Site.", category: "Historical", mustVisit: true },
      { name: "India Gate", description: "A war memorial dedicated to the soldiers of the British Indian Army who died in the First World War, surrounded by lush green lawns.", category: "Memorial", mustVisit: true },
      { name: "Lotus Temple", description: "A Bahá'í House of Worship notable for its flowerlike shape made of white marble, open to all regardless of religion.", category: "Spiritual", mustVisit: false },
      { name: "Red Fort", description: "A historic fort built by Shah Jahan in the 17th century, serving as the main residence of the Mughal Emperors for nearly 200 years.", category: "Historical", mustVisit: true },
      { name: "Humayun's Tomb", description: "The tomb of the Mughal Emperor Humayun, a masterpiece of Mughal architecture and a precursor to the Taj Mahal.", category: "Historical", mustVisit: true }
    ],
    delicacies: [
      { name: "Butter Chicken", description: "Tender chicken cooked in a rich, creamy, spiced tomato sauce. Originating at Moti Mahal restaurant in Delhi during the 1950s.", category: "Main Course", priceRange: "₹₹" },
      { name: "Chole Bhature", description: "A combination of spicy chickpeas (chole) and fried bread (bhatura), a staple street food across Delhi's bustling markets.", category: "Street Food", priceRange: "₹" },
      { name: "Paranthas of Gali Paranthe Wali", description: "Deep-fried flatbreads stuffed with various unique fillings like potatoes, paneer, and even bananas, served at the famous lane in Chandni Chowk.", category: "Local Fast Food", priceRange: "₹" },
      { name: "Daulat Ki Chaat", description: "A sweet, frothy milk dessert prepared only during winter nights by collecting dew and served fresh in the morning with saffron.", category: "Dessert", priceRange: "₹" },
      { name: "Nihari", description: "A slow-cooked stew of meat braised overnight with spices, traditionally eaten as a hearty breakfast in Old Delhi.", category: "Traditional", priceRange: "₹₹" }
    ],
    attractions: [
      { name: "Chandni Chowk Market", description: "One of the oldest and busiest markets in Old Delhi, full of spices, silver jewelry, and mouthwatering street food stalls.", category: "Shopping", duration: "3-4 hours" },
      { name: "National Gallery of Modern Art", description: "The premier art gallery showcasing modern and contemporary Indian art spanning over 160 years, housed in a beautiful colonial palace.", category: "Museum", duration: "2 hours" },
      { name: "Lodhi Gardens", description: "A city park containing the tombs of Sayyid and Lodi rulers, popular for morning walks, yoga sessions, and peaceful picnics.", category: "Nature", duration: "1-2 hours" },
      { name: "Dilli Haat", description: "An open-air food plaza and craft bazaar where artisans from all over India showcase their handloom and handicraft products.", category: "Cultural Market", duration: "2-3 hours" }
    ]
  },
  {
    id: "jaipur",
    name: "Jaipur",
    country: "India",
    emoji: "🇮🇳",
    tagline: "The Pink City of Royalty and Grandeur",
    description: "Jaipur is the capital of India's Rajasthan state. It evokes the royal family that once ruled the region and that, in 1727, founded what is now called the Old City, or 'Pink City' for its trademark building color.",
    image: "https://images.unsplash.com/photo-1477584305852-30c2f839b9a4?auto=format&fit=crop&w=800&q=80",
    quickFacts: {
      population: "3.1 million",
      language: "Rajasthani, Hindi, English",
      currency: "Indian Rupee (₹)",
      bestTime: "November to February",
      timezone: "IST (UTC+5:30)"
    },
    landmarks: [
      { name: "Hawa Mahal", description: "The 'Palace of Winds', a five-story pyramidal monument built with red and pink sandstone featuring 953 small intricately carved windows.", category: "Historical", mustVisit: true },
      { name: "Amer Fort", description: "A majestic fort located high on a hill, known for its artistic style elements, stunning mirror work, and breathtaking views of Maota Lake.", category: "Historical", mustVisit: true },
      { name: "City Palace", description: "A spectacular complex of courtyards, gardens, and buildings, featuring the Chandra Mahal and Mubarak Mahal, blending Rajput and Mughal architecture.", category: "Royal Palace", mustVisit: true },
      { name: "Jantar Mantar", description: "An astronomical observation site built by King Sawai Jai Singh II, featuring the world's largest stone sundial and UNESCO World Heritage status.", category: "Science / Historical", mustVisit: false },
      { name: "Nahargarh Fort", description: "Standing on the edge of the Aravalli Hills, this fort offers panoramic views of the entire Jaipur city, especially stunning at sunset.", category: "Scenic / Historical", mustVisit: true }
    ],
    delicacies: [
      { name: "Dal Baati Churma", description: "A Rajasthani classic comprising hard, unleavened bread (Baati) baked in a coal fire, spiced lentil curry (Dal), and sweet crumbled wheat (Churma).", category: "Traditional Meal", priceRange: "₹₹" },
      { name: "Pyaaz Kachori", description: "A fried pastry filled with a spicy onion mixture, popular as a breakfast item and tea-time snack, best savored at Rawat Mishthan Bhandar.", category: "Snacks", priceRange: "₹" },
      { name: "Gatte Ki Sabji", description: "Gram flour (besan) dumplings cooked in a rich, tangy yogurt-based gravy, a quintessential Rajasthani vegetarian delicacy.", category: "Main Course", priceRange: "₹₹" },
      { name: "Ghevar", description: "A disc-shaped sweet cake made from flour and soaked in sugar syrup, typically prepared during the Teej and Raksha Bandhan festivals.", category: "Dessert", priceRange: "₹" },
      { name: "Laal Maas", description: "A fiery hot mutton curry cooked with mathania chilies and traditional Rajput spices — not for the faint-hearted.", category: "Non-Veg Main", priceRange: "₹₹" }
    ],
    attractions: [
      { name: "Chokhi Dhani", description: "An ethnic village resort offering a realistic experience of Rajasthani culture, folk dances, puppet shows, camel rides, and authentic food.", category: "Cultural Experience", duration: "4-5 hours" },
      { name: "Johri Bazar", description: "A vibrant market famous for exquisite Kundan jewelry, gemstones, traditional tie-and-dye fabrics, and lac bangles.", category: "Shopping", duration: "2-3 hours" },
      { name: "Elefantastic Elephant Sanctuary", description: "An ethical sanctuary where you can feed, bathe, and walk with rescued elephants in their natural habitat.", category: "Wildlife / Ethical Tourism", duration: "3 hours" }
    ]
  },
  {
    id: "mumbai",
    name: "Mumbai",
    country: "India",
    emoji: "🇮🇳",
    tagline: "The City of Dreams That Never Sleeps",
    description: "Mumbai (formerly Bombay) is a densely populated city on India's west coast. A financial center, it's India's largest city. On the Mumbai Harbour waterfront stands the iconic Gateway of India stone arch.",
    image: "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&w=800&q=80",
    quickFacts: {
      population: "21 million",
      language: "Marathi, Hindi, English",
      currency: "Indian Rupee (₹)",
      bestTime: "October to March",
      timezone: "IST (UTC+5:30)"
    },
    landmarks: [
      { name: "Gateway of India", description: "An arch-monument built in the early 20th century to commemorate the landing of King-Emperor George V and Queen-Empress Mary, overlooking the Arabian Sea.", category: "Historical", mustVisit: true },
      { name: "Chhatrapati Shivaji Maharaj Terminus", description: "A historic terminal train station and UNESCO World Heritage Site showcasing outstanding Victorian Gothic Revival architecture with Indian influences.", category: "Architecture", mustVisit: true },
      { name: "Bandra-Worli Sea Link", description: "A cable-stayed bridge linking Bandra in the Western Suburbs with Worli in South Mumbai — a modern engineering marvel lit up spectacularly at night.", category: "Infrastructure", mustVisit: false },
      { name: "Taj Mahal Palace Hotel", description: "A luxurious heritage hotel standing next to the Gateway of India since 1903, renowned for its legendary hospitality and resilient history.", category: "Historical Hotel", mustVisit: true }
    ],
    delicacies: [
      { name: "Vada Pav", description: "The ultimate Mumbai street burger: a deep-fried spiced potato dumpling placed inside a sliced bread bun with fiery garlic and tamarind chutneys.", category: "Street Food", priceRange: "₹" },
      { name: "Pav Bhaji", description: "A thick spiced vegetable curry cooked in generous amounts of butter, served with soft bread rolls toasted on a flat griddle.", category: "Street Food", priceRange: "₹" },
      { name: "Bombil Fry (Bombay Duck)", description: "A crispy deep-fried coastal fish delicacy unique to Mumbai, coated in rice flour and spices, best enjoyed fresh from the sea.", category: "Seafood", priceRange: "₹₹" },
      { name: "Bhel Puri", description: "A savory snack made of puffed rice, sev, vegetables, and a tangy-sweet tamarind sauce, synonymous with Chowpatty Beach.", category: "Street Food", priceRange: "₹" }
    ],
    attractions: [
      { name: "Marine Drive Promenade", description: "A 3.6-kilometer-long arc-shaped boulevard along the coast, perfect for viewing sunsets and famously nicknamed the Queen's Necklace at night.", category: "Scenic View", duration: "1-2 hours" },
      { name: "Elephanta Caves", description: "A collection of cave temples predominantly dedicated to the Hindu god Shiva on Elephanta Island, reachable by a scenic ferry ride.", category: "Historical Heritage", duration: "4-5 hours" },
      { name: "Dharavi Slum Tour", description: "An insightful guided tour through Asia's largest slum, showcasing its incredible micro-economy, industries, and resilient community spirit.", category: "Cultural Tour", duration: "2-3 hours" },
      { name: "Colaba Causeway", description: "A bustling commercial street filled with cafes, boutiques, bookshops, and street vendors selling everything from clothing to antiques.", category: "Shopping", duration: "2-3 hours" }
    ]
  },
  {
    id: "varanasi",
    name: "Varanasi",
    country: "India",
    emoji: "🇮🇳",
    tagline: "The Spiritual Heart of India",
    description: "Varanasi is a city in the northern Indian state of Uttar Pradesh dating to the 11th century B.C. Regarded as the spiritual capital of India, it draws Hindu pilgrims who bathe in the Ganges River's sacred waters.",
    image: "https://images.unsplash.com/photo-1561361513-2d000a50f0db?auto=format&fit=crop&w=800&q=80",
    quickFacts: {
      population: "1.2 million",
      language: "Bhojpuri, Hindi, English",
      currency: "Indian Rupee (₹)",
      bestTime: "November to February",
      timezone: "IST (UTC+5:30)"
    },
    landmarks: [
      { name: "Kashi Vishwanath Temple", description: "One of the most famous Hindu temples dedicated to Lord Shiva, located on the western bank of the holy river Ganges in the Vishwanath Gali.", category: "Religious", mustVisit: true },
      { name: "Dashashwamedh Ghat", description: "The main and most spectacular ghat in Varanasi, located close to Vishwanath Temple, famous for its mesmerizing evening Ganga Aarti.", category: "Religious / Historical", mustVisit: true },
      { name: "Sarnath", description: "Located 10km from Varanasi, this is the deer park where Gautama Buddha first taught the Dharma after attaining enlightenment.", category: "Buddhist Heritage", mustVisit: true },
      { name: "Ramnagar Fort", description: "An 18th-century fort and palace on the eastern bank of the Ganges, home to a fascinating museum of vintage cars, weapons, and royal artifacts.", category: "Historical", mustVisit: false }
    ],
    delicacies: [
      { name: "Tamatar Chaat", description: "A spicy street snack unique to Varanasi, made with mashed tomatoes, potatoes, tangy spices, and topped with surprising sweet syrup.", category: "Street Food", priceRange: "₹" },
      { name: "Banarasi Paan", description: "A betel leaf preparation containing areca nut, tobacco, or sweet fillings, famous worldwide for its elaborate preparation and ritual.", category: "Local Speciality", priceRange: "₹" },
      { name: "Kachori Sabzi", description: "Spicy fried pastries filled with lentils, served with a hot potato curry — a beloved traditional Varanasi breakfast.", category: "Breakfast", priceRange: "₹" },
      { name: "Malaiyo", description: "A seasonal milk dessert available only in winter, flavored with saffron and cardamom, garnished with pistachios and silver leaf.", category: "Dessert", priceRange: "₹" }
    ],
    attractions: [
      { name: "Ganga Aarti Ceremony", description: "A breathtaking evening devotional ritual at Dashashwamedh Ghat where priests wave brass lamps in synchronized movements to sacred chants.", category: "Cultural Event", duration: "1.5 hours" },
      { name: "Sunrise Boat Ride on the Ganges", description: "A serene rowboat tour along the ghats at dawn, offering unmatched views of morning prayers, cremation rituals, and the rising sun.", category: "Scenic Experience", duration: "1-2 hours" },
      { name: "Silk Weaving Workshops", description: "Visit artisan workshops to see how the world-famous Banarasi silk sarees are handwoven with intricate gold and silver zari work.", category: "Cultural / Craft", duration: "2 hours" }
    ]
  },
  {
    id: "goa",
    name: "Goa",
    country: "India",
    emoji: "🇮🇳",
    tagline: "The Sun-Kissed Paradise of Beaches and Culture",
    description: "Goa is a state in western India with coastlines stretching along the Arabian Sea. Its long history as a Portuguese colony prior to 1961 is evident in its preserved 17th-century churches and tropical spice plantations.",
    image: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80",
    quickFacts: {
      population: "1.5 million",
      language: "Konkani, Marathi, English",
      currency: "Indian Rupee (₹)",
      bestTime: "November to February",
      timezone: "IST (UTC+5:30)"
    },
    landmarks: [
      { name: "Basilica of Bom Jesus", description: "A UNESCO World Heritage Site holding the mortal remains of St. Francis Xavier, a landmark of Baroque Portuguese colonial architecture.", category: "Religious / Historical", mustVisit: true },
      { name: "Fort Aguada", description: "A well-preserved seventeenth-century Portuguese fort and lighthouse standing on Sinquerim Beach, offering panoramic sea views.", category: "Historical Fort", mustVisit: true },
      { name: "Dudhsagar Falls", description: "A four-tiered waterfall on the Mandovi River, cascading from 310 meters and looking like a flowing sea of milk from a distance.", category: "Nature", mustVisit: true },
      { name: "Chapora Fort", description: "Popularized by Bollywood's 'Dil Chahta Hai', this fort offers breathtaking panoramic views of Vagator Beach and the Arabian Sea.", category: "Scenic Ruins", mustVisit: false }
    ],
    delicacies: [
      { name: "Goan Fish Curry Rice", description: "Fresh kingfish or pomfret cooked in a tangy coconut and kokum gravy, served with steaming white rice — Goa's soul food.", category: "Main Course", priceRange: "₹₹" },
      { name: "Pork Vindaloo", description: "A fiery Goan curry with Portuguese roots, prepared with palm vinegar, garlic, ginger, and dry red Kashmiri chilies.", category: "Main Course", priceRange: "₹₹" },
      { name: "Bebinca", description: "A traditional seven-layered Goan dessert made of flour, egg yolk, coconut milk, and ghee, requiring hours of patient baking.", category: "Dessert", priceRange: "₹" },
      { name: "Feni", description: "A unique local spirit distilled from either cashew apples or coconut sap, holding a GI tag exclusive to Goa.", category: "Drinks", priceRange: "₹" }
    ],
    attractions: [
      { name: "Anjuna Flea Market", description: "A lively weekly market near the beach selling bohemian clothing, handmade crafts, spices, and musical instruments.", category: "Shopping", duration: "2-3 hours" },
      { name: "Grand Island Scuba Diving", description: "Explore vibrant coral reefs and shipwrecks teeming with tropical fish through thrilling underwater diving expeditions.", category: "Adventure", duration: "4-5 hours" },
      { name: "Fontainhas Latin Quarter", description: "An old Latin quarter in Panaji, filled with colorful Portuguese houses, narrow streets, heritage galleries, and artisan bakeries.", category: "Heritage Walk", duration: "2 hours" }
    ]
  },
  {
    id: "kerala",
    name: "Kerala",
    country: "India",
    emoji: "🇮🇳",
    tagline: "God's Own Country of Serene Backwaters",
    description: "Kerala is a state on India's tropical Malabar Coast. It's famous for its palm-lined beaches, backwaters network of canals, and the Western Ghats mountains supporting tea, coffee, and spice plantations.",
    image: "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=800&q=80",
    quickFacts: {
      population: "35 million",
      language: "Malayalam, English",
      currency: "Indian Rupee (₹)",
      bestTime: "September to March",
      timezone: "IST (UTC+5:30)"
    },
    landmarks: [
      { name: "Alleppey Backwaters", description: "A network of interconnected canals, rivers, lakes, and inlets — often called the 'Venice of the East' — best explored on traditional houseboats.", category: "Natural Wonder", mustVisit: true },
      { name: "Chinese Fishing Nets", description: "Vast cantilevered fishing nets in Fort Kochi, land-based and operated since the 14th century by settlers from the court of Kublai Khan.", category: "Historical Monument", mustVisit: true },
      { name: "Sree Padmanabhaswamy Temple", description: "An ancient golden Hindu temple in Thiruvananthapuram, famous for its Dravidian architecture and immensely valuable hidden treasure vaults.", category: "Religious", mustVisit: false },
      { name: "Munnar Tea Gardens", description: "Breathtakingly beautiful green carpet-like valleys of tea estates cascading over the Western Ghats at 1,600m elevation.", category: "Nature Reserve", mustVisit: true }
    ],
    delicacies: [
      { name: "Kerala Sadya", description: "A grand vegetarian feast served on a banana leaf, consisting of 24-28 traditional dishes arranged in a specific order, served during Onam.", category: "Traditional Feast", priceRange: "₹₹" },
      { name: "Karimeen Pollichathu", description: "Pearl spot fish marinated in a fiery red spice paste, wrapped in banana leaf, and slow-baked to absorb all the smoky flavors.", category: "Main Course", priceRange: "₹₹" },
      { name: "Appam with Stew", description: "Soft, lacy fermented rice pancakes with crispy edges, served alongside a fragrant coconut-milk-based vegetable or chicken stew.", category: "Breakfast", priceRange: "₹" },
      { name: "Banana Chips", description: "Thin, crispy slices of raw plantain deep-fried in pure coconut oil and lightly salted — Kerala's most beloved snack export.", category: "Snacks", priceRange: "₹" }
    ],
    attractions: [
      { name: "Alleppey Houseboat Cruise", description: "A leisurely overnight cruise through palm-fringed canals and lagoons on an authentic kettuvallam (thatched houseboat).", category: "Leisure Experience", duration: "Full Day" },
      { name: "Kathakali Dance Performance", description: "A centuries-old classical dance-drama featuring elaborate colorful makeup, ornate costumes, and dramatic facial expressions.", category: "Cultural Art", duration: "2 hours" },
      { name: "Periyar Tiger Reserve", description: "A protected area in the Western Ghats where you can spot wild elephants, bison, and tigers on a guided bamboo rafting safari.", category: "Wildlife Safari", duration: "4-5 hours" }
    ]
  },
  {
    id: "paris",
    name: "Paris",
    country: "France",
    emoji: "🇫🇷",
    tagline: "The Romantic Capital of Art and Fashion",
    description: "Paris, France's capital, is a major European city and a global center for art, fashion, gastronomy, and culture. Its 19th-century cityscape is crisscrossed by wide boulevards and the River Seine.",
    image: "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=800&q=80",
    quickFacts: {
      population: "2.1 million",
      language: "French",
      currency: "Euro (€)",
      bestTime: "June – August / September – October",
      timezone: "CET (UTC+1)"
    },
    landmarks: [
      { name: "Eiffel Tower", description: "A wrought-iron lattice tower on the Champ de Mars, constructed for the 1889 World's Fair and now the undisputed global icon of France.", category: "Monument", mustVisit: true },
      { name: "Arc de Triomphe", description: "One of the most famous monuments in Paris, standing grandly at the western end of the Champs-Élysées honoring those who fought for France.", category: "Monument", mustVisit: true },
      { name: "Notre-Dame Cathedral", description: "A medieval Catholic cathedral on the Île de la Cité, a masterpiece of French Gothic architecture, currently undergoing historic restoration.", category: "Religious / Gothic", mustVisit: true },
      { name: "Sacré-Cœur Basilica", description: "A gleaming white Roman Catholic church perched at the summit of Montmartre, offering the best panoramic views of Paris.", category: "Religious / Scenic", mustVisit: false }
    ],
    delicacies: [
      { name: "Croissant", description: "A buttery, flaky, viennoiserie pastry named for its crescent shape, baked to a perfect golden crispness and best enjoyed warm.", category: "Pastry", priceRange: "€" },
      { name: "Escargots de Bourgogne", description: "Snails cooked in their shells with a heavenly compound butter of garlic, shallots, and fresh parsley — a quintessential French experience.", category: "Appetizer", priceRange: "€€€" },
      { name: "Macarons", description: "Sweet meringue-based confections made with egg white, icing sugar, and almond meal — a burst of color and delicate flavor.", category: "Dessert", priceRange: "€€" },
      { name: "Coq au Vin", description: "A hearty French dish of chicken braised slowly with red Burgundy wine, lardons, mushrooms, and garlic until meltingly tender.", category: "Main Course", priceRange: "€€€" }
    ],
    attractions: [
      { name: "Louvre Museum", description: "The world's largest art museum and home to Leonardo da Vinci's Mona Lisa, the Winged Victory, and Venus de Milo, housed in a former royal palace.", category: "Museum", duration: "3-4 hours" },
      { name: "Seine River Cruise", description: "A glass-topped boat tour along the Seine River at twilight, gliding past Paris's famous illuminated monuments bathed in golden light.", category: "Scenic Tour", duration: "1 hour" },
      { name: "Montmartre & Sacré-Cœur Walk", description: "A charming hill district walk through cobblestone streets, past artist easels, cabarets, and cozy cafés to the gleaming basilica.", category: "Walking Tour", duration: "2-3 hours" }
    ]
  },
  {
    id: "rome",
    name: "Rome",
    country: "Italy",
    emoji: "🇮🇹",
    tagline: "The Eternal City of Ancient Emperors",
    description: "Rome is the capital city of Italy and a sprawling, cosmopolitan city with nearly 3,000 years of globally influential art, architecture, and culture on display. Ancient ruins such as the Forum and the Colosseum evoke the power of the former Roman Empire.",
    image: "https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=800&q=80",
    quickFacts: {
      population: "2.8 million",
      language: "Italian",
      currency: "Euro (€)",
      bestTime: "April – June / September – October",
      timezone: "CET (UTC+1)"
    },
    landmarks: [
      { name: "Colosseum", description: "An oval amphitheatre in the heart of Rome, the largest ancient amphitheatre ever built, once hosting gladiatorial combats for 80,000 spectators.", category: "Historical", mustVisit: true },
      { name: "Trevi Fountain", description: "The largest Baroque fountain in the city, where the tradition of tossing coins over your shoulder ensures your return to the Eternal City.", category: "Artistic Monument", mustVisit: true },
      { name: "Pantheon", description: "A former Roman temple from 125 AD, now a Catholic church, famous for its magnificent unreinforced concrete dome with a central oculus open to the sky.", category: "Historical / Religious", mustVisit: true },
      { name: "Roman Forum", description: "A rectangular plaza surrounded by the ruins of several ancient government buildings — the political, religious, and social heart of the Roman Republic.", category: "Historical", mustVisit: false }
    ],
    delicacies: [
      { name: "Pasta Carbonara", description: "The authentic Roman version made only with guanciale, Pecorino Romano, egg yolks, and cracked black pepper — no cream ever.", category: "Main Course", priceRange: "€€" },
      { name: "Pizza al Taglio", description: "Rectangular Roman-style pizza baked in large trays, sold by weight with a thousand topping variations — the ultimate Roman street food.", category: "Fast Food", priceRange: "€" },
      { name: "Gelato", description: "Creamy Italian gelato churned daily with fresh milk and natural flavorings, denser and more intense than regular ice cream.", category: "Dessert", priceRange: "€" },
      { name: "Supplì", description: "Golden fried rice balls with a molten mozzarella heart that stretches when you pull them apart — nicknamed 'supplì al telefono'.", category: "Street Food", priceRange: "€" }
    ],
    attractions: [
      { name: "Vatican Museums & Sistine Chapel", description: "Walk through galleries of priceless art amassed over centuries before standing beneath Michelangelo's breathtaking ceiling fresco.", category: "Museum / Religious", duration: "3-4 hours" },
      { name: "St. Peter's Basilica", description: "The world's largest church, a Renaissance masterpiece designed by Bramante, Michelangelo, and Bernini, crowned with its iconic dome.", category: "Religious", duration: "2 hours" },
      { name: "Trastevere Night Walk", description: "A charming cobblestone neighborhood across the Tiber, famous for its bustling piazzas, lively trattorias, and authentic Roman nightlife.", category: "Nightlife Walk", duration: "2-3 hours" }
    ]
  },
  {
    id: "barcelona",
    name: "Barcelona",
    country: "Spain",
    emoji: "🇪🇸",
    tagline: "The Coastal Capital of Modernist Wonder",
    description: "Barcelona is a city on the coast of northeastern Spain. It is the capital and largest city of Catalonia, known for its art and architecture. The fantastical Sagrada Família and other modernist landmarks designed by Antoni Gaudí dot the city.",
    image: "https://images.unsplash.com/photo-1583422409516-291507467da5?auto=format&fit=crop&w=800&q=80",
    quickFacts: {
      population: "1.6 million",
      language: "Catalan, Spanish",
      currency: "Euro (€)",
      bestTime: "May – June / September – October",
      timezone: "CET (UTC+1)"
    },
    landmarks: [
      { name: "La Sagrada Família", description: "Gaudí's unfinished monumental basilica, a breathtaking fusion of Gothic and Art Nouveau forms under construction since 1882.", category: "Religious / Architecture", mustVisit: true },
      { name: "Park Güell", description: "A whimsical public park on Carmel Hill featuring colorful mosaic serpentine benches, organic stone structures, and city views.", category: "Architecture / Park", mustVisit: true },
      { name: "Casa Batlló", description: "A Gaudí-redesigned building with an undulating façade resembling skeletal bones and iridescent tiles evoking a dragon's spine.", category: "Architecture", mustVisit: false },
      { name: "Gothic Quarter (Barri Gòtic)", description: "The historic heart of the old city with narrow medieval streets, hidden plazas, Roman ruins, and trendy bars and boutiques.", category: "Historical Quarter", mustVisit: true }
    ],
    delicacies: [
      { name: "Paella Marinera", description: "A classic saffron rice dish loaded with fresh mussels, clams, shrimp, and squid, cooked in a wide shallow pan over open fire.", category: "Main Course", priceRange: "€€" },
      { name: "Patatas Bravas", description: "Crispy fried potato cubes served with a bold spicy tomato sauce and creamy garlic aioli — the essential tapas bar snack.", category: "Tapas", priceRange: "€" },
      { name: "Crema Catalana", description: "A rich custard dessert infused with cinnamon and lemon zest, topped with a shattering layer of caramelized sugar.", category: "Dessert", priceRange: "€" },
      { name: "Jamón Ibérico", description: "Cured ham from free-range black Iberian pigs fed on acorns, aged for years and sliced paper-thin to release its nutty aroma.", category: "Local Speciality", priceRange: "€€€" }
    ],
    attractions: [
      { name: "La Rambla Walkway", description: "A central tree-lined pedestrian boulevard stretching 1.2 km, alive with flower stalls, human statues, and outdoor cafés.", category: "Scenic Walk", duration: "1-2 hours" },
      { name: "Barceloneta Beach", description: "The city's beloved golden sand beach, perfect for swimming, surfing, or dining at chiringuito beach bars as the sun sets.", category: "Beach / Leisure", duration: "2-3 hours" },
      { name: "La Boqueria Market", description: "A world-famous covered market off La Rambla bursting with colorful fresh fruits, Iberian meats, seafood, fresh juices, and tapas.", category: "Food Market", duration: "1-2 hours" }
    ]
  },
  {
    id: "london",
    name: "London",
    country: "United Kingdom",
    emoji: "🇬🇧",
    tagline: "The Royal Cosmopolitan City of Traditions",
    description: "London is the capital and largest city of England and the United Kingdom. Standing on the River Thames, it has been a major settlement for two millennia and is a leading global city in arts, commerce, and education.",
    image: "https://images.unsplash.com/photo-1513635269975-59663e0ca1ad?auto=format&fit=crop&w=800&q=80",
    quickFacts: {
      population: "8.9 million",
      language: "English",
      currency: "Pound Sterling (£)",
      bestTime: "May to September",
      timezone: "GMT (UTC+0) / BST (UTC+1)"
    },
    landmarks: [
      { name: "Big Ben & Palace of Westminster", description: "The iconic Elizabeth Tower and its Great Bell, standing alongside the Houses of Parliament on the north bank of the Thames.", category: "Historical", mustVisit: true },
      { name: "Tower of London", description: "A historic castle founded in 1066 by William the Conqueror, home to the Crown Jewels and guarded by the Yeoman Warders (Beefeaters).", category: "Historical Castle", mustVisit: true },
      { name: "Tower Bridge", description: "A majestic combined bascule and suspension bridge from the Victorian era, with glass-floored walkways 42 meters above the river.", category: "Infrastructure", mustVisit: false },
      { name: "Buckingham Palace", description: "The London residence of the reigning monarch since 1837, famous for the Changing of the Guard ceremony held in its forecourt.", category: "Royal Palace", mustVisit: true }
    ],
    delicacies: [
      { name: "Fish and Chips", description: "Crispy battered cod or haddock with thick-cut golden chips, traditionally seasoned with salt and malt vinegar, wrapped in paper.", category: "Traditional", priceRange: "£" },
      { name: "Beef Wellington", description: "A tender fillet of beef coated with mushroom duxelles and pâté, wrapped in puff pastry and baked to flaky perfection.", category: "Main Course", priceRange: "£££" },
      { name: "Afternoon Tea", description: "An elegant light meal of finger sandwiches, warm scones with clotted cream and jam, and dainty pastries served with fine teas.", category: "Experience", priceRange: "££" },
      { name: "Sunday Roast", description: "A traditional British feast of roasted meat, crispy potatoes, Yorkshire pudding, seasonal vegetables, and rich onion gravy.", category: "Traditional Meal", priceRange: "£" }
    ],
    attractions: [
      { name: "The British Museum", description: "A world-renowned museum dedicated to human history, housing the Rosetta Stone, Elgin Marbles, Egyptian mummies — all free to enter.", category: "Museum", duration: "3-4 hours" },
      { name: "The London Eye", description: "Europe's tallest observation wheel on the South Bank, offering spectacular 360-degree views across 55 of London's landmarks.", category: "Scenic View", duration: "1 hour" },
      { name: "West End Theatre", description: "London's legendary theater district featuring world-class musicals and plays including The Phantom of the Opera and Hamilton.", category: "Show / Theatre", duration: "3 hours" }
    ]
  },
  {
    id: "istanbul",
    name: "Istanbul",
    country: "Turkey",
    emoji: "🇹🇷",
    tagline: "The Crossroads of Europe and Asia",
    description: "Istanbul straddles the Bosphorus strait, lying in both Europe and Asia. Its Old City reflects the cultural impacts of the many empires that once ruled here, from Roman and Byzantine to Ottoman.",
    image: "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?auto=format&fit=crop&w=800&q=80",
    quickFacts: {
      population: "15.6 million",
      language: "Turkish",
      currency: "Turkish Lira (₺)",
      bestTime: "April – May / September – October",
      timezone: "TRT (UTC+3)"
    },
    landmarks: [
      { name: "Hagia Sophia", description: "An architectural masterpiece built as a Byzantine cathedral in 537 AD, later an Ottoman mosque, blending Christian mosaics with Islamic calligraphy.", category: "Religious / Historical", mustVisit: true },
      { name: "Blue Mosque (Sultan Ahmed)", description: "Named for its stunning 20,000+ hand-painted blue İznik tiles, this 17th-century mosque is the only one in Istanbul with six minarets.", category: "Religious", mustVisit: true },
      { name: "Topkapi Palace", description: "The opulent administrative headquarters of the Ottoman sultans for 400 years, housing sacred relics, imperial treasures, and lush courtyards.", category: "Royal Palace", mustVisit: true },
      { name: "Galata Tower", description: "A medieval Genoese stone tower in the Galata quarter, offering a 360-degree panoramic view of the Bosphorus, Golden Horn, and both continents.", category: "Scenic Monument", mustVisit: false }
    ],
    delicacies: [
      { name: "Döner Kebab", description: "Seasoned lamb or chicken slowly cooked on a vertical rotisserie, sliced thin and served in fresh flatbread with herbs and garlic yogurt.", category: "Street Food", priceRange: "₺" },
      { name: "Baklava", description: "A rich, sweet pastry of 40+ layers of paper-thin filo dough filled with crushed pistachios and drenched in honey syrup.", category: "Dessert", priceRange: "₺" },
      { name: "Turkish Delight (Lokum)", description: "Jewel-toned gel confections flavored with rosewater, pomegranate, mastic, or bergamot, dusted with powdered sugar.", category: "Sweet Treat", priceRange: "₺" },
      { name: "Turkish Coffee", description: "Unfiltered coffee made with ultra-fine grounds in a copper cezve, served thick and strong with a side of Turkish delight.", category: "Drinks", priceRange: "₺" }
    ],
    attractions: [
      { name: "The Grand Bazaar", description: "One of the world's largest and oldest covered markets — 61 streets, 4,000+ shops selling carpets, lanterns, spices, and jewelry since 1461.", category: "Shopping", duration: "3-4 hours" },
      { name: "Bosphorus Cruise", description: "A scenic boat cruise along the strait separating two continents, passing Ottoman waterfront mansions, palaces, and medieval fortresses.", category: "Scenic Tour", duration: "2 hours" },
      { name: "Basilica Cistern", description: "A vast underground 6th-century water storage chamber supported by 336 marble columns, including two mysterious Medusa-head bases.", category: "Underground Monument", duration: "1 hour" }
    ]
  },
  {
    id: "tokyo",
    name: "Tokyo",
    country: "Japan",
    emoji: "🇯🇵",
    tagline: "The Neon Wonderland of Technology and Tradition",
    description: "Tokyo is Japan's busy capital, mixing the ultramodern and the traditional, from neon-lit skyscrapers to historic temples. The city is known for its vibrant food scene and varied nightlife.",
    image: "https://images.unsplash.com/photo-1540959733332-eab4deceeaf7?auto=format&fit=crop&w=800&q=80",
    quickFacts: {
      population: "37 million (Metro)",
      language: "Japanese",
      currency: "Japanese Yen (¥)",
      bestTime: "March – May (Sakura) / Sept – Nov",
      timezone: "JST (UTC+9)"
    },
    landmarks: [
      { name: "Shibuya Crossing", description: "The world's busiest pedestrian crossing outside Shibuya Station, where up to 3,000 people cross simultaneously beneath massive neon screens.", category: "Urban Landscape", mustVisit: true },
      { name: "Senso-ji Temple", description: "Tokyo's oldest Buddhist temple founded in 628 AD, located in Asakusa with a dramatic Thunder Gate entrance and bustling Nakamise shopping street.", category: "Religious / Historical", mustVisit: true },
      { name: "Tokyo Skytree", description: "A broadcasting and observation tower standing at 634 meters — the tallest structure in Japan with observation decks offering views to Mount Fuji.", category: "Observation Tower", mustVisit: false },
      { name: "Meiji Jingu Shrine", description: "A serene Shinto shrine dedicated to Emperor Meiji and Empress Shōken, surrounded by 170,000 trees forming a lush forest in the city center.", category: "Religious / Forest", mustVisit: true }
    ],
    delicacies: [
      { name: "Sushi (Omakase)", description: "The ultimate sushi experience: a chef-curated multi-course meal of premium nigiri using the freshest seasonal fish from Toyosu Market.", category: "Fine Dining", priceRange: "¥¥¥" },
      { name: "Tonkotsu Ramen", description: "Rich, creamy pork-bone broth simmered for 12+ hours, served with springy noodles, chashu pork, ajitsuke egg, and nori.", category: "Main Course", priceRange: "¥" },
      { name: "Tempura", description: "Seasonal vegetables and seafood coated in light, airy batter and fried to crispy perfection, served with tentsuyu dipping sauce.", category: "Traditional", priceRange: "¥¥" },
      { name: "Matcha Parfait", description: "A layered masterpiece of matcha green tea gelato, chewy mochi, sweet azuki bean paste, whipped cream, and crunchy cornflakes.", category: "Dessert", priceRange: "¥" }
    ],
    attractions: [
      { name: "Akihabara Electric Town", description: "The global epicenter of anime, manga, and gaming culture, with multi-story arcades, maid cafés, and specialty electronics shops.", category: "Pop Culture", duration: "3-4 hours" },
      { name: "teamLab Borderless", description: "A mind-bending digital art museum where immersive, projection-mapped installations flow across rooms without boundaries.", category: "Modern Art", duration: "3 hours" },
      { name: "Tsukiji Outer Market", description: "A bustling market adjacent to the old fish market, offering the freshest sushi, tamagoyaki, and wagyu beef skewers for breakfast.", category: "Food Market", duration: "2 hours" }
    ]
  },
  {
    id: "bangkok",
    name: "Bangkok",
    country: "Thailand",
    emoji: "🇹🇭",
    tagline: "The Vibrant Metropolis of Golden Temples",
    description: "Bangkok, Thailand's capital, is a large city known for ornate shrines, vibrant street life, and serene canals. The boat-filled Chao Phraya River feeds its network of canals flowing past the Rattanakosin royal district.",
    image: "https://images.unsplash.com/photo-1508009603885-50cf7c579365?auto=format&fit=crop&w=800&q=80",
    quickFacts: {
      population: "8.3 million",
      language: "Thai",
      currency: "Thai Baht (฿)",
      bestTime: "November to February",
      timezone: "ICT (UTC+7)"
    },
    landmarks: [
      { name: "The Grand Palace", description: "A dazzling complex of gilded buildings at the heart of Bangkok, the official residence of the Kings of Siam since 1782.", category: "Royal Palace", mustVisit: true },
      { name: "Wat Arun (Temple of Dawn)", description: "A riverside Buddhist temple adorned with towers encrusted with colorful Chinese porcelain shards and seashells, stunning at sunset.", category: "Religious", mustVisit: true },
      { name: "Wat Pho", description: "Home to a massive 46-meter-long gold-plated Reclining Buddha and Thailand's earliest center for public education and traditional massage.", category: "Religious / Historical", mustVisit: true },
      { name: "Mahanakhon SkyWalk", description: "Thailand's highest observation deck featuring a vertigo-inducing glass tray floor suspended 314 meters above the Bangkok skyline.", category: "Scenic / Modern", mustVisit: false }
    ],
    delicacies: [
      { name: "Pad Thai", description: "Stir-fried rice noodles with eggs, tofu, bean sprouts, crushed peanuts, and shrimp in a sweet-savory tamarind and fish sauce glaze.", category: "Street Food", priceRange: "฿" },
      { name: "Tom Yum Goong", description: "An intensely aromatic spicy-sour lemongrass soup with juicy shrimp, galangal, kaffir lime leaves, and roasted chili paste.", category: "Soup", priceRange: "฿" },
      { name: "Mango Sticky Rice", description: "Thailand's beloved dessert: perfectly ripe Alphonso-style mango with coconut-cream-soaked glutinous rice, topped with crunchy mung beans.", category: "Dessert", priceRange: "฿" },
      { name: "Som Tum (Green Papaya Salad)", description: "A fiery, tangy salad of shredded green papaya pounded with chilies, garlic, peanuts, dried shrimp, lime, and fish sauce.", category: "Street Food", priceRange: "฿" }
    ],
    attractions: [
      { name: "Chatuchak Weekend Market", description: "One of the world's largest weekend markets: 15,000+ stalls across 27 sections selling everything from vintage clothing to exotic pets.", category: "Shopping", duration: "3-4 hours" },
      { name: "Chao Phraya Dinner Cruise", description: "A luxurious evening buffet aboard a beautifully decorated boat, gliding past illuminated temples and the glowing Grand Palace.", category: "Scenic Tour", duration: "2 hours" },
      { name: "Khao San Road", description: "Bangkok's legendary backpacker street bursting with neon signs, street food carts, pad thai woks, cheap cocktail bars, and live music.", category: "Nightlife", duration: "2-3 hours" }
    ]
  },
  {
    id: "dubai",
    name: "Dubai",
    country: "United Arab Emirates",
    emoji: "🇦🇪",
    tagline: "The Oasis of Futurism and Boundless Luxury",
    description: "Dubai is a city of superlatives — the tallest building, the largest mall, man-made islands. Originally a small fishing village, it has transformed into a futuristic global hub of tourism, commerce, and architectural ambition.",
    image: "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=800&q=80",
    quickFacts: {
      population: "3.6 million",
      language: "Arabic, English",
      currency: "UAE Dirham (AED)",
      bestTime: "November to March",
      timezone: "GST (UTC+4)"
    },
    landmarks: [
      { name: "Burj Khalifa", description: "The tallest building in the world at 828 meters with 163 floors, offering observation decks with views stretching to the curvature of the Earth.", category: "Modern Skyscraper", mustVisit: true },
      { name: "Burj Al Arab", description: "An ultra-luxury hotel on its own artificial island, shaped like a billowing sail and synonymous with Dubai's ambition and opulence.", category: "Hotel / Icon", mustVisit: true },
      { name: "Palm Jumeirah", description: "The world's largest man-made island shaped like a palm tree, home to luxury resorts, private villas, and the iconic Atlantis resort.", category: "Engineering Marvel", mustVisit: false },
      { name: "Museum of the Future", description: "A stunning torus-shaped building with Arabic calligraphy windows, housing interactive exhibitions on AI, space travel, and sustainability.", category: "Museum / Architecture", mustVisit: true }
    ],
    delicacies: [
      { name: "Shawarma", description: "Marinated chicken or lamb slow-roasted on a vertical spit, wrapped in fresh flatbread with garlic toum, pickles, and crispy fries.", category: "Street Food", priceRange: "AED" },
      { name: "Al Machboos", description: "A fragrant Emirati rice dish slow-cooked with spiced meat, dried lime (loomi), and a blend of bezar spices unique to the Gulf.", category: "Traditional", priceRange: "AED AED" },
      { name: "Luqaimat", description: "Irresistible bite-sized fried dough balls with a crispy exterior and soft core, drizzled with date syrup and sprinkled with sesame.", category: "Dessert", priceRange: "AED" },
      { name: "Knafeh", description: "A beloved Middle Eastern dessert of crispy shredded kadaif pastry, melty Nabulsi cheese, and fragrant orange-blossom syrup.", category: "Dessert", priceRange: "AED" }
    ],
    attractions: [
      { name: "The Dubai Mall", description: "A retail universe spanning 1,200+ shops, an Olympic ice rink, a 10-million-liter aquarium, and an indoor waterfall — all under one roof.", category: "Shopping / Family", duration: "3-4 hours" },
      { name: "Desert Safari & BBQ", description: "An adrenaline-pumping desert adventure of dune bashing, camel riding, sandboarding, and a starlit BBQ dinner with belly dancing.", category: "Adventure", duration: "5-6 hours" },
      { name: "Dubai Fountain Show", description: "The world's largest choreographed fountain shooting water 150m high on Burj Khalifa Lake, synchronized to music and 6,600 lights.", category: "Scenic Show", duration: "30 mins" }
    ]
  },
  {
    id: "new-york",
    name: "New York City",
    country: "United States",
    emoji: "🇺🇸",
    tagline: "The Cultural Capital of the Modern World",
    description: "New York City comprises 5 boroughs sitting where the Hudson River meets the Atlantic Ocean. At its core is Manhattan, a densely populated borough that's among the world's major commercial, financial, and cultural centers.",
    image: "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=800&q=80",
    quickFacts: {
      population: "8.3 million",
      language: "English, Spanish",
      currency: "US Dollar ($)",
      bestTime: "April – June / September – November",
      timezone: "EST (UTC-5) / EDT (UTC-4)"
    },
    landmarks: [
      { name: "Statue of Liberty", description: "A colossal neoclassical copper sculpture on Liberty Island, a gift from France in 1886 symbolizing freedom and democracy worldwide.", category: "Monument", mustVisit: true },
      { name: "Empire State Building", description: "A 102-story Art Deco masterpiece in Midtown Manhattan that defined the NYC skyline for decades, offering two observation decks.", category: "Observation Tower", mustVisit: true },
      { name: "Brooklyn Bridge", description: "A hybrid cable-stayed/suspension bridge completed in 1883, connecting Manhattan and Brooklyn with stunning walking-path views.", category: "Infrastructure", mustVisit: false },
      { name: "Times Square", description: "The dazzling 'Crossroads of the World' — a neon-lit intersection of massive LED billboards, Broadway theaters, and non-stop energy.", category: "Urban Landscape", mustVisit: true }
    ],
    delicacies: [
      { name: "New York Style Pizza", description: "Large, thin-crusted slices with a perfect fold, crispy yet pliable, topped with tangy tomato sauce and gooey mozzarella.", category: "Fast Food", priceRange: "$" },
      { name: "Bagel with Lox", description: "A fresh-boiled, chewy bagel schmeared with cream cheese and topped with silky smoked salmon, red onions, capers, and dill.", category: "Breakfast", priceRange: "$$" },
      { name: "Pastrami on Rye", description: "A towering deli sandwich of warm, peppery cured beef pastrami piled high on seeded rye bread with spicy mustard.", category: "Deli Classic", priceRange: "$$" },
      { name: "New York Cheesecake", description: "A dense, velvety smooth baked cheesecake made with cream cheese, heavy cream, and eggs — rich, decadent, and iconic.", category: "Dessert", priceRange: "$$" }
    ],
    attractions: [
      { name: "Central Park", description: "An 843-acre urban oasis in Manhattan featuring lakes, trails, the Bethesda Fountain, Strawberry Fields, and horse-drawn carriages.", category: "Nature / Park", duration: "2-3 hours" },
      { name: "The Metropolitan Museum of Art", description: "The largest art museum in the Americas, with a collection spanning 5,000 years — from Egyptian temples to contemporary installations.", category: "Museum", duration: "3-4 hours" },
      { name: "Broadway Show", description: "Catch a world-class theatrical performance in one of 41 professional theaters along the legendary Great White Way.", category: "Show / Theatre", duration: "3 hours" }
    ]
  },
  {
    id: "sydney",
    name: "Sydney",
    country: "Australia",
    emoji: "🇦🇺",
    tagline: "The Coastal City of Iconic Sails and Surf",
    description: "Sydney is a vibrant, cosmopolitan city built around one of the world's most stunning natural harbours. Known for its iconic Opera House and Harbour Bridge, it seamlessly blends beach culture with urban sophistication.",
    image: "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?auto=format&fit=crop&w=800&q=80",
    quickFacts: {
      population: "5.3 million",
      language: "English",
      currency: "Australian Dollar (A$)",
      bestTime: "September – November / March – May",
      timezone: "AEST (UTC+10)"
    },
    landmarks: [
      { name: "Sydney Opera House", description: "A UNESCO-listed multi-venue performing arts centre at Bennelong Point, its white shell-shaped roof sails are among the most recognizable images of the 20th century.", category: "Arts / Architecture", mustVisit: true },
      { name: "Sydney Harbour Bridge", description: "A heritage-listed steel through arch bridge nicknamed 'The Coathanger', offering the BridgeClimb experience with 360-degree harbour views from the summit.", category: "Infrastructure", mustVisit: true },
      { name: "Sydney Tower Eye", description: "Sydney's tallest structure at 309 meters, featuring the Skywalk outdoor glass platform for breathtaking views of the harbour and Blue Mountains.", category: "Observation Tower", mustVisit: false },
      { name: "The Rocks Historic District", description: "Sydney's oldest neighbourhood with cobblestone lanes, colonial sandstone buildings, weekend markets, and fascinating convict-era history.", category: "Heritage Quarter", mustVisit: true }
    ],
    delicacies: [
      { name: "Barramundi", description: "A prized native Australian fish, pan-seared to golden crispy skin and served with fresh lemon, native herbs, and macadamia.", category: "Seafood", priceRange: "A$$" },
      { name: "Meat Pie", description: "A hand-sized golden pastry shell filled with diced or minced meat in thick gravy, eaten with a generous dollop of tomato sauce.", category: "Snacks", priceRange: "A$" },
      { name: "Lamington", description: "Cubes of light sponge cake dipped in chocolate icing and rolled in desiccated coconut — Australia's beloved national cake.", category: "Dessert", priceRange: "A$" },
      { name: "Flat White", description: "An espresso-based coffee perfected in Australia, topped with velvety microfoam steamed milk — now a global café staple.", category: "Coffee", priceRange: "A$" }
    ],
    attractions: [
      { name: "Bondi to Coogee Coastal Walk", description: "A stunning 6km seaside trail winding along dramatic cliffs, past hidden beaches, natural rock pools, and Aboriginal carvings.", category: "Scenic Walk", duration: "2 hours" },
      { name: "Taronga Zoo", description: "A world-class harbour-side zoo home to 4,000+ animals including koalas, platypuses, and kangaroos, with the best skyline backdrop in the world.", category: "Wildlife", duration: "3-4 hours" },
      { name: "Royal Botanic Garden", description: "A heritage-listed 30-hectare garden adjacent to the Opera House, offering stunning harbour views, themed walks, and flying fox colonies.", category: "Nature / Park", duration: "1-2 hours" }
    ]
  }
];
