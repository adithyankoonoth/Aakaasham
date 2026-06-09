# ml/dataset.py — Aakaasham: Build historical weather dataset for all Kerala locations
# Uses Open-Meteo (free, no API key required)

import requests
import pandas as pd
import numpy as np
from datetime import datetime
import time
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import KERALA_LOCATIONS


def fetch_location_weather(name: str, info: dict,
                           start: str = "2021-01-01",
                           end:   str = "2024-12-31") -> pd.DataFrame:
    """Fetch hourly historical weather for one location from Open-Meteo."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude":   info["lat"],
        "longitude":  info["lon"],
        "start_date": start,
        "end_date":   end,
        "hourly": [
            "cloudcover",
            "relativehumidity_2m",
            "windspeed_10m",
            "precipitation",
            "visibility",
            "temperature_2m",
            "weathercode",
        ],
        "timezone": "Asia/Kolkata"
    }

    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()["hourly"]

    df = pd.DataFrame(data)
    df.rename(columns={
        "time":                "timestamp",
        "cloudcover":          "cloud_pct",
        "relativehumidity_2m": "humidity_pct",
        "windspeed_10m":       "wind_kmh",
        "precipitation":       "precip_mm",
        "visibility":          "visibility_m",
        "temperature_2m":      "temp_c",
        "weathercode":         "weather_code",
    }, inplace=True)

    df["timestamp"]   = pd.to_datetime(df["timestamp"])
    df["location"]    = name
    df["lat"]         = info["lat"]
    df["lon"]         = info["lon"]
    df["elevation_m"] = info["elevation"]
    df["bortle"]      = info["bortle"]
    df.dropna(inplace=True)
    return df


def add_moon_phase(df: pd.DataFrame) -> pd.DataFrame:
    """Approximate moon illumination using synodic period formula."""
    known_new_moon = datetime(2000, 1, 6)
    def illumination(dt):
        if hasattr(dt, 'to_pydatetime'):
            dt = dt.to_pydatetime()
        dt = dt.replace(tzinfo=None)
        days = (dt - known_new_moon).days % 29.53
        angle = (days / 29.53) * 360
        return round((1 - np.cos(np.radians(angle))) / 2 * 100, 1)
    df["moon_illumination_pct"] = df["timestamp"].apply(illumination)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create all features the ML model will use."""
    df = df.copy()
    df["month"] = df["timestamp"].dt.month
    df["hour"]  = df["timestamp"].dt.hour

    # Kerala seasonal features
    df["is_monsoon"]     = df["month"].between(6, 9).astype(int)
    df["is_pre_monsoon"] = df["month"].between(3, 5).astype(int)
    df["is_winter"]      = df["month"].isin([11, 12, 1, 2]).astype(int)  # best season

    # Sky conditions
    df["is_raining"]        = (df["precip_mm"] > 0.1).astype(int)
    df["moon_interference"] = (df["moon_illumination_pct"] > 50).astype(int)

    # Location-based features
    df["elevation_bonus"] = (df["elevation_m"] / 1600).clip(0, 1)
    df["bortle_penalty"]  = df["bortle"] / 9.0

    # Atmospheric seeing index (0–10, higher = better)
    df["seeing_index"] = (
        10
        - (df["humidity_pct"] / 25)
        - (df["wind_kmh"] / 15)
        - (df["cloud_pct"] / 25)
        + (df["elevation_bonus"] * 2)
        - (df["bortle_penalty"] * 1.5)
    ).clip(0, 10).round(2)

    return df


def create_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Label each hour as astronomically observable (1) or not (0).
    Criteria: clear sky, low humidity, no rain, good visibility, nighttime.
    """
    BAD_WEATHER_CODES = {
        45, 48,                  # fog
        51, 53, 55,              # drizzle
        61, 63, 65,              # rain
        71, 73, 75,              # snow
        80, 81, 82,              # showers
        95, 96, 99,              # thunderstorm
    }

    is_night = df["hour"].isin(list(range(19, 24)) + list(range(0, 6)))

    df["good_sky"] = (
        (df["cloud_pct"]    < 30) &
        (df["humidity_pct"] < 75) &
        (df["precip_mm"]    < 0.1) &
        (df["visibility_m"] > 8000) &
        (~df["weather_code"].isin(BAD_WEATHER_CODES)) &
        is_night
    ).astype(int)

    return df


def build_full_kerala_dataset(save_path: str = "data/kerala_sky_dataset.csv",
                               cache_dir: str = "data/cache",
                               start_year: int = 2021,
                               end_year:   int = 2024) -> pd.DataFrame:
    """
    Main pipeline: fetch all Kerala locations → engineer features → label → save.
    Caches each location separately so reruns are fast.
    """
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    all_dfs = []

    print("=" * 55)
    print("  Aakaasham — Dataset Builder")
    print(f"  Period: {start_year}–{end_year} · {len(KERALA_LOCATIONS)} locations")
    print("=" * 55)

    for name, info in KERALA_LOCATIONS.items():
        cache_file = f"{cache_dir}/{name.lower().replace(' ', '_')}.csv"

        if os.path.exists(cache_file):
            df = pd.read_csv(cache_file, parse_dates=["timestamp"])
            print(f"  ✓ {name:<22} {len(df):>7,} rows  (cached)")
        else:
            print(f"  ↓ {name:<22} fetching...", end=" ", flush=True)
            try:
                df = fetch_location_weather(
                    name, info,
                    start=f"{start_year}-01-01",
                    end=f"{end_year}-12-31"
                )
                df.to_csv(cache_file, index=False)
                print(f"{len(df):>7,} rows")
                time.sleep(0.6)  # rate limit courtesy
            except Exception as e:
                print(f"FAILED — {e}")
                continue

        all_dfs.append(df)

    if not all_dfs:
        raise RuntimeError("No data fetched. Check internet connection.")

    print(f"\nCombining {len(all_dfs)} locations...")
    full = pd.concat(all_dfs, ignore_index=True)
    full = add_moon_phase(full)
    full = engineer_features(full)
    full = create_labels(full)

    # Night hours only
    night = full[full["hour"].isin(list(range(19, 24)) + list(range(0, 6)))]
    night = night.reset_index(drop=True)
    night.to_csv(save_path, index=False)

    # Summary
    good  = night["good_sky"].sum()
    total = len(night)
    print(f"\n{'='*55}")
    print(f"  Total rows     : {total:,}")
    print(f"  Locations      : {night['location'].nunique()}")
    print(f"  Good sky hours : {good:,} ({good/total*100:.1f}%)")
    print(f"  Bad sky hours  : {total-good:,} ({(total-good)/total*100:.1f}%)")
    print(f"\n  Good sky % by location:")

    loc_summary = night.groupby("location")["good_sky"].mean().sort_values(ascending=False)
    for loc, pct in loc_summary.items():
        bar = "█" * int(pct * 25)
        pad = " " * (25 - len(bar))
        print(f"    {loc:<22} {bar}{pad} {pct*100:.1f}%")

    print(f"\n  Dataset saved → {save_path}")
    return night


if __name__ == "__main__":
    build_full_kerala_dataset()
