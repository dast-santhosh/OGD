import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import time # For exponential backoff retry logic

# ====================================================================
# 1. CONSTANTS AND GLOBAL CONFIGURATION
# ====================================================================

# Global variables for Bengaluru's coordinates
BENGALURU_LAT = 12.9716
BENGALURU_LON = 77.5946
API_KEY = "" # The key will be provided by the runtime environment if needed

# Page configuration
st.set_page_config(
    page_title="Climate-Resilient Bengaluru Dashboard",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to force the sidebar into DARK mode and adjust the main container
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }

/* 0. Force Main App Container to Dark Mode Background */
[data-testid="stAppViewContainer"] > .main {
    background-color: #0E1117 !important; /* Streamlit default dark mode background */
    color: #FAFAFA; /* Light text for dark background */
}
/* 0.1 Force all text in main content to be light */
h1, h2, h3, h4, p, label, .stMarkdown {
    color: #FAFAFA !important;
}

/* 1. Sidebar Background and General Text Color */
section[data-testid="stSidebar"] {
    background-color: #1F2937; /* Dark slate background */
    border-right: 2px solid #374151;
}

/* 2. Sidebar Header Titles and Text */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: #F9FAFB !important; /* Light text color */
}

/* 3. Selectbox/Dropdown background and text */
section[data-testid="stSidebar"] div[role="button"] {
    background-color: #374151; /* Darker button background */
    color: #F9FAFB;
    border-radius: 8px;
    border: 1px solid #4B5563;
}

/* 4. Fixed Footer Styling */
.fixed-footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #151E28; /* Very dark background for footer */
    color: white;
    text-align: center;
    padding: 10px;
    font-size: 14px;
    border-top: 1px solid #374151;
    z-index: 1000;
}

/* 5. Main Content Styling */
div.block-container {
    padding-top: 2rem;
    padding-bottom: 5rem; /* Add space for the footer */
}

/* 6. Metric Styling */
[data-testid="stMetric"] {
    background-color: #1E2B3E; /* Dark card background for metrics */
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    border: 1px solid #374151;
    color: #FAFAFA !important;
}

/* 7. Dataframe styling for dark mode */
.stDataFrame {
    color: #FAFAFA;
}
</style>
""", unsafe_allow_html=True)


# ====================================================================
# 2. MOCK UTILITY FUNCTIONS (To ensure single-file runnability)
# ====================================================================

def load_environmental_data():
    """Mock function for data loading."""
    return pd.DataFrame()

def get_sample_locations():
    """Mock function for map locations."""
    return [
        {"name": "Bellandur Lake", "lat": 12.924, "lon": 77.674, "type": "Water Quality", "color": "red"},
        {"name": "Lal Bagh Botanical Garden", "lat": 12.949, "lon": 77.584, "type": "Green Cover", "color": "green"},
        {"name": "Electronic City", "lat": 12.84, "lon": 77.678, "type": "Heat Island", "color": "orange"},
        {"name": "MG Road Traffic", "lat": 12.975, "lon": 77.608, "type": "Air Quality", "color": "blue"},
    ]

def create_base_map():
    """Mock function to create a Folium map."""
    m = folium.Map(
        location=[BENGALURU_LAT, BENGALURU_LON],
        zoom_start=11,
        tiles="cartodbdarkmatter"
    )
    return m

# Mock component functions
def create_heat_map(stakeholder):
    st.header(f"🔥 Heat Islands Analysis for {stakeholder}")
    st.info("Module content for Heat Islands analysis goes here, integrating NASA Land Surface Temperature data.")

def create_water_dashboard(stakeholder):
    st.header(f"💧 Water Monitoring Dashboard for {stakeholder}")
    st.info("Module content for Water Monitoring goes here, integrating GPM and Landsat data for lake health and flooding.")

def create_air_quality_dashboard(stakeholder):
    st.header(f"💨 Air Quality Dashboard for {stakeholder}")
    st.info("Module content for Air Quality goes here, integrating TROPOMI and ground sensor data.")

def create_urban_growth_analyzer(stakeholder):
    st.header(f"🏙️ Urban Growth Analyzer for {stakeholder}")
    st.info("Module content for Urban Growth goes here, using historical Landsat imagery to track expansion and green cover loss.")

def create_community_reports(stakeholder):
    st.header(f"📢 Community Reports for {stakeholder}")
    st.info("Module content for Community Reports goes here, showing citizen-reported issues like trash, water logging, and localized heat/air quality.")

def create_chatbot(stakeholder, env_data):
    st.header(f"🤖 AI Climate Assistant for {stakeholder}")
    st.info("Module content for the AI Chatbot goes here, using the Gemini API to answer queries based on environmental data.")


# ====================================================================
# 3. API CALLS WITH BACKOFF
# ====================================================================

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_live_weather_data():
    """Fetches real-time weather and air quality data with retry logic."""
    max_retries = 3
    base_delay = 1

    for attempt in range(max_retries):
        try:
            # Fetching temperature and other weather data
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={BENGALURU_LAT}&longitude={BENGALURU_LON}&current=temperature_2m,relative_humidity_2m"
            
            # Fetching air quality data
            aqi_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={BENGALURU_LAT}&longitude={BENGALURU_LON}&current=european_aqi"

            weather_response = requests.get(weather_url, timeout=10)
            weather_response.raise_for_status()
            weather_data = weather_response.json()
            current_temp = weather_data['current']['temperature_2m']
            
            aqi_response = requests.get(aqi_url, timeout=10)
            aqi_response.raise_for_status()
            aqi_data = aqi_response.json()
            current_aqi = aqi_data['current']['european_aqi']
            
            return {
                "temperature": current_temp,
                "aqi": current_aqi
            }
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
            else:
                st.error(f"Error fetching live data after {max_retries} attempts. Displaying mock data.")
                return None
    return None

@st.cache_data(ttl=3600*24) # Cache for 24 hours
def create_trend_graph():
    """
    Generates a dual-axis trend graph using simulated historical data only.
    API integration for this function has been disabled.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # --- Using only mock data as requested ---
    st.warning("Displaying **simulated** trend data. API connection for historical trends has been disabled.")
    
    dates = [start_date + timedelta(days=i) for i in range(7)]
    df = pd.DataFrame({
        'date': dates,
        'max_temperature': [32.5, 33.0, 34.1, 35.5, 34.9, 33.5, 32.8], # Mock temps
        'max_aqi': [90, 105, 120, 115, 100, 85, 95] # Mock AQI
    })
    # ----------------------------------------
    
    if df is None or df.empty:
        return None

    # Fix: Explicitly define rows and cols for make_subplots to prevent Plotly ValueError
    fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]])

    # Add Temperature trace (Red for urgency)
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['max_temperature'], name="Max Daily Temp (°C)", line=dict(color='red', width=3)),
        secondary_y=False,
    )

    # Add AQI trace (Orange/Brown for pollution urgency)
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['max_aqi'], name="Max Daily AQI", line=dict(color='orange', width=3, dash='dot')),
        secondary_y=True,
    )

    # Add shaded area for high-risk zones (Temperature > 35C)
    fig.add_hrect(y0=35, y1=df['max_temperature'].max() + 2, line_width=0, fillcolor="rgba(255, 0, 0, 0.1)", secondary_y=False, annotation_text="Danger Heat Zone", annotation_position="top left")
    # Add shaded area for poor AQI (AQI > 100)
    fig.add_hrect(y0=100, y1=df['max_aqi'].max() + 20, line_width=0, fillcolor="rgba(165, 42, 42, 0.1)", secondary_y=True, annotation_text="Danger Air Zone", annotation_position="bottom right")


    # Update layout for maximum impact
    fig.update_layout(
        title_text="<b>⚠️ Environmental Stress Trends: Max Temp vs. Air Quality (Last 7 Days)</b>",
        title_font_size=20,
        title_font_color="#FAFAFA", # Updated for Dark Mode
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        template="plotly_dark", # Use plotly dark template
        margin=dict(l=20, r=20, t=50, b=20)
    )

    fig.update_xaxes(title_text="Date", showgrid=False)
    fig.update_yaxes(title_text="Max Temperature (°C)", secondary_y=False, color='red', gridcolor='#374151')
    fig.update_yaxes(title_text="Max Air Quality Index (AQI)", secondary_y=True, color='orange', gridcolor='#374151')
    fig.update_traces(mode='lines+markers')

    return fig

# ====================================================================
# 4. MAIN APPLICATION LAYOUT
# ====================================================================

# Main title and description
st.title("🌍 Climate-Resilient Bengaluru Geospatial Dashboard")
st.markdown("""
A decision-support platform integrating NASA Earth observation data
for urban resilience planning and citizen awareness.
""")

# --- Sidebar Logo/Branding ---
# Using st.sidebar.image for the user-provided logo.png file
st.sidebar.image("logo1.png", use_column_width=True)

# Adding a stylized title below the logo image
st.sidebar.markdown(
    """
    <div style='text-align: center; padding: 10px 0 20px 0;'>
        <h4 style='color: #4CAF50; margin-bottom: 0px;'>
            **BENGALURU Resilience Hub**
        </h4>
    </div>
    """, unsafe_allow_html=True
)
# --- End Sidebar Logo/Branding ---

# Sidebar for stakeholder selection and navigation
st.sidebar.title("🎯 Stakeholder View")
stakeholder = st.sidebar.selectbox(
    "Select Stakeholder View:",
    ["Citizens", "BBMP (City Planning)", "BWSSB (Water Board)", "BESCOM (Electricity)", "Parks Department", "Researchers"]
)

st.sidebar.title("📊 Dashboard Modules")
module = st.sidebar.selectbox(
    "Select Module:",
    ["Overview", "Heat Islands", "Water Monitoring", "Air Quality", "Urban Growth", "Community Reports", "AI Assistant"]
)

# Load environmental data (mocked)
env_data = load_environmental_data()

# Main dashboard content based on selected module
if module == "Overview":
    st.header(f"📈 {stakeholder} Overview Dashboard")

    # Fetch live data (still uses API, so we keep the function)
    live_data = get_live_weather_data()

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)

    # Use live data or mock data
    current_temp = live_data['temperature'] if live_data else 33.1
    current_aqi = live_data['aqi'] if live_data else 165

    with col1:
        st.metric("🌡️ Live Temperature", f"{current_temp}°C", f"+{round(current_temp - 30.0, 1)}°C above normal")
    with col3:
        st.metric("🌬️ Live Air Quality (AQI)", f"{current_aqi}", "Unhealthy")
    with col2:
        st.metric("💧 Lake Health Index", "6.2/10", "-0.8 points (Poor)")
    with col4:
        st.metric("🌳 Green Cover Status", "18.2%", "-1.3% since 2020")

    # --- URGENCY GRAPH ---
    st.subheader("Combined Environmental Stress Indicator")
    # This function now uses only mock data
    trend_fig = create_trend_graph() 
    if trend_fig:
        st.plotly_chart(trend_fig, use_container_width=True)
    else:
        # This error case should now be impossible since it uses mock data
        st.error("Failed to load or generate the trend graph.")

    # Overview map
    st.subheader("🗺️ Key Environmental Monitoring Locations")
    base_map = create_base_map()
    locations = get_sample_locations()
    for loc in locations:
        folium.CircleMarker(
            location=[loc['lat'], loc['lon']],
            radius=8,
            popup=f"<b>{loc['name']}</b> ({loc['type']})",
            color=loc['color'],
            fillColor=loc['color'],
            fillOpacity=0.7
        ).add_to(base_map)

    st_folium(base_map, width="100%", height=500)

    # Recent alerts
    st.subheader("🚨 Recent High-Priority Alerts")
    alerts_df = pd.DataFrame([
        {"Time": "2 hours ago", "Type": "Heat Wave", "Location": "Electronic City", "Severity": "High", "Action Required": "Public cooling centers activated."},
        {"Time": "6 hours ago", "Type": "Air Quality", "Location": "Silk Board", "Severity": "Moderate", "Action Required": "Restrict non-essential vehicle movement."},
        {"Time": "1 day ago", "Type": "Water Quality", "Location": "Bellandur Lake", "Severity": "High", "Action Required": "BWSSB dispatched testing team."},
        {"Time": "2 days ago", "Type": "Flooding Risk", "Location": "Majestic Area", "Severity": "Low", "Action Required": "Storm water drains clearing initiated."}
    ])
    st.dataframe(alerts_df, use_container_width=True, hide_index=True)

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
st.markdown("""
**Data Sources:** NASA MODIS, Landsat, VIIRS, TROPOMI, GPM, Open-Meteo API (for Live Data) | **Last Updated:** {current_time}
""".format(current_time=datetime.now().strftime("%Y-%m-%d %H:%M UTC")))

# Project Team Credits
st.markdown("""
**Project by:** Santhosh P, Aysu A & Team
""")

# NEW FIXED FOOTER/DOWNBAR
st.markdown("""
    <div class="fixed-footer">
        CodeSphere Institute | DAST India | Building Climate Resilience
    </div>
""", unsafe_allow_html=True)
