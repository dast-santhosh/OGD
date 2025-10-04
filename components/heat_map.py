import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import requests
from datetime import datetime, timedelta
import time
from typing import Dict, List, Any

# --- CONFIGURATION ---
BENGALURU_LAT = 12.9716
BENGALURU_LON = 77.5946
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# --- HELPER / MOCK FUNCTIONS (for a self-contained app) ---

def get_bengaluru_coordinates() -> List[float]:
    """Returns the central coordinates for Bengaluru."""
    return [BENGALURU_LAT, BENGURU_LON]

def create_base_map(lat: float = BENGALURU_LAT, lon: float = BENGALURU_LON, zoom: int = 11) -> folium.Map:
    """Creates a base Folium map centered on Bengaluru."""
    base_map = folium.Map(location=[lat, lon], zoom_start=zoom, tiles="cartodbdarkmatter")
    return base_map

def load_environmental_data() -> Dict[str, Any]:
    """Mock function to simulate loading all environmental data."""
    return {
        "temp_base": 30.0,
        "aqi": 156,
        "lake_health": 6.2
    }

def get_sample_locations() -> List[Dict[str, Any]]:
    """Mock function for key locations/points of interest."""
    return [
        {'name': 'Bellandur Lake', 'type': 'Water Body', 'lat': 12.915, 'lon': 77.678, 'color': '#00BFFF'},
        {'name': 'Cubbon Park', 'type': 'Green Cover', 'lat': 12.977, 'lon': 77.594, 'color': '#3CB371'},
        {'name': 'Electronic City', 'type': 'Industrial/High-Growth', 'lat': 12.840, 'lon': 77.679, 'color': '#FF4500'},
    ]

# --- API INTEGRATION ---

@st.cache_data(ttl=3600) # Cache the data for 1 hour to prevent API overuse
def fetch_open_meteo_data(lat: float, lon: float) -> Dict[str, Any]:
    """Fetches current temperature and forecast from Open-Meteo."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m",
        "current": "temperature_2m",
        "timezone": "Asia/Kolkata",
        "forecast_days": 7
    }
    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current_temp = data.get('current', {}).get('temperature_2m', 30.0)
        hourly_data = data.get('hourly', {})
        
        # Prepare 7-day trend data
        temp_trend = pd.DataFrame({
            'Date': [datetime.fromisoformat(t).date() for t in hourly_data['time']],
            'Temperature': hourly_data['temperature_2m']
        })
        
        # Aggregate to daily Max/Min/Avg
        daily_trend = temp_trend.groupby('Date')['Temperature'].agg(
            Max_Temp='max',
            Min_Temp='min',
            Average='mean'
        ).reset_index()
        
        return {
            'success': True,
            'current_temp': current_temp,
            'daily_trend': daily_trend.head(7) # Just take the next 7 days of forecast
        }

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching real-time weather data: {e}. Using simulated data.")
        return {'success': False, 'current_temp': 30.0, 'daily_trend': None}
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}. Using simulated data.")
        return {'success': False, 'current_temp': 30.0, 'daily_trend': None}


def get_temperature_grid(base_temp: float) -> List[Dict[str, Any]]:
    """
    Generates simulated temperature points around Bengaluru, grounded by the real base_temp,
    to visualize the Urban Heat Island effect.
    """
    # Define characteristic points in Bengaluru
    points = [
        {'lat': 12.9716, 'lon': 77.5946, 'area_type': 'urban_core', 'name': 'CBD (Majestic)'},
        {'lat': 12.9200, 'lon': 77.6200, 'area_type': 'residential', 'name': 'Koramangala'},
        {'lat': 13.0400, 'lon': 77.5600, 'area_type': 'industrial', 'name': 'Peenya'},
        {'lat': 12.9300, 'lon': 77.5600, 'area_type': 'green', 'name': 'Banerghatta Forest'},
        {'lat': 12.8400, 'lon': 77.6790, 'area_type': 'urban_core', 'name': 'Electronic City'},
        {'lat': 13.0000, 'lon': 77.6900, 'area_type': 'water_body', 'name': 'KR Puram Lake'},
        {'lat': 13.0800, 'lon': 77.5800, 'area_type': 'residential', 'name': 'Yelahanka'},
    ]
    
    temp_grid = []
    
    for point in points:
        # Define average heat offset based on land cover type
        if point['area_type'] == 'urban_core':
            offset = np.random.normal(3.5, 0.8)  # Hottest
        elif point['area_type'] == 'industrial':
            offset = np.random.normal(2.5, 0.7)
        elif point['area_type'] == 'residential':
            offset = np.random.normal(1.5, 0.5)
        elif point['area_type'] == 'green' or point['area_type'] == 'water_body':
            offset = np.random.normal(-1.5, 0.5) # Coolest
        else:
            offset = np.random.normal(0, 0.5)

        temp = base_temp + offset
        
        # Ensure temperature is within a reasonable range (25°C to 45°C)
        temp_value = max(25, min(45, temp))
        
        temp_grid.append({
            'lat': point['lat'], 
            'lon': point['lon'], 
            'temp': temp_value,
            'name': point['name']
        })
        
    return temp_grid

# --- MAIN DASHBOARD COMPONENT ---

def create_heat_map(stakeholder: str):
    st.header("🌡️ Urban Heat Islands Analysis - Live Data Grounding")
    
    # Fetch real-time data
    weather_data = fetch_open_meteo_data(BENGALURU_LAT, BENGALURU_LON)
    current_temp = weather_data['current_temp']
    daily_trend_df = weather_data['daily_trend']
    
    if weather_data['success']:
        st.success(f"Real-time Base Temperature (2m Air): **{current_temp:.1f}°C** (Source: Open-Meteo)")
    
    # Stakeholder-specific information 
    with st.container(border=True):
        st.subheader(f"Focus for {stakeholder}")
        if stakeholder == "BBMP (City Planning)":
            st.markdown("🏛️ Use heat island data to plan green corridors and prioritize tree plantation areas for heat mitigation.")
        elif stakeholder == "Citizens":
            st.markdown("👥 Identify the coolest routes for commuting and report heat-related issues in your neighborhood.")
        elif stakeholder == "Parks Department":
            st.markdown("🌳 Identify critical areas needing immediate green cover intervention based on surface temperature anomalies.")
        else:
             st.markdown("💡 General focus: Analyze the relationship between land cover and temperature extremes.")

    # Temperature analysis controls 
    col1, col2, col3 = st.columns(3)

    with col1:
        time_period = st.selectbox(
            "Time Period:", 
            ["Current", "Daily Forecast", "Weekly Trend", "Monthly Comparison"], key="time_period_select"
        )
    with col2:
        temperature_layer = st.selectbox(
            "Temperature Layer:", 
            ["Simulated Surface Temperature (UHI)", "2m Air Temperature", "Heat Index"], key="temp_layer_select"
        )
    with col3:
        overlay_data = st.selectbox(
            "Overlay Data:", 
            ["None", "NDVI (Vegetation)", "Population Density", "Building Density"], key="overlay_data_select"
        )
    
    # --- 1. Heat Island Map Visualization ---
    st.subheader("🗺️ Live Heat Island Map")
    
    heat_map = create_base_map()
    temp_grid = get_temperature_grid(current_temp)

    # Prepare data for Folium HeatMap plugin
    heat_data = [[p['lat'], p['lon'], p['temp']] for p in temp_grid]
    
    # Add HeatMap layer
    HeatMap(heat_data, 
            radius=15, 
            blur=10, 
            min_opacity=0.4, 
            max_val=40, # Normalizing the scale based on expected max temperature
            gradient={
                0.0: 'blue', 0.5: 'green', 0.7: 'yellow', 0.85: 'orange', 1.0: 'red'
            }
    ).add_to(heat_map)
    
    # Add markers for key points with popups showing simulated temp
    for point in temp_grid:
        folium.CircleMarker(
            location=[point['lat'], point['lon']],
            radius=4,
            color=f"#{'FF0000' if point['temp'] > current_temp + 3 else '008000'}",
            fill=True,
            fillColor=f"#{'FF0000' if point['temp'] > current_temp + 3 else '008000'}",
            fillOpacity=0.9,
            popup=f"**{point['name']}**<br>Simulated Temp: **{point['temp']:.1f}°C**<br>({point['temp'] - current_temp:.1f}°C Anomaly)",
        ).add_to(heat_map)

    # Display map
    st_folium(heat_map, width=900, height=550, key="heat_map_display", returned_objects=[])

    # --- 2. Interactive Data and Trends ---
    st.markdown("---")
    col1, col2 = st.columns([1.5, 2])

    with col1:
        st.subheader("📊 Current Zone Temperature Anomaly")
        # Create a DataFrame for statistics based on the simulated grid data
        temp_stats = pd.DataFrame(temp_grid).rename(columns={'temp': 'Simulated Temp (°C)'})
        temp_stats['Anomaly (°C)'] = (temp_stats['Simulated Temp (°C)'] - current_temp).round(1)
        temp_stats['Heat Index'] = np.select(
            [temp_stats['Anomaly (°C)'] > 3.0, temp_stats['Anomaly (°C)'] > 1.5],
            ['Extreme', 'High'],
            default='Moderate'
        )
        temp_stats = temp_stats[['name', 'Simulated Temp (°C)', 'Anomaly (°C)', 'Heat Index']]
        temp_stats.set_index('name', inplace=True)
        
        # FIX: Removed .style.background_gradient which required matplotlib
        st.dataframe(
            temp_stats, 
            use_container_width=True
        )

    with col2:
        st.subheader("📈 7-Day Temperature Forecast")
        if daily_trend_df is not None:
            # Aggregate to daily Max/Min/Avg for the next 7 forecast days
            trend_display_df = daily_trend_df.groupby('Date')[['Max_Temp', 'Min_Temp', 'Average']].first().reset_index()

            fig = px.line(trend_display_df, x='Date', y=['Max_Temp', 'Min_Temp', 'Average'],
                          title='Air Temperature Forecast (Next 7 Days)',
                          labels={'value': 'Temperature (°C)', 'variable': 'Metric'},
                          color_discrete_map={'Max_Temp': 'red', 'Min_Temp': 'blue', 'Average': 'orange'})

            fig.update_layout(hovermode="x unified", legend_title_text='Temperature Type')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.warning("Cannot display forecast due to API error.")


    # --- 3. Recommendations ---
    st.subheader("💡 Recommended Actions")
    if stakeholder == "BBMP (City Planning)":
        st.markdown("""
        - **Prioritize:** Focus tree canopy expansion in Peenya and Electronic City (highest temperature anomaly).
        - **Policy:** Mandate cool roofs and reflective paving materials in all new commercial developments.
        - **Monitoring:** Integrate real-time temperature sensors in vulnerable wards.
        """)
    elif stakeholder == "Citizens":
        st.markdown("""
        - **Safety:** Avoid strenuous outdoor activity in Extreme/High Heat Index zones between 11 AM - 4 PM. 
        - **Cooling:** Use the map to identify the coolest parks (Green zones) for evening walks.
        - **Action:** Participate in local tree planting drives to reduce neighborhood heat.
        """)
    elif stakeholder == "Parks Department":
        st.markdown("""
        - **Intervention:** Allocate 70% of new saplings to areas with less than 15% Green Cover (e.g., Mahadevapura).
        - **Water:** Implement drought-resistant native species to survive increased average temperatures.
        - **Inventory:** Map existing large trees and implement protective measures against urban development encroachment.
        """)

# --- STREAMLIT APP ENTRY POINT ---

if __name__ == "__main__":
    st.set_page_config(
        page_title="Climate-Resilient Bengaluru Dashboard",
        page_icon="🛰️",
        layout="wide"
    )

    # Initial setup
    if 'stakeholder' not in st.session_state:
        st.session_state.stakeholder = "Citizens"
    if 'env_data' not in st.session_state:
        st.session_state.env_data = load_environmental_data()
        
    st.sidebar.title("🎯 Dashboard Navigation")
    st.sidebar.markdown("---")
    
    stakeholder_select = st.sidebar.selectbox(
        "Select Stakeholder View:", 
        ["Citizens", "BBMP (City Planning)", "Parks Department", "General"],
        key="main_stakeholder_select"
    )
    st.sidebar.markdown("---")
    
    # Run the enhanced heat map component
    create_heat_map(stakeholder_select)

    st.markdown("---")
    st.markdown(f"**Live Data Source:** Open-Meteo API | **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    st.markdown("Project by: Santhosh P & Team")
