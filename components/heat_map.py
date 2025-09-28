import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.map_utils import create_base_map
from data.bengaluru_data import get_bengaluru_coordinates, get_temperature_grid

def create_heat_map(stakeholder):
    st.header("🌡️ Urban Heat Islands Analysis")
    
    # Stakeholder-specific information
    if stakeholder == "BBMP (City Planning)":
        st.info("🏛️ **BBMP Focus:** Use heat island data to plan green corridors and prioritize tree plantation areas.")
    elif stakeholder == "Citizens":
        st.info("👥 **Citizen View:** Find cooler neighborhoods and report heat-related issues in your area.")
    elif stakeholder == "Parks Department":
        st.info("🌳 **Parks Dept:** Identify critical areas needing immediate green cover intervention.")
    
    # Temperature analysis controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        time_period = st.selectbox(
            "Time Period:",
            ["Current", "Daily Average", "Weekly Trend", "Monthly Comparison"]
        )
    
    with col2:
        temperature_layer = st.selectbox(
            "Temperature Layer:",
            ["Surface Temperature", "Air Temperature", "Heat Index", "Temperature Anomaly"]
        )
    
    with col3:
        overlay_data = st.selectbox(
            "Overlay Data:",
            ["None", "NDVI (Vegetation)", "Population Density", "Building Density"]
        )
    
    # Temperature map
    st.subheader("🗺️ Heat Island Map")
    
    # Create base map
    heat_map = create_base_map()
    
    # Get temperature grid data
    temp_grid = get_temperature_grid()
    
    # Add heat map layer
    heat_data = []
    for point in temp_grid:
        # Simulate temperature variations based on location characteristics
        base_temp = 32.0
        if point['area_type'] == 'urban_core':
            temp = base_temp + np.random.normal(3.5, 1.0)
        elif point['area_type'] == 'residential':
            temp = base_temp + np.random.normal(1.5, 0.8)
        elif point['area_type'] == 'industrial':
            temp = base_temp + np.random.normal(4.0, 1.2)
        elif point['area_type'] == 'green':
            temp = base_temp + np.random.normal(-1.5, 0.5)
        else:
            temp = base_temp + np.random.normal(0, 1.0)
        
        heat_data.append([point['lat'], point['lon'], max(25, min(45, temp))])
    
    # Add heat map to folium
    from folium.plugins import HeatMap
    HeatMap(heat_data, radius=15, blur=10, gradient={
        0.0: 'blue',
        0.3: 'green', 
        0.5: 'yellow',
        0.7: 'orange',
        1.0: 'red'
    }).add_to(heat_map)
    
    # Display map
    map_data = st_folium(heat_map, width=700, height=500)
    
    # Temperature statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Temperature Statistics")
        temp_stats = pd.DataFrame({
            'Zone': ['CBD', 'Electronic City', 'Whitefield', 'Koramangala', 'Indiranagar', 'Hebbal'],
            'Current Temp (°C)': [36.2, 34.8, 35.1, 33.9, 34.3, 32.1],
            'Daily Max (°C)': [38.5, 36.2, 37.1, 35.8, 36.0, 34.2],
            'Heat Index': ['Extreme', 'High', 'High', 'Moderate', 'High', 'Moderate']
        })
        st.dataframe(temp_stats, width='stretch')
    
    with col2:
        st.subheader("📈 Temperature Trend")
        # Create temperature trend chart
        dates = pd.date_range(start=datetime.now() - timedelta(days=6), end=datetime.now(), freq='D')
        trend_data = pd.DataFrame({
            'Date': dates,
            'Max Temp': [35.2, 36.1, 37.8, 38.2, 36.9, 35.4, 36.2],
            'Min Temp': [24.1, 25.2, 26.1, 25.8, 24.9, 23.8, 24.5],
            'Average': [29.7, 30.7, 31.9, 32.0, 30.9, 29.6, 30.4]
        })
        
        fig = px.line(trend_data, x='Date', y=['Max Temp', 'Min Temp', 'Average'],
                     title='7-Day Temperature Trend',
                     labels={'value': 'Temperature (°C)', 'variable': 'Metric'})
        st.plotly_chart(fig, width='stretch')
    
    # Heat vulnerability analysis
    st.subheader("🎯 Heat Vulnerability Analysis")
    
    vulnerability_df = pd.DataFrame({
        'Ward': ['Mahadevapura', 'Bommanahalli', 'Yelahanka', 'Dasarahalli', 'East Zone'],
        'Heat Risk Score': [8.2, 7.8, 6.4, 7.1, 8.5],
        'Population Exposed': [125000, 98000, 87000, 76000, 142000],
        'Green Cover %': [12, 15, 22, 18, 8],
        'Priority Level': ['Critical', 'High', 'Medium', 'High', 'Critical']
    })
    
    st.dataframe(vulnerability_df, width='stretch')
    
    # Recommendations based on stakeholder
    st.subheader("💡 Recommended Actions")
    
    if stakeholder == "BBMP (City Planning)":
        st.markdown("""
        - **Immediate:** Deploy mobile cooling centers in high-risk areas
        - **Short-term:** Increase tree plantation by 40% in CBD and Electronic City
        - **Long-term:** Implement green building codes and rooftop gardens mandate
        """)
    elif stakeholder == "Citizens":
        st.markdown("""
        - **Stay hydrated** and avoid outdoor activities between 11 AM - 4 PM
        - **Use public transport** during peak heat hours
        - **Report heat-related health issues** through the community module
        """)
    elif stakeholder == "Parks Department":
        st.markdown("""
        - **Priority areas:** CBD, Electronic City, and East Zone need immediate intervention
        - **Species selection:** Use native drought-resistant trees
        - **Maintenance:** Increase watering frequency for existing green cover
        """)
