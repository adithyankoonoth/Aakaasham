# ml/dataset.py — Aakaasham
# Build historical astronomy-weather dataset for Kerala
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


# --------------------------------------------------
# Fetch historical weather
# --------------------------------------------------

def fetch_location_weather(
    name: str,
    info: dict,
    start: str = "2021-01-01",
    end: str = "2024-12-31"
) -> pd.DataFrame:
    """Fetch hourly historical weather for one location from Open-Meteo."""
    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": info["lat"],
        "longitude": info["lon"],
        "start_date": start,
        "end_date": end,
        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "cloud_cover",
            "wind_speed_10m",
            "weather_code"
        ]),
        "timezone": "Asia/Kolkata"
    }

    # Retry loop for rate-limiting (HTTP 429)
    for attempt in range(5):
        response = requests.get(url, params=params, timeout=60)
        if response.status_code == 429:
            wait = (attempt + 1) * 5
            print(f"Rate limited. Waiting {wait}s...")
            time.sleep(wait)
            continue
        response.raise_for_status()
        break

    payload = response.json()

    if "hourly" not in payload:
        raise RuntimeError(
            f"Open-Meteo returned unexpected response for {name}"
        )

    hourly = payload["hourly"]

    df = pd.DataFrame({
        "timestamp": hourly.get("time", []),
        "temp_c": hourly.get("temperature_2m", []),
        "humidity_pct": hourly.get("relative_humidity_2m", []),
        "precip_mm": hourly.get("precipitation", []),
        "cloud_pct": hourly.get("cloud_cover", []),
        "wind_kmh": hourly.get("wind_speed_10m", []),
        "weather_code": hourly.get("weather_code", [])
    })

    if len(df) == 0:
        raise RuntimeError(
            f"No rows returned for {name}. "
            f"Available keys: {list(hourly.keys())}"
        )

    # Open-Meteo archive doesn't reliably provide visibility in all regions; baseline it
    df["visibility_m"] = 10000.0

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["location"] = name
    df["lat"] = info["lat"]
    df["lon"] = info["lon"]
    df["elevation_m"] = info["elevation"]
    df["bortle"] = info["bortle"]

    df = df.dropna(
        subset=[
            "timestamp",
            "temp_c",
            "humidity_pct",
            "precip_mm",
            "wind_kmh",
            "weather_code"
        ]
    )

    return df


# --------------------------------------------------
# Moon illumination
# --------------------------------------------------

def add_moon_phase(df: pd.DataFrame) -> pd.DataFrame:
    """Approximate moon illumination using synodic period formula."""
    known_new_moon = datetime(2000, 1, 6)
    moon_values = []

    for ts in df["timestamp"]:
        if pd.isna(ts):
            moon_values.append(np.nan)
            continue

        if hasattr(ts, "to_pydatetime"):
            ts = ts.to_pydatetime()

        ts = ts.replace(tzinfo=None)
        days = (ts - known_new_moon).days % 29.53
        angle = (days / 29.53) * 360
        illumination = (1 - np.cos(np.radians(angle))) / 2 * 100
        moon_values.append(round(float(illumination), 1))

    df["moon_illumination_pct"] = pd.Series(moon_values, dtype="float64")
    return df


# --------------------------------------------------
# Feature engineering
# --------------------------------------------------

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create all features the ML model will use."""
    df = df.copy()
    df["month"] = df["timestamp"].dt.month
    df["hour"] = df["timestamp"].dt.hour

    # Kerala seasonal features
    df["is_monsoon"] = df["month"].between(6, 9).astype(int)
    df["is_pre_monsoon"] = df["month"].between(3, 5).astype(int)
    df["is_winter"] = df["month"].isin([11, 12, 1, 2]).astype(int)

    # Sky conditions
    df["is_raining"] = (df["precip_mm"] > 0.1).astype(int)
    
    df["moon_illumination_pct"] = pd.to_numeric(df["moon_illumination_pct"], errors="coerce")
    df["moon_interference"] = (df["moon_illumination_pct"].fillna(0) > 50).astype(int)

    # Location-based features
    df["elevation_bonus"] = (df["elevation_m"] / 1600).clip(0, 1)
    df["bortle_penalty"] = df["bortle"] / 9.0

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


# --------------------------------------------------
# Label generation
# --------------------------------------------------

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
        (df["cloud_pct"] < 30) &
        (df["humidity_pct"] < 75) &
        (df["precip_mm"] < 0.1) &
        (df["visibility_m"] > 8000) &
        (~df["weather_code"].isin(BAD_WEATHER_CODES)) &
        is_night
    ).astype(int)

    return df


# --------------------------------------------------
# Main pipeline
# --------------------------------------------------

def build_full_kerala_dataset(
    save_path: str = "data/kerala_sky_dataset.csv",
    cache_dir: str = "data/cache",
    start_year: int = 2021,
    end_year: int = 2024
) -> pd.DataFrame:
    """Main pipeline: fetch all Kerala locations → engineer features → label → save."""
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    all_dfs = []

    print("=" * 60)
    print("  Aakaasham — Dataset Builder")
    print(f"  Period: {start_year}–{end_year} · {len(KERALA_LOCATIONS)} locations")
    print("=" * 60)

    for name, info in KERALA_LOCATIONS.items():
        cache_file = f"{cache_dir}/{name.lower().replace(' ', '_')}.csv"

        if os.path.exists(cache_file):
            df = pd.read_csv(cache_file, parse_dates=["timestamp"])
            print(f"  ✓ {name:<22} {len(df):>7,}-rows (cached)")
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

    # Summary outputs
    good = int(night["good_sky"].sum())
    total = len(night)
    print(f"\n{'='*60}")
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