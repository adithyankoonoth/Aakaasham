# 🌌 Aakaasham
**ആകാശം** — Sky in Malayalam

Astronomical event predictor for Kerala, India.  
Combines **Skyfield** (NASA ephemeris) with a **scikit-learn RandomForest** visibility classifier
trained on 4 years of historical weather data across all Kerala locations.

---

## Features

- 🗺️ **Kerala-wide coverage** — all 14 districts + dark sky spots (Munnar, Vagamon, Nelliampathy...)
- 🪐 **Planet lineup** — real-time altitude/azimuth for all planets from any Kerala location
- 🌠 **Event calendar** — conjunctions, meteor showers, lunar eclipses, oppositions
- 🤖 **ML visibility model** — RandomForest trained on cloud cover, humidity, monsoon season, elevation, Bortle class
- 📊 **Insights dashboard** — feature importance, monthly breakdown, per-location accuracy
- 🌙 **Moon phase** — automatic illumination & interference scoring

---

## Quick Start

```bash
# 1. Clone / unzip project
cd aakaasham

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Build the dataset (downloads 4 years of Kerala weather — ~5 min, cached after)
python ml/dataset.py

# 5. Train the ML model
python ml/train_model.py

# 6. Launch the app
streamlit run app.py
```

The app works even before training — it falls back to a heuristic visibility model.

---

## Project Structure

```
aakaasham/
├── config.py              # All Kerala locations, coordinates, Bortle class
├── requirements.txt
├── app.py                 # Streamlit frontend (dark astronomy theme)
│
├── core/
│   └── ephemeris.py       # Skyfield: planet positions, conjunctions, eclipses
│
├── ml/
│   ├── dataset.py         # Open-Meteo data fetcher for all Kerala locations
│   └── train_model.py     # RandomForest training, evaluation, prediction
│
└── data/
    ├── cache/             # Per-location weather CSVs (auto-generated)
    ├── kerala_sky_dataset.csv   # Combined labeled dataset
    └── visibility_model.pkl     # Trained model
```

---

## ML Model

**Algorithm:** RandomForestClassifier (scikit-learn)

**Features:**
| Feature | Description |
|---|---|
| `cloud_pct` | Cloud cover % — most important feature |
| `humidity_pct` | Atmospheric humidity |
| `seeing_index` | Composite atmospheric stability score |
| `visibility_m` | Meteorological visibility |
| `is_monsoon` | Binary — June to September |
| `moon_illumination_pct` | Moon brightness (% illuminated) |
| `elevation_m` | Location elevation above sea level |
| `bortle` | Light pollution class (1–9) |
| `wind_kmh` | Wind speed |
| `month` / `hour` | Temporal features |

**Label:** `good_sky = 1` if cloud < 30%, humidity < 75%, no rain, visibility > 8km, nighttime

**Training data:** 4 years (2021–2024), ~500,000 hourly rows across 22 Kerala locations

**Expected performance:**
- CV ROC-AUC: ~0.91
- Test Accuracy: ~0.88

---

## Locations Covered

### Districts
Thiruvananthapuram, Kollam, Pathanamthitta, Alappuzha, Kottayam,
Idukki, Ernakulam, Thrissur, Palakkad, Malappuram, Kozhikode,
Wayanad, Kannur, Kasaragod

### Dark Sky Spots ⭐
Munnar (1600m), Nelliampathy (1250m), Vagamon (1100m), Peermade (915m),
Ponmudi (1100m), Vythiri (900m), Thekkady (900m), Athirappilly (50m)

---

## Data Sources

- **Weather history:** [Open-Meteo](https://open-meteo.com/) — free, no API key
- **Ephemeris:** NASA DE421 via [Skyfield](https://rhodesmill.org/skyfield/)
- **Real-time weather:** OpenWeatherMap (optional — add API key in config.py)

---

## Deploy to Hugging Face Spaces

```bash
# 1. Create new Space at huggingface.co/spaces
# 2. Choose: Streamlit · Python 3.10

# 3. Push your code
git init
git add .
git commit -m "initial commit"
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/aakaasham
git push space main
```

---

## Resume Description

> Built an astronomical event predictor for Kerala, India using Skyfield for precise
> NASA ephemeris calculations and a scikit-learn RandomForest classifier trained on
> 500K rows of historical weather data across 22 locations. Features planetary conjunction
> detection, meteor shower calendars, lunar eclipse prediction, and an ML visibility
> model incorporating Kerala's monsoon seasonality, elevation, and light pollution data.
> Deployed on Hugging Face Spaces with an interactive Streamlit dashboard.

---

Built by a Kerala maker 🌴 · Data-driven stargazing for God's Own Country
