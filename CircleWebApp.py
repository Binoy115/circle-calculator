import streamlit as st
import pandas as pd
import math
from pathlib import Path

st.set_page_config(page_title="Metrolite Roofing - Circle Punch Calculator", layout="centered")

# --- Blue header ---
st.markdown("""
    <div style="background-color:#0b62a4;padding:18px;border-radius:8px">
        <h1 style="color:white;margin:0;">🏢 Metrolite Roofing Pvt Ltd</h1>
        <p style="color:#e8f2fb;margin:0;">Circle Punch Calculator</p>
    </div>
    """, unsafe_allow_html=True)

st.write("")

st.markdown("### Enter arch geometry (units: feet). Results shown in **millimetres (mm)**.")

# Try to load RadiustoPunch.xlsx from app folder first (works for Streamlit Cloud when file is in repo)
local_excel = Path("RadiustoPunch.xlsx")
uploaded_excel = None
df_excel = None
if local_excel.exists():
    try:
        df_excel = pd.read_excel(local_excel)
    except Exception as e:
        st.warning(f"Found local RadiustoPunch.xlsx but failed to read it: {e}")

# If local not available or failed, allow user upload
if df_excel is None:
    uploaded_excel = st.file_uploader("Upload RadiustoPunch.xlsx (optional if already in repo)", type=["xlsx"])
    if uploaded_excel is not None:
        try:
            df_excel = pd.read_excel(uploaded_excel)
        except Exception as e:
            st.error(f"Error reading uploaded Excel file: {e}")

# Input fields
col1, col2, col3 = st.columns(3)
length_ft = col1.number_input("Enter Arc Outer Length (feet)", min_value=0.0, step=0.1, format="%.3f")
width_ft  = col2.number_input("Enter Bottom Width / Chord (feet)", min_value=0.0, step=0.1, format="%.3f")
height_ft = col3.number_input("Enter Sagitta / Height (feet)", min_value=0.0, step=0.1, format="%.3f")

st.write("")

def radius_from_chord_sagitta(L, h):
    if L <= 0 or h <= 0:
        raise ValueError("L and h must be positive.")
    return (h*h + (L*L)/4.0) / (2.0*h)

def _bisection(f, low, high, args=(), tol=1e-12, maxiter=200):
    fl = f(low, *args); fh = f(high, *args)
    if fl == 0: return low
    if fh == 0: return high
    if fl * fh > 0:
        raise ValueError("Bisection failed: root not bracketed.")
    for _ in range(maxiter):
        mid = 0.5*(low + high)
        fm = f(mid, *args)
        if abs(fm) < tol:
            return mid
        if fl * fm < 0:
            high = mid; fh = fm
        else:
            low = mid; fl = fm
    return 0.5*(low+high)

def radius_from_chord_arc(L, a):
    if L <= 0 or a <= 0:
        raise ValueError("L and a must be positive.")
    if a + 1e-12 < L:
        raise ValueError("Arc length a should be >= chord length L.")
    def f(r, L, a): return 2.0*r*math.sin(a/(2.0*r)) - L
    low = max(L/2.0 + 1e-12, 1e-12)
    high = max(1e6, a*100.0, L*100.0)
    return _bisection(f, low, high, args=(L,a))

def radius_from_sagitta_arc(h, a):
    if h <= 0 or a <= 0:
        raise ValueError("h and a must be positive")
    def f(r, h, a): return r*(1.0 - math.cos(a/(2.0*r))) - h
    low = h + 1e-12
    high = max(1e6, a*100.0, h*100.0)
    return _bisection(f, low, high, args=(h,a))

def find_arc_length_from_sagitta_and_chord(sagitta, chord_length):
    radius = (sagitta**2 + (chord_length/2)**2) / (2*sagitta)
    central_angle_rad = 2*math.asin(chord_length/(2*radius))
    arc_length = radius * central_angle_rad
    return arc_length

def get_punch_distance_from_excel(radius, df):
    if 'Radius' not in df.columns or 'PunchDistance' not in df.columns:
        raise ValueError("Excel must contain 'Radius' and 'PunchDistance' columns")
    df = df.copy()
    df['Diff'] = (df['Radius'] - radius).abs()
    nearest = df.loc[df['Diff'].idxmin()]
    return float(nearest['PunchDistance']), float(nearest['Radius'])

def calculate_punches_and_distance(total_length_ft, punch_distance_excel):
    total_length_mm = total_length_ft * 304.8
    if total_length_mm <= 0 or punch_distance_excel is None or punch_distance_excel <= 0:
        return 0, 0.0
    num_punch = int(total_length_mm / punch_distance_excel) - 1
    if num_punch < 1:
        num_punch = 1
    punch_distance_mm = total_length_mm / (num_punch + 1)
    return num_punch, punch_distance_mm

# Button and calculation
if st.button("Calculate"):
    if df_excel is None:
        st.error("Please provide RadiustoPunch.xlsx (place it in repo or upload it).")
    else:
        try:
            radius_val = None
            if length_ft > 0 and height_ft > 0:
                radius_val = radius_from_sagitta_arc(height_ft, length_ft)
            elif width_ft > 0 and height_ft > 0:
                radius_val = radius_from_chord_sagitta(width_ft, height_ft)
                length_ft = find_arc_length_from_sagitta_and_chord(height_ft, width_ft)
            else:
                st.error("Please enter at least Length & Height or Width & Height.")
                st.stop()

            radius_val = round(radius_val, 3)
            punch_excel_value, matched_radius = get_punch_distance_from_excel(radius_val, df_excel)

            num_punch, punch_distance_mm = calculate_punches_and_distance(length_ft, punch_excel_value)

            st.success("Calculation complete")
            st.write(f"**Computed Radius:** {radius_val:.3f} ft (matched Excel radius: {matched_radius})")
            st.write(f"**Punch Distance (from Excel used as base):** {punch_excel_value:.2f} mm")
            st.write(f"**Adjusted Punch Distance (total_length / (num_punch+1)):** {punch_distance_mm:.2f} mm")
            st.write(f"**Number of punches:** {num_punch}")
            st.write(f"**Start distance:** {punch_distance_mm:.2f} mm")
            st.write('---')
            st.write("Note: If you want different behaviour, update RadiustoPunch.xlsx values or contact developer.")
        except Exception as e:
            st.error(f"Error during calculation: {e}")
