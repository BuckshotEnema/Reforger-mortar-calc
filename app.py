import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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
    origin_x = st.number_input("Origin X Grid", value=1000, step=1, key="ox")
    origin_y = st.number_input("Origin Y Grid", value=1000, step=1, key="oy")
    origin_elv = st.number_input("Origin Elevation (m ASL)", value=120, step=1, key="oe")

with col2:
    st.markdown("**Point of Impact (Target)**")
    target_x = st.number_input("Impact X Grid", value=1500, step=1, key="tx")
    target_y = st.number_input("Impact Y Grid", value=1500, step=1, key="ty")
    target_elv = st.number_input("Impact Elevation (m ASL)", value=145, step=1, key="te")

# --- Mathematical Basic Formulas ---
dx = float(target_x - origin_x)
dy = float(target_y - origin_y)
dz = float(target_elv - origin_elv)

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
if mortar_type == "US M252 (81mm)":
    he_min = [80, 200, 400, 700, 1100]
    he_max = [450, 900, 1500, 2200, 2900]
else:
    he_min = [50, 150, 350, 600, 950]
    he_max = [400, 800, 1300, 1800, 2300]

if round_type == "High Explosive (HE)" or round_type == "Training":
    min_ranges = he_min
    max_ranges = he_max
    t_mod = 1.0
elif round_type == "Smoke":
    min_ranges = [m + 20 for m in he_min]
    max_ranges = [int(m * 0.95) for m in he_max]
    t_mod = 1.05
else:
    min_ranges = [m + 40 for m in he_min]
    max_ranges = [int(m * 0.92) for m in he_max]
    t_mod = 0.95

elevations = []
flight_times = []
valid_rings = []

# Populate Columns for 0-4 Rings
for i in range(5):
    if min_ranges[i] <= distance <= max_ranges[i]:
        simulated_elev = int(1540 - ((distance - min_ranges[i]) / (max_ranges[i] - min_ranges[i])) * 400)
        base_time = 12.0 + (i * 3.5) + (distance / 250)
        simulated_time = f"{round(base_time * t_mod, 1)}s"
        
        elevations.append(str(simulated_elev))
        flight_times.append(simulated_time)
        valid_rings.append((i, simulated_elev))
    else:
        elevations.append("0")
        flight_times.append("0")

df = pd.DataFrame(
    [elevations, flight_times],
    index=["Gun Elevation (mils)", "Flight Time"],
    columns=["0 rings", "1 ring", "2 rings", "3 rings", "4 rings"]
)

st.subheader(f"Charge Card Options ({round_type})")
st.dataframe(df, use_container_width=True).style.map(
    lambda val: "color: red; font-weight: bold;" if val == "0" else ""
)

# --- Real-Time Visual Trajectory Chart ---
st.subheader("Side-View Ballistics Preview")

if distance > 0:
    fig, ax = plt.subplots(figsize=(6, 3))
    x_vals = np.linspace(0, distance, 100)
    
    ax.scatter(distance, dz, color="red", zorder=5, label="Target Point")
    ax.scatter(0, 0, color="green", zorder=5, label="Mortar Battery")
    
    has_valid_curve = False
    for ring_idx, elev_mils in valid_rings:
        peak_height = (distance / 2) * (1.1 + (ring_idx * 0.3)) + max(0.0, dz)
        y_vals = 4 * peak_height * (x_vals / distance) * (1 - (x_vals / distance)) + (x_vals / distance) * dz
        
        ax.plot(x_vals, y_vals, linestyle="--", alpha=0.8, label=f"Ring {ring_idx}")
        has_valid_curve = True
        
    ax.set_xlabel("Ground Distance (meters)", fontsize=8)
    ax.set_ylabel("Relative Alt (meters)", fontsize=8)
    ax.tick_params(axis='both', labelsize=7)
    ax.grid(True, linestyle=":", alpha=0.6)
    
    if has_valid_curve:
        ax.legend(loc="upper right", fontsize=7)
    else:
        ax.text(0.5, 0.5, "Out of Range / No Solution", color="red", 
                ha="center", va="center", transform=ax.transAxes, weight="bold")
        
    plt.tight_layout()
    st.pyplot(fig)
