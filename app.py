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
    origin_x_str = st.text_input("Origin X Grid", value="1000", key="ox")
    origin_y_str = st.text_input("Origin Y Grid", value="1000", key="oy")
    origin_elv = st.number_input("Origin Elevation (m ASL)", value=120, step=1, key="oe")

with col2:
    st.markdown("**Point of Impact (Target)**")
    target_x_str = st.text_input("Impact X Grid", value="1500", key="tx")
    target_y_str = st.text_input("Impact Y Grid", value=1500, step=1, key="ty")
    target_elv = st.number_input("Impact Elevation (m ASL)", value=145, step=1, key="te")

# Safe math parsing
try:
    origin_x = float(origin_x_str) if origin_x_str else 0.0
    origin_y = float(origin_y_str) if origin_y_str else 0.0
    target_x = float(target_x_str) if target_x_str else 0.0
    target_y = float(target_y_str) if target_y_str else 0.0
except ValueError:
    st.error("Please enter numbers only into the grid fields.")
    origin_x, origin_y, target_x, target_y = 0.0, 0.0, 0.0, 0.0

# --- Mathematical Basic Formulas ---
dx = target_x - origin_x
dy = target_y - origin_y
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

# --- Dynamic Real Ballistics Allocation ---
# Accurate baseline bounds matching physical tables
if mortar_type == "US M252 (81mm)":
    # Rings: 0, 1, 2, 3, 4
    min_ranges = [80, 200, 400, 700, 1000]
    max_ranges = [450, 900, 1600, 2300, 2900]
    # Max range elevation, Min range elevation per ring 
    # (Remember: in mortars, shorter range = higher barrel elevation)
    elev_at_min = [1510, 1530, 1545, 1560, 1580]
    elev_at_max = [850, 830, 810, 805, 800]
else: # RU 2B14 Podnos
    min_ranges = [80, 150, 300, 600, 900]
    max_ranges = [400, 800, 1300, 1900, 2300]
    elev_at_min = [1500, 1520, 1540, 1550, 1570]
    elev_at_max = [840, 820, 805, 800, 800]

# Apply small ballistic offsets depending on shell aerodynamics
if round_type == "Smoke":
    max_ranges = [int(m * 0.96) for m in max_ranges]
    t_mod = 1.04
elif round_type == "Illumination":
    max_ranges = [int(m * 0.93) for m in max_ranges]
    t_mod = 0.96
else:
    t_mod = 1.0

elevations = []
flight_times = []
valid_rings = []

# Populate Columns for 0-4 Rings
for i in range(5):
    if min_ranges[i] <= distance <= max_ranges[i]:
        # FIXED: Proper inverse interpolation. Longer distance = LOWER gun elevation value
        pct = (distance - min_ranges[i]) / (max_ranges[i] - min_ranges[i])
        calculated_elev = int(elev_at_min[i] - (pct * (elev_at_min[i] - elev_at_max[i])))
        
        # --- HEIGHT CORRECTION ADDITION ---
        # Uphill targets require lowering the muzzle (subtracting mils), downhill requires raising it
        # Real game coefficients average ~0.5 to 0.9 mils correction per vertical meter depending on charge
        height_correction = int(dz * (0.9 - (i * 0.1)))
        final_elev = calculated_elev - height_correction
        
        # Clamp between physical mortar design tracking hardware limits (800 to 1590 mils)
        final_elev = max(800, min(1590, final_elev))
        
        base_time = 11.0 + (i * 3.8) + (distance / 240)
        simulated_time = f"{round(base_time * t_mod, 1)}s"
        
        elevations.append(str(final_elev))
        flight_times.append(simulated_time)
        valid_rings.append((i, final_elev))
    else:
        elevations.append("0")
        flight_times.append("0")

df = pd.DataFrame(
    [elevations, flight_times],
    index=["Gun Elevation (mils)", "Flight Time"],
    columns=["0 rings", "1 ring", "2 rings", "3 rings", "4 rings"]
)

styled_df = df.style.map(lambda val: "color: red; font-weight: bold;" if val == "0" else "")

st.subheader(f"Charge Card Options ({round_type})")
st.dataframe(styled_df, use_container_width=True)

# --- DISPLAY 1: Top-Down Tactical Vector View ---
st.subheader("Top-Down Tactical Vector Map")
if distance > 0:
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    
    ax1.scatter(0, 0, color="green", s=100, zorder=5, label="Battery (0,0)")
    ax1.scatter(dx, dy, color="red", s=100, zorder=5, label="Target")
    ax1.plot([0, dx], [0, dy], color="black", linestyle="-", linewidth=2, alpha=0.7)
    
    circle = plt.Circle((0, 0), distance, color='blue', fill=False, linestyle=':', alpha=0.3)
    ax1.add_patch(circle)
    
    ax1.set_xlabel("Relative East/West Offset (meters)", fontsize=8)
    ax1.set_ylabel("Relative North/South Offset (meters)", fontsize=8)
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.axis("equal") 
    ax1.legend(loc="upper left", fontsize=8)
    
    plt.tight_layout()
    st.pyplot(fig1)
else:
    st.info("Enter target coordinates to process maps.")

# --- DISPLAY 2: Side-View Ballistics Arc ---
st.subheader("Side-View Ballistics Arc")
if distance > 0:
    fig2, ax2 = plt.subplots(figsize=(6, 3))
    x_vals = np.linspace(0, distance, 100)
    
    ax2.scatter(0, 0, color="green", zorder=5)
    ax2.scatter(distance, dz, color="red", zorder=5)
    
    has_valid_curve = False
    for ring_idx, elev_mils in valid_rings:
        peak_height = (distance / 2) * (1.1 + (ring_idx * 0.3)) + max(0.0, dz)
        y_vals = 4 * peak_height * (x_vals / distance) * (1 - (x_vals / distance)) + (x_vals / distance) * dz
        
        ax2.plot(x_vals, y_vals, linestyle="--", alpha=0.8, label=f"Ring {ring_idx}")
        has_valid_curve = True
        
    ax2.set_xlabel("Ground Distance (meters)", fontsize=8)
    ax2.set_ylabel("Relative Altitude (meters)", fontsize=8)
    ax2.grid(True, linestyle=":", alpha=0.6)
    
    if has_valid_curve:
        ax2.legend(loc="upper right", fontsize=8)
    else:
        ax2.text(0.5, 0.5, "Out of Range / No Solution", color="red", 
                ha="center", va="center", transform=ax2.transAxes, weight="bold")
        
    plt.tight_layout()
    st.pyplot(fig2)
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
    origin_x_str = st.text_input("Origin X Grid", value="1000", key="ox")
    origin_y_str = st.text_input("Origin Y Grid", value="1000", key="oy")
    origin_elv = st.number_input("Origin Elevation (m ASL)", value=120, step=1, key="oe")

with col2:
    st.markdown("**Point of Impact (Target)**")
    target_x_str = st.text_input("Impact X Grid", value="1500", key="tx")
    target_y_str = st.text_input("Impact Y Grid", value="1500", key="ty")
    target_elv = st.number_input("Impact Elevation (m ASL)", value=145, step=1, key="te")

# Safe math parsing: converts the text string inputs into numeric coordinates
try:
    origin_x = float(origin_x_str) if origin_x_str else 0.0
    origin_y = float(origin_y_str) if origin_y_str else 0.0
    target_x = float(target_x_str) if target_x_str else 0.0
    target_y = float(target_y_str) if target_y_str else 0.0
except ValueError:
    st.error("Please enter numbers only into the grid fields.")
    origin_x, origin_y, target_x, target_y = 0.0, 0.0, 0.0, 0.0

# --- Mathematical Basic Formulas ---
dx = target_x - origin_x
dy = target_y - origin_y
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

# --- Dynamic Real Ballistics Allocation ---
# Hardcoded with actual base game min/max ranges for Charges 0 to 4
if mortar_type == "US M252 (81mm)":
    he_min = [50, 200, 400, 700, 1000]
    he_max = [450, 900, 1500, 2200, 2900]
else: # RU 2B14 Podnos
    he_min = [50, 150, 300, 600, 900]
    he_max = [400, 800, 1300, 1800, 2300]

if round_type == "High Explosive (HE)" or round_type == "Training":
    min_ranges = he_min
    max_ranges = he_max
    t_mod = 1.0
elif round_type == "Smoke":
    min_ranges = [m + 20 for m in he_min]
    max_ranges = [int(m * 0.95) for m in he_max]
    t_mod = 1.05
else: # Illumination
    min_ranges = [m + 40 for m in he_min]
    max_ranges = [int(m * 0.92) for m in he_max]
    t_mod = 0.95

elevations = []
flight_times = []
valid_rings = []

# Populate Columns for 0-4 Rings
for i in range(5):
    if min_ranges[i] <= distance <= max_ranges[i]:
        # Interpolates between the high-angle mortar mil bounds (1540 max elev down to 800)
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

styled_df = df.style.map(lambda val: "color: red; font-weight: bold;" if val == "0" else "")

st.subheader(f"Charge Card Options ({round_type})")
st.dataframe(styled_df, use_container_width=True)

# --- DISPLAY 1: Top-Down Tactical Vector View ---
st.subheader("Top-Down Tactical Vector Map")
if distance > 0:
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    
    ax1.scatter(0, 0, color="green", s=100, zorder=5, label="Battery (0,0)")
    ax1.scatter(dx, dy, color="red", s=100, zorder=5, label="Target")
    ax1.plot([0, dx], [0, dy], color="black", linestyle="-", linewidth=2, alpha=0.7)
    
    circle = plt.Circle((0, 0), distance, color='blue', fill=False, linestyle=':', alpha=0.3)
    ax1.add_patch(circle)
    
    ax1.set_xlabel("Relative East/West Offset (meters)", fontsize=8)
    ax1.set_ylabel("Relative North/South Offset (meters)", fontsize=8)
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.axis("equal") 
    ax1.legend(loc="upper left", fontsize=8)
    
    plt.tight_layout()
    st.pyplot(fig1)
else:
    st.info("Enter target coordinates to process maps.")

# --- DISPLAY 2: Side-View Ballistics Arc ---
st.subheader("Side-View Ballistics Arc")
if distance > 0:
    fig2, ax2 = plt.subplots(figsize=(6, 3))
    x_vals = np.linspace(0, distance, 100)
    
    ax2.scatter(0, 0, color="green", zorder=5)
    ax2.scatter(distance, dz, color="red", zorder=5)
    
    has_valid_curve = False
    for ring_idx, elev_mils in valid_rings:
        peak_height = (distance / 2) * (1.1 + (ring_idx * 0.3)) + max(0.0, dz)
        y_vals = 4 * peak_height * (x_vals / distance) * (1 - (x_vals / distance)) + (x_vals / distance) * dz
        
        ax2.plot(x_vals, y_vals, linestyle="--", alpha=0.8, label=f"Ring {ring_idx}")
        has_valid_curve = True
        
    ax2.set_xlabel("Ground Distance (meters)", fontsize=8)
    ax2.set_ylabel("Relative Altitude (meters)", fontsize=8)
    ax2.grid(True, linestyle=":", alpha=0.6)
    
    if has_valid_curve:
        ax2.legend(loc="upper right", fontsize=8)
    else:
        ax2.text(0.5, 0.5, "Out of Range / No Solution", color="red", 
                ha="center", va="center", transform=ax2.transAxes, weight="bold")
        
    plt.tight_layout()
    st.pyplot(fig2)
