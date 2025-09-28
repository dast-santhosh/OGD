import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.map_utils import create_base_map
from data.bengaluru_data import get_lake_locations

def create_water_dashboard(stakeholder):
    st.header("💧 Water Bodies & Flood Risk Monitoring")
    
    # Stakeholder-specific information
    if stakeholder == "BWSSB (Water Board)":
        st.info("🚰 **BWSSB Focus:** Monitor water quality, lake health, and supply sustainability.")
    elif stakeholder == "Citizens":
        st.info("👥 **Citizen View:** Track water quality in your area and report pollution incidents.")
    elif stakeholder == "BBMP (City Planning)":
        st.info("🏛️ **BBMP Focus:** Flood risk assessment and drainage infrastructure planning.")
    
    # Water monitoring controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        monitoring_type = st.selectbox(
            "Monitoring Type:",
            ["Lake Health", "Water Quality", "Flood Risk", "Groundwater Levels"]
        )
    
    with col2:
        time_range = st.selectbox(
            "Time Range:",
            ["Real-time", "Last 24 Hours", "Last Week", "Last Month"]
        )
    
    with col3:
        data_source = st.selectbox(
            "Data Source:",
            ["NASA Satellites", "Ground Sensors", "Citizen Reports", "All Sources"]
        )
    
    # Water bodies map
    st.subheader("🗺️ Water Bodies Status Map")
    
    water_map = create_base_map()
    
    # Get lake data
    lakes = get_lake_locations()
    
    # Add lake markers with health status
    for lake in lakes:
        # Determine marker color based on health status
        if lake['health_score'] >= 7:
            color = 'green'
            status = 'Good'
        elif lake['health_score'] >= 4:
            color = 'yellow'
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
    
    # Add flood risk zones
    flood_zones = [
        {'lat': 12.9716, 'lon': 77.5946, 'risk': 'High', 'area': 'Silk Board'},
        {'lat': 12.9352, 'lon': 77.6245, 'risk': 'High', 'area': 'Electronic City'},
        {'lat': 12.9698, 'lon': 77.7500, 'risk': 'Medium', 'area': 'Whitefield'},
        {'lat': 12.9833, 'lon': 77.6167, 'risk': 'Medium', 'area': 'Koramangala'}
    ]
    
    for zone in flood_zones:
        color = 'darkred' if zone['risk'] == 'High' else 'orange'
        folium.Circle(
            location=[zone['lat'], zone['lon']],
            radius=1000,
            popup=f"Flood Risk: {zone['risk']} - {zone['area']}",
            color=color,
            fillColor=color,
            fillOpacity=0.3,
            weight=2
        ).add_to(water_map)
    
    map_data = st_folium(water_map, width=700, height=500)
    
    # Water quality metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Lake Health Summary")
        lake_health_df = pd.DataFrame({
            'Lake Name': ['Bellandur', 'Varthur', 'Ulsoor', 'Sankey Tank', 'Hebbal', 'Agara'],
            'Health Score': [3.2, 4.1, 6.8, 7.5, 5.9, 4.7],
            'Area (hectares)': [361, 220, 50, 15, 75, 80],
            'Water Quality': ['Poor', 'Poor', 'Moderate', 'Good', 'Moderate', 'Poor'],
            'Pollution Source': ['Industrial', 'Sewage', 'Urban runoff', 'Minimal', 'Mixed', 'Sewage']
        })
        st.dataframe(lake_health_df, width='stretch')
    
    with col2:
        st.subheader("📈 Water Quality Trends")
        # Create water quality trend chart
        dates = pd.date_range(start=datetime.now() - timedelta(days=29), end=datetime.now(), freq='D')
        quality_data = pd.DataFrame({
            'Date': dates,
            'Bellandur Lake': np.random.normal(3.2, 0.5, 30),
            'Ulsoor Lake': np.random.normal(6.8, 0.3, 30),
            'Sankey Tank': np.random.normal(7.5, 0.2, 30)
        })
        
        fig = px.line(quality_data, x='Date', y=['Bellandur Lake', 'Ulsoor Lake', 'Sankey Tank'],
                     title='30-Day Water Quality Trend',
                     labels={'value': 'Health Score (1-10)', 'variable': 'Water Body'})
        fig.add_hline(y=5, line_dash="dash", line_color="red", annotation_text="Critical Threshold")
        st.plotly_chart(fig, width='stretch')
    
    # Flood risk analysis
    st.subheader("🌊 Flood Risk Assessment")
    
    flood_risk_df = pd.DataFrame({
        'Area': ['Silk Board Junction', 'Electronic City', 'Majestic', 'Koramangala', 'Whitefield'],
        'Risk Level': ['Very High', 'High', 'High', 'Medium', 'Medium'],
        'Historical Floods': [12, 8, 10, 5, 3],
        'Drainage Capacity': ['Poor', 'Moderate', 'Poor', 'Good', 'Good'],
        'Population at Risk': [45000, 78000, 32000, 28000, 15000]
    })
    
    st.dataframe(flood_risk_df, width='stretch')
    
    # Water supply metrics
    if stakeholder == "BWSSB (Water Board)":
        st.subheader("🚰 Water Supply Status")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Daily Supply", "1,450 MLD", "+50 MLD")
        with col2:
            st.metric("Groundwater Level", "-2.3m", "-0.5m")
        with col3:
            st.metric("Lake Storage", "65%", "-12%")
        with col4:
            st.metric("Quality Score", "7.2/10", "+0.3")
    
    # Recommendations
    st.subheader("💡 Recommended Actions")
    
    if stakeholder == "BWSSB (Water Board)":
        st.markdown("""
        - **Critical:** Immediate intervention needed for Bellandur and Varthur lakes
        - **Infrastructure:** Upgrade sewage treatment capacity by 30%
        - **Monitoring:** Install real-time water quality sensors in all major lakes
        """)
    elif stakeholder == "Citizens":
        st.markdown("""
        - **Avoid** recreational activities in Bellandur, Varthur, and Agara lakes
        - **Report** any sewage discharge or industrial pollution immediately
        - **Conserve** water during monsoon shortages
        """)
    elif stakeholder == "BBMP (City Planning)":
        st.markdown("""
        - **Flood mitigation:** Upgrade drainage in Silk Board and Electronic City
        - **Lake restoration:** Allocate ₹200 crores for lake cleanup projects
        - **Early warning:** Implement flood alert system for high-risk areas
        """)
