import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Circle Punch Calculator", layout="centered")

st.title("🔵 Circle Punch Calculator (Web Version)")
st.markdown("### Auto-calculates punch distance and count from arch dimensions")

# ---- File upload ----
uploaded_excel = st.file_uploader("Upload RadiustoPunch.xlsx", type=["xlsx"])

# ---- Input fields ----
col1, col2, col3 = st.columns(3)
length_ft = col1.number_input("Enter Arc Length (feet)", min_value=0.0, step=0.1)
width_ft = col2.number_input("Enter Bottom Width (feet)", min_value=0.0, step=0.1)
height_ft = col3.number_input("Enter Height (feet)", min_value=0.0, step=0.1)

# ---- Functions ----
def radius_from_sagitta_arc(h, a):
    def f(r): return r * (1 - math.cos(a / (2 * r))) - h
    low, high = h + 1e-12, max(1e6, a * 100, h * 100)
    for _ in range(200):
        mid = 0.5 * (low + high)
        fm = f(mid)
        if abs(fm) < 1e-12:
            return mid
        if f(low) * fm < 0:
            high = mid
        else:
            low = mid
    return mid

def get_punch_distance(radius, df):
    df["Diff"] = abs(df["Radius"] - radius)
    return df.loc[df["Diff"].idxmin(), "PunchDistance"]

def calculate_punches(total_length_ft, punch_dist_excel):
    total_length_mm = total_length_ft * 304.8
    num_punch = int(total_length_mm / punch_dist_excel) - 1
    num_punch = max(num_punch, 1)
    punch_dist = total_length_mm / (num_punch + 1)
    return num_punch, punch_dist

# ---- Main logic ----
if st.button("Calculate"):
    if uploaded_excel is None:
        st.error("Please upload RadiustoPunch.xlsx file first.")
    elif (length_ft <= 0 or height_ft <= 0) and (width_ft <= 0 or height_ft <= 0):
        st.error("Please enter at least Length & Height or Width & Height.")
    else:
        df = pd.read_excel(uploaded_excel)
        if "Radius" not in df.columns or "PunchDistance" not in df.columns:
            st.error("Excel must have 'Radius' and 'PunchDistance' columns.")
        else:
            radius_ft = radius_from_sagitta_arc(height_ft, length_ft)
            punch_excel = get_punch_distance(radius_ft, df)
            num_punch, punch_distance = calculate_punches(length_ft, punch_excel)

            st.success("✅ Calculation complete:")
            st.write(f"**Radius:** {radius_ft:.2f} ft")
            st.write(f"**Punch Distance:** {punch_distance:.2f} mm")
            st.write(f"**Number of Punches:** {num_punch}")
            st.write(f"**Starting Length:** {punch_distance:.2f} mm")
