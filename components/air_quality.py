import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import requests # Kept for the Urban Heat Map section
from datetime import datetime, timedelta
from typing import Dict, List, Any

# --- CONFIGURATION & CONSTANTS ---
BENGALURU_LAT = 12.9716
BENGALURU_LON = 77.5946
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
# AQI_API_URL is no longer needed as we use internal mock data

# --- UTILITY FUNCTIONS ---

def get_bengaluru_coordinates() -> List[float]:
    """Returns the central coordinates for Bengaluru."""
    return [BENGALURU_LAT, BENGALURU_LON]

def create_base_map(lat: float = BENGALURU_LAT, lon: float = BENGALURU_LON, zoom: int = 11) -> folium.Map:
    """Creates a base Folium map centered on Bengaluru."""
    base_map = folium.Map(location=[lat, lon], zoom_start=zoom, tiles="cartodbdarkmatter")
    return base_map

def get_aqi_category(aqi: float) -> str:
    """Returns the descriptive category for the European AQI."""
    if pd.isna(aqi): return "Unknown"
    
    if aqi <= 20: return "Good"
    if aqi <= 40: return "Fair"
    if aqi <= 60: return "Moderate"
    if aqi <= 90: return "Poor"
    if aqi <= 120: return "Very Poor"
    return "Extremely Poor"

def get_aqi_color(aqi: float) -> str:
    """Returns a color for the AQI level."""
    if pd.isna(aqi): return "gray"
    if aqi <= 20: return "green"
    if aqi <= 40: return "lightgreen"
    if aqi <= 60: return "orange"
    if aqi <= 90: return "red"
    return "darkred"

# --- API INTEGRATION (Weather - Kept) ---

@st.cache_data(ttl=3600) # Cache the data for 1 hour
def fetch_weather_data(lat: float, lon: float) -> Dict[str, Any]:
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
        response = requests.get(WEATHER_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        current_temp = data.get('current', {}).get('temperature_2m', 30.0)
        hourly_data = data.get('hourly', {})
        
        temp_trend = pd.DataFrame({
            'Date': [datetime.fromisoformat(t).date() for t in hourly_data['time']],
            'Temperature': hourly_data['temperature_2m']
        })
        
        daily_trend = temp_trend.groupby('Date')['Temperature'].agg(
            Max_Temp='max',
            Min_Temp='min',
            Average='mean'
        ).reset_index()
        
        return {
            'success': True,
            'current_temp': current_temp,
            'daily_trend': daily_trend.head(7)
        }
    except requests.exceptions.RequestException:
        # Fallback to mock data if API fails
        st.warning("Could not fetch live Weather data. Using mock temperature data.")
        mock_daily_trend = pd.DataFrame({
            'Date': pd.to_datetime(pd.date_range(start=datetime.now().date(), periods=7)).date,
            'Max_Temp': [33, 34, 32, 31, 33, 35, 36],
            'Min_Temp': [20, 21, 20, 19, 20, 22, 23],
            'Average': [26.5, 27.5, 26, 25, 26.5, 28.5, 29.5]
        })
        return {'success': False, 'current_temp': 30.0, 'daily_trend': mock_daily_trend}
    except Exception:
        return {'success': False, 'current_temp': 30.0, 'daily_trend': None}


# --- DASHBOARD COMPONENTS ---

def create_air_quality_dashboard(stakeholder):
    """Generates the Air Quality Dashboard module using internal MOCK data."""
    st.header("🌬️ Air Quality Monitoring Dashboard (Mock Data)")
    st.warning("⚠️ This section uses hardcoded mock data for consistent demonstration, bypassing external APIs.")

    # --- HARDCODED MOCK DATA (MODERATE AQI) ---
    current_aqi = 55.0  # Set to "Moderate"
    current_category = get_aqi_category(current_aqi)
    
    # Mock data for current pollutant levels (μg/m³) - consistent with Moderate AQI
    pollutant_data = {
        "Pollutant": ["$\text{PM}_{2.5}$", "$\text{PM}_{10}$", "$\text{NO}_{2}$", "$\text{SO}_{2}$", "$\text{O}_{3}$"],
        "Value ($\mu g / m^3$)": [28.0, 45.0, 25.0, 10.0, 40.0], 
        "EAC Limit": [25, 50, 40, 20, 100]
    }
    pollutant_df = pd.DataFrame(pollutant_data)
    
    # Mock data for 7-day average trend
    daily_trend_df = pd.DataFrame({
        'Date': pd.date_range(end=datetime.now(), periods=7, freq='D').date,
        'AQI': [42, 48, 52, 58, 65, 50, current_aqi] # Showing a slight spike a couple of days ago
    })
    
    # Generate mock data for Streamgraph (hourly composition)
    mock_hours = pd.to_datetime(pd.date_range(end=datetime.now(), periods=24*7, freq='H'))
    mock_stream_df = pd.DataFrame({
        'Time': mock_hours,
        # Pollutant levels adjusted for a Moderate day
        'PM2.5': np.random.uniform(15, 40, size=len(mock_hours)),
        'PM10': np.random.uniform(30, 60, size=len(mock_hours)),
        'NO2': np.random.uniform(15, 35, size=len(mock_hours)),
        'SO2': np.random.uniform(5, 15, size=len(mock_hours)),
        'O3': np.random.uniform(30, 50, size=len(mock_hours)),
    })
    pollutant_cols = ['PM2.5', 'PM10', 'NO2', 'SO2', 'O3']
    stream_long = mock_stream_df.melt(id_vars=['Time'], value_vars=pollutant_cols, 
                                      var_name='Pollutant', value_name='Concentration')
    
    # --- CHART GENERATION (Using Mock Data) ---
    
    # 1. Streamgraph
    fig_stream = px.area(
        stream_long, x='Time', y='Concentration', color='Pollutant',
        title='Hourly Pollutant Stacked Trend (7 Days)', template='plotly_white',
        labels={'Concentration': 'Concentration ($\mu g / m^3$)'}
    )
    fig_stream.update_layout(yaxis=dict(title=None, showgrid=True), xaxis=dict(title=None))
    
    # 2. Waterfall (Day-over-Day Change)
    mock_daily_aqi = daily_trend_df.copy()
    mock_daily_aqi['Change'] = mock_daily_aqi['AQI'].diff()
    waterfall_df = mock_daily_aqi.iloc[1:].copy()
    waterfall_df['Date'] = waterfall_df['Date'].apply(lambda x: x.strftime('%b %d'))

    fig_waterfall = px.bar(
        waterfall_df, 
        x='Date', 
        y='Change', 
        title='Daily Change in Average AQI',
        labels={'Change': 'AQI Change (Day/Day)'},
        color=waterfall_df['Change'].apply(lambda x: 'Increase' if x > 0 else 'Decrease'),
        color_discrete_map={'Increase': 'darkred', 'Decrease': 'darkgreen'},
        template='plotly_white',
        text=waterfall_df['Change'].round(1).apply(lambda x: f'{x:+.1f}')
    )
    fig_waterfall.update_layout(showlegend=False, yaxis_title="AQI Change")
    fig_waterfall.update_traces(textposition='outside')
    
    # --- LAYOUT ---

    # Stakeholder Messaging
    if stakeholder == "Citizens":
        st.info(f"👥 **Citizen View:** Current AQI is **{current_category}**. Air quality is generally acceptable but could be worse for sensitive groups.")
    elif stakeholder == "BBMP (City Planning)":
        st.info(f"🏛️ **BBMP Focus:** Current AQI is **{current_category}**. Monitor $\text{PM}_{2.5}$ levels, which are close to the threshold.")
    else:
        st.info(f"The **{stakeholder}** view focuses on key pollutants and trends.")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Current Status (EAC Index)")
        # Display AQI safely
        display_aqi = f"{current_aqi:.0f}"
        st.metric("European AQI", display_aqi, help="European Air Quality Index (EAC) based on mock data.")
        st.markdown(f"**Health Risk:** <span style='color:{get_aqi_color(current_aqi)};'>**{current_category}**</span>", unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("Key Pollutant Levels")
        st.dataframe(pollutant_df, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("AQI Trend (Last 7 Days Average)")
        fig = px.bar(daily_trend_df, x='Date', y='AQI', title='AQI Daily Average',
                     color='AQI', color_continuous_scale=px.colors.sequential.Plasma_r)
        
        # Add horizontal lines for AQI thresholds
        fig.add_hline(y=60, line_dash="dash", line_color="red", annotation_text="Poor/Very Poor Threshold (60)", annotation_position="top left")
        fig.add_hline(y=40, line_dash="dash", line_color="orange", annotation_text="Moderate Threshold (40)", annotation_position="bottom right")
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
    # --- New Charts: Streamgraph and Waterfall (Day-over-Day Change) ---
    st.markdown("---")
    st.subheader("Advanced Air Quality Trend Analysis")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.caption("Pollutant Composition Trend (Last 7 Days Hourly)")
        st.plotly_chart(fig_stream, use_container_width=True, config={'displayModeBar': False})
        
    with col4:
        st.caption("Daily AQI Change (Day-over-Day)")
        st.plotly_chart(fig_waterfall, use_container_width=True, config={'displayModeBar': False})
    
    # --- Map Visualization (Simulated Stations) ---
    st.subheader("Air Quality Monitoring Stations (Simulated Hotspots)")
    aq_map = create_base_map()
    
    # Simulate variations around the fixed AQI
    base_aqi = current_aqi
    stations = [
        {'lat': 12.975, 'lon': 77.58, 'name': 'City Centre (High Traffic)', 'type': 'traffic', 'factor': 1.1},
        {'lat': 12.92, 'lon': 77.65, 'name': 'Whitefield (Residential)', 'type': 'residential', 'factor': 0.9},
        {'lat': 13.0, 'lon': 77.55, 'name': 'Peenya (Industrial Zone)', 'type': 'industrial', 'factor': 1.3},
        {'lat': 12.93, 'lon': 77.56, 'name': 'Banerghatta (Green Zone)', 'type': 'green', 'factor': 0.7},
    ]

    for station in stations:
        # Calculate simulated AQI with random noise
        sim_aqi = round(max(10, min(150, base_aqi * station['factor'] + np.random.normal(0, 3))))
        color = get_aqi_color(sim_aqi)
        
        folium.Marker(
            location=[station['lat'], station['lon']],
            popup=f"**{station['name']}** - AQI: **{sim_aqi}** ({get_aqi_category(sim_aqi)})",
            icon=folium.Icon(color=color, icon='smog', prefix='fa')
        ).add_to(aq_map)
            
    st_folium(aq_map, width=900, height=550, key="aqi_map", returned_objects=[])

# --- Heat Map Component (Included for completeness and multi-tab functionality) ---
# (fetch_weather_data and create_heat_map remain unchanged, using the API)

def get_temperature_grid(base_temp: float) -> List[Dict[str, Any]]:
    """Generates simulated temperature points grounded by the real base_temp."""
    points = [
        {'lat': 12.9716, 'lon': 77.5946, 'area_type': 'urban_core', 'name': 'CBD (Majestic)'},
        {'lat': 12.9200, 'lon': 77.6200, 'area_type': 'residential', 'name': 'Koramangala'},
        {'lat': 13.0400, 'lon': 77.5600, 'area_type': 'industrial', 'name': 'Peenya'},
        {'lat': 12.9300, 'lon': 77.5600, 'area_type': 'green', 'name': 'Banerghatta Forest'},
        {'lat': 12.8400, 'lon': 77.6790, 'area_type': 'urban_core', 'name': 'Electronic City'},
    ]
    
    temp_grid = []
    for point in points:
        offset_map = {'urban_core': 3.5, 'industrial': 2.5, 'residential': 1.5, 'green': -1.5}
        offset = np.random.normal(offset_map.get(point['area_type'], 0), 0.7)
        temp = base_temp + offset
        temp_grid.append({'lat': point['lat'], 'lon': point['lon'], 'temp': max(25, min(45, temp)), 'name': point['name']})
        
    return temp_grid

def create_heat_map(stakeholder: str):
    st.header("🌡️ Urban Heat Islands Analysis - Live Data Grounding")
    
    weather_data = fetch_weather_data(BENGALURU_LAT, BENGALURU_LON)
    current_temp = weather_data['current_temp']
    daily_trend_df = weather_data['daily_trend']
    
    if weather_data['success']:
        st.success(f"Real-time Base Temperature (2m Air): **{current_temp:.1f}°C** (Source: Open-Meteo)")
    else:
         st.error("Using mock data for temperature due to API error.")
    
    with st.container(border=True):
        st.subheader(f"Focus for {stakeholder}")
        if stakeholder == "BBMP (City Planning)":
            st.markdown("🏛️ Use heat island data to plan green corridors and prioritize tree plantation areas for heat mitigation.")
        elif stakeholder == "Citizens":
            st.markdown("👥 Identify the coolest routes for commuting and report heat-related issues in your neighborhood.")
        else:
            st.markdown("🌳 Identify critical areas needing immediate green cover intervention.")

    col1, col2, col3 = st.columns(3)
    with col1: st.selectbox("Time Period:", ["Current", "Daily Forecast"], key="time_period_select")
    with col2: st.selectbox("Temperature Layer:", ["Simulated Surface Temperature (UHI)", "2m Air Temperature"], key="temp_layer_select")
    with col3: st.selectbox("Overlay Data:", ["None", "NDVI (Vegetation)", "Population Density"], key="overlay_data_select")
    
    st.subheader("🗺️ Live Heat Island Map")
    heat_map = create_base_map()
    temp_grid = get_temperature_grid(current_temp)
    heat_data = [[p['lat'], p['lon'], p['temp']] for p in temp_grid]
    
    HeatMap(heat_data, radius=15, blur=10, min_opacity=0.4, max_val=40, gradient={0.0: 'blue', 0.5: 'green', 0.85: 'orange', 1.0: 'red'}).add_to(heat_map)
    for point in temp_grid:
        folium.CircleMarker(
            location=[point['lat'], point['lon']], radius=4,
            color=f"#{'FF0000' if point['temp'] > current_temp + 3 else '008000'}",
            fill=True, fillOpacity=0.9,
            popup=f"**{point['name']}**<br>Simulated Temp: **{point['temp']:.1f}°C**",
        ).add_to(heat_map)

    st_folium(heat_map, width=900, height=550, key="heat_map_display", returned_objects=[])

    # --- 2. Interactive Data and Trends ---
    st.markdown("---")
    col1, col2 = st.columns([1.5, 2])
    with col1:
        st.subheader("📊 Current Zone Temperature Anomaly")
        temp_stats = pd.DataFrame(temp_grid).rename(columns={'temp': 'Simulated Temp (°C)'})
        temp_stats['Anomaly (°C)'] = (temp_stats['Simulated Temp (°C)'] - current_temp).round(1)
        temp_stats['Heat Index'] = np.select(
            [temp_stats['Anomaly (°C)'] > 3.0, temp_stats['Anomaly (°C)'] > 1.5],
            ['Extreme', 'High'], default='Moderate'
        )
        temp_stats = temp_stats[['name', 'Simulated Temp (°C)', 'Anomaly (°C)', 'Heat Index']]
        temp_stats.set_index('name', inplace=True)
        st.dataframe(temp_stats, use_container_width=True)

    with col2:
        st.subheader("📈 7-Day Temperature Forecast")
        if daily_trend_df is not None:
            trend_display_df = daily_trend_df.groupby('Date')[['Max_Temp', 'Min_Temp', 'Average']].first().reset_index()
            fig = px.line(trend_display_df, x='Date', y=['Max_Temp', 'Min_Temp', 'Average'],
                          title='Air Temperature Forecast (Next 7 Days)',
                          labels={'value': 'Temperature (°C)', 'variable': 'Metric'})
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.warning("Cannot display forecast due to API error.")

# --- STREAMLIT APP ENTRY POINT ---

if __name__ == "__main__":
    st.set_page_config(
        page_title="Climate-Resilient Bengaluru Dashboard",
        page_icon="🛰️",
        layout="wide"
    )
        
    st.sidebar.title("🎯 Dashboard Navigation")
    st.sidebar.markdown("---")
    
    stakeholder_select = st.sidebar.selectbox(
        "Select Stakeholder View:", 
        ["Citizens", "BBMP (City Planning)", "Parks Department", "General"],
        key="main_stakeholder_select"
    )
    st.sidebar.markdown("---")

    # Use tabs for a cleaner, multi-module dashboard structure
    tab1, tab2 = st.tabs(["🌡️ Urban Heat Map", "🌬️ Air Quality"])

    with tab1:
        create_heat_map(stakeholder_select)

    with tab2:
        create_air_quality_dashboard(stakeholder_select)

    st.markdown("---")
    st.markdown(f"**Data Source:** Air Quality is Mock Data | Weather is Open-Meteo API | **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
