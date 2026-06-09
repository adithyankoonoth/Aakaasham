# ml/collect_weather.py — Live weather fetcher for Kerala locations
# Optional: needs OpenWeatherMap API key in config.py
# Run hourly via cron to build real-time prediction data

import requests
import pandas as pd
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import KERALA_LOCATIONS, OPENWEATHER_API_KEY

LOG_FILE = "data/live_weather_log.csv"


def fetch_current_weather(name: str, info: dict) -> dict | None:
    """Fetch current weather for one Kerala location."""
    if OPENWEATHER_API_KEY == "YOUR_API_KEY_HERE":
        print("⚠  Set OPENWEATHER_API_KEY in config.py (free at openweathermap.org)")
        return None

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": info["lat"], "lon": info["lon"],
        "appid": OPENWEATHER_API_KEY, "units": "metric"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        d = r.json()
        return {
            "timestamp":       datetime.utcnow().isoformat(),
            "location":        name,
            "cloud_pct":       d["clouds"]["all"],
            "humidity_pct":    d["main"]["humidity"],
            "wind_kmh":        d["wind"]["speed"] * 3.6,
            "temp_c":          d["main"]["temp"],
            "precip_mm":       d.get("rain", {}).get("1h", 0),
            "visibility_m":    d.get("visibility", 10000),
            "weather_main":    d["weather"][0]["main"],
            "weather_code":    d["weather"][0]["id"],
        }
    except Exception as e:
        print(f"  Failed {name}: {e}")
        return None


def fetch_all_kerala(locations: list = None) -> list:
    """Fetch current weather for all (or selected) Kerala locations."""
    if locations is None:
        locations = list(KERALA_LOCATIONS.keys())

    results = []
    for name in locations:
        info = KERALA_LOCATIONS[name]
        row = fetch_current_weather(name, info)
        if row:
            results.append(row)
            print(f"  ✓ {name:<22} Cloud: {row['cloud_pct']}%  Humidity: {row['humidity_pct']}%")
    return results


def log_weather(locations: list = None):
    """Append current weather snapshot to CSV log."""
    os.makedirs("data", exist_ok=True)
    rows = fetch_all_kerala(locations)
    if not rows:
        return

    df_new = pd.DataFrame(rows)
    if os.path.exists(LOG_FILE):
        df_new.to_csv(LOG_FILE, mode='a', header=False, index=False)
    else:
        df_new.to_csv(LOG_FILE, index=False)

    print(f"\n  Logged {len(rows)} locations → {LOG_FILE}")


def get_current_conditions(location: str) -> dict | None:
    """Get current weather dict for a single location (used by app.py)."""
    info = KERALA_LOCATIONS.get(location)
    if not info:
        return None
    return fetch_current_weather(location, info)


# ── Cron setup ──────────────────────────────────────────────────────────────
CRON_INSTRUCTIONS = """
To log weather every hour automatically:

  Linux/Mac — add to crontab:
    crontab -e
    0 * * * * cd /path/to/kerala-sky-tracker && python ml/collect_weather.py

  Windows — Task Scheduler:
    Action: python ml/collect_weather.py
    Trigger: Daily, repeat every 1 hour
"""

if __name__ == "__main__":
    print("Aakaasham — Live Weather Logger")
    print("=" * 45)
    log_weather()
    print(CRON_INSTRUCTIONS)
