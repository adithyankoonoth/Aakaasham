#!/usr/bin/env python3
# run_pipeline.py — Run the complete Aakaasham pipeline
# Usage: python run_pipeline.py

import subprocess
import sys
import os
import time

def run(cmd, label):
    print(f"\n{'='*55}")
    print(f"  {label}")
    print(f"{'='*55}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"\n❌ Failed: {label}")
        sys.exit(1)
    print(f"✓ Done: {label}")

def main():
    print("""
╔══════════════════════════════════════════════════╗
║      Aakaasham — Full Pipeline          ║
║      ആകാശം · Astronomy + ML + Streamlit                  ║
╚══════════════════════════════════════════════════╝
    """)

    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        sys.exit(1)

    # Step 1: Install dependencies
    run(f"{sys.executable} -m pip install -r requirements.txt -q",
        "Step 1/3 — Installing dependencies")

    # Step 2: Build dataset
    if os.path.exists("data/kerala_sky_dataset.csv"):
        print("\n✓ Dataset already exists — skipping download")
        print("  (delete data/kerala_sky_dataset.csv to re-fetch)")
    else:
        run(f"{sys.executable} ml/dataset.py",
            "Step 2/3 — Building dataset (4 years × 22 locations)")

    # Step 3: Train model
    if os.path.exists("data/visibility_model.pkl"):
        print("\n✓ Model already trained — skipping")
        print("  (delete data/visibility_model.pkl to retrain)")
    else:
        run(f"{sys.executable} ml/train_model.py",
            "Step 3/3 — Training ML visibility model")

    print(f"""
{'='*55}
  ✅ Pipeline complete! Launching app...
{'='*55}

  Open in browser: http://localhost:8501
  Press Ctrl+C to stop
""")

    time.sleep(1)
    os.system(f"{sys.executable} -m streamlit run app.py")


if __name__ == "__main__":
    main()
