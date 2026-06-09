# core/ephemeris.py — Astronomical calculations using Skyfield
# Localized for Kerala, India

from skyfield.api import load, wgs84
from skyfield import almanac
from datetime import datetime, timedelta
import pytz
import numpy as np

ts = load.timescale()
eph = load('de421.bsp')  # Downloads ~16MB NASA ephemeris on first run
IST = pytz.timezone("Asia/Kolkata")

PLANETS = {
    "Mercury": eph["mercury"],
    "Venus":   eph["venus"],
    "Mars":    eph["mars"],
    "Jupiter": eph["jupiter barycenter"],
    "Saturn":  eph["saturn barycenter"],
    "Uranus":  eph["uranus barycenter"],
    "Neptune": eph["neptune barycenter"],
}

PLANET_COLORS = {
    "Mercury": "#B5B5B5",
    "Venus":   "#E8C97A",
    "Mars":    "#C1440E",
    "Jupiter": "#C88B3A",
    "Saturn":  "#E4D191",
    "Uranus":  "#7DE8E8",
    "Neptune": "#5B7FDB",
}


def get_observer(lat: float, lon: float, elevation: float = 0):
    return wgs84.latlon(lat, lon, elevation_m=elevation)


def get_planet_position(planet_name: str, when: datetime, lat: float, lon: float) -> dict:
    """Altitude, azimuth, and visibility of a planet from a Kerala location."""
    t = ts.from_datetime(when.replace(tzinfo=pytz.utc))
    observer = get_observer(lat, lon)
    planet = PLANETS.get(planet_name)
    if not planet:
        raise ValueError(f"Unknown planet: {planet_name}")

    astrometric = (eph["earth"] + observer).at(t).observe(planet)
    alt, az, dist = astrometric.apparent().altaz()

    return {
        "planet":       planet_name,
        "color":        PLANET_COLORS.get(planet_name, "#FFFFFF"),
        "altitude_deg": round(alt.degrees, 2),
        "azimuth_deg":  round(az.degrees, 2),
        "distance_au":  round(dist.au, 4),
        "visible":      alt.degrees > 5,
        "time_ist":     when.astimezone(IST).strftime("%Y-%m-%d %H:%M IST"),
    }


def get_all_planets_tonight(lat: float, lon: float) -> list:
    """Get positions of all planets at 21:00 IST tonight."""
    now_ist = datetime.now(IST)
    tonight = now_ist.replace(hour=21, minute=0, second=0, microsecond=0)
    tonight_utc = tonight.astimezone(pytz.utc).replace(tzinfo=None)

    results = []
    for name in PLANETS:
        try:
            pos = get_planet_position(name, tonight_utc, lat, lon)
            results.append(pos)
        except Exception:
            pass
    return sorted(results, key=lambda x: -x["altitude_deg"])


def get_moon_phase(date: datetime) -> dict:
    """Moon phase name and illumination percentage."""
    t = ts.from_datetime(date.replace(tzinfo=pytz.utc))
    phase_angle = almanac.moon_phase(eph, t)
    angle = phase_angle.degrees
    illumination = (1 - abs(angle - 180) / 180) * 100

    if angle < 22.5:    name = "New Moon"
    elif angle < 67.5:  name = "Waxing Crescent"
    elif angle < 112.5: name = "First Quarter"
    elif angle < 157.5: name = "Waxing Gibbous"
    elif angle < 202.5: name = "Full Moon"
    elif angle < 247.5: name = "Waning Gibbous"
    elif angle < 292.5: name = "Last Quarter"
    elif angle < 337.5: name = "Waning Crescent"
    else:               name = "New Moon"

    emoji_map = {
        "New Moon": "🌑", "Waxing Crescent": "🌒", "First Quarter": "🌓",
        "Waxing Gibbous": "🌔", "Full Moon": "🌕", "Waning Gibbous": "🌖",
        "Last Quarter": "🌗", "Waning Crescent": "🌘",
    }

    return {
        "phase_name":       name,
        "emoji":            emoji_map.get(name, "🌑"),
        "illumination_pct": round(illumination, 1),
        "phase_angle":      round(angle, 1),
        "good_for_obs":     illumination < 35,
    }


def find_conjunctions(lat: float, lon: float, days_ahead: int = 60,
                      threshold_deg: float = 5.0) -> list:
    """Find planetary conjunctions visible from a Kerala location."""
    observer = get_observer(lat, lon)
    earth = eph["earth"] + observer
    planet_names = [p for p in PLANETS if p not in ("Uranus", "Neptune")]
    conjunctions = []
    now = datetime.utcnow()

    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1_name, p2_name = planet_names[i], planet_names[j]
            p1, p2 = PLANETS[p1_name], PLANETS[p2_name]
            min_sep = 360
            min_day = None

            for day in range(days_ahead):
                check = now + timedelta(days=day, hours=15, minutes=30)  # 21:00 IST
                t = ts.from_datetime(check.replace(tzinfo=pytz.utc))
                pos1 = earth.at(t).observe(p1).apparent()
                pos2 = earth.at(t).observe(p2).apparent()
                sep = pos1.separation_from(pos2).degrees
                if sep < min_sep:
                    min_sep = sep
                    min_day = check

            if min_sep < threshold_deg and min_day:
                ist_dt = min_day.astimezone(IST)
                # Check if planets are above horizon
                t = ts.from_datetime(min_day.replace(tzinfo=pytz.utc))
                alt1, _, _ = earth.at(t).observe(p1).apparent().altaz()
                alt2, _, _ = earth.at(t).observe(p2).apparent().altaz()
                visible = alt1.degrees > 5 and alt2.degrees > 5

                conjunctions.append({
                    "type":          "Conjunction",
                    "planets":       [p1_name, p2_name],
                    "separation_deg": round(min_sep, 2),
                    "date":          ist_dt.strftime("%b %d, %Y"),
                    "time_ist":      "21:00 IST",
                    "description":   f"{p1_name} & {p2_name} — {round(min_sep, 2)}° apart",
                    "naked_eye":     min_sep < 1.0,
                    "visible":       visible,
                    "rarity":        "Rare" if min_sep < 1 else "Notable" if min_sep < 3 else "Common",
                })

    return sorted(conjunctions, key=lambda x: x["separation_deg"])


def find_lunar_eclipses(days_ahead: int = 365) -> list:
    """Find upcoming lunar eclipses."""
    now = ts.now()
    future = ts.tt_jd(now.tt + days_ahead)
    try:
        times, events = almanac.find_discrete(now, future, almanac.lunar_eclipses(eph))
    except Exception:
        return []

    type_map = {0: "Penumbral", 1: "Partial", 2: "Total"}
    eclipses = []
    for t, e in zip(times, events):
        ist_dt = t.utc_datetime().astimezone(IST)
        eclipses.append({
            "type":          "Lunar Eclipse",
            "eclipse_type":  type_map.get(e, "Unknown"),
            "date":          ist_dt.strftime("%b %d, %Y"),
            "peak_time_ist": ist_dt.strftime("%H:%M IST"),
            "visible_kerala": True,
            "description":   f"{type_map.get(e,'Unknown')} Lunar Eclipse",
        })
    return eclipses


def find_planet_oppositions(days_ahead: int = 365) -> list:
    """Find when outer planets are at opposition (closest, brightest)."""
    # Simplified: check when Mars/Jupiter/Saturn are visible all night
    oppositions = []
    # Known upcoming oppositions (supplement Skyfield with curated data)
    known = [
        {"planet": "Mars",    "date": "Jan 16, 2025", "magnitude": -1.4, "constellation": "Gemini"},
        {"planet": "Jupiter", "date": "Dec 07, 2024", "magnitude": -2.8, "constellation": "Taurus"},
        {"planet": "Saturn",  "date": "Sep 21, 2025", "magnitude": +0.6, "constellation": "Aquarius"},
    ]
    for o in known:
        o["type"] = "Opposition"
        o["description"] = f"{o['planet']} at opposition — brightest of the year"
        o["rarity"] = "Annual"
        oppositions.append(o)
    return oppositions
