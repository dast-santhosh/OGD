import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# Import custom components
from components.heat_map import create_heat_map
from components.water_monitoring import create_water_dashboard
from components.air_quality import create_air_quality_dashboard
from components.urban_growth import create_urban_growth_analyzer
from components.community_reports import create_community_reports
from components.chatbot import create_chatbot
from data.bengaluru_data import get_bengaluru_coordinates, get_sample_locations
from utils.map_utils import create_base_map
from utils.data_processing import load_environmental_data

# Page configuration
st.set_page_config(
    page_title="Climate-Resilient Bengaluru Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title and description
st.title("🌍 Climate-Resilient Bengaluru Geospatial Dashboard")
st.markdown("""
Real-time decision-support platform integrating NASA Earth observation data 
for urban planners, policymakers, and citizens.
""")

# ⚠️ CORRECTION 1: Add logos to the sidebar
# This is a good way to add images to the sidebar.
st.sidebar.image("nasa.png", use_column_width=True)
st.sidebar.image("logo.png", use_column_width=True)


# Sidebar for stakeholder selection and navigation
st.sidebar.title("🎯 Stakeholder Dashboard")
stakeholder = st.sidebar.selectbox(
    "Select Stakeholder View:",
    ["Citizens", "BBMP (City Planning)", "BWSSB (Water Board)", "BESCOM (Electricity)", "Parks Department", "Researchers"]
)

st.sidebar.title("📊 Dashboard Modules")
module = st.sidebar.selectbox(
    "Select Module:",
    ["Overview", "Heat Islands", "Water Monitoring", "Air Quality", "Urban Growth", "Community Reports", "AI Assistant"]
)

# Load environmental data
@st.cache_data
def load_data():
    # You might need to add a placeholder or mock function for load_environmental_data()
    # if it's not defined in the provided code snippet.
    # For example:
    # return pd.DataFrame()
    return load_environmental_data()

env_data = load_data()

# Main dashboard content based on selected module
if module == "Overview":
    st.header(f"📈 {stakeholder} Overview Dashboard")

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🌡️ Avg Temperature", "32.5°C", "+2.1°C")

    with col2:
        st.metric("💧 Lake Health Index", "6.2/10", "-0.8")

    with col3:
        st.metric("🌬️ Air Quality (AQI)", "156", "+12")

    with col4:
        st.metric("🏙️ Green Cover", "18.2%", "-1.3%")

    # Overview map
    st.subheader("🗺️ Bengaluru Environmental Overview")
    # Assuming create_base_map() and get_sample_locations() are defined elsewhere
    base_map = create_base_map()
    locations = get_sample_locations()
    for loc in locations:
        folium.CircleMarker(
            location=[loc['lat'], loc['lon']],
            radius=8,
            popup=f"{loc['name']}: {loc['type']}",
            color=loc['color'],
            fillColor=loc['color'],
            fillOpacity=0.7
        ).add_to(base_map)

    map_data = st_folium(base_map, width=700, height=500)

    # Recent alerts
    st.subheader("🚨 Recent Environmental Alerts")
    alerts_df = pd.DataFrame([
        {"Time": "2 hours ago", "Type": "Heat Wave", "Location": "Electronic City", "Severity": "High"},
        {"Time": "6 hours ago", "Type": "Air Quality", "Location": "Silk Board", "Severity": "Moderate"},
        {"Time": "1 day ago", "Type": "Water Quality", "Location": "Bellandur Lake", "Severity": "High"},
        {"Time": "2 days ago", "Type": "Flooding Risk", "Location": "Majestic Area", "Severity": "Low"}
    ])
    st.dataframe(alerts_df, width='stretch')

elif module == "Heat Islands":
    # Assuming create_heat_map is defined
    create_heat_map(stakeholder)

elif module == "Water Monitoring":
    # Assuming create_water_dashboard is defined
    create_water_dashboard(stakeholder)

elif module == "Air Quality":
    # Assuming create_air_quality_dashboard is defined
    create_air_quality_dashboard(stakeholder)

elif module == "Urban Growth":
    # Assuming create_urban_growth_analyzer is defined
    create_urban_growth_analyzer(stakeholder)

elif module == "Community Reports":
    # Assuming create_community_reports is defined
    create_community_reports(stakeholder)

elif module == "AI Assistant":
    # Assuming create_chatbot is defined
    create_chatbot(stakeholder, env_data)

# Footer
st.markdown("---")
st.markdown("""
**Data Sources:** NASA MODIS, Landsat, VIIRS, TROPOMI, GPM | **Last Updated:** {current_time}
""".format(current_time=datetime.now().strftime("%Y-%m-%d %H:%M UTC")))

# ⚠️ CORRECTION 2: Add project team credits at the bottom
st.markdown("""
**Project by:**
Santhosh P
Aysu A & Team
""")
