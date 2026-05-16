import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page layout configuration
st.set_page_config(page_title="Global Solar Analytics Pro", layout="wide")

st.title("🌍 Global Renewable Energy: Solar & Grid Analytics")
st.markdown("Is advanced system ke zariye dunya bhar se kahin bhi solar efficiency, load shifting, aur net-metering revenue track karein.")

# --- GLOBAL COUNTRIES DATABASE (With Optimal Angles & Currencies) ---
countries_db = {
    "Pakistan": {"angle": 30, "currency": "PKR", "rate_sell": 42.0, "rate_buy": 60.0},
    "India": {"angle": 22, "currency": "INR", "rate_sell": 4.5, "rate_buy": 7.0},
    "USA": {"angle": 38, "currency": "USD", "rate_sell": 0.10, "rate_buy": 0.16},
    "Germany": {"angle": 48, "currency": "EUR", "rate_sell": 0.08, "rate_buy": 0.35},
    "UAE": {"angle": 24, "currency": "AED", "rate_sell": 0.15, "rate_buy": 0.30},
    "Australia": {"angle": 35, "currency": "AUD", "rate_sell": 0.07, "rate_buy": 0.30},
    "United Kingdom": {"angle": 50, "currency": "GBP", "rate_sell": 0.15, "rate_buy": 0.40},
    "Saudi Arabia": {"angle": 25, "currency": "SAR", "rate_sell": 0.10, "rate_buy": 0.18}
}

# --- SIDEBAR: USER INPUTS ---
st.sidebar.header("📍 1. Location Settings")
selected_country = st.sidebar.selectbox("Select Client Country", list(countries_db.keys()))

# Fetching default values based on selected country
default_angle = countries_db[selected_country]["angle"]
currency = countries_db[selected_country]["currency"]
default_sell = countries_db[selected_country]["rate_sell"]
default_buy = countries_db[selected_country]["rate_buy"]

st.sidebar.markdown(f"**💡 Auto-Detected Optimal Angle for {selected_country}:** `{default_angle}°`")

st.sidebar.header("🏗️ 2. Hardware Specs")
panel_power = st.sidebar.number_input("Single Panel Power (Watts)", min_value=100, max_value=800, value=580)
num_panels = st.sidebar.number_input("Total Number of Panels", min_value=1, max_value=100, value=12)
orientation = st.sidebar.radio("Panel Orientation Type", ["Latitudinal (Horizontal)", "Longitudinal (Vertical)"])

# User can tweak the auto-suggested angle if they want
manual_angle = st.sidebar.slider("Adjustment Tilt Angle (Degrees)", 0, 90, default_angle)

st.sidebar.header("☀️ 3. Sunlight & Load")
sun_hours = st.sidebar.slider("Peak Sunlight Hours (Daily)", 1.0, 14.0, 6.0)
daily_load_total = st.sidebar.number_input("Client 24-Hour Total Load (Units/kWh)", min_value=1.0, value=20.0)

st.sidebar.header("💰 4. Grid Economics")
sale_rate = st.sidebar.number_input(f"Selling Rate to Grid (Per Unit {currency})", value=default_sell)
purchase_rate = st.sidebar.number_input(f"Purchase Rate from Grid (Per Unit {currency})", value=default_buy)

# --- CORE MATHEMATICAL LOGIC & SIMULATION ---
system_size_kw = (panel_power * num_panels) / 1000

# Angle & Orientation Losses
angle_deviation = abs(manual_angle - default_angle)
loss_factor = 0.85 # Base efficiency (15% standard inverter/dust losses)
if angle_deviation > 5:
    loss_factor -= (angle_deviation * 0.005) # 0.5% loss per degree away from optimal
if orientation == "Longitudinal (Vertical)":
    loss_factor *= 0.95 # 5% orientation loss

daily_generation_total = system_size_kw * sun_hours * loss_factor

# 24-Hour Simulation Arrays
hours = np.arange(24)
gen_hourly = []
load_hourly = []

for h in hours:
    # Solar generation curve (Bell curve between 6 AM and 6 PM)
    if 6 <= h <= 18:
        # Sine wave to simulate sun rising, peaking at noon, and setting
        factor = np.sin(np.pi * (h - 6) / 12)
        gen_hourly.append(max(0.0, (daily_generation_total / (sun_hours * 0.6)) * factor * 0.5))
    else:
        gen_hourly.append(0.0)
    
    # Load profile: Night load is full grid, daytime load is lower
    if h >= 18 or h < 6:
        # Night Load (Air Conditioners, lights, full grid dependence)
        load_hourly.append((daily_load_total / 24) * 1.4)
    else:
        # Day Load (Running on Solar)
        load_hourly.append((daily_load_total / 24) * 0.6)

# Calculating Self-Consumption, Grid Sales, and Grid Purchases
self_used = [min(g, l) for g, l in zip(gen_hourly, load_hourly)]
units_sold = [max(0.0, g - l) for g, l in zip(gen_hourly, load_hourly)]
units_bought = [max(0.0, l - g) for g, l in zip(gen_hourly, load_hourly)]

# --- MAIN DASHBOARD INTERFACE ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("System Size", f"{system_size_kw:.2f} kW")
col2.metric("Daily Production", f"{sum(gen_hourly):.1f} Units")
col3.metric("Daily Grid Export (Sale)", f"{sum(units_sold):.1f} Units")
col4.metric("Daily Grid Import (Night)", f"{sum(units_bought):.1f} Units")

st.divider()

# --- SEPARATE GRAPH TABS (As Requested: Clean Line Charts) ---
st.subheader("📊 Energy Analysis Dashboard")
tab1, tab2, tab3 = st.tabs(["🕒 24-Hour Detailed Flow", "📅 Weekly Energy View", "🗓️ Monthly Projection"])

with tab1:
    st.markdown("#### 24-Hour Real-Time Generation, Consumption & Sale Balance")
    df_24h = pd.DataFrame({
        "Hour of Day": hours,
        "Solar Produced (kWh)": gen_hourly,
        "Home Load Demand (kWh)": load_hourly,
        "Units Sold to Grid": units_sold,
        "Grid Purchase (Night/Deficit)": units_bought
    })
    
    # Melting dataframe for Plotly express line chart
    df_melted = df_24h.melt(id_vars=["Hour of Day"], var_name="Parameter", value_name="Energy (Units)")
    fig_24h = px.line(df_melted, x="Hour of Day", y="Energy (Units)", color="Parameter",
                      title="Hourly System Simulation (Day vs Night Split)",
                      color_discrete_sequence=["#FF9900", "#109618", "#3366CC", "#DC3912"])
    fig_24h.update_layout(hovermode="x unified", xaxis=dict(tickmode='linear', dtick=2))
    st.plotly_chart(fig_24h, use_container_width=True)

with tab2:
    st.markdown("#### Weekly Estimated Energy Trends")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Adding slight weather variations safely without dynamic state bugs
    np.random.seed(42) 
    weekly_prod = [sum(gen_hourly) * np.random.uniform(0.85, 1.05) for _ in range(7)]
    weekly_sold = [sum(units_sold) * np.random.uniform(0.85, 1.05) for _ in range(7)]
    weekly_use = [sum(self_used) for _ in range(7)]
    
    df_week = pd.DataFrame({
        "Day": days,
        "Total Produced": weekly_prod,
        "Exported (Sold)": weekly_sold,
        "Self Consumption": weekly_use
    }).melt(id_vars=["Day"], var_name="Metrics", value_name="Units (kWh)")
    
    fig_week = px.line(df_week, x="Day", y="Units (kWh)", color="Metrics", 
                       title="7-Day Performance Outlook",
                       color_discrete_sequence=["#FF9900", "#3366CC", "#109618"])
    st.plotly_chart(fig_week, use_container_width=True)

with tab3:
    st.markdown("#### 12-Month Seasonal Projection")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    # Seasonal modifiers for standard solar shifts across months
    seasonal_modifiers = [0.7, 0.8, 1.0, 1.2, 1.3, 1.25, 1.1, 1.15, 1.0, 0.9, 0.75, 0.65]
    monthly_prod = [sum(gen_hourly) * 30 * mod for mod in seasonal_modifiers]
    monthly_sold = [sum(units_sold) * 30 * mod for mod in seasonal_modifiers]
    monthly_bought = [sum(units_bought) * 30 for _ in range(12)]
    
    df_month = pd.DataFrame({
        "Month": months,
        "Produced Units": monthly_prod,
        "Sold Units": monthly_sold,
        "Purchased from Grid": monthly_bought
    }).melt(id_vars=["Month"], var_name="Monthly Metrics", value_name="Units")
    
    fig_month = px.line(df_month, x="Month", y="Units", color="Monthly Metrics",
                        title="Annual Performance Curve (Base Simulation)",
                        color_discrete_sequence=["#FF9900", "#3366CC", "#DC3912"])
    st.plotly_chart(fig_month, use_container_width=True)

# --- FINANCIAL ECONOMICS STATEMENT ---
st.divider()
st.subheader("📋 Monthly Commercial Report")

total_sold_monthly = sum(units_sold) * 30
total_bought_monthly = sum(units_bought) * 30

gross_earnings = total_sold_monthly * sale_rate
gross_expenses = total_bought_monthly * purchase_rate
net_financial_status = gross_earnings - gross_expenses

f_col1, f_col2, f_col3 = st.columns(3)
f_col1.metric("Est. Monthly Grid Earnings", f"{gross_earnings:,.2f} {currency}")
f_col2.metric("Est. Monthly Grid Bill", f"{gross_expenses:,.2f} {currency}")

if net_financial_status >= 0:
    f_col3.metric("Net Monthly Profit ✨", f"+ {net_financial_status:,.2f} {currency}", delta_color="inverse")
    st.success(f"**Excellent:** Client ka solar system unke night-load expense ko cover kar ke mahana **{net_financial_status:,.2f} {currency}** ka net profit de raha hai.")
else:
    f_col3.metric("Net Monthly Bill Payable 📉", f"{net_financial_status:,.2f} {currency}", delta_color="normal")
    st.warning(f"**Notice:** Raat ka load zyada hone ya grid rates high hone ki wajah se client ko net **{abs(net_financial_status):,.2f} {currency}** pay karne parenge.")
