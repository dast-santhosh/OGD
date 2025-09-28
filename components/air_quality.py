import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# This function creates a base map centered on Bengaluru.
def create_base_map():
    bengaluru_coords = [12.9716, 77.5946]
    return folium.Map(location=bengaluru_coords, zoom_start=11)

# This is a placeholder function to simulate temperature data points.
def get_temperature_grid():
    return [
        {'lat': 12.97, 'lon': 77.59, 'area_type': 'urban_core'},
        {'lat': 12.92, 'lon': 77.62, 'area_type': 'residential'},
        {'lat': 13.0, 'lon': 77.56, 'area_type': 'industrial'},
        {'lat': 12.93, 'lon': 77.56, 'area_type': 'green'}
    ]

def create_heat_map_dashboard(stakeholder):
    """
    Main function to build the Urban Heat Island dashboard UI.
    """
    st.header("🌡️ Urban Heat Islands Analysis")

    # Stakeholder-specific information
    stakeholder_info = {
        "BBMP (City Planning)": "🏛️ **BBMP Focus:** Use heat island data to plan green corridors and prioritize tree plantation areas.",
        "Citizens": "👥 **Citizen View:** Find cooler neighborhoods and report heat-related issues in your area.",
        "Parks Department": "🌳 **Parks Dept:** Identify critical areas needing immediate green cover intervention."
    }
    st.info(stakeholder_info.get(stakeholder, "Select a stakeholder to see relevant information."))

    # ---
    # User Controls Section
    st.subheader("📊 Data Controls")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.selectbox("Time Period:", ["Current", "Daily Average", "Weekly Trend", "Monthly Comparison"], key="time_period_select")
    with col2:
        st.selectbox("Temperature Layer:", ["Surface Temperature", "Air Temperature", "Heat Index", "Temperature Anomaly"], key="temp_layer_select")
    with col3:
        st.selectbox("Overlay Data:", ["None", "NDVI (Vegetation)", "Population Density", "Building Density"], key="overlay_data_select")

    # ---
    # Map Visualization Section
    st.subheader("🗺️ Heat Island Map")
    heat_map = create_base_map()
    temp_grid = get_temperature_grid()
    heat_data = []

    for point in temp_grid:
        base_temp = 32.0
        # Simulate temperature based on area type
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

    HeatMap(heat_data, radius=15, blur=10, gradient={
        0.0: 'blue', 0.3: 'green', 0.5: 'yellow', 0.7: 'orange', 1.0: 'red'
    }).add_to(heat_map)

    # Use a key to prevent the map from reloading on every rerun
    st_folium(heat_map, width=700, height=500, key="heat_map_display")
    
    # ---
    # Analytics and Recommendations Section
    st.subheader("📊 Analytics and Recommendations")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Temperature Statistics")
        temp_stats = pd.DataFrame({
            'Zone': ['CBD', 'Electronic City', 'Whitefield', 'Koramangala', 'Indiranagar', 'Hebbal'],
            'Current Temp (°C)': [36.2, 34.8, 35.1, 33.9, 34.3, 32.1],
            'Daily Max (°C)': [38.5, 36.2, 37.1, 35.8, 36.0, 34.2],
            'Heat Index': ['Extreme', 'High', 'High', 'Moderate', 'High', 'Moderate']
        })
        st.dataframe(temp_stats, use_container_width=True)

    with col2:
        st.subheader("Temperature Trend")
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
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # ---
    # Heat Vulnerability Analysis Section
    st.subheader("🎯 Heat Vulnerability Analysis")
    vulnerability_df = pd.DataFrame({
        'Ward': ['Mahadevapura', 'Bommanahalli', 'Yelahanka', 'Dasarahalli', 'East Zone'],
        'Heat Risk Score': [8.2, 7.8, 6.4, 7.1, 8.5],
        'Population Exposed': [125000, 98000, 87000, 76000, 142000],
        'Green Cover %': [12, 15, 22, 18, 8],
        'Priority Level': ['Critical', 'High', 'Medium', 'High', 'Critical']
    })
    st.dataframe(vulnerability_df, use_container_width=True)

    # ---
    # Recommended Actions Section
    st.subheader("💡 Recommended Actions")
    recommendations = {
        "BBMP (City Planning)": """
        - **Immediate:** Deploy mobile cooling centers in high-risk areas
        - **Short-term:** Increase tree plantation by 40% in CBD and Electronic City
        - **Long-term:** Implement green building codes and rooftop gardens mandate
        """,
        "Citizens": """
        - **Stay hydrated** and avoid outdoor activities between 11 AM - 4 PM
        - **Use public transport** during peak heat hours
        - **Report heat-related health issues** through the community module
        """,
        "Parks Department": """
        - **Priority areas:** CBD, Electronic City, and East Zone need immediate intervention
        - **Species selection:** Use native drought-resistant trees
        - **Maintenance:** Increase watering frequency for existing green cover
        """
    }
    st.markdown(recommendations.get(stakeholder, "Select a stakeholder to see recommended actions."))

if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Urban Heat Dashboard", page_icon="🌡️")
    st.sidebar.title("App Navigation")
    stakeholder_select = st.sidebar.selectbox("Select Stakeholder View:", ["BBMP (City Planning)", "Citizens", "Parks Department"], key="stakeholder_select")
    create_heat_map_dashboard(stakeholder_select)
