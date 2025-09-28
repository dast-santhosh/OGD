import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utils.map_utils import create_base_map
from streamlit_folium import st_folium
import folium

def create_air_quality_dashboard(stakeholder):
    """Generates the Air Quality Dashboard module."""
    st.header("🌬️ Air Quality Monitoring Dashboard")

    if stakeholder == "Citizens":
        st.info("👥 **Citizen View:** Monitor local air quality and understand health risks. Note: AQI is currently Moderate.")
    elif stakeholder == "BBMP (City aPlanning)":
        st.info("🏛️ **BBMP Focus:** Identify pollution hotspots and target areas for traffic regulation or industrial controls.")
    else:
        st.info(f"The **{stakeholder}** view focuses on key pollutants and trends.")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Current AQI", "156 (Moderate)", "Avg. 24h: 148")
        st.markdown("---")
        st.subheader("Key Pollutant Levels (μg/m³)")
        
        # Mock pollutant data
        pollutant_data = {
            "Pollutant": ["PM2.5", "PM10", "NO2", "SO2"],
            "Value": [68, 120, 45, 15],
            "Standard Limit": [40, 100, 80, 40]
        }
        pollutant_df = pd.DataFrame(pollutant_data)
        st.dataframe(pollutant_df, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("AQI Trend (Last 7 Days)")
        dates = pd.date_range(start=datetime.now() - timedelta(days=6), end=datetime.now(), freq='D')
        aqi_trend = pd.DataFrame({
            'Date': dates,
            'AQI': [135, 140, 150, 165, 158, 148, 156]
        })
        fig = px.bar(aqi_trend, x='Date', y='AQI', title='AQI Daily Average',
                     color='AQI', color_continuous_scale=px.colors.sequential.Plasma_r)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
    st.subheader("Air Quality Monitoring Stations")
    aq_map = create_base_map()
    
    # Mock monitoring stations
    stations = [
        {'lat': 12.975, 'lon': 77.58, 'name': 'City Centre', 'aqi': 156},
        {'lat': 12.92, 'lon': 77.65, 'name': 'Whitefield', 'aqi': 122},
        {'lat': 13.0, 'lon': 77.55, 'name': 'Peenya', 'aqi': 195},
    ]

    for station in stations:
        color = 'red' if station['aqi'] > 180 else ('orange' if station['aqi'] > 100 else 'green')
        folium.Marker(
            location=[station['lat'], station['lon']],
            popup=f"{station['name']} - AQI: {station['aqi']}",
            icon=folium.Icon(color=color, icon='cloud', prefix='fa')
        ).add_to(aq_map)
        
    st_folium(aq_map, width=700, height=500, key="aqi_map")
