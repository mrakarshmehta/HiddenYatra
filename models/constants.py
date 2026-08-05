"""
HiddenYatra — Database Domain Constants
Centralized categories and display constants.
"""

PLACE_CATEGORIES = [
    ('tourist_spot', '📸 Tourist Spot'),
    ('temple', '🛕 Temple / Religious'),
    ('food_place', '🍽️ Food Place'),
    ('hidden_gem', '💎 Hidden Gem'),
    ('nature', '🌿 Nature / Wildlife'),
    ('historical', '🏛️ Historical Monument'),
    ('beach', '🏖️ Beach'),
    ('mountain', '⛰️ Mountain / Hill Station'),
    ('market', '🛍️ Market / Shopping'),
    ('adventure', '🧗 Adventure / Sport'),
    ('cultural', '🎭 Cultural Site'),
    ('waterfall', '💧 Waterfall'),
    ('lake', '🌊 Lake / River'),
    ('other', '📌 Other'),
]

SPECIALTY_CATEGORIES = [
    ('food', '🍛 Food'),
    ('sweet', '🍬 Sweet / Dessert'),
    ('drink', '🥤 Drink / Beverage'),
    ('craft', '🎨 Craft / Handicraft'),
    ('textile', '🧵 Textile / Fabric'),
    ('souvenir', '🎁 Souvenir'),
    ('other', '📌 Other'),
]

ACCOMMODATION_TYPES = [
    ('hotel', '🏨 Hotel'),
    ('resort', '🏖️ Resort'),
    ('guesthouse', '🏠 Guest House'),
    ('hostel', '🛏️ Hostel'),
    ('homestay', '🏡 Homestay'),
    ('dharamshala', '🛕 Dharamshala'),
    ('motel', '🚗 Motel'),
    ('lodge', '🏢 Lodge'),
]

SERVICE_GROUP_ORDER = ['Health & Emergency', 'Transport & Fuel', 'Financial & Admin', 'Local Services']


def get_category_label(code, categories=PLACE_CATEGORIES):
    if not code or not isinstance(code, str):
        return 'General'
    for c, label in categories:
        if c == code:
            return label
    return code.replace('_', ' ').title()
