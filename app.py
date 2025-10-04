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

# Page config
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
    nasa_service = NASAService()
    weather_service = WeatherService()
    gemini_service = GeminiService()
    return nasa_service, weather_service, gemini_service

# Main app
def main():
    # Title
    st.title("🌍 Aeroterra – Climate-Resilient Bengaluru Dashboard")
    st.markdown("*Interactive geospatial decision-support platform powered by NASA Earth observation data and AI*")
    
    # Initialize services
    nasa_service, weather_service, gemini_service = initialize_services()
    
    # Add NASA logo to sidebar (if available)
    # st.sidebar.image("nasa.png", use_container_width=True)
    
    # Sidebar - Stakeholder Selection
    st.sidebar.title("🎯 Stakeholder Dashboard")
    stakeholder = st.sidebar.selectbox(
        "Select Stakeholder View:",
        ["Citizens", "BBMP (City Planning)", "BWSSB (Water Board)", 
         "BESCOM (Electricity)", "Parks Department", "Researchers"]
    )
    
    # Sidebar - Dashboard Modules
    st.sidebar.title("📊 Dashboard Modules")
    module = st.sidebar.selectbox(
        "Select Module:",
        ["Overview", "Heat Islands", "Water Monitoring", "Air Quality", 
         "Urban Growth", "Community Reports", "AI Assistant"]
    )
    
    # Main content area
    if module == "Overview":
        render_overview(weather_service, nasa_service, stakeholder)
    elif module == "Heat Islands":
        render_heat_islands(nasa_service, weather_service)
    elif module == "Water Monitoring":
        render_water_monitoring(nasa_service)
    elif module == "Air Quality":
        render_air_quality(nasa_service, weather_service)
    elif module == "Urban Growth":
        render_urban_growth(nasa_service)
    elif module == "Community Reports":
        render_community_reports(stakeholder)
    elif module == "AI Assistant":
        render_chatbot(gemini_service, nasa_service, weather_service)

def render_overview(weather_service, nasa_service, stakeholder):
    st.header(f"📊 Overview Dashboard - {stakeholder}")
    
    # Get coordinates for Bengaluru
    lat, lon = get_bengaluru_coordinates()
    
    # Fetch real-time data
    with st.spinner("Loading real-time climate data..."):
        try:
            weather_data = weather_service.get_current_weather(lat, lon)
            air_quality_data = weather_service.get_air_quality(lat, lon)
        except Exception as e:
            st.error(f"Failed to load weather data: {str(e)}")
            weather_data = None
            air_quality_data = None
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if weather_data:
            temp = weather_data.get('temperature_2m', 'N/A')
            st.metric(
                label="🌡️ Current Temperature",
                value=f"{temp}°C" if temp != 'N/A' else "N/A",
                delta=None
            )
        else:
            st.metric(label="🌡️ Current Temperature", value="Data unavailable")
    
    with col2:
        # Lake Health Index (simulated based on available data)
        if weather_data:
            humidity = weather_data.get('relative_humidity_2m', 50)
            lake_health = min(100, max(0, humidity + 20))  # Simple calculation
            st.metric(
                label="💧 Lake Health Index",
                value=f"{lake_health}/100",
                delta=f"{'↑' if lake_health > 70 else '↓'} {'Good' if lake_health > 70 else 'Poor'}"
            )
        else:
            st.metric(label="💧 Lake Health Index", value="Data unavailable")
    
    with col3:
        if air_quality_data:
            aqi = air_quality_data.get('pm2_5', 'N/A')
            st.metric(
                label="🌫️ Air Quality (PM2.5)",
                value=f"{aqi} μg/m³" if aqi != 'N/A' else "N/A",
                delta=f"{'Poor' if isinstance(aqi, (int, float)) and aqi > 25 else 'Good'}"
            )
        else:
            st.metric(label="🌫️ Air Quality (PM2.5)", value="Data unavailable")
    
    with col4:
        # Green Cover (placeholder - would need satellite data processing)
        st.metric(
            label="🌳 Green Cover Estimate",
            value="68%",
            delta="↓ 2% from last year"
        )
    
    # Interactive Map
    st.subheader("🗺️ Environmental Overview Map")
    render_interactive_map(lat, lon, weather_data or {}, air_quality_data or {})
    
    # Environmental Alerts
    st.subheader("🚨 Recent Environmental Alerts")
    
    alerts_data = {
        'Time': ['2 hours ago', '6 hours ago', '1 day ago', '2 days ago'],
        'Type': ['Heat Wave', 'Air Quality', 'Water Quality', 'Urban Heat'],
        'Location': ['Electronic City', 'Whitefield', 'Bellandur Lake', 'Koramangala'],
        'Severity': ['High', 'Moderate', 'High', 'Low']
    }
    
    alerts_df = pd.DataFrame(alerts_data)
    
    # Color-code alerts by severity
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
        if weather_data:
            # Temperature trend chart
            dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='D')
            temps = [weather_data.get('temperature_2m', 25) + (i * 0.5) for i in range(len(dates))]
            
            fig = px.line(
                x=dates, y=temps,
                title="Temperature Trend (7 Days)",
                labels={'x': 'Date', 'y': 'Temperature (°C)'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if air_quality_data:
            # Air quality gauge
            aqi_value = air_quality_data.get('pm2_5', 25)
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = aqi_value,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Air Quality (PM2.5)"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 25], 'color': "lightgray"},
                        {'range': [25, 50], 'color': "yellow"},
                        {'range': [50, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 50
                    }
                }
            ))
            st.plotly_chart(fig, use_container_width=True)

def render_heat_islands(nasa_service, weather_service):
    st.header("🌡️ Heat Island Monitoring")
    
    # Get Bengaluru coordinates
    lat, lon = get_bengaluru_coordinates()
    
    # Heat island analysis
    st.subheader("Urban Heat Island Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**Heat Island Hotspots Detected:**")
        hotspots = [
            "Electronic City - 4.2°C above average",
            "Whitefield - 3.8°C above average", 
            "Koramangala - 3.1°C above average",
            "Banashankari - 2.9°C above average"
        ]
        for hotspot in hotspots:
            st.write(f"🔥 {hotspot}")
    
    with col2:
        st.info("**Cooling Zones:**")
        cooling_zones = [
            "Cubbon Park - 2.1°C below average",
            "Lalbagh Gardens - 1.8°C below average",
            "Ulsoor Lake - 1.3°C below average",
            "Sankey Tank - 1.1°C below average"
        ]
        for zone in cooling_zones:
            st.write(f"❄️ {zone}")
    
    # Heat island map
    render_interactive_map(lat, lon, {}, {}, map_type="heat_island")

def render_water_monitoring(nasa_service):
    st.header("💧 Water Body Monitoring")
    
    st.subheader("Bengaluru Lakes Status")
    
    # Lake data
    lakes_data = {
        'Lake Name': ['Bellandur Lake', 'Ulsoor Lake', 'Sankey Tank', 'Hebbal Lake', 'Madivala Lake'],
        'Health Score': [45, 78, 82, 67, 59],
        'Water Quality': ['Poor', 'Good', 'Excellent', 'Fair', 'Poor'],
        'Algal Bloom Risk': ['High', 'Low', 'Very Low', 'Medium', 'High'],
        'Area (hectares)': [361, 50, 15, 72, 114]
    }
    
    df = pd.DataFrame(lakes_data)
    
    # Display data table
    st.dataframe(df, use_container_width=True)
    
    # Visualization
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(df, x='Lake Name', y='Health Score', 
                     color='Health Score',
                     title='Lake Health Scores',
                     color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(df, values='Area (hectares)', names='Lake Name',
                     title='Lake Areas Distribution')
        st.plotly_chart(fig, use_container_width=True)

def render_air_quality(nasa_service, weather_service):
    st.header("🌫️ Air Quality Monitoring")
    
    # Get current air quality
    lat, lon = get_bengaluru_coordinates()
    
    try:
        air_quality_data = weather_service.get_air_quality(lat, lon)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            pm25 = air_quality_data.get('pm2_5', 0)
            st.metric("PM2.5", f"{pm25} μg/m³", 
                     delta=f"{'Unhealthy' if pm25 > 25 else 'Good'}")
        
        with col2:
            pm10 = air_quality_data.get('pm10', 0)
            st.metric("PM10", f"{pm10} μg/m³",
                     delta=f"{'Unhealthy' if pm10 > 50 else 'Good'}")
        
        with col3:
            no2 = air_quality_data.get('nitrogen_dioxide', 0)
            st.metric("NO₂", f"{no2} μg/m³",
                     delta=f"{'High' if no2 > 40 else 'Normal'}")
        
        # Air quality trends
        st.subheader("Air Quality Trends")
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        pm25_trend = [pm25 + (i % 10 - 5) for i in range(len(dates))]
        
        fig = px.line(x=dates, y=pm25_trend, title="PM2.5 Trend (30 Days)")
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Failed to load air quality data: {str(e)}")

def render_urban_growth(nasa_service):
    st.header("🏙️ Urban Growth Analysis")
    
    st.subheader("Urban Expansion Patterns")
    
    # Urban growth metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Built-up Area Growth", "12.3%", delta="↑ 2.1% from last year")
    
    with col2:
        st.metric("Green Space Loss", "8.7%", delta="↓ Critical")
    
    with col3:
        st.metric("New Construction", "847 projects", delta="↑ 156 from last quarter")
    
    # Growth visualization
    years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
    built_area = [450, 465, 478, 492, 510, 525, 542]  # km²
    green_area = [180, 175, 170, 165, 158, 152, 147]  # km²
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=built_area, name='Built-up Area (km²)', 
                            line=dict(color='red')))
    fig.add_trace(go.Scatter(x=years, y=green_area, name='Green Area (km²)', 
                            line=dict(color='green')))
    fig.update_layout(title='Urban vs Green Area Trends', xaxis_title='Year', yaxis_title='Area (km²)')
    
    st.plotly_chart(fig, use_container_width=True)

def render_community_reports(stakeholder):
    st.header("📋 Community Reports")
    
    st.subheader(f"Reports for {stakeholder}")
    
    if stakeholder == "Citizens":
        st.info("**Air Quality Alert**: PM2.5 levels are elevated in Electronic City. Consider wearing masks outdoors.")
        st.success("**Good News**: Cubbon Park air quality is excellent today - perfect for outdoor activities!")
        st.warning("**Water Advisory**: Bellandur Lake showing signs of algal bloom. Avoid direct contact.")
        
    elif stakeholder == "BBMP (City Planning)":
        st.error("**Urgent**: Heat island intensity increased by 15% in IT corridor. Immediate green cover intervention needed.")
        st.info("**Planning Update**: 3 new parks approved for Whitefield area to combat urban heat.")
        st.success("**Progress**: Tree plantation drive achieved 78% of quarterly target.")
        
    elif stakeholder == "BWSSB (Water Board)":
        st.warning("**Water Quality Alert**: 4 lakes show deteriorating conditions requiring immediate attention.")
        st.info("**Treatment Update**: New water treatment facility operational in Hebbal.")
        st.success("**Conservation**: Rainwater harvesting compliance reached 65% in monitored areas.")

def render_chatbot(gemini_service, nasa_service, weather_service):
    st.header("🤖 Terrabot - AI Climate Assistant")
    from components.chatbot import render_chatbot_interface
    render_chatbot_interface(gemini_service, nasa_service, weather_service)

if __name__ == "__main__":
    main()
    
    # Footer with data sources and credits
    st.markdown("---")
    st.markdown(f"""
    **Data Sources:** NASA MODIS, Landsat, VIIRS, Sentinel | Open-Meteo API | **Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}
    """)
    
    # Fixed footer with credits
    st.markdown("""
    <div class="fixed-footer">
        🌍 Aeroterra Dashboard | Powered by NASA Earth Observations & Gemini AI
    </div>
    """, unsafe_allow_html=True)
