import streamlit as st
import math

st.set_page_config(page_title="Mortar FDC", layout="centered")
st.title("Mortar FDC")

# Setup Columns
col1, col2 = st.columns(2)

# Column 1: POO (Green and Bold Header)
with col1:
    st.markdown("<span style='color: green; font-weight: bold; font-size: 1.25rem;'>POO</span>", unsafe_allow_html=True)
    origin_x_str = st.text_input("POO X", value="1000")
    origin_y_str = st.text_input("POO Y", value="1000")

# Column 2: POI (Red and Bold Header)
with col2:
    st.markdown("<span style='color: red; font-weight: bold; font-size: 1.25rem;'>POI</span>", unsafe_allow_html=True)
    target_x_str = st.text_input("POI X", value="1500")
    target_y_str = st.text_input("POI Y", value="1500")

# Parse Strings to Numbers
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
st.markdown("---")
st.metric("Distance", f"{distance:.1f} m")
st.metric("Deflection (Mils)", f"{int(round(mils))}")
