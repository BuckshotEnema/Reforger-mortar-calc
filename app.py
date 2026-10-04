import streamlit as st
import math

# Force a tight, centered mobile layout and inject CSS to remove unneeded spacing
st.set_page_config(page_title="Mortar FDC", layout="centered")

st.markdown("""
    <style>
        /* Tighten global application layout padding to eliminate scrolling */
        .block-container { padding-top: 1rem; padding-bottom: 1rem; }
        div[data-testid="stVerticalBlock"] > div { padding-bottom: 0.2rem; }
        /* Center metric widgets explicitly */
        div[data-testid="stMetric"] { text-align: center; }
        div[data-testid="stMetricValue"] { font-size: 2rem !important; justify-content: center; }
        div[data-testid="stMetricLabel"] { justify-content: center; }
    </style>
""", unsafe_allow_html=True)

st.title("Mortar FDC")

# Left Column (POO) and Right Column (POI)
col1, col2 = st.columns(2)

with col1:
    st.markdown("<span style='color: green; font-weight: bold; font-size: 1.2rem;'>POO</span>", unsafe_allow_html=True)
    origin_x_str = st.text_input("POO X", value="1000", label_visibility="collapsed")
    origin_y_str = st.text_input("POO Y", value="1000", label_visibility="collapsed")

with col2:
    st.markdown("<span style='color: red; font-weight: bold; font-size: 1.2rem;'>POI</span>", unsafe_allow_html=True)
    target_x_str = st.text_input("POI X", value="1500", label_visibility="collapsed")
    target_y_str = st.text_input("POI Y", value="1500", label_visibility="collapsed")

# Parse Strings to Numbers
try:
    ox = float(origin_x_str) if origin_x_str else 0.0
    oy = float(origin_y_str) if origin_y_str else 0.0
    tx = float(target_x_str) if target_x_str else 0.0
    ty = float(target_y_str) if target_y_str else 0.0
except ValueError:
    st.error("Numbers only.")
    ox, oy, tx, ty = 0.0, 0.0, 0.0, 0.0

# Vector Math
dx = tx - ox
dy = ty - oy

distance = math.sqrt(dx**2 + dy**2)
angle_rad = math.atan2(dx, dy)
degrees = math.degrees(angle_rad) % 360.0
mils = (degrees * 6400.0) / 360.0

st.markdown("---")

# Centered Outputs at the Bottom using columns
out_col1, out_col2 = st.columns(2)
with out_col1:
    st.metric("Distance", f"{distance:.1f} m")
with out_col2:
    st.metric("Deflection (Mils)", f"{int(round(mils))}")
