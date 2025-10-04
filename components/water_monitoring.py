import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any

# --- CONFIGURATION & CONSTANTS ---
BENGALURU_LAT = 12.9716
BENGALURU_LON = 77.5946
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
AQI_API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WATER_API_URL = "https://api.open-meteo.com/v1/forecast" # Re-using standard API for soil moisture and rain

# --- UTILITY FUNCTIONS ---

def get_bengaluru_coordinates() -> List[float]:
    """Returns the central coordinates for Bengaluru."""
    return [BENGALURU_LAT, BENGALURU_LON]

def create_base_map(lat: float = BENGALURU_LAT, lon: float = BENGALURU_LON, zoom: int = 11) -> folium.Map:
    """Creates a base Folium map centered on Bengaluru."""
    base_map = folium.Map(location=[lat, lon], zoom_start=zoom, tiles="cartodbdarkmatter")
    return base_map

def get_lake_locations() -> List[Dict[str, Any]]:
    """Provides mock data for major Bengaluru lakes. (Lake Health scores are simulated)"""
    return [
        {'name': 'Bellandur Lake', 'lat': 12.937, 'lon': 77.683, 'health_score': 3.2, 'area_hectares': 361, 'pollution_level': 'Very High'},
        {'name': 'Varthur Lake', 'lat': 12.937, 'lon': 77.728, 'health_score': 4.1, 'area_hectares': 220, 'pollution_level': 'High'},
        {'name': 'Ulsoor Lake', 'lat': 12.977, 'lon': 77.615, 'health_score': 6.8, 'area_hectares': 50, 'pollution_level': 'Moderate'},
        {'name': 'Sankey Tank', 'lat': 13.007, 'lon': 77.581, 'health_score': 7.5, 'area_hectares': 15, 'pollution_level': 'Low'},
        {'name': 'Hebbal Lake', 'lat': 13.045, 'lon': 77.595, 'health_score': 5.9, 'area_hectares': 75, 'pollution_level': 'Moderate'},
        {'name': 'Agara Lake', 'lat': 12.915, 'lon': 77.636, 'health_score': 4.7, 'area_hectares': 80, 'pollution_level': 'High'}
    ]

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

# --- API INTEGRATION ---

@st.cache_data(ttl=3600) # Cache the data for 1 hour
def fetch_weather_data(lat: float, lon: float) -> Dict[str, Any]:
    """Fetches current temperature and forecast from Open-Meteo."""
    # ... (omitted for brevity, assume this function is robust and returns weather data) ...
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


@st.cache_data(ttl=3600) # Cache the data for 1 hour
def fetch_air_quality_data(lat: float, lon: float) -> Dict[str, Any]:
    # ... (omitted for brevity, assume this function is robust and returns air quality data) ...
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["european_aqi", "pm10", "pm2_5", "nitrogen_dioxide", "sulphur_dioxide", "ozone"],
        "timezone": "Asia/Kolkata",
        "forecast_days": 7
    }
    
    # Define a consistent mock data fallback structure
    now = datetime.now()
    mock_hours = pd.to_datetime(pd.date_range(end=now, periods=24*7, freq='H'))
    mock_daily_dates = pd.date_range(end=now.date(), periods=7, freq='D').date
    current_aqi_mock = 55.0 # Moderate fallback value
    
    mock_pollutant_values = [28.0, 45.0, 25.0, 10.0, 40.0] 
    
    mock_data = {
        'success': False,
        'current_aqi': current_aqi_mock,
        'pollutant_data_df': pd.DataFrame({
            "Pollutant": ["$\text{PM}_{2.5}$", "$\text{PM}_{10}$", "$\text{NO}_{2}$", "$\text{SO}_{2}$", "$\text{O}_{3}$"],
            "Value ($\mu g / m^3$)": mock_pollutant_values, 
            "EAC Limit": [25, 50, 40, 20, 100]
        }),
        'daily_trend_df': pd.DataFrame({
            'Date': mock_daily_dates,
            'AQI': [42, 48, 52, 58, 65, 50, current_aqi_mock]
        }),
        'stream_long_df': pd.DataFrame({
            'Time': mock_hours,
            'PM2.5': np.random.uniform(15, 40, size=len(mock_hours)),
            'PM10': np.random.uniform(30, 60, size=len(mock_hours)),
            'NO2': np.random.uniform(15, 35, size=len(mock_hours)),
            'SO2': np.random.uniform(5, 15, size=len(mock_hours)),
            'O3': np.random.uniform(30, 50, size=len(mock_hours)),
        }).melt(id_vars=['Time'], value_vars=['PM2.5', 'PM10', 'NO2', 'SO2', 'O3'], var_name='Pollutant', value_name='Concentration')
    }
    
    try:
        response = requests.get(AQI_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        hourly_data = data.get('hourly', {})
        times = [datetime.fromisoformat(t) for t in hourly_data['time']]
        
        # 1. Current AQI - Find the latest non-null AQI value
        aqi_values = hourly_data.get('european_aqi', [])
        latest_aqi = next((aqi for aqi in reversed(aqi_values) if aqi is not None), mock_data['current_aqi'])
        
        # Determine the index of the latest AQI value
        try:
            latest_index = len(aqi_values) - 1 - aqi_values[::-1].index(latest_aqi) if latest_aqi in aqi_values else -1
        except ValueError:
            latest_index = len(aqi_values) - 1
            
        # 2. Pollutant Data (use the same index as the latest AQI, fallback to mock if API returns None)
        pollutant_map = {
            "$\text{PM}_{2.5}$": hourly_data.get('pm2_5', [None])[latest_index] if latest_index != -1 else None,
            "$\text{PM}_{10}$": hourly_data.get('pm10', [None])[latest_index] if latest_index != -1 else None,
            "$\text{NO}_{2}$": hourly_data.get('nitrogen_dioxide', [None])[latest_index] if latest_index != -1 else None,
            "$\text{SO}_{2}$": hourly_data.get('sulphur_dioxide', [None])[latest_index] if latest_index != -1 else None,
            "$\text{O}_{3}$": hourly_data.get('ozone', [None])[latest_index] if latest_index != -1 else None
        }

        pollutant_df_real = pd.DataFrame({
            "Pollutant": ["$\text{PM}_{2.5}$", "$\text{PM}_{10}$", "$\text{NO}_{2}$", "$\text{SO}_{2}$", "$\text{O}_{3}$"],
            "Value ($\mu g / m^3$)": [pollutant_map.get(p) if pollutant_map.get(p) is not None else mock_pollutant_values[i] for i, p in enumerate(["$\text{PM}_{2.5}$", "$\text{PM}_{10}$", "$\text{NO}_{2}$", "$\text{SO}_{2}$", "$\text{O}_{3}$"])], 
            "EAC Limit": [25, 50, 40, 20, 100]
        })

        # 3. Daily Trend DF
        hourly_df = pd.DataFrame({
            'Time': times,
            'AQI': hourly_data.get('european_aqi', [])
        }).dropna(subset=['AQI'])
        
        hourly_df['Date'] = hourly_df['Time'].dt.date
        daily_trend_df_real = hourly_df.groupby('Date')['AQI'].mean().reset_index().rename(columns={'AQI': 'AQI'})
        
        # 4. Streamgraph DF
        stream_df_real = pd.DataFrame({
            'Time': times,
            'PM2.5': hourly_data.get('pm2_5', []),
            'PM10': hourly_data.get('pm10', []),
            'NO2': hourly_data.get('nitrogen_dioxide', []),
            'SO2': hourly_data.get('sulphur_dioxide', []),
            'O3': hourly_data.get('ozone', []),
        })
        # Keep only the last 7 days of hourly data for the streamgraph
        stream_df_real = stream_df_real.dropna(subset=['PM2.5', 'PM10', 'NO2', 'SO2', 'O3']).tail(24 * 7)

        pollutant_cols = ['PM2.5', 'PM10', 'NO2', 'SO2', 'O3']
        stream_long_real = stream_df_real.melt(id_vars=['Time'], value_vars=pollutant_cols, 
                                               var_name='Pollutant', value_name='Concentration')

        return {
            'success': True,
            'current_aqi': latest_aqi,
            'pollutant_data_df': pollutant_df_real,
            'daily_trend_df': daily_trend_df_real,
            'stream_long_df': stream_long_real
        }
    except requests.exceptions.RequestException as e:
        st.error(f"Air Quality API call failed. Displaying mock data for fall-back. Error: {e}")
        return mock_data
    except Exception as e:
        st.error(f"An unexpected error occurred while processing AQI data. Displaying mock data for fall-back. Error: {e}")
        return mock_data


@st.cache_data(ttl=3600) # Cache the data for 1 hour
def fetch_water_related_data(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetches live precipitation and soil moisture data from Open-Meteo.
    This data is used as a proxy for Flood Risk and Groundwater/Lake levels.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["precipitation", "soil_moisture_0_1cm", "soil_moisture_1_3cm"],
        "current": "soil_moisture_0_1cm",
        "timezone": "Asia/Kolkata",
        "forecast_days": 7
    }

    # Define mock data fallback
    now = datetime.now()
    mock_times = pd.to_datetime(pd.date_range(end=now + timedelta(days=7), periods=24*7, freq='H'))
    
    mock_data = {
        'success': False,
        'current_soil_moisture': 0.35, # Moderate moisture content
        'daily_precipitation': pd.DataFrame({
            'Date': mock_times.date.unique()[:7],
            'Rainfall (mm)': [0, 0.5, 5.0, 15.2, 8.1, 0, 0]
        }),
        'soil_moisture_trend': pd.DataFrame({
            'Time': mock_times.normalize(),
            'Soil Moisture (0-1cm)': np.clip(np.random.normal(0.35, 0.05, len(mock_times)), 0.1, 0.5)
        }).groupby('Time').mean().reset_index().rename(columns={'Time': 'Date'})
    }

    try:
        response = requests.get(WATER_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        hourly_data = data.get('hourly', {})
        times = pd.to_datetime([datetime.fromisoformat(t) for t in hourly_data['time']])
        
        # 1. Current Soil Moisture (0-1cm)
        current_moisture = data.get('current', {}).get('soil_moisture_0_1cm', mock_data['current_soil_moisture'])
        
        # 2. Daily Precipitation Trend
        hourly_df = pd.DataFrame({
            'Time': times,
            'Precipitation': hourly_data.get('precipitation', [])
        }).dropna()
        
        hourly_df['Date'] = hourly_df['Time'].dt.date
        daily_precipitation = hourly_df.groupby('Date')['Precipitation'].sum().reset_index().rename(columns={'Precipitation': 'Rainfall (mm)'})
        
        # 3. Soil Moisture Trend
        soil_moisture_trend = pd.DataFrame({
            'Time': times,
            'Soil Moisture (0-1cm)': hourly_data.get('soil_moisture_0_1cm', [])
        }).dropna()
        
        soil_moisture_trend['Date'] = soil_moisture_trend['Time'].dt.date
        daily_soil_moisture = soil_moisture_trend.groupby('Date')['Soil Moisture (0-1cm)'].mean().reset_index()

        return {
            'success': True,
            'current_soil_moisture': current_moisture,
            'daily_precipitation': daily_precipitation.head(7),
            'soil_moisture_trend': daily_soil_moisture.head(7)
        }
    except requests.exceptions.RequestException as e:
        st.error(f"Water/Soil API call failed. Displaying mock data for fall-back. Error: {e}")
        return mock_data
    except Exception as e:
        st.error(f"An unexpected error occurred while processing Water data. Displaying mock data for fall-back. Error: {e}")
        return mock_data

# --- DASHBOARD COMPONENTS ---

def create_air_quality_dashboard(stakeholder):
    """Generates the Air Quality Dashboard module using live API data with mock data fallback."""
    
    aqi_data = fetch_air_quality_data(BENGALURU_LAT, BENGALURU_LON)
    
    # Assign fetched data to local variables for clarity
    current_aqi = aqi_data['current_aqi']
    current_category = get_aqi_category(current_aqi)
    pollutant_df = aqi_data['pollutant_data_df']
    daily_trend_df = aqi_data['daily_trend_df']
    stream_long_df = aqi_data['stream_long_df']
    
    st.header("🌬️ Air Quality Monitoring Dashboard")
    
    if aqi_data['success']:
        st.info("✅ Displaying **Live Air Quality Data** (Source: Open-Meteo Air Quality API).")
    else:
        st.warning("⚠️ Could not connect to the live Air Quality API. Displaying **Mock Data** as a fallback.")

    # --- CHART GENERATION ---
    
    # 1. Streamgraph
    fig_stream = px.area(
        stream_long_df, x='Time', y='Concentration', color='Pollutant',
        title='Hourly Pollutant Stacked Trend (Last 7 Days)', template='plotly_white',
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
        st.info(f"👥 **Citizen View:** Current AQI is **{current_category}**. Consult your local health guidelines.")
    elif stakeholder == "BBMP (City Planning)":
        st.info(f"🏛️ **BBMP Focus:** Current AQI is **{current_category}**. Analyze pollutant mix for source mitigation.")
    else:
        st.info(f"The **{stakeholder}** view focuses on key pollutants and trends.")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Current Status (EAC Index)")
        # Display AQI safely
        display_aqi = f"{current_aqi:.0f}"
        st.metric("European AQI", display_aqi, help="European Air Quality Index (EAC) based on live/mock data.")
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
    
    # Simulate variations around the current AQI
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

def create_heat_map(stakeholder: str):
    st.header("🌡️ Urban Heat Islands Analysis - Live Data Grounding")
    
    weather_data = fetch_weather_data(BENGALURU_LAT, BENGALURU_LON)
    current_temp = weather_data['current_temp']
    daily_trend_df = weather_data['daily_trend']
    
    if weather_data['success']:
        st.success(f"Real-time Base Temperature (2m Air): **{current_temp:.1f}°C** (Source: Open-Meteo)")
    else:
         st.error("Using mock data for temperature due to API error.")
    
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


def create_water_dashboard(stakeholder):
    """Generates the Water Bodies & Flood Risk Monitoring dashboard."""
    
    water_data = fetch_water_related_data(BENGALURU_LAT, BENGALURU_LON)
    
    # Extract live/proxied data
    current_soil_moisture = water_data['current_soil_moisture']
    daily_precipitation = water_data['daily_precipitation']
    soil_moisture_trend = water_data['soil_moisture_trend']

    st.header("💧 Water Bodies & Flood Risk Monitoring")
    
    if water_data['success']:
        st.info(f"✅ Displaying **Live Precipitation and Soil Moisture** data (Source: Open-Meteo). Lake Health and Quality are simulated.")
    else:
        st.warning("⚠️ Could not connect to the live Open-Meteo API for water data. Displaying **Mock Data**.")
    
    # Stakeholder-specific information
    if stakeholder == "BWSSB (Water Board)":
        st.info("🚰 **BWSSB Focus:** Monitor water quality, lake health, and supply sustainability.")
    elif stakeholder == "Citizens":
        st.info("👥 **Citizen View:** Track water quality in your area and report pollution incidents.")
    elif stakeholder == "BBMP (City Planning)":
        st.info("🏛️ **BBMP Focus:** Flood risk assessment and drainage infrastructure planning.")
    
    # Water monitoring controls (still interactive but based on proxies)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        monitoring_type = st.selectbox(
            "Monitoring Type:",
            ["Lake Health (Simulated)", "Water Quality (Simulated)", "Flood Risk (Proxied)", "Groundwater Levels (Proxied)"]
        )
    
    with col2:
        # Time range determines which part of the 7-day forecast/history is shown
        time_range = st.selectbox(
            "Time Range:",
            ["Current/Today", "7-Day Forecast", "Last Week", "Last Month (Simulated)"]
        )
    
    with col3:
        data_source = st.selectbox(
            "Data Source:",
            ["Open-Meteo (Rain/Soil)", "Ground Sensors (Simulated)", "Citizen Reports (Simulated)", "All Sources"]
        )
    
    # Water bodies map
    st.subheader("🗺️ Water Bodies Status Map")
    
    water_map = create_base_map()
    
    # Get lake data (still simulated)
    lakes = get_lake_locations()
    
    # Add lake markers with health status
    for lake in lakes:
        # Determine marker color based on health status
        if lake['health_score'] >= 7:
            color = 'green'
            status = 'Good'
        elif lake['health_score'] >= 4:
            color = 'orange'
            status = 'Moderate'
        else:
            color = 'red'
            status = 'Poor'
            
        folium.CircleMarker(
            location=[lake['lat'], lake['lon']],
            radius=12,
            popup=f"""
            <b>{lake['name']}</b><br>
            Health Score: {lake['health_score']}/10<br>
            Status: {status}<br>
            Area: {lake['area_hectares']} hectares<br>
            Pollution Level: {lake['pollution_level']}
            """,
            color=color,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(water_map)
    
    # Flood risk zones
    flood_zones = [
        {'lat': 12.9716, 'lon': 77.5946, 'area': 'Silk Board'},
        {'lat': 12.9352, 'lon': 77.6245, 'area': 'Electronic City'},
        {'lat': 12.9698, 'lon': 77.7500, 'area': 'Whitefield'},
        {'lat': 12.9833, 'lon': 77.6167, 'area': 'Koramangala'}
    ]
    
    # Flood risk is proxied by max forecast precipitation
    max_forecast_rain = daily_precipitation['Rainfall (mm)'].max() if not daily_precipitation.empty else 0.0

    if max_forecast_rain > 15:
        risk_level = 'Very High'
        risk_color = 'darkred'
    elif max_forecast_rain > 5:
        risk_level = 'High'
        risk_color = 'red'
    else:
        risk_level = 'Medium/Low'
        risk_color = 'orange'
    
    for zone in flood_zones:
        # Simulate risk variation based on location
        zone_risk_color = risk_color
        if zone['area'] == 'Silk Board' and max_forecast_rain > 5:
            zone_risk_color = 'darkred'
        
        folium.Circle(
            location=[zone['lat'], zone['lon']],
            radius=1000,
            popup=f"Flood Risk: {risk_level} - {zone['area']}<br>Proxied by Max Rain: {max_forecast_rain:.1f} mm",
            color=zone_risk_color,
            fillColor=zone_risk_color,
            fillOpacity=0.3,
            weight=2
        ).add_to(water_map)
    
    map_data = st_folium(water_map, width=900, height=550, key="water_map_display", returned_objects=[])
    
    st.markdown("---")
    
    # Water supply metrics - proxied by live soil moisture
    st.subheader("🚰 Water Supply & Soil Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # This remains mock, as MLD is a specific output metric
        st.metric("Daily Supply (MLD)", "1,450 MLD", "+50 MLD (Simulated)")
    with col2:
        soil_moisture_percentage = current_soil_moisture * 100
        # Change in moisture based on whether it is above or below a typical average (0.35)
        soil_delta = (current_soil_moisture - 0.35) * 100
        st.metric("Surface Soil Moisture", f"{soil_moisture_percentage:.1f}%", f"{soil_delta:+.1f} points (Live Proxy)")
    with col3:
        # Lake Storage is now informed by soil moisture (proxy)
        lake_storage_proxy = np.clip(65 + (current_soil_moisture - 0.35) * 50, 50, 80)
        lake_delta = (lake_storage_proxy - 65)
        st.metric("Lake Storage (Proxy)", f"{lake_storage_proxy:.0f}%", f"{lake_delta:+.1f}% (Proxy)")
    with col4:
        # Quality score remains mock
        st.metric("Quality Score (Simulated)", "7.2/10", "+0.3")

    st.markdown("---")
    
    # Flood risk analysis and trends
    col5, col6 = st.columns(2)
    
    with col5:
        st.subheader("🌊 Flood Risk: 7-Day Precipitation Forecast")
        
        fig_rain = px.bar(daily_precipitation, x='Date', y='Rainfall (mm)', 
                         title='Daily Forecasted Rainfall (Next 7 Days)',
                         labels={'Rainfall (mm)': 'Rainfall (mm)'},
                         color_discrete_sequence=['#4C78A8'])
        fig_rain.add_hline(y=10, line_dash="dash", line_color="red", annotation_text="High Flood Risk Threshold (10mm)")
        st.plotly_chart(fig_rain, use_container_width=True, config={'displayModeBar': False})

    with col6:
        st.subheader("🌱 Groundwater Proxy: Soil Moisture Trend")
        
        fig_moisture = px.line(soil_moisture_trend, x='Date', y='Soil Moisture (0-1cm)', 
                              title='7-Day Average Soil Moisture (Live Proxy)',
                              labels={'Soil Moisture (0-1cm)': 'Moisture Content (v/v)'},
                              color_discrete_sequence=['#A8A84C'])
        fig_moisture.add_hline(y=0.45, line_dash="dash", line_color="green", annotation_text="High Saturation")
        fig_moisture.add_hline(y=0.20, line_dash="dash", line_color="red", annotation_text="Drought Risk")
        st.plotly_chart(fig_moisture, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("---")
    
    # Lake Health Summary (Still simulated)
    col7, col8 = st.columns(2)
    
    with col7:
        st.subheader("📊 Lake Health Summary (Simulated)")
        lake_health_df = pd.DataFrame({
            'Lake Name': ['Bellandur', 'Varthur', 'Ulsoor', 'Sankey Tank', 'Hebbal', 'Agara'],
            'Health Score': [3.2, 4.1, 6.8, 7.5, 5.9, 4.7],
            'Area (hectares)': [361, 220, 50, 15, 75, 80],
            'Water Quality': ['Poor', 'Poor', 'Moderate', 'Good', 'Moderate', 'Poor'],
            'Pollution Source': ['Industrial', 'Sewage', 'Urban runoff', 'Minimal', 'Mixed', 'Sewage']
        })
        st.dataframe(lake_health_df, use_container_width=True)
    
    with col8:
        st.subheader("📈 Water Quality Trends (Simulated)")
        # Create water quality trend chart (retains original mock data logic)
        dates = pd.date_range(start=datetime.now() - timedelta(days=29), end=datetime.now(), freq='D')
        quality_data = pd.DataFrame({
            'Date': dates,
            'Bellandur Lake': np.random.normal(3.2, 0.5, 30),
            'Ulsoor Lake': np.random.normal(6.8, 0.3, 30),
            'Sankey Tank': np.random.normal(7.5, 0.2, 30)
        })
        
        fig = px.line(quality_data, x='Date', y=['Bellandur Lake', 'Ulsoor Lake', 'Sankey Tank'],
                      title='30-Day Water Quality Trend (Simulated)',
                      labels={'value': 'Health Score (1-10)', 'variable': 'Water Body'})
        fig.add_hline(y=5, line_dash="dash", line_color="red", annotation_text="Critical Threshold")
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Recommendations
    st.subheader("💡 Recommended Actions")
    
    if stakeholder == "BWSSB (Water Board)":
        st.markdown(f"""
        - **Flood Alert:** Monitor expected rainfall of **{daily_precipitation['Rainfall (mm)'].max():.1f} mm** on {daily_precipitation.iloc[daily_precipitation['Rainfall (mm)'].idxmax()]['Date']} for potential strain.
        - **Critical:** Immediate intervention needed for Bellandur and Varthur lakes (Simulated Health Scores).
        - **Infrastructure:** Upgrade sewage treatment capacity by 30%.
        """)
    elif stakeholder == "Citizens":
        st.markdown(f"""
        - **Flood Risk:** Be aware of potential flooding due to high precipitation forecast (Max: **{daily_precipitation['Rainfall (mm)'].max():.1f} mm**).
        - **Avoid** recreational activities in Bellandur, Varthur, and Agara lakes.
        - **Report** any sewage discharge or industrial pollution immediately.
        """)
    elif stakeholder == "BBMP (City Planning)":
        st.markdown(f"""
        - **Flood Mitigation:** Upgrade drainage in Silk Board and Electronic City immediately due to **{risk_level}** rainfall risk.
        - **Lake Restoration:** Allocate ₹200 crores for lake cleanup projects.
        - **Water Conservation:** Surface soil moisture is **{current_soil_moisture*100:.1f}%**. Continue promoting rainwater harvesting.
        """)


# --- STREAMLIT APP ENTRY POINT ---

if __name__ == "__main__":
    st.set_page_config(
        page_title="Climate-Resilient Bengaluru Dashboard",
        page_icon="🛰️",
        layout="wide"
    )
    
    # Pre-fetch data for status display
    # Note: We rely on the internal success flags to determine if live data is used.
    # The first API call for AQI is made here just to ensure it's in the cache/error is handled.
    aqi_status = fetch_air_quality_data(BENGALURU_LAT, BENGALURU_LON)
    water_status = fetch_water_related_data(BENGALURU_LAT, BENGALURU_LON)
        
    st.sidebar.title("🎯 Dashboard Navigation")
    st.sidebar.markdown("---")
    
    stakeholder_select = st.sidebar.selectbox(
        "Select Stakeholder View:", 
        ["Citizens", "BBMP (City Planning)", "BWSSB (Water Board)", "General"],
        key="main_stakeholder_select"
    )
    st.sidebar.markdown("---")

    # Use tabs for a cleaner, multi-module dashboard structure
    tab1, tab2, tab3 = st.tabs(["🌡️ Urban Heat Map", "🌬️ Air Quality", "💧 Water Monitoring"])

    with tab1:
        create_heat_map(stakeholder_select)

    with tab2:
        create_air_quality_dashboard(stakeholder_select)

    with tab3:
        create_water_dashboard(stakeholder_select)

    st.markdown("---")
    
    data_source_status = (
        f"AQI: {'Live' if aqi_status['success'] else 'Mock'} | "
        f"Water/Soil: {'Live' if water_status['success'] else 'Mock'}"
    )
    st.markdown(f"**Data Source Status:** {data_source_status} | **Base API:** Open-Meteo | **Last Checked:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
