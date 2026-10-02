import streamlit as st
import math
import pandas as pd

st.set_page_config(page_title="Tactical Mortar FDC", layout="centered")
st.title("Arma Reforger Mortar FDC")

# 1. Setup Dropdowns
col_sys1, col_sys2 = st.columns(2)
with col_sys1:
    mortar_type = st.selectbox("Select Mortar System", ["US M252 (81mm)", "RU 2B14 (82mm)"])
with col_sys2:
    round_type = st.selectbox("Select Ammunition", ["High Explosive (HE)", "Smoke", "Illumination", "Training"])

st.subheader("Coordinates & Environment")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Point of Origin (Battery)**")
    origin_x = st.number_input("Origin X Grid", value=1000.0, step=10.0, key="ox")
    origin_y = st.number_input("Origin Y Grid", value=1000.0, step=10.0, key="oy")
    origin_elv = st.number_input("Origin Elevation (m ASL)", value=120.0, step=1.0, key="oe")

with col2:
    st.markdown("**Point of Impact (Target)**")
    target_x = st.number_input("Impact X Grid", value=1500.0, step=10.0, key="tx")
    target_y = st.number_input("Impact Y Grid", value=1500.0, step=10.0, key="ty")
    target_elv = st.number_input("Impact Elevation (m ASL)", value=145.0, step=1.0, key="te")

# --- Mathematical Basic Formulas ---
dx = target_x - origin_x
dy = target_y - origin_y
dz = target_elv - origin_elv

distance = math.sqrt(dx**2 + dy**2)
angle_rad = math.atan2(dx, dy)
degrees = math.degrees(angle_rad) % 360.0
mils = (degrees * 6400.0) / 360.0

st.subheader("Firing Solutions")
out1, out2, out3 = st.columns(3)
out1.metric("Distance", f"{distance:.1f} m")
out2.metric("Direction (Degrees)", f"{degrees:.1f}°")
out3.metric("Direction (NATO Mils)", f"{int(round(mils))} mils")

# --- Fixed Ballistics Configuration ---
# Min and Max range profiles mapped to arrays for charges 0 to 4
ballistics_presets = {
    "High Explosive (HE)": {
        "min": [50, 150, 250, 330, 410],
        "max": [540, 890, 1400, 1870, 2900],
        "time_modifier": 1.0
    },
    "Smoke": {
        "min": [50, 150, 250, 330, 410],
        "max": [540, 890, 1400, 1870, 2900],
        "time_modifier": 1.05
    },
    "Illumination": {
        "min": [50, 150, 250, 330, 410],
        "max": [540, 890, 1400, 1870, 2900],
        "time_modifier": 0.95
    },
    "Training": {
        "min": [50, 150, 250, 330, 410],
        "max": [540, 890, 1400, 1870, 2900],
        "time_modifier": 1.0
    }
}

active_profile = ballistics_presets[round_type]
min_ranges = active_profile["min"]
max_ranges = active_profile["max"]

elevations = []
flight_times = []

# Populate Columns for 0-4 Rings
for i in range(5):
    if min_ranges[i] <= distance <= max_ranges[i]:
        # Calculated elevation arc lookup
        simulated_elev = int(1550 - ((distance - min_ranges[i]) / (max_ranges[i] - min_ranges[i])) * 450)
        base_time = 12.0 + (i * 4.5) + (distance / 220)
        simulated_time = f"{round(base_time * active_profile['time_modifier'], 1)}s"
        
        elevations.append(str(simulated_elev))
        flight_times.append(simulated_time)
    else:
        # Plain text marker used internally, swapped to a red zero on screen
        elevations.append("FAIL_MARKER")
        flight_times.append("FAIL_MARKER")

df = pd.DataFrame(
    [elevations, flight_times],
    index=["Gun Elevation (mils)", "Flight Time"],
    columns=["0 rings", "1 ring", "2 rings", "3 rings", "4 rings"]
)

def color_red_zeros(val):
    if val == "FAIL_MARKER":
        return '<span style="color:red; font-weight:bold;">0</span>'
    return val

df_html = df.map(color_red_zeros).to_html(escape=False)

st.subheader(f"Charge Card Options ({round_type})")
st.markdown(df_html, unsafe_html=True)
