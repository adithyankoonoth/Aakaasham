# config.py — Kerala Sky Tracker
# All major locations + dark sky spots across Kerala

KERALA_LOCATIONS = {
    # 14 Districts
    "Thiruvananthapuram": {"lat": 8.5241,  "lon": 76.9366, "elevation": 16,   "bortle": 6, "district": True},
    "Kollam":             {"lat": 8.8932,  "lon": 76.6141, "elevation": 9,    "bortle": 5, "district": True},
    "Pathanamthitta":     {"lat": 9.2648,  "lon": 76.7870, "elevation": 37,   "bortle": 4, "district": True},
    "Alappuzha":          {"lat": 9.4981,  "lon": 76.3388, "elevation": 2,    "bortle": 5, "district": True},
    "Kottayam":           {"lat": 9.5916,  "lon": 76.5222, "elevation": 4,    "bortle": 5, "district": True},
    "Idukki":             {"lat": 9.9189,  "lon": 77.1025, "elevation": 748,  "bortle": 3, "district": True},
    "Ernakulam":          {"lat": 9.9816,  "lon": 76.2999, "elevation": 8,    "bortle": 7, "district": True},
    "Thrissur":           {"lat": 10.5276, "lon": 76.2144, "elevation": 3,    "bortle": 5, "district": True},
    "Palakkad":           {"lat": 10.7867, "lon": 76.6548, "elevation": 80,   "bortle": 4, "district": True},
    "Malappuram":         {"lat": 11.0510, "lon": 76.0711, "elevation": 108,  "bortle": 4, "district": True},
    "Kozhikode":          {"lat": 11.2588, "lon": 75.7804, "elevation": 5,    "bortle": 6, "district": True},
    "Wayanad":            {"lat": 11.6854, "lon": 76.1320, "elevation": 778,  "bortle": 3, "district": True},
    "Kannur":             {"lat": 11.8745, "lon": 75.3704, "elevation": 5,    "bortle": 5, "district": True},
    "Kasaragod":          {"lat": 12.4996, "lon": 74.9869, "elevation": 20,   "bortle": 4, "district": True},

    # Dark Sky Spots
    "Munnar":             {"lat": 10.0889, "lon": 77.0595, "elevation": 1600, "bortle": 2, "district": False},
    "Vagamon":            {"lat": 9.6865,  "lon": 76.9085, "elevation": 1100, "bortle": 2, "district": False},
    "Ponmudi":            {"lat": 8.7419,  "lon": 77.0982, "elevation": 1100, "bortle": 3, "district": False},
    "Vythiri":            {"lat": 11.5854, "lon": 76.0242, "elevation": 900,  "bortle": 3, "district": False},
    "Nelliampathy":       {"lat": 10.5667, "lon": 76.6833, "elevation": 1250, "bortle": 2, "district": False},
    "Thekkady":           {"lat": 9.5980,  "lon": 77.1700, "elevation": 900,  "bortle": 2, "district": False},
    "Athirappilly":       {"lat": 10.2833, "lon": 76.5667, "elevation": 50,   "bortle": 3, "district": False},
    "Peermade":           {"lat": 9.5833,  "lon": 77.0167, "elevation": 915,  "bortle": 2, "district": False},
}

# BORTLE SCALE DESCRIPTIONS
BORTLE_DESC = {
    1: "Pristine dark sky",
    2: "Truly dark sky",
    3: "Rural sky",
    4: "Rural/suburban transition",
    5: "Suburban sky",
    6: "Bright suburban sky",
    7: "Suburban/urban transition",
    8: "City sky",
    9: "Inner-city sky",
}

# Meteor showers visible from Kerala
METEOR_SHOWERS = [
    {"name": "Quadrantids",  "peak_month": 1,  "peak_day": 4,  "rate": 110, "radiant": "N",  "best_time": "03:00–05:30"},
    {"name": "Lyrids",       "peak_month": 4,  "peak_day": 22, "rate": 18,  "radiant": "NE", "best_time": "22:00–03:00"},
    {"name": "Eta Aquarids", "peak_month": 5,  "peak_day": 6,  "rate": 50,  "radiant": "SE", "best_time": "03:00–05:00"},
    {"name": "Perseids",     "peak_month": 8,  "peak_day": 12, "rate": 100, "radiant": "NE", "best_time": "00:30–04:00"},
    {"name": "Orionids",     "peak_month": 10, "peak_day": 21, "rate": 20,  "radiant": "SE", "best_time": "22:00–03:00"},
    {"name": "Leonids",      "peak_month": 11, "peak_day": 17, "rate": 15,  "radiant": "E",  "best_time": "01:00–04:00"},
    {"name": "Geminids",     "peak_month": 12, "peak_day": 14, "rate": 120, "radiant": "E",  "best_time": "22:00–03:00"},
    {"name": "Ursids",       "peak_month": 12, "peak_day": 22, "rate": 10,  "radiant": "N",  "best_time": "00:00–05:00"},
]

OPENWEATHER_API_KEY = "YOUR_API_KEY_HERE"  # free at openweathermap.org
DEFAULT_LOCATION = "Thrissur"
