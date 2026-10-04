import streamlit as st
import math

st.set_page_config(page_title="Mortar FDC", layout="centered")
st.title("Mortar FDC")

# Input Fields
origin_x_str = st.text_input("POO X", value="1000")
origin_y_str = st.text_input("POO Y", value="1000")
target_x_str = st.text_input("POI X", value="1500")
target_y_str = st.text_input("POI Y", value="1500")

# Parse Strings to Numbers (Preserves Leading Zeros)
try:
    ox = float(origin_x_str) if origin_x_str else 0.0
    oy = float(origin_y_str) if origin_y_str else 0.0
    tx = float(target_x_str) if target_x_str else 0.0
    ty = float(target_y_str) if target_y_str else 0.0
except ValueError:
    st.error("Enter numbers only.")
    ox, oy, tx, ty = 0.0, 0.0, 0.0, 0.0

# Vector Math
dx = tx - ox
dy = ty - oy

distance = math.sqrt(dx**2 + dy**2)
angle_rad = math.atan2(dx, dy)
degrees = math.degrees(angle_rad) % 360.0
mils = (degrees * 6400.0) / 360.0

# Outputs
st.metric("Distance", f"{distance:.1f} m")
st.metric("Deflection (Mils)", f"{int(round(mils))}")

