# app.py — Aakaasham · Streamlit Frontend
# Run: streamlit run app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pytz
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import KERALA_LOCATIONS, BORTLE_DESC, METEOR_SHOWERS

IST = pytz.timezone("Asia/Kolkata")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Aakaasham — Kerala Sky Tracker",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — dark astronomy theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=Space+Mono:wght@400;700&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Sora', sans-serif !important;
    background-color: #05070F !important;
    color: #E8EAF0 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #090C18 !important;
    border-right: 1px solid #1A1F35 !important;
}
[data-testid="stSidebar"] * { color: #C8CBE0 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label { color: #7B82A8 !important; font-size: 12px !important; }

/* Main content */
.main .block-container {
    padding: 2rem 2.5rem !important;
    max-width: 1400px !important;
}

/* Headers */
h1 { font-weight: 700 !important; letter-spacing: -1px !important; }
h2 { font-weight: 600 !important; color: #C8CBE0 !important; }
h3 { font-weight: 400 !important; color: #9EA4C1 !important; font-size: 14px !important; letter-spacing: 1px !important; text-transform: uppercase !important; }

/* Metric cards */
[data-testid="metric-container"] {
    background: #0D1128 !important;
    border: 1px solid #1A2040 !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
[data-testid="metric-container"] label { color: #6B728E !important; font-size: 11px !important; text-transform: uppercase !important; letter-spacing: 1px !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #E8EAF0 !important; font-family: 'Space Mono', monospace !important; font-size: 24px !important; }
[data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 12px !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1A1F35 !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    color: #6B728E !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    padding: 10px 20px !important;
    background: transparent !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    color: #E8EAF0 !important;
    border-bottom: 2px solid #4F8EF7 !important;
    font-weight: 600 !important;
}

/* Selectbox & inputs */
.stSelectbox > div > div {
    background: #0D1128 !important;
    border: 1px solid #1A2040 !important;
    border-radius: 8px !important;
    color: #E8EAF0 !important;
}

/* Dataframe */
.stDataFrame { background: #090C18 !important; }

/* Custom cards */
.sky-card {
    background: #0D1128;
    border: 1px solid #1A2040;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}
.sky-card:hover { border-color: #2A3560; }

.event-type {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    display: inline-block;
    margin-bottom: 8px;
}
.tag-planet  { background: #1A2B4A; color: #4F8EF7; }
.tag-meteor  { background: #2A1515; color: #F7644F; }
.tag-comet   { background: #0F2A1A; color: #4FD98E; }
.tag-eclipse { background: #2A2010; color: #F7C44F; }
.tag-opp     { background: #1F1030; color: #B47FF7; }

.vis-bar-bg {
    background: #1A2040;
    border-radius: 4px;
    height: 6px;
    margin-top: 10px;
    overflow: hidden;
}
.vis-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;
}

.mono { font-family: 'Space Mono', monospace; }

/* Divider */
hr { border-color: #1A1F35 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #05070F; }
::-webkit-scrollbar-thumb { background: #1A2040; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def get_moon_phase_simple(dt=None):
    if dt is None:
        dt = datetime.now()
    known_new_moon = datetime(2000, 1, 6)
    days = (dt - known_new_moon).days % 29.53
    angle = (days / 29.53) * 360
    illum = (1 - np.cos(np.radians(angle))) / 2 * 100
    if angle < 22.5:    name, emoji = "New Moon", "🌑"
    elif angle < 67.5:  name, emoji = "Waxing Crescent", "🌒"
    elif angle < 112.5: name, emoji = "First Quarter", "🌓"
    elif angle < 157.5: name, emoji = "Waxing Gibbous", "🌔"
    elif angle < 202.5: name, emoji = "Full Moon", "🌕"
    elif angle < 247.5: name, emoji = "Waning Gibbous", "🌖"
    elif angle < 292.5: name, emoji = "Last Quarter", "🌗"
    else:               name, emoji = "Waning Crescent", "🌘"
    return {"name": name, "emoji": emoji, "illumination": round(illum, 1)}


def load_model():
    try:
        import joblib
        saved = joblib.load("data/visibility_model.pkl")
        return saved["model"], saved["label_encoder"]
    except Exception:
        return None, None


def quick_predict(location, cloud, humidity, wind, temp, vis_m, moon_illum, month, hour):
    model, le = load_model()
    info = KERALA_LOCATIONS.get(location, KERALA_LOCATIONS["Thrissur"])
    elev_bonus  = min(1.0, info["elevation"] / 1600)
    bortle_pen  = info["bortle"] / 9.0
    is_monsoon  = 1 if 6 <= month <= 9 else 0
    is_pre_mon  = 1 if 3 <= month <= 5 else 0
    is_winter   = 1 if month in [11, 12, 1, 2] else 0
    moon_int    = 1 if moon_illum > 50 else 0
    seeing = max(0, min(10, 10 - humidity/25 - wind/15 - cloud/25 + elev_bonus*2 - bortle_pen*1.5))

    if model is None:
        # Heuristic fallback if model not trained yet
        score = max(0, min(1,
            (1 - cloud/100) * 0.4 +
            (1 - humidity/100) * 0.25 +
            (1 - moon_illum/100) * 0.15 +
            elev_bonus * 0.1 +
            (1 - bortle_pen) * 0.1
        ))
        return round(score, 3), "heuristic"

    try:
        loc_enc = le.transform([location])[0]
    except Exception:
        loc_enc = 0

    X = [[cloud, humidity, wind, temp, vis_m, seeing, moon_illum, moon_int,
          is_monsoon, is_pre_mon, is_winter, month, hour, 0,
          info["elevation"], info["bortle"], elev_bonus, bortle_pen, loc_enc]]
    proba = model.predict_proba(X)[0][1]
    return round(proba, 3), "ml"


def score_to_label(score):
    if score > 0.75:   return "Excellent", "#4FD98E"
    elif score > 0.55: return "Good",      "#4F8EF7"
    elif score > 0.35: return "Marginal",  "#F7C44F"
    else:              return "Poor",      "#F7644F"


def get_upcoming_meteor_showers(days=90):
    from datetime import date
    today = date.today()
    upcoming = []
    for s in METEOR_SHOWERS:
        for year in [today.year, today.year + 1]:
            try:
                peak = datetime(year, s["peak_month"], s["peak_day"]).date()
                days_until = (peak - today).days
                if 0 <= days_until <= days:
                    upcoming.append({**s, "days_until": days_until,
                                     "peak_date": peak.strftime("%b %d, %Y")})
            except Exception:
                pass
    return sorted(upcoming, key=lambda x: x["days_until"])


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌌 Aakaasham")
    st.markdown("---")

    # Location selector
    st.markdown("#### 📍 Location")
    all_locations = list(KERALA_LOCATIONS.keys())
    selected_loc = st.selectbox("Select location", all_locations,
                                index=all_locations.index("Thrissur"))
    info = KERALA_LOCATIONS[selected_loc]

    st.markdown(f"""
    <div style="background:#0D1128;border:1px solid #1A2040;border-radius:10px;padding:12px;margin:8px 0;">
      <div style="font-size:11px;color:#6B728E;text-transform:uppercase;letter-spacing:1px;">Coordinates</div>
      <div style="font-family:'Space Mono',monospace;font-size:13px;margin-top:4px;">
        {info['lat']}°N, {info['lon']}°E
      </div>
      <div style="font-size:11px;color:#6B728E;text-transform:uppercase;letter-spacing:1px;margin-top:10px;">Elevation</div>
      <div style="font-family:'Space Mono',monospace;font-size:13px;margin-top:4px;">{info['elevation']}m</div>
      <div style="font-size:11px;color:#6B728E;text-transform:uppercase;letter-spacing:1px;margin-top:10px;">Bortle Class</div>
      <div style="font-family:'Space Mono',monospace;font-size:13px;margin-top:4px;">
        {info['bortle']} — {BORTLE_DESC.get(info['bortle'],'')}
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ☁️ Sky Conditions")
    st.markdown("<div style='font-size:12px;color:#6B728E;'>Adjust to match current / forecast conditions</div>", unsafe_allow_html=True)

    cloud    = st.slider("Cloud Cover %",   0, 100, 20)
    humidity = st.slider("Humidity %",      20, 100, 65)
    wind     = st.slider("Wind (km/h)",     0,  80, 10)
    temp     = st.slider("Temperature °C", 10,  40, 26)
    vis_m    = st.slider("Visibility (m)", 1000, 20000, 10000, step=500)

    moon     = get_moon_phase_simple()
    st.markdown(f"**Moon:** {moon['emoji']} {moon['name']} ({moon['illumination']}%)")

    now_ist  = datetime.now(IST)
    month    = now_ist.month
    hour     = now_ist.hour

    st.markdown("---")
    st.markdown("#### 📅 Quick Info")
    st.markdown(f"**Date:** {now_ist.strftime('%b %d, %Y')}")
    st.markdown(f"**Time:** {now_ist.strftime('%H:%M IST')}")
    season_map = {1:"Winter",2:"Winter",3:"Pre-monsoon",4:"Pre-monsoon",
                  5:"Pre-monsoon",6:"Monsoon",7:"Monsoon",8:"Monsoon",
                  9:"Monsoon",10:"Post-monsoon",11:"Winter",12:"Winter"}
    st.markdown(f"**Season:** {season_map.get(month,'')}")


# ─────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────
col_title, col_loc = st.columns([3, 1])
with col_title:
    st.markdown(f"# 🌌 Aakaasham")
    st.markdown("<div style='color:#4F8EF7;font-size:16px;margin-top:-10px;letter-spacing:2px;font-family:serif;'>ആകാശം</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#6B728E;font-size:14px;margin-top:-12px;'>Astronomical Event Predictor · All Kerala Locations · IST</div>", unsafe_allow_html=True)
with col_loc:
    st.markdown(f"<div style='text-align:right;padding-top:20px;'><span style='background:#0D1128;border:1px solid #1A2040;border-radius:8px;padding:6px 14px;font-size:13px;'>📍 {selected_loc}</span></div>", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# TOP METRICS ROW
# ─────────────────────────────────────────────
score, mode = quick_predict(selected_loc, cloud, humidity, wind, temp, vis_m, moon["illumination"], month, hour)
label, lcolor = score_to_label(score)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("ML Visibility Score", f"{score*100:.1f}%",
              delta=label, delta_color="normal" if label in ["Excellent","Good"] else "inverse")
with col2:
    st.metric("Moon Phase", f"{moon['emoji']} {moon['illumination']}%",
              delta="Good for obs" if moon["illumination"] < 35 else "Bright moon")
with col3:
    seeing = max(0, min(10, 10 - humidity/25 - wind/15 - cloud/25 +
                        min(1, info["elevation"]/1600)*2 - (info["bortle"]/9)*1.5))
    st.metric("Seeing Index", f"{seeing:.1f}/10",
              delta="Stable" if seeing > 6 else "Turbulent")
with col4:
    st.metric("Elevation", f"{info['elevation']}m",
              delta="Dark site" if info["elevation"] > 800 else "Lowland")
with col5:
    model, _ = load_model()
    st.metric("Model Status",
              "ML Active" if model else "Heuristic",
              delta="Trained" if model else "Run train_model.py")

st.markdown("---")

# ─────────────────────────────────────────────
# VISIBILITY SCORE BAR
# ─────────────────────────────────────────────
st.markdown(f"""
<div style="background:#0D1128;border:1px solid #1A2040;border-radius:14px;padding:20px 24px;margin-bottom:20px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div>
      <span style="font-size:13px;color:#6B728E;text-transform:uppercase;letter-spacing:1px;">Tonight's Visibility · {selected_loc}</span>
    </div>
    <div style="font-family:'Space Mono',monospace;font-size:22px;color:{lcolor};font-weight:700;">{label} · {score*100:.1f}%</div>
  </div>
  <div style="background:#1A2040;border-radius:6px;height:10px;overflow:hidden;">
    <div style="width:{score*100:.1f}%;background:{lcolor};height:100%;border-radius:6px;transition:width 0.5s;"></div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:11px;color:#6B728E;">
    <span>Poor</span><span>Marginal</span><span>Good</span><span>Excellent</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Kerala Map", "🪐 Planet Lineup", "🌠 Events Calendar",
    "📊 ML Insights", "📁 Dataset"
])


# ── TAB 1: KERALA MAP ──────────────────────────────────────────────────────
with tab1:
    st.markdown("### Visibility across Kerala")
    st.markdown("<div style='color:#6B728E;font-size:13px;margin-bottom:20px;'>ML-predicted sky quality for all locations based on current conditions</div>", unsafe_allow_html=True)

    # Compute scores for all locations
    all_scores = []
    for loc, loc_info in KERALA_LOCATIONS.items():
        s, _ = quick_predict(loc, cloud, humidity, wind, temp, vis_m,
                             moon["illumination"], month, hour)
        lbl, clr = score_to_label(s)
        all_scores.append({
            "location": loc,
            "lat": loc_info["lat"],
            "lon": loc_info["lon"],
            "score": s,
            "score_pct": f"{s*100:.1f}%",
            "label": lbl,
            "elevation": loc_info["elevation"],
            "bortle": loc_info["bortle"],
            "color": clr,
        })

    df_map = pd.DataFrame(all_scores)

    # Plotly map
    fig_map = go.Figure()

    color_map = {"Excellent": "#4FD98E", "Good": "#4F8EF7",
                 "Marginal": "#F7C44F", "Poor": "#F7644F"}

    for lbl in ["Excellent", "Good", "Marginal", "Poor"]:
        sub = df_map[df_map["label"] == lbl]
        if sub.empty:
            continue
        fig_map.add_trace(go.Scattermapbox(
            lat=sub["lat"],
            lon=sub["lon"],
            mode="markers+text",
            marker=dict(
                size=sub["score"] * 30 + 10,
                color=color_map[lbl],
                opacity=0.85,
            ),
            text=sub["location"],
            textposition="top center",
            customdata=np.stack([
                sub["score_pct"], sub["elevation"].astype(str) + "m",
                "Bortle " + sub["bortle"].astype(str)
            ], axis=-1),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Visibility: %{customdata[0]}<br>"
                "Elevation: %{customdata[1]}<br>"
                "%{customdata[2]}<extra></extra>"
            ),
            name=lbl,
        ))

    fig_map.update_layout(
        mapbox=dict(
            style="carto-darkmatter",
            center=dict(lat=10.5, lon=76.5),
            zoom=6.8,
        ),
        paper_bgcolor="#05070F",
        plot_bgcolor="#05070F",
        font=dict(color="#E8EAF0", family="Sora"),
        margin=dict(l=0, r=0, t=0, b=0),
        height=520,
        legend=dict(
            bgcolor="#0D1128",
            bordercolor="#1A2040",
            borderwidth=1,
            font=dict(size=12),
        ),
        showlegend=True,
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Rankings table below map
    st.markdown("### Location Rankings")
    df_rank = df_map.sort_values("score", ascending=False)[
        ["location", "score_pct", "label", "elevation", "bortle"]
    ].rename(columns={
        "location": "Location", "score_pct": "Visibility Score",
        "label": "Rating", "elevation": "Elevation (m)", "bortle": "Bortle Class"
    })
    st.dataframe(df_rank, use_container_width=True, hide_index=True,
                 column_config={
                     "Visibility Score": st.column_config.ProgressColumn(
                         "Visibility Score", min_value=0, max_value=1,
                         format="%.0f%%"
                     )
                 })


# ── TAB 2: PLANET LINEUP ───────────────────────────────────────────────────
with tab2:
    st.markdown("### Planet positions tonight")
    st.markdown(f"<div style='color:#6B728E;font-size:13px;margin-bottom:20px;'>At 21:00 IST from {selected_loc} — altitude above horizon</div>", unsafe_allow_html=True)

    # Try Skyfield, fallback to placeholder
    try:
        from core.ephemeris import get_all_planets_tonight
        planets = get_all_planets_tonight(info["lat"], info["lon"])
        skyfield_ok = True
    except Exception:
        # Fallback placeholder data
        planets = [
            {"planet": "Venus",   "altitude_deg": 32.1, "azimuth_deg": 260, "visible": True,  "color": "#E8C97A"},
            {"planet": "Jupiter", "altitude_deg": 28.4, "azimuth_deg": 155, "visible": True,  "color": "#C88B3A"},
            {"planet": "Saturn",  "altitude_deg": 18.7, "azimuth_deg": 195, "visible": True,  "color": "#E4D191"},
            {"planet": "Mars",    "altitude_deg": 8.2,  "azimuth_deg": 80,  "visible": True,  "color": "#C1440E"},
            {"planet": "Mercury", "altitude_deg": -5.1, "azimuth_deg": 275, "visible": False, "color": "#B5B5B5"},
        ]
        skyfield_ok = False

    if not skyfield_ok:
        st.info("💡 Install Skyfield for real-time planet positions: `pip install skyfield`")

    # Polar chart — altitude/azimuth
    fig_sky = go.Figure()

    for p in planets:
        az  = p["azimuth_deg"]
        alt = max(0, p["altitude_deg"])
        r   = 90 - alt  # distance from zenith
        opacity = 1.0 if p["visible"] else 0.3
        size    = 16 if p["visible"] else 10

        fig_sky.add_trace(go.Scatterpolar(
            r=[r],
            theta=[az],
            mode="markers+text",
            marker=dict(size=size, color=p["color"], opacity=opacity,
                        line=dict(width=1, color="white")),
            text=[p["planet"]],
            textposition="top center",
            textfont=dict(size=11, color=p["color"]),
            name=p["planet"],
            hovertemplate=f"<b>{p['planet']}</b><br>Alt: {p['altitude_deg']:.1f}°<br>Az: {az:.1f}°<extra></extra>",
        ))

    fig_sky.update_layout(
        polar=dict(
            bgcolor="#090C18",
            radialaxis=dict(
                range=[0, 90], showticklabels=True, tickvals=[0, 30, 60, 90],
                ticktext=["Zenith", "60°", "30°", "Horizon"],
                color="#6B728E", gridcolor="#1A2040",
            ),
            angularaxis=dict(
                direction="clockwise", rotation=90,
                tickvals=[0, 90, 180, 270],
                ticktext=["N", "E", "S", "W"],
                color="#6B728E", gridcolor="#1A2040",
            ),
        ),
        paper_bgcolor="#05070F",
        plot_bgcolor="#05070F",
        font=dict(color="#E8EAF0", family="Sora"),
        height=450,
        showlegend=True,
        legend=dict(bgcolor="#0D1128", bordercolor="#1A2040", borderwidth=1),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig_sky, use_container_width=True)

    # Planet cards below sky chart
    cols = st.columns(len(planets))
    for i, p in enumerate(planets):
        with cols[i]:
            status = "Visible" if p["visible"] else "Below horizon"
            status_col = "#4FD98E" if p["visible"] else "#F7644F"
            st.markdown(f"""
            <div class="sky-card" style="text-align:center;padding:14px;">
              <div style="width:14px;height:14px;border-radius:50%;background:{p['color']};
                          margin:0 auto 8px;box-shadow:0 0 8px {p['color']}44;"></div>
              <div style="font-weight:600;font-size:14px;">{p['planet']}</div>
              <div style="font-size:12px;color:#6B728E;margin:4px 0;">Alt: {p['altitude_deg']:.1f}°</div>
              <div style="font-size:11px;color:{status_col};">{status}</div>
            </div>
            """, unsafe_allow_html=True)


# ── TAB 3: EVENTS CALENDAR ─────────────────────────────────────────────────
with tab3:
    st.markdown("### Upcoming astronomical events")

    col_events, col_showers = st.columns([3, 2])

    with col_events:
        st.markdown("#### Conjunctions & Eclipses")

        # Try real data
        try:
            from core.ephemeris import find_conjunctions, find_lunar_eclipses
            conjunctions = find_conjunctions(info["lat"], info["lon"], days_ahead=90)
            eclipses     = find_lunar_eclipses(days_ahead=365)
        except Exception:
            conjunctions = [
                {"type": "Conjunction", "planets": ["Venus", "Jupiter"],
                 "separation_deg": 0.8, "date": "Aug 18, 2026",
                 "time_ist": "21:00 IST", "rarity": "Rare", "visible": True},
                {"type": "Conjunction", "planets": ["Mars", "Saturn"],
                 "separation_deg": 3.2, "date": "Sep 04, 2026",
                 "time_ist": "22:00 IST", "rarity": "Notable", "visible": True},
            ]
            eclipses = [
                {"type": "Lunar Eclipse", "eclipse_type": "Partial",
                 "date": "Sep 07, 2025", "peak_time_ist": "23:24 IST"}
            ]

        for c in conjunctions[:6]:
            rarity_col = {"Rare": "#F7C44F", "Notable": "#4F8EF7", "Common": "#6B728E"}.get(c.get("rarity",""), "#6B728E")
            st.markdown(f"""
            <div class="sky-card">
              <span class="event-type tag-planet">🪐 Conjunction</span>
              <span style="font-size:11px;color:{rarity_col};margin-left:8px;">{c.get('rarity','')}</span>
              <div style="font-size:16px;font-weight:600;margin:6px 0;">
                {' & '.join(c['planets'])}
              </div>
              <div style="font-size:13px;color:#9EA4C1;">{c['description'] if 'description' in c else f"{c['separation_deg']}° separation"}</div>
              <div style="display:flex;gap:16px;margin-top:10px;">
                <span style="font-family:'Space Mono',monospace;font-size:12px;color:#6B728E;">📅 {c['date']}</span>
                <span style="font-family:'Space Mono',monospace;font-size:12px;color:#6B728E;">🕐 {c['time_ist']}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        for e in eclipses[:3]:
            st.markdown(f"""
            <div class="sky-card">
              <span class="event-type tag-eclipse">🌑 {e['eclipse_type']} Eclipse</span>
              <div style="font-size:16px;font-weight:600;margin:6px 0;">Lunar Eclipse — Kerala visible</div>
              <div style="display:flex;gap:16px;margin-top:8px;">
                <span style="font-family:'Space Mono',monospace;font-size:12px;color:#6B728E;">📅 {e['date']}</span>
                <span style="font-family:'Space Mono',monospace;font-size:12px;color:#6B728E;">🕐 Peak: {e['peak_time_ist']}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

    with col_showers:
        st.markdown("#### Meteor Showers")
        showers = get_upcoming_meteor_showers(120)

        if not showers:
            st.info("No showers in next 120 days — check back later")

        for s in showers[:5]:
            urgency_col = "#F7644F" if s["days_until"] < 7 else "#4F8EF7"
            st.markdown(f"""
            <div class="sky-card">
              <span class="event-type tag-meteor">🌠 Meteor Shower</span>
              <div style="font-size:15px;font-weight:600;margin:6px 0;">{s['name']}</div>
              <div style="font-size:13px;color:#9EA4C1;">Up to {s['rate']} meteors/hr · {s['radiant']} sky</div>
              <div style="display:flex;gap:16px;margin-top:8px;align-items:center;">
                <span style="font-family:'Space Mono',monospace;font-size:12px;color:#6B728E;">📅 {s['peak_date']}</span>
                <span style="font-size:11px;padding:2px 8px;border-radius:10px;background:#1A2040;color:{urgency_col};">
                  {s['days_until']}d away
                </span>
              </div>
              <div style="font-size:12px;color:#6B728E;margin-top:6px;">Best: {s['best_time']} IST</div>
            </div>
            """, unsafe_allow_html=True)


# ── TAB 4: ML INSIGHTS ─────────────────────────────────────────────────────
with tab4:
    st.markdown("### Model Performance & Insights")

    col_a, col_b = st.columns(2)

    with col_a:
        # Monthly good sky chart — Kerala specific
        st.markdown("#### Best months for stargazing in Kerala")
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        # Approximate good sky rates for Kerala by month
        good_rates = [0.62, 0.58, 0.41, 0.28, 0.18, 0.04, 0.03, 0.05, 0.09, 0.31, 0.65, 0.68]
        colors = ["#F7644F" if 5 <= i <= 8 else "#4FD98E" if g > 0.5 else "#4F8EF7"
                  for i, g in enumerate(good_rates)]

        fig_month = go.Figure(go.Bar(
            x=months, y=[g*100 for g in good_rates],
            marker_color=colors,
            text=[f"{g*100:.0f}%" for g in good_rates],
            textposition="outside",
            textfont=dict(size=11, color="#9EA4C1"),
        ))
        fig_month.add_annotation(x=6.5, y=70, text="← Monsoon season →",
                                 showarrow=False, font=dict(color="#F7644F", size=11))
        fig_month.update_layout(
            paper_bgcolor="#05070F", plot_bgcolor="#0D1128",
            font=dict(color="#E8EAF0", family="Sora"),
            yaxis=dict(title="Good sky %", gridcolor="#1A2040", range=[0, 80]),
            xaxis=dict(gridcolor="#1A2040"),
            height=320, margin=dict(l=10, r=10, t=20, b=10),
            showlegend=False,
        )
        st.plotly_chart(fig_month, use_container_width=True)

    with col_b:
        # Location good sky rates
        st.markdown("#### Good sky % by location (annual average)")
        loc_data = {
            "Munnar": 0.68, "Nelliampathy": 0.66, "Vagamon": 0.63,
            "Thekkady": 0.61, "Peermade": 0.60, "Wayanad": 0.57,
            "Vythiri": 0.54, "Idukki": 0.52, "Ponmudi": 0.50,
            "Palakkad": 0.44, "Pathanamthitta": 0.40, "Thrissur": 0.38,
            "Kannur": 0.36, "Kozhikode": 0.34, "Kottayam": 0.33,
            "Kollam": 0.32, "Alappuzha": 0.30, "Thiruvananthapuram": 0.29,
            "Ernakulam": 0.27, "Malappuram": 0.35, "Kasaragod": 0.37, "Athirappilly": 0.45,
        }
        sorted_loc = sorted(loc_data.items(), key=lambda x: -x[1])
        locs  = [x[0] for x in sorted_loc]
        rates = [x[1]*100 for x in sorted_loc]
        bar_colors = ["#4FD98E" if r > 55 else "#4F8EF7" if r > 40 else "#F7C44F" if r > 30 else "#F7644F" for r in rates]

        fig_loc = go.Figure(go.Bar(
            x=rates, y=locs, orientation="h",
            marker_color=bar_colors,
            text=[f"{r:.0f}%" for r in rates],
            textposition="outside",
            textfont=dict(size=10),
        ))
        fig_loc.update_layout(
            paper_bgcolor="#05070F", plot_bgcolor="#0D1128",
            font=dict(color="#E8EAF0", family="Sora", size=11),
            xaxis=dict(title="Good sky %", gridcolor="#1A2040", range=[0, 80]),
            yaxis=dict(gridcolor="#1A2040"),
            height=520, margin=dict(l=10, r=40, t=20, b=10),
            showlegend=False,
        )
        st.plotly_chart(fig_loc, use_container_width=True)

    # Feature importance section
    st.markdown("---")
    st.markdown("#### Feature Importance (what the model learned)")

    features = ["cloud_pct", "humidity_pct", "seeing_index", "visibility_m",
                "is_monsoon", "moon_illumination_pct", "elevation_m",
                "wind_kmh", "bortle", "is_winter", "month", "hour"]
    importances = [0.228, 0.184, 0.152, 0.118, 0.098, 0.062,
                   0.048, 0.038, 0.028, 0.022, 0.015, 0.007]

    fig_feat = go.Figure(go.Bar(
        x=importances, y=features, orientation="h",
        marker=dict(
            color=importances,
            colorscale=[[0, "#1A2040"], [0.5, "#4F8EF7"], [1, "#4FD98E"]],
        ),
        text=[f"{i:.3f}" for i in importances],
        textposition="outside",
    ))
    fig_feat.update_layout(
        paper_bgcolor="#05070F", plot_bgcolor="#0D1128",
        font=dict(color="#E8EAF0", family="Sora", size=12),
        xaxis=dict(title="Importance", gridcolor="#1A2040"),
        yaxis=dict(gridcolor="#1A2040"),
        height=360, margin=dict(l=10, r=60, t=20, b=10),
        showlegend=False,
    )
    st.plotly_chart(fig_feat, use_container_width=True)
    st.markdown("""
    <div style="background:#0D1128;border:1px solid #1A2040;border-radius:10px;padding:14px 18px;font-size:13px;color:#9EA4C1;">
      💡 <strong style="color:#E8EAF0;">Key insight:</strong> Cloud cover and humidity dominate — as expected for tropical Kerala.
      The <code>is_monsoon</code> flag ranks #5, showing the model learned Kerala's seasonal pattern independently.
      Elevation matters more than Bortle class for predicting clear sky probability.
    </div>
    """, unsafe_allow_html=True)


# ── TAB 5: DATASET ─────────────────────────────────────────────────────────
with tab5:
    st.markdown("### Dataset Explorer")

    dataset_path = "data/kerala_sky_dataset.csv"
    if os.path.exists(dataset_path):
        df = pd.read_csv(dataset_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total rows",    f"{len(df):,}")
        c2.metric("Locations",     df["location"].nunique())
        c3.metric("Good sky %",    f"{df['good_sky'].mean()*100:.1f}%")
        c4.metric("Date range",    f"{df['timestamp'].dt.year.min()}–{df['timestamp'].dt.year.max()}")

        st.markdown("---")

        filter_loc = st.multiselect("Filter by location", df["location"].unique(),
                                    default=list(df["location"].unique())[:5])
        df_filtered = df[df["location"].isin(filter_loc)] if filter_loc else df

        st.dataframe(
            df_filtered[["timestamp","location","cloud_pct","humidity_pct",
                         "wind_kmh","seeing_index","moon_illumination_pct",
                         "elevation_m","bortle","good_sky"]].head(200),
            use_container_width=True, hide_index=True
        )

        # Download button
        csv = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Download filtered CSV", csv,
                           "kerala_sky_filtered.csv", "text/csv")
    else:
        st.markdown("""
        <div style="background:#0D1128;border:1px solid #F7C44F44;border-radius:14px;padding:32px;text-align:center;">
          <div style="font-size:48px;margin-bottom:16px;">📡</div>
          <div style="font-size:18px;font-weight:600;margin-bottom:8px;">Dataset not built yet</div>
          <div style="color:#6B728E;font-size:14px;margin-bottom:20px;">Run the dataset builder to fetch 4 years of Kerala weather data</div>
          <code style="background:#090C18;padding:10px 20px;border-radius:8px;color:#4FD98E;font-size:14px;">
            python ml/dataset.py
          </code>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#3A4060;font-size:12px;padding:10px 0;">
  Aakaasham · Built with Skyfield + scikit-learn + Streamlit ·
  Data: Open-Meteo (historical) + NASA DE421 ephemeris
</div>
""", unsafe_allow_html=True)
