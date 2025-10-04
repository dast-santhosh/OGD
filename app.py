import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests

# Import the utility function from the specified module
from utils.map_utils import create_base_map

# Global variables for Bengaluru's coordinates
BENGALURU_LAT = 12.9716
BENGALURU_LON = 77.5946

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


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_live_weather_and_aqi():
    """Fetches real-time weather and air quality data from Open-Meteo APIs."""
    try:
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={BENGALURU_LAT}&longitude={BENGALURU_LON}&current=temperature_2m,relative_humidity_2m"
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        current_temp = weather_data['current']['temperature_2m']
        current_humidity = weather_data['current']['relative_humidity_2m']
        
        aqi_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={BENGALURU_LAT}&longitude={BENGALURU_LON}&current=european_aqi"
        aqi_response = requests.get(aqi_url)
        aqi_response.raise_for_status()
        aqi_data = aqi_response.json()
        current_aqi = aqi_data['current']['european_aqi']
        
        return {
            "temperature": current_temp,
            "humidity": current_humidity,
            "aqi": current_aqi
        }
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching live data: {e}")
        return None

def get_sample_locations():
    """Returns sample data for markers on the map."""
    return [
        {"name": "Bellandur Lake", "lat": 12.9234, "lon": 77.6784, "type": "Water Quality", "color": "blue"},
        {"name": "Cubbon Park", "lat": 12.9760, "lon": 77.5929, "type": "Green Space", "color": "green"},
        {"name": "Electronic City", "lat": 12.8452, "lon": 77.6601, "type": "Heat Island", "color": "red"},
        {"name": "Whitefield", "lat": 12.9698, "lon": 77.7500, "type": "Air Quality", "color": "orange"},
        {"name": "Ulsoor Lake", "lat": 12.9774, "lon": 77.6258, "type": "Water Quality", "color": "blue"}
    ]

def render_overview():
    """Renders the main Overview dashboard section."""
    st.header(f"📈 Overview Dashboard")
    
    # Fetch live data
    live_data = get_live_weather_and_aqi()
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)

    if live_data:
        with col1:
            st.metric("🌡️ Avg Temperature", f"{live_data['temperature']}°C")
        with col2:
            st.metric("💧 Humidity", f"{live_data['humidity']}%")
        with col3:
            st.metric("🌬️ Air Quality (AQI)", f"{live_data['aqi']}")
    else:
        # Use mock data if API call fails
        with col1:
            st.metric("🌡️ Avg Temperature", "32.5°C", "+2.1°C")
        with col2:
            st.metric("💧 Humidity", "65%", "-5%")
        with col3:
            st.metric("🌬️ Air Quality (AQI)", "156", "+12")
    
    with col4:
        st.metric("🌳 Green Cover", "18.2%", "-1.3%")

    # Overview map
    st.subheader("🗺️ Environmental Overview Map")
    base_map = create_base_map(BENGALURU_LAT, BENGALURU_LON)
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

    # Environmental Alerts
    st.subheader("🚨 Recent Environmental Alerts")
    
    alerts_data = {
        'Time': ['2 hours ago', '6 hours ago', '1 day ago', '2 days ago'],
        'Type': ['Heat Wave', 'Air Quality', 'Water Quality', 'Urban Heat'],
        'Location': ['Electronic City', 'Whitefield', 'Bellandur Lake', 'Koramangala'],
        'Severity': ['High', 'Moderate', 'High', 'Low']
    }
    
    alerts_df = pd.DataFrame(alerts_data)
    
    def get_alert_class(severity):
        if severity == 'High':
            return 'alert-high'
        elif severity == 'Moderate':
            return 'alert-moderate'
        else:
            return 'alert-low'
    
    for _, alert in alerts_df.iterrows():
        alert_class = get_alert_class(alert['Severity'])
        st.markdown(f"""
        <div class="{alert_class}">
            <strong>{alert['Type']}</strong> - {alert['Location']}<br>
            <small>{alert['Time']} • Severity: {alert['Severity']}</small>
        </div>
        """, unsafe_allow_html=True)

    # Charts and Analysis
    st.subheader("📈 Climate Trends Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Temperature trend chart (simulated data)
        dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='D')
        temps = [32 + (i % 3 - 1) for i in range(len(dates))]
        df_temp = pd.DataFrame({"Date": dates, "Temperature": temps})
        fig = px.line(df_temp, x='Date', y='Temperature', title="Temperature Trend (7 Days)", labels={'Date': 'Date', 'Temperature': 'Temperature (°C)'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Air quality gauge (using live or mock data)
        aqi_value = live_data['aqi'] if live_data else 156
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=aqi_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Air Quality (AQI)"},
            gauge={
                'axis': {'range': [None, 300]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "green"},
                    {'range': [50, 100], 'color': "yellow"},
                    {'range': [100, 150], 'color': "orange"},
                    {'range': [150, 200], 'color': "red"},
                    {'range': [200, 300], 'color': "purple"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 150
                }
            }
        ))
        st.plotly_chart(fig, use_container_width=True)

# Main app function
def main():
    """Main function to run the Streamlit application."""
    st.title("🌍 Aeroterra – Climate-Resilient Bengaluru Dashboard")
    st.markdown("*Interactive geospatial decision-support platform powered by NASA Earth observation data*")

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
        ["Overview", "Heat Islands", "Water Monitoring", "Air Quality", "Urban Growth", "Community Reports"]
    )

    # Main dashboard content based on selected module
    if module == "Overview":
        render_overview()
    elif module == "Heat Islands":
        st.header("🌡️ Heat Island Monitoring")
        st.info("Module under development. Displaying a static map for now.")
        st_folium(create_base_map(BENGALURU_LAT, BENGALURU_LON), width=700, height=500)
    elif module == "Water Monitoring":
        st.header("💧 Water Monitoring")
        st.info("Module under development. Displaying a static map for now.")
        st_folium(create_base_map(BENGALURU_LAT, BENGALURU_LON), width=700, height=500)
    elif module == "Air Quality":
        st.header("🌬️ Air Quality Monitoring")
        st.info("Module under development. Displaying a static map for now.")
        st_folium(create_base_map(BENGALURU_LAT, BENGALURU_LON), width=700, height=500)
    elif module == "Urban Growth":
        st.header("🏙️ Urban Growth Analyzer")
        st.info("Module under development. Displaying a static map for now.")
        st_folium(create_base_map(BENGALURU_LAT, BENGALURU_LON), width=700, height=500)
    elif module == "Community Reports":
        st.header("📋 Community Reports")
        st.info("Module under development. Displaying a static map for now.")
        st_folium(create_base_map(BENGALURU_LAT, BENGALURU_LON), width=700, height=500)

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
            🌍 Aeroterra Dashboard | Powered by NASA Earth Observations
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
