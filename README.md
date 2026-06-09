---
title: Aakaasham
emoji: 🌌
colorFrom: blue
colorTo: green
sdk: streamlit
python_version: "3.11"
app_file: app.py
pinned: false
---

# 🌌 Aakaasham

**ആകാശം** — Sky in Malayalam

Astronomical event predictor for Kerala, India.

Aakaasham combines precise astronomical calculations using Skyfield and NASA ephemeris data with a machine learning visibility model trained on historical weather patterns across Kerala. The platform helps users identify the best locations and times for astronomical observation, planetary viewing, meteor showers, conjunctions, and other celestial events.

---

## Features

- 🗺️ Kerala-wide coverage across districts and dark-sky locations
- 🪐 Real-time planetary positions and visibility
- 🌠 Astronomical event calendar
- 🤖 Machine learning sky visibility prediction
- 📊 Weather and visibility analytics dashboard
- 🌙 Moon phase and illumination tracking
- 📍 Location-specific observation recommendations
- ☁️ Historical weather-based visibility scoring

---

## Quick Start

### Clone the Repository

```bash
git clone https://github.com/adithyankoonoth/aakaasham.git
cd aakaasham
```

### Create a Virtual Environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux / macOS:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Generate Dataset

```bash
python ml/dataset.py
```

### Train the Model

```bash
python ml/train_model.py
```

### Launch the Application

```bash
streamlit run app.py
```

---

## Project Structure

```text
aakaasham/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
│
├── core/
│   └── ephemeris.py
│
├── ml/
│   ├── dataset.py
│   └── train_model.py
│
├── data/
│   ├── cache/
│   ├── kerala_sky_dataset.csv
│   └── visibility_model.pkl
│
└── assets/
```

---

## Machine Learning Model

### Algorithm

- Random Forest Classifier
- Scikit-learn

### Features Used

| Feature | Description |
|----------|-------------|
| cloud_pct | Cloud cover percentage |
| humidity_pct | Relative humidity |
| visibility_m | Atmospheric visibility |
| seeing_index | Sky stability score |
| moon_illumination_pct | Moon brightness |
| wind_kmh | Wind speed |
| elevation_m | Elevation of location |
| bortle | Light pollution class |
| is_monsoon | Monsoon season indicator |
| month | Month of observation |
| hour | Hour of observation |

### Prediction Target

Good sky visibility conditions for astronomical observation.

---

## Locations Covered

### Kerala Districts

- Thiruvananthapuram
- Kollam
- Pathanamthitta
- Alappuzha
- Kottayam
- Idukki
- Ernakulam
- Thrissur
- Palakkad
- Malappuram
- Kozhikode
- Wayanad
- Kannur
- Kasaragod

### Dark Sky Locations

- Munnar
- Vagamon
- Ponmudi
- Peermade
- Nelliampathy
- Vythiri
- Thekkady
- Athirappilly

---

## Technology Stack

### Frontend

- Streamlit

### Astronomy

- Skyfield
- NASA DE421 Ephemeris

### Machine Learning

- Scikit-learn
- Pandas
- NumPy

### Data Sources

- Open-Meteo Historical Weather API
- NASA Ephemeris Data

---

## Deployment

This application is configured for deployment on Hugging Face Spaces using Streamlit.

```bash
git add .
git commit -m "deploy update"
git push space main
```

---

## Future Improvements

- Satellite pass predictions
- ISS tracking
- Deep-sky object recommendations
- Real-time weather integration
- Mobile-responsive interface
- Advanced astrophotography planning tools

---

## License

MIT License

---

Built with ❤️ in Kerala.
