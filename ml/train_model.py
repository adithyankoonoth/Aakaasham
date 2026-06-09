# ml/train_model.py — Train visibility classifier for Kerala sky conditions
# RandomForest trained on 4 years of Kerala weather data

import pandas as pd
import numpy as np
import joblib
import os
import sys
import warnings
warnings.filterwarnings("ignore")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import KERALA_LOCATIONS

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, roc_auc_score, roc_curve
)
from sklearn.preprocessing import LabelEncoder

FEATURES = [
    "cloud_pct",
    "humidity_pct",
    "wind_kmh",
    "temp_c",
    "visibility_m",
    "seeing_index",
    "moon_illumination_pct",
    "moon_interference",
    "is_monsoon",
    "is_pre_monsoon",
    "is_winter",
    "month",
    "hour",
    "is_raining",
    "elevation_m",
    "bortle",
    "elevation_bonus",
    "bortle_penalty",
    "location_encoded",
]

TARGET = "good_sky"
MODEL_PATH = "data/visibility_model.pkl"


def load_and_prepare(path: str = "data/kerala_sky_dataset.csv"):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found at {path}\n"
            "Run: python ml/dataset.py  first!"
        )
    df = pd.read_csv(path)
    le = LabelEncoder()
    df["location_encoded"] = le.fit_transform(df["location"])
    df.dropna(subset=FEATURES + [TARGET], inplace=True)

    X = df[FEATURES]
    y = df[TARGET]
    print(f"Dataset  : {len(df):,} rows · {df['location'].nunique()} locations")
    print(f"Balance  : {y.mean()*100:.1f}% good sky nights")
    return X, y, df, le


def train(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=15,
        min_samples_split=8,
        min_samples_leaf=4,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    print("\nRunning 5-fold cross-validation...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="roc_auc")
    print(f"CV ROC-AUC : {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

    print("Training final model...")
    model.fit(X_train, y_train)

    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    print(f"\nTest Accuracy : {accuracy_score(y_test, y_pred):.3f}")
    print(f"Test ROC-AUC  : {roc_auc_score(y_test, y_proba):.3f}")
    print(f"\n{classification_report(y_test, y_pred, target_names=['Bad Sky', 'Good Sky'])}")
    return model, X_test, y_test, y_pred, y_proba


def feature_importance_report(model):
    print("\nFeature Importances:")
    importances = sorted(
        zip(FEATURES, model.feature_importances_),
        key=lambda x: -x[1]
    )
    for feat, imp in importances:
        bar = "▓" * int(imp * 200)
        print(f"  {feat:<25} {bar} {imp:.4f}")
    return importances


def location_report(model, df):
    """Per-location accuracy — the star of the show."""
    df = df.copy()
    df["prediction"] = model.predict(df[FEATURES])
    df["correct"]    = (df["prediction"] == df[TARGET]).astype(int)

    report = df.groupby("location").agg(
        accuracy      = ("correct",   "mean"),
        good_sky_rate = ("good_sky",  "mean"),
        total         = ("correct",   "count"),
    ).sort_values("good_sky_rate", ascending=False).round(3)

    print("\nPer-location report (sorted by good sky %):")
    print(f"  {'Location':<22} {'Good Sky':>9}  {'Accuracy':>9}  {'Nights':>7}")
    print("  " + "-" * 52)
    for loc, row in report.iterrows():
        bar = "▓" * int(row.good_sky_rate * 20)
        print(f"  {loc:<22} {row.good_sky_rate*100:>8.1f}%  "
              f"{row.accuracy*100:>8.1f}%  {int(row.total):>7,}")
    return report


def monthly_report(model, df):
    """Which months are best for Kerala astronomy."""
    df = df.copy()
    df["prediction"] = model.predict(df[FEATURES])
    df["correct"]    = (df["prediction"] == df[TARGET]).astype(int)

    months = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
              7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

    report = df.groupby("month").agg(
        good_sky_rate = ("good_sky", "mean"),
        accuracy      = ("correct",  "mean"),
    ).round(3)
    report.index = report.index.map(months)

    print("\nMonthly breakdown (Kerala):")
    for month, row in report.iterrows():
        bar = "█" * int(row.good_sky_rate * 30)
        tag = " ← monsoon" if month in ["Jun","Jul","Aug","Sep"] else \
              " ← best!"   if month in ["Nov","Dec","Jan"] else ""
        print(f"  {month}  {bar:<30}  {row.good_sky_rate*100:.1f}%{tag}")
    return report


def save_model(model, le):
    os.makedirs("data", exist_ok=True)
    joblib.dump({"model": model, "features": FEATURES, "label_encoder": le}, MODEL_PATH)
    print(f"\nModel saved → {MODEL_PATH}")


def predict_visibility(location: str, weather: dict) -> dict:
    """
    Predict sky visibility for any Kerala location.

    Args:
        location: Name matching config.KERALA_LOCATIONS (e.g. "Munnar")
        weather: dict with keys:
            cloud_pct, humidity_pct, wind_kmh, temp_c,
            visibility_m, moon_illumination_pct,
            month, hour, precip_mm (optional)

    Returns:
        dict with visibility_score, label, seeing_index
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model not trained yet. Run: python ml/train_model.py")

    saved = joblib.load(MODEL_PATH)
    model = saved["model"]
    le    = saved["label_encoder"]
    info  = KERALA_LOCATIONS.get(location, KERALA_LOCATIONS["Thrissur"])

    elev_bonus  = min(1.0, info["elevation"] / 1600)
    bortle_pen  = info["bortle"] / 9.0
    is_monsoon  = 1 if 6 <= weather["month"] <= 9 else 0
    is_pre_mon  = 1 if 3 <= weather["month"] <= 5 else 0
    is_winter   = 1 if weather["month"] in [11, 12, 1, 2] else 0
    is_raining  = 1 if weather.get("precip_mm", 0) > 0.1 else 0
    moon_int    = 1 if weather["moon_illumination_pct"] > 50 else 0

    seeing = (
        10
        - (weather["humidity_pct"] / 25)
        - (weather["wind_kmh"] / 15)
        - (weather["cloud_pct"] / 25)
        + (elev_bonus * 2)
        - (bortle_pen * 1.5)
    )
    seeing = max(0.0, min(10.0, seeing))

    try:
        loc_enc = le.transform([location])[0]
    except Exception:
        loc_enc = 0

    X = [[
        weather["cloud_pct"],
        weather["humidity_pct"],
        weather["wind_kmh"],
        weather["temp_c"],
        weather["visibility_m"],
        seeing,
        weather["moon_illumination_pct"],
        moon_int,
        is_monsoon,
        is_pre_mon,
        is_winter,
        weather["month"],
        weather["hour"],
        is_raining,
        info["elevation"],
        info["bortle"],
        elev_bonus,
        bortle_pen,
        loc_enc,
    ]]

    proba = model.predict_proba(X)[0][1]

    if proba > 0.75:   label, color = "Excellent", "#1D9E75"
    elif proba > 0.55: label, color = "Good",      "#378ADD"
    elif proba > 0.35: label, color = "Marginal",  "#BA7517"
    else:              label, color = "Poor",       "#E24B4A"

    return {
        "location":         location,
        "visibility_score": round(proba, 3),
        "visibility_pct":   f"{proba*100:.1f}%",
        "label":            label,
        "label_color":      color,
        "seeing_index":     round(seeing, 2),
        "bortle_class":     info["bortle"],
        "elevation_m":      info["elevation"],
    }


def predict_all_locations(weather: dict) -> list:
    """Predict visibility for all Kerala locations for given weather."""
    results = []
    for loc in KERALA_LOCATIONS:
        try:
            r = predict_visibility(loc, weather)
            results.append(r)
        except Exception:
            pass
    return sorted(results, key=lambda x: -x["visibility_score"])


if __name__ == "__main__":
    X, y, df, le = load_and_prepare()
    model, X_test, y_test, y_pred, y_proba = train(X, y)
    feature_importance_report(model)
    location_report(model, df)
    monthly_report(model, df)
    save_model(model, le)

    print("\n" + "="*50)
    print("Sample predictions — Nov 21, 22:00 IST, clear night")
    sample = {
        "cloud_pct": 8, "humidity_pct": 55, "wind_kmh": 6,
        "temp_c": 22, "visibility_m": 14000,
        "moon_illumination_pct": 10, "month": 11, "hour": 22, "precip_mm": 0
    }
    results = predict_all_locations(sample)
    print(f"\n  {'Location':<22} {'Score':>7}  {'Label':<10}  {'Bortle':>6}  {'Elev':>6}")
    print("  " + "-"*58)
    for r in results:
        print(f"  {r['location']:<22} {r['visibility_pct']:>7}  "
              f"{r['label']:<10}  {r['bortle_class']:>6}  {r['elevation_m']:>5}m")
