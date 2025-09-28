import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
from utils.map_utils import create_base_map

def create_urban_growth_analyzer(stakeholder):
    st.header("🏙️ Urban Growth & Land Use Analysis")
    
    # Stakeholder-specific information
    if stakeholder == "BBMP (City Planning)":
        st.info("🏛️ **BBMP Focus:** Monitor urban sprawl patterns and plan sustainable development corridors.")
    elif stakeholder == "Researchers":
        st.info("🔬 **Research Focus:** Analyze urbanization impacts on environment and infrastructure.")
    elif stakeholder == "Citizens":
        st.info("👥 **Citizen View:** Understand development patterns in your neighborhood.")
    
    # Urban growth analysis controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        analysis_type = st.selectbox(
            "Analysis Type:",
            ["Land Use Change", "Urban Sprawl", "Night Lights", "Building Density", "Green Cover Loss"]
        )
    
    with col2:
        time_comparison = st.selectbox(
            "Time Comparison:",
            ["2020 vs 2025", "2015 vs 2025", "2010 vs 2025", "Yearly Progression"]
        )
    
    with col3:
        data_overlay = st.selectbox(
            "Overlay Data:",
            ["Population Density", "Infrastructure", "Transport Networks", "Zoning Plans"]
        )
    
    # Urban growth map
    st.subheader("🗺️ Urban Development Map")
    
    growth_map = create_base_map()
    
    # Define different development zones
    development_zones = [
        # Established urban areas
        {'lat': 12.9716, 'lon': 77.5946, 'zone': 'CBD', 'growth_rate': 2.1, 'type': 'established'},
        {'lat': 12.9698, 'lon': 77.7500, 'zone': 'Whitefield', 'growth_rate': 8.5, 'type': 'tech_hub'},
        {'lat': 12.9352, 'lon': 77.6245, 'zone': 'Electronic City', 'growth_rate': 12.3, 'type': 'tech_hub'},
        {'lat': 12.8456, 'lon': 77.6636, 'zone': 'Bannerghatta', 'growth_rate': 15.7, 'type': 'expanding'},
        {'lat': 13.0358, 'lon': 77.5970, 'zone': 'Yelahanka', 'growth_rate': 18.2, 'type': 'expanding'},
        {'lat': 12.9833, 'lon': 77.6167, 'zone': 'Koramangala', 'growth_rate': 5.4, 'type': 'established'},
        {'lat': 13.0827, 'lon': 77.5946, 'zone': 'Hebbal', 'growth_rate': 9.8, 'type': 'residential'},
        {'lat': 12.9141, 'lon': 77.6101, 'zone': 'Jayanagar', 'growth_rate': 3.2, 'type': 'established'}
    ]
    
    # Add development zone markers
    for zone in development_zones:
        # Color coding based on growth rate
        if zone['growth_rate'] < 5:
            color = 'green'
            status = 'Stable'
        elif zone['growth_rate'] < 10:
            color = 'yellow'
            status = 'Moderate Growth'
        elif zone['growth_rate'] < 15:
            color = 'orange'
            status = 'High Growth'
        else:
            color = 'red'
            status = 'Rapid Growth'
        
        # Marker size based on growth rate
        radius = 8 + (zone['growth_rate'] / 2)
        
        folium.CircleMarker(
            location=[zone['lat'], zone['lon']],
            radius=radius,
            popup=f"""
            <b>{zone['zone']}</b><br>
            Growth Rate: {zone['growth_rate']}%<br>
            Status: {status}<br>
            Type: {zone['type'].replace('_', ' ').title()}
            """,
            color=color,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(growth_map)
    
    # Add transport infrastructure
    transport_lines = [
        # Metro lines
        [[12.9716, 77.5946], [12.9698, 77.7500]],  # Purple line
        [[13.0827, 77.5946], [12.8456, 77.6636]],  # Green line
        [[12.9141, 77.6101], [12.9833, 77.6167]]   # Blue line
    ]
    
    for i, line in enumerate(transport_lines):
        colors = ['purple', 'green', 'blue']
        folium.PolyLine(
            locations=line,
            color=colors[i],
            weight=4,
            opacity=0.8,
            popup=f"Metro Line {i+1}"
        ).add_to(growth_map)
    
    map_data = st_folium(growth_map, width=700, height=500)
    
    # Urban growth statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Growth Rate Analysis")
        growth_stats_df = pd.DataFrame({
            'Zone': ['Yelahanka', 'Bannerghatta', 'Electronic City', 'Hebbal', 'Whitefield', 'Koramangala', 'Jayanagar', 'CBD'],
            'Growth Rate (%)': [18.2, 15.7, 12.3, 9.8, 8.5, 5.4, 3.2, 2.1],
            'New Buildings': [2340, 1890, 1560, 1200, 980, 620, 340, 180],
            'Population Change': ['+45,000', '+38,000', '+29,000', '+22,000', '+18,000', '+12,000', '+6,000', '+3,000'],
            'Development Type': ['Residential', 'Mixed Use', 'IT/Commercial', 'Residential', 'IT/Commercial', 'Commercial', 'Residential', 'Commercial']
        })
        st.dataframe(growth_stats_df, width='stretch')
    
    with col2:
        st.subheader("📈 5-Year Development Trend")
        # Create development trend chart
        years = ['2020', '2021', '2022', '2023', '2024', '2025']
        development_data = pd.DataFrame({
            'Year': years,
            'Built-up Area (sq km)': [741, 768, 798, 832, 871, 915],
            'Green Cover (sq km)': [189, 182, 174, 168, 161, 153],
            'Population (millions)': [12.3, 12.8, 13.4, 14.1, 14.8, 15.6]
        })
        
        fig = px.line(development_data, x='Year', y=['Built-up Area (sq km)', 'Green Cover (sq km)'],
                     title='Built-up Area vs Green Cover Trend',
                     labels={'value': 'Area (sq km)', 'variable': 'Land Use Type'})
        st.plotly_chart(fig, width='stretch')
    
    # Land use change analysis
    st.subheader("🌍 Land Use Change Matrix (2020-2025)")
    
    land_use_change = pd.DataFrame({
        'Original Use (2020)': ['Agricultural', 'Forest/Green', 'Water Bodies', 'Residential', 'Commercial', 'Industrial'],
        'Current Use (2025)': ['45% Residential, 30% Commercial, 25% Agricultural',
                              '60% Residential, 25% Forest, 15% Commercial',
                              '70% Water, 20% Residential, 10% Commercial',
                              '80% Residential, 15% Commercial, 5% Mixed',
                              '90% Commercial, 10% Mixed Use',
                              '85% Industrial, 15% Commercial'],
        'Area Lost (sq km)': [125, 78, 12, 5, 2, 3],
        'Impact Level': ['High', 'Critical', 'Moderate', 'Low', 'Low', 'Low']
    })
    
    st.dataframe(land_use_change, width='stretch')
    
    # Infrastructure strain analysis
    st.subheader("🚧 Infrastructure Strain Assessment")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Traffic Congestion", "+45%", "vs 2020")
        st.metric("Water Demand", "+38%", "vs 2020")
    
    with col2:
        st.metric("Power Consumption", "+52%", "vs 2020")
        st.metric("Waste Generation", "+41%", "vs 2020")
    
    with col3:
        st.metric("Sewage Load", "+47%", "vs 2020")
        st.metric("Air Pollution", "+29%", "vs 2020")
    
    # Development hotspots
    st.subheader("🔥 Development Hotspots")
    
    hotspots_df = pd.DataFrame({
        'Hotspot Area': ['Aerospace Park', 'Kempegowda International Airport Area', 'Outer Ring Road Corridor', 
                        'Hosur Road Extension', 'Sarjapur Road', 'Tumkur Road'],
        'Development Intensity': ['Very High', 'High', 'Very High', 'High', 'Very High', 'Moderate'],
        'Primary Driver': ['IT/Aerospace', 'Airport Connectivity', 'IT Companies', 'Industrial Growth', 'Residential/IT', 'Residential'],
        'Infrastructure Readiness': ['Moderate', 'Good', 'Poor', 'Moderate', 'Poor', 'Good'],
        'Environmental Impact': ['High', 'Moderate', 'Very High', 'High', 'High', 'Moderate']
    })
    
    st.dataframe(hotspots_df, width='stretch')
    
    # Predictions and recommendations
    st.subheader("🔮 Growth Projections & Recommendations")
    
    if stakeholder == "BBMP (City Planning)":
        st.markdown("""
        **2030 Projections:**
        - Urban area will expand by additional 180 sq km
        - Population will reach 18.2 million (+2.6 million)
        - Green cover may decrease to 135 sq km without intervention
        
        **Immediate Actions Needed:**
        - Implement zoning restrictions in Yelahanka and Bannerghatta
        - Fast-track Metro Phase 3 to reduce sprawl pressure
        - Mandate 30% green space in new developments
        """)
    elif stakeholder == "Researchers":
        st.markdown("""
        **Research Insights:**
        - Urban heat island effect increasing by 0.3°C per year
        - 65% of agricultural land converted in outer areas
        - Infrastructure lag causing 40% efficiency loss
        
        **Study Recommendations:**
        - Monitor satellite data for real-time sprawl detection
        - Implement smart growth models from Singapore/Copenhagen
        - Study impact on biodiversity corridors
        """)
    elif stakeholder == "Citizens":
        st.markdown("""
        **What This Means for You:**
        - New residential areas may face water/power shortages
        - Traffic congestion will worsen without public transport
        - Property values rising fastest in Yelahanka/Bannerghatta
        
        **How to Help:**
        - Support public transport initiatives
        - Choose eco-friendly housing developments
        - Report unauthorized constructions through app
        """)
