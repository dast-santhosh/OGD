import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import requests

# Import custom modules
from components.heat_map import create_heat_map
from components.water_monitoring import create_water_dashboard
from components.air_quality import create_air_quality_dashboard
from components.urban_growth import create_urban_growth_analyzer
from components.community_reports import create_community_reports
from components.chatbot import create_chatbot
from services.nasa_service import NASAService
from services.weather_service import WeatherService
from services.gemini_service import GeminiService
from utils.data_utils import get_bengaluru_coordinates, get_sample_locations, load_environmental_data
from utils.map_utils import create_base_map

# Page configuration
st.set_page_config(
    page_title="🌍 Aeroterra - Climate Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #f0f2f6;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: #31333F !important;
}

section[data-testid="stSidebar"] div[role="button"] {
    background-color: white;
    color: #31333F;
}

/* Fixed footer */
.fixed-footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #31333F;
    color: white;
    text-align: center;
    padding: 10px;
    font-size: 14px;
    border-top: 1px solid #4f4f4f;
    z-index: 1000;
}

/* Alert severity colors */
.alert-high {
    background-color: #ffebee;
    padding: 8px;
    border-left: 4px solid #f44336;
    margin: 4px 0;
}

.alert-moderate {
    background-color: #fff3e0;
    padding: 8px;
    border-left: 4px solid #ff9800;
    margin: 4px 0;
}

.alert-low {
    background-color: #e8f5e9;
    padding: 8px;
    border-left: 4px solid #4caf50;
    margin: 4px 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize services
@st.cache_resource
def initialize_services():
    """Initializes and caches API services."""
    nasa_service = NASAService()
    weather_service = WeatherService()
    gemini_service = GeminiService()
    return nasa_service, weather_service, gemini_service

# Main app function
def main():
    """Main function to run the Streamlit application."""
    st.title("🌍 Aeroterra – Climate-Resilient Bengaluru Dashboard")
    st.markdown("*Interactive geospatial decision-support platform powered by NASA Earth observation data and AI*")

    # Initialize services
    nasa_service, weather_service, gemini_service = initialize_services()

    # Add logos to the sidebar
    st.sidebar.image("nasa.png", use_container_width=True)
    st.sidebar.image("logo.png", use_container_width=True)

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
    BENGALURU_LAT, BENGALURU_LON = get_bengaluru_coordinates()

    # Load environmental data
    env_data = load_environmental_data()

    # Main dashboard content based on selected module
    if module == "Overview":
        render_overview(stakeholder, BENGALURU_LAT, BENGALURU_LON, weather_service, env_data)
    elif module == "Heat Islands":
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
    st.markdown(f"""
    **Data Sources:** NASA MODIS, Landsat, VIIRS, TROPOMI, GPM, Open-Meteo API | **Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}
    """)

    # Project Team Credits
    st.markdown("""
    **Project by:** Santhosh P & Aysu A & Team
    """)

    # NEW FIXED FOOTER/DOWNBAR
    st.markdown("""
        <div class="fixed-footer">
            🌍 Aeroterra Dashboard | Powered by NASA Earth Observations & Gemini AI
        </div>
    """, unsafe_allow_html=True)


def render_overview(stakeholder, lat, lon, weather_service, env_data):
    """Renders the main Overview dashboard section."""
    st.header(f"📈 {stakeholder} Overview Dashboard")

    # Fetch live data
    with st.spinner("Loading real-time climate data..."):
        try:
            live_weather = weather_service.get_current_weather(lat, lon)
            live_aqi = weather_service.get_air_quality(lat, lon)
        except Exception as e:
            st.error(f"Failed to fetch live data: {e}")
            live_weather, live_aqi = None, None

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)

    if live_weather:
        with col1:
            temp = live_weather.get('temperature_2m', 'N/A')
            st.metric("🌡️ Avg Temperature", f"{temp}°C")
        with col2:
            humidity = live_weather.get('relative_humidity_2m', 0)
            st.metric("💧 Humidity", f"{humidity}%")
    else:
        with col1:
            st.metric("🌡️ Avg Temperature", "32.5°C", "+2.1°C")
        with col2:
            st.metric("💧 Humidity", "65%", "-5%")

    if live_aqi:
        with col3:
            aqi_value = live_aqi.get('european_aqi', 'N/A')
            st.metric("🌬️ Air Quality (AQI)", f"{aqi_value}")
    else:
        with col3:
            st.metric("🌬️ Air Quality (AQI)", "156", "+12")

    with col4:
        st.metric("🌳 Green Cover", "18.2%", "-1.3%")

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

    st_folium(base_map, width=700, height=500)

    # Recent alerts
    st.subheader("🚨 Recent Environmental Alerts")
    alerts_data = pd.DataFrame([
        {"Time": "2 hours ago", "Type": "Heat Wave", "Location": "Electronic City", "Severity": "High"},
        {"Time": "6 hours ago", "Type": "Air Quality", "Location": "Silk Board", "Severity": "Moderate"},
        {"Time": "1 day ago", "Type": "Water Quality", "Location": "Bellandur Lake", "Severity": "High"},
        {"Time": "2 days ago", "Type": "Flooding Risk", "Location": "Majestic Area", "Severity": "Low"}
    ])
    st.dataframe(alerts_data, width='stretch')


if __name__ == "__main__":
    main()
