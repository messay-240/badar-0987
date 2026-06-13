import streamlit as st
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Solar Power Estimator Pro", layout="wide", page_icon="⚡")

# --- LOAD LOTTIE ANIMATION ---
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

solar_panel_anim = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_solarpanel.json")
wind_anim = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_wind.json")

# --- HEADER ---
st.markdown("<h1 class='main-header'>⚡ Solar Power Estimator Pro</h1>", unsafe_allow_html=True)

# --- WIND LOAD SIMULATION ---
st.subheader("🌬️ Wind Load Analysis with Animation")

wind_speed = st.slider("Select Wind Speed (km/h)", 10, 150, 60)
tilt_angle = st.slider("Panel Tilt Angle (°)", 0, 45, 25)
panel_qty = st.slider("Number of Panels", 1, 50, 10)

# Physics calculation
wind_ms = wind_speed / 3.6
q = 0.613 * wind_ms ** 2
cp = 1.2 if tilt_angle > 30 else 0.8
force_per_panel = q * cp * 2.6 / 1000
total_force = force_per_panel * panel_qty

st.metric("Total Wind Load (kN)", f"{total_force:.2f}")

# --- ANIMATION DISPLAY ---
col1, col2 = st.columns(2)
with col1:
    st_lottie(solar_panel_anim, height=250, key="solar")
    st.caption("Solar panels under normal conditions")
with col2:
    if wind_speed > 100:
        st_lottie(wind_anim, height=250, key="wind")
        st.caption("⚠️ Extreme wind detected! Panels show stress effect.")
    else:
        st_lottie(wind_anim, height=250, key="wind")
        st.caption("Moderate wind flow across panels")

# --- 3D PANEL STRUCTURE ---
st.subheader("📐 3D Panel Structure Visualization")

x = np.array([0, 1, 1, 0, 0])
y = np.array([0, 0, 1, 1, 0])
z = np.array([0, 0, 0, 0, 0])

fig = go.Figure(data=[go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='blue', width=6))])
fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Height'),
                  margin=dict(l=0, r=0, b=0, t=0))
st.plotly_chart(fig, use_container_width=True)

# --- SAFETY ALERT ---
if wind_speed > 120:
    st.error("🚨 Warning: Extreme wind load may cause structural failure. Reinforced clamps and wind deflectors required.")
else:
    st.success("✅ Wind load within safe limits.")
