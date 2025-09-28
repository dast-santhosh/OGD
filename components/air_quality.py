import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
from utils.map_utils import create_base_map
from data.bengaluru_data import get_air_quality_stations

def create_air_quality_dashboard(stakeholder):
    st.header("🌬️ Air Quality & Pollution Monitoring")
    
    # Stakeholder-specific information
    if stakeholder == "Citizens":
        st.info("👥 **Citizen View:** Check air quality before outdoor activities and report pollution sources.")
    elif stakeholder == "BBMP (City Planning)":
        st.info("🏛️ **BBMP Focus:** Identify pollution hotspots for traffic management and green belt planning.")
    elif stakeholder == "Researchers":
        st.info("🔬 **Research Focus:** Analyze pollution patterns and their correlation with health impacts.")
    
    # Air quality controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pollutant = st.selectbox(
            "Pollutant Type:",
            ["PM2.5", "PM10", "NO2", "SO2", "CO", "Ozone", "AQI Overall"]
        )
    
    with col2:
        time_period = st.selectbox(
            "Time Period:",
            ["Current Hour", "Last 24 Hours", "Weekly Average", "Monthly Trend"]
        )
    
    with col3:
        visualization = st.selectbox(
            "Visualization:",
            ["Heat Map", "Contour Map", "Station Points", "Wind Patterns"]
        )
    
    # Air quality map
    st.subheader("🗺️ Air Quality Distribution Map")
    
    air_map = create_base_map()
    
    # Get air quality monitoring stations
    stations = get_air_quality_stations()
    
    # Add air quality markers
    for station in stations:
        # Determine AQI category and color
        aqi = station['aqi']
        if aqi <= 50:
            color = 'green'
            category = 'Good'
        elif aqi <= 100:
            color = 'yellow'
            category = 'Moderate'
        elif aqi <= 150:
            color = 'orange'
            category = 'Unhealthy for Sensitive'
        elif aqi <= 200:
            color = 'red'
            category = 'Unhealthy'
        else:
            color = 'purple'
            category = 'Very Unhealthy'
        
        folium.CircleMarker(
            location=[station['lat'], station['lon']],
            radius=10,
            popup=f"""
            <b>{station['name']}</b><br>
            AQI: {station['aqi']}<br>
            Category: {category}<br>
            PM2.5: {station['pm25']} μg/m³<br>
            PM10: {station['pm10']} μg/m³<br>
            NO2: {station['no2']} μg/m³
            """,
            color=color,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(air_map)
    
    # Add pollution source markers
    pollution_sources = [
        {'lat': 12.9716, 'lon': 77.5946, 'type': 'Traffic Hub', 'name': 'Silk Board'},
        {'lat': 12.9698, 'lon': 77.7500, 'type': 'Industrial', 'name': 'Whitefield Industrial'},
        {'lat': 12.9352, 'lon': 77.6245, 'type': 'Construction', 'name': 'Electronic City'},
        {'lat': 12.9833, 'lon': 77.6167, 'type': 'Commercial', 'name': 'Commercial Street'}
    ]
    
    for source in pollution_sources:
        icon_color = 'black' if source['type'] == 'Industrial' else 'darkred'
        folium.Marker(
            location=[source['lat'], source['lon']],
            popup=f"Pollution Source: {source['type']} - {source['name']}",
            icon=folium.Icon(color=icon_color, icon='exclamation-triangle')
        ).add_to(air_map)
    
    map_data = st_folium(air_map, width=700, height=500)
    
    # Air quality metrics dashboard
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Current Air Quality Status")
        current_aqi_df = pd.DataFrame({
            'Station': ['City Railway Station', 'Hebbal', 'BTM Layout', 'Silk Board', 'Whitefield', 'Electronic City'],
            'AQI': [156, 132, 178, 203, 145, 189],
            'PM2.5 (μg/m³)': [68, 52, 89, 112, 58, 94],
            'PM10 (μg/m³)': [98, 76, 125, 156, 82, 134],
            'NO2 (μg/m³)': [45, 38, 52, 67, 41, 58],
            'Category': ['Unhealthy', 'Unhealthy', 'Unhealthy', 'Very Unhealthy', 'Unhealthy', 'Unhealthy']
        })
        st.dataframe(current_aqi_df, width='stretch')
    
    with col2:
        st.subheader("📈 24-Hour AQI Trend")
        # Create hourly AQI trend
        hours = pd.date_range(start=datetime.now() - timedelta(hours=23), end=datetime.now(), freq='H')
        aqi_trend = pd.DataFrame({
            'Time': hours,
            'City Average': np.random.normal(165, 25, 24),
            'Silk Board': np.random.normal(203, 30, 24),
            'Hebbal': np.random.normal(132, 20, 24)
        })
        
        fig = px.line(aqi_trend, x='Time', y=['City Average', 'Silk Board', 'Hebbal'],
                     title='24-Hour AQI Trend',
                     labels={'value': 'AQI Value', 'variable': 'Location'})
        
        # Add AQI category lines
        fig.add_hline(y=50, line_dash="dash", line_color="green", annotation_text="Good")
        fig.add_hline(y=100, line_dash="dash", line_color="yellow", annotation_text="Moderate")
        fig.add_hline(y=150, line_dash="dash", line_color="orange", annotation_text="Unhealthy for Sensitive")
        fig.add_hline(y=200, line_dash="dash", line_color="red", annotation_text="Unhealthy")
        
        st.plotly_chart(fig, width='stretch')
    
    # Pollutant breakdown
    st.subheader("🔬 Pollutant Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # PM2.5 vs PM10 comparison
        pollutant_data = pd.DataFrame({
            'Location': ['City Railway', 'Hebbal', 'BTM Layout', 'Silk Board', 'Whitefield', 'Electronic City'],
            'PM2.5': [68, 52, 89, 112, 58, 94],
            'PM10': [98, 76, 125, 156, 82, 134]
        })
        
        fig = px.bar(pollutant_data, x='Location', y=['PM2.5', 'PM10'],
                    title='PM2.5 vs PM10 Levels by Location',
                    labels={'value': 'Concentration (μg/m³)'})
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        # Air quality health impact
        health_impact_df = pd.DataFrame({
            'Age Group': ['Children (0-14)', 'Adults (15-64)', 'Elderly (65+)', 'Pregnant Women'],
            'Risk Level': ['Very High', 'High', 'Very High', 'High'],
            'Recommended Action': ['Stay Indoors', 'Limit Outdoor Activity', 'Stay Indoors', 'Avoid Outdoors'],
            'Health Effects': ['Respiratory Issues', 'Eye Irritation', 'Heart Problems', 'Breathing Difficulty']
        })
        st.dataframe(health_impact_df, width='stretch')
    
    # Weekly air quality forecast
    st.subheader("🔮 7-Day Air Quality Forecast")
    
    forecast_dates = pd.date_range(start=datetime.now(), periods=7, freq='D')
    forecast_df = pd.DataFrame({
        'Date': forecast_dates,
        'Predicted AQI': [165, 142, 178, 156, 189, 134, 167],
        'Weather': ['Cloudy', 'Sunny', 'Rainy', 'Partly Cloudy', 'Sunny', 'Windy', 'Cloudy'],
        'Category': ['Unhealthy', 'Unhealthy', 'Unhealthy', 'Unhealthy', 'Unhealthy', 'Unhealthy', 'Unhealthy']
    })
    
    fig = px.bar(forecast_df, x='Date', y='Predicted AQI', color='Category',
                title='7-Day AQI Forecast',
                labels={'Predicted AQI': 'AQI Value'})
    st.plotly_chart(fig, width='stretch')
    
    # Recommendations based on stakeholder
    st.subheader("💡 Air Quality Recommendations")
    
    if stakeholder == "Citizens":
        st.markdown("""
        - **Current Status:** Air quality is unhealthy - limit outdoor activities
        - **Best Times:** Early morning (6-8 AM) has relatively better air quality
        - **Protection:** Use N95 masks when outdoors, especially near traffic areas
        - **Health:** Monitor children and elderly for respiratory symptoms
        """)
    elif stakeholder == "BBMP (City Planning)":
        st.markdown("""
        - **Traffic Management:** Implement odd-even vehicle scheme during high pollution days
        - **Green Barriers:** Plant trees along major roads to reduce PM levels
        - **Industrial Control:** Enforce stricter emission norms for industries
        - **Public Transport:** Increase Metro and bus frequency to reduce private vehicle usage
        """)
    elif stakeholder == "Researchers":
        st.markdown("""
        - **Data Correlation:** PM2.5 levels show 80% correlation with traffic density
        - **Seasonal Patterns:** Winter months show 40% higher pollution levels
        - **Health Impact:** 15% increase in respiratory admissions during high AQI days
        - **Mitigation:** Green cover increase of 10% could reduce PM levels by 25%
        """)
