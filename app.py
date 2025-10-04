import streamlit as st 
import folium 
from streamlit_folium import st_folium 
import pandas as pd 
import plotly.express as px 
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import requests

# Import custom components (assuming these exist in your project structure)
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
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to force the sidebar into light mode
st.markdown("""
<style>
/* 1. Sidebar Background and General Text Color */
section[data-testid="stSidebar"] {
    background-color: #f0f2f6; /* Light gray background */
}

/* 2. Sidebar Header Titles and Text */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: #31333F !important; /* Dark text color */
}

/* 3. Selectbox/Dropdown background and text */
section[data-testid="stSidebar"] div[role="button"] {
    background-color: white;
    color: #31333F;
}

/* 4. Fixed Footer Styling */
.fixed-footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #31333F; /* Dark background for visibility */
    color: white;
    text-align: center;
    padding: 10px;
    font-size: 14px;
    border-top: 1px solid #4f4f4f;
    z-index: 1000; /* Ensure it stays on top of other elements */
}
</style>
""", unsafe_allow_html=True)


# Main title and description
st.title("🌍 Climate-Resilient Bengaluru Geospatial Dashboard")
st.markdown("""
Real-time decision-support platform integrating NASA Earth observation data
for urban planners, policymakers, and citizens.
""")

# Add logos to the sidebar
# FIX: Replaced deprecated `use_column_width` with `use_container_width`
st.sidebar.image("logo1.png", use_container_width=True)

# --- Added Brand and Subtitle ---
st.sidebar.title("AEROTERRA")
st.sidebar.markdown("### Bangalore's Geospatial Dashboard")
# ---------------------------------

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

# Global variables for Bengaluru's coordinates
BENGALURU_LAT = 12.9716
BENGALURU_LON = 77.5946

# Load environmental data
@st.cache_data
def load_data():
    return load_environmental_data()

env_data = load_data()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_live_weather_data():
    """
    Fetches real-time weather and air quality data from Open-Meteo APIs.
    """
    try:
        # Fetching temperature and other weather data
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={BENGALURU_LAT}&longitude={BENGALURU_LON}&current=temperature_2m,relative_humidity_2m"
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        current_temp = weather_data['current']['temperature_2m']
        
        # Fetching air quality data
        aqi_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={BENGALURU_LAT}&longitude={BENGALURU_LON}&current=european_aqi"
        aqi_response = requests.get(aqi_url)
        aqi_response.raise_for_status()
        aqi_data = aqi_response.json()
        current_aqi = aqi_data['current']['european_aqi']
        
        return {
            "temperature": current_temp,
            "aqi": current_aqi
        }
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching live data: {e}")
        return None

# Main dashboard content based on selected module
if module == "Overview":
    st.header(f"📈 {stakeholder} Overview Dashboard")
    
    # Fetch live data
    live_data = get_live_weather_data()
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)

    if live_data:
        with col1:
            st.metric("🌡️ Avg Temperature", f"{live_data['temperature']}°C")

        with col3:
            st.metric("🌬️ Air Quality (AQI)", f"{live_data['aqi']}")
    else:
        # Use mock data if API call fails
        with col1:
            st.metric("🌡️ Avg Temperature", "32.5°C", "+2.1°C")

        with col3:
            st.metric("🌬️ Air Quality (AQI)", "156", "+12")

    # Metrics that don't change in real-time
    with col2:
        st.metric("💧 Lake Health Index", "6.2/10", "-0.8")
        
    with col4:
        st.metric("🏙️ Green Cover", "18.2%", "-1.3%")
        
    # Overview map
    st.subheader("🗺️ Bengaluru Environmental Overview")
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

    st.subheader("🚨 Recent Environmental Alerts")

    alerts = [
        {"Time": "2 hours ago", "Type": "Mild Heat Wave", "Location": "Electronic City", "Severity": "High"},
        {"Time": "6 hours ago", "Type": "Air Quality", "Location": "Silk Board", "Severity": "Moderate"},
        {"Time": "1 day ago", "Type": "Water Quality", "Location": "Bellandur Lake", "Severity": "High"},
        {"Time": "2 days ago", "Type": "Flooding Risk", "Location": "Majestic Area", "Severity": "Low"}
    ]
    
    # Custom CSS for the alert boxes (dark mode theme)
    alert_style = """
    <style>
    .alert-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .alert-box {
        padding: 15px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        display: flex;
        align-items: center;
    }
    .alert-box.high {
        background-color: #dc3545; /* Red */
        border-left: 5px solid #bd2130;
    }
    .alert-box.moderate {
        background-color: #ffc107; /* Orange/Yellow */
        border-left: 5px solid #d39e00;
    }
    .alert-box.low {
        background-color: #007bff; /* Blue */
        border-left: 5px solid #0056b3;
    }
    .alert-box .icon {
        margin-right: 15px;
        font-size: 24px;
    }
    </style>
    """
    st.markdown(alert_style, unsafe_allow_html=True)
    
    # Generate and display the alerts
    st.markdown('<div class="alert-container">', unsafe_allow_html=True)
    for alert in alerts:
        severity = alert['Severity'].lower()
        icon = "⚠️" if severity == "high" else "📢"
        alert_html = f"""
        <div class="alert-box {severity}">
            <span class="icon">{icon}</span>
            <div>
                <div>{alert['Type']} at {alert['Location']}</div>
                <div style="font-size: 0.9em; font-weight: normal;">{alert['Time']}</div>
            </div>
        </div>
        """
        st.markdown(alert_html, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Recent alerts
    # ... (inside the if module == "Overview": block)

# Recent alerts


# ... (the rest of your code)

if module == "Heat Islands":
    create_heat_map(stakeholder)

elif module == "Water Monitoring":
    create_water_dashboard(stakeholder)

elif module == "Air Quality":
    create_air_quality_dashboard(stakeholder)

elif module == "Urban Growth":
    create_urban_growth_analyzer(stakeholder)

elif module == "Community Reports":
    create_community_reports(stakeholder)

elif module == "AI Assistant":
    create_chatbot(stakeholder, env_data)

# Main Content Footer (just above the fixed footer)
st.markdown("---")
st.markdown("""
**Data Sources:** NASA MODIS, Landsat, VIIRS, TROPOMI, GPM, Open-Meteo API | **Last Updated:** {current_time}
""".format(current_time=datetime.now().strftime("%Y-%m-%d %H:%M UTC")))

# Project Team Credits
st.markdown("""
**Project by:** Santhosh P 
Aysu A & Team
""")

# NEW FIXED FOOTER/DOWNBAR
st.markdown("""
    <div class="fixed-footer">
        CodeSphere Institute | DAST India | Santhosh P & Team
    </div>
""", unsafe_allow_html=True)
