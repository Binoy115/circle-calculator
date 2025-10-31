# Circle Calculator (Streamlit) - Metrolite Roofing

This package contains a Streamlit web app that calculates radius, punch distance and number of punches for arch segments.
The app displays results in **millimetres (mm)** and uses `RadiustoPunch.xlsx` to derive base punch distances by radius.

---
## Files included
- `CircleWebApp.py`  : Streamlit application
- `RadiustoPunch.xlsx` : Example Excel mapping (Radius -> PunchDistance)
- `README.md` : This guide

---
## How to deploy to Streamlit Cloud (one-time setup)
1. Create a GitHub repository (or use an existing one).
2. Upload the entire folder `circle-calculator` contents to the repository (use Add file → Upload files).
3. Go to https://share.streamlit.io and click **New app**.
4. Connect your GitHub account if prompted, choose the repository and set **Main file path** to `CircleWebApp.py`.
5. Click **Deploy**. Streamlit will build and provide you with a public URL (e.g. https://yourname-appname.streamlit.app).
6. Open that URL on any mobile or PC — the app runs online and is available 24/7.

---
## Running locally (for testing)
1. Make sure Python is installed.
2. Install dependencies in your environment:
   ```bash
   pip install streamlit pandas openpyxl pillow
   ```
3. Run locally:
   ```bash
   streamlit run CircleWebApp.py
   ```
4. Open `http://localhost:8501` in your browser.

---
## Notes
- The app tries to read `RadiustoPunch.xlsx` from the app folder (this works after upload to GitHub). If not found, use the upload control in the app UI.
- The app expects the Excel file to have columns: `Radius` and `PunchDistance`.
- Results are given in millimetres (mm) for fabrication use.

If you want, I can also directly deploy to Streamlit Cloud for you (you will need to authorize access).
