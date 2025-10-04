import streamlit as st 
import folium 
from streamlit_folium import st_folium 
import pandas as pd 
import plotly.express as px 
import numpy as np 

# --- Utility Functions (Simulating external imports) ---

def create_base_map(center_lat=12.9716, center_lon=77.5946, zoom_start=11):
    """
    Creates a basic Folium map centered on Bengaluru (simulated center).
    Uses satellite imagery by default, or dark tiles for 'Night Lights' analysis.
    """
    # Set default tile to Satellite, but use dark_matter for the Night Lights analysis
    if st.session_state.get('analysis_type') == 'Night Lights':
        tiles_to_use = "CartoDB dark_matter"
        attr_text = "CartoDB / Simulated Data"
    else:
        # Use Satellite imagery as the new default for an urban analysis context
        tiles_to_use = "Esri WorldImagery" 
        attr_text = 'Esri WorldImagery / Simulated Data'

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles=tiles_to_use,
        attr=attr_text
    )
    return m

# --- Data Simulation Functions ---

@st.cache_data
def get_growth_zones():
    """Defines hard-coded development zones data."""
    return [
        {'lat': 12.9716, 'lon': 77.5946, 'zone': 'CBD', 'base_growth': 2.1, 'type': 'established'}, 
        {'lat': 12.9698, 'lon': 77.7500, 'zone': 'Whitefield', 'base_growth': 8.5, 'type': 'tech_hub'}, 
        {'lat': 12.9352, 'lon': 77.6245, 'zone': 'Electronic City', 'base_growth': 12.3, 'type': 'tech_hub'}, 
        {'lat': 12.8456, 'lon': 77.6636, 'zone': 'Bannerghatta', 'base_growth': 15.7, 'type': 'expanding'}, 
        {'lat': 13.0358, 'lon': 77.5970, 'zone': 'Yelahanka', 'base_growth': 18.2, 'type': 'expanding'}, 
        {'lat': 12.9833, 'lon': 77.6167, 'zone': 'Koramangala', 'base_growth': 5.4, 'type': 'established'}, 
        {'lat': 13.0827, 'lon': 77.5946, 'zone': 'Hebbal', 'base_growth': 9.8, 'type': 'residential'}, 
        {'lat': 12.9141, 'lon': 77.6101, 'zone': 'Jayanagar', 'base_growth': 3.2, 'type': 'established'}
    ]

@st.cache_data
def get_simulated_trend_data(time_comparison):
    """Generates synthetic data for the 5-Year Development Trend chart."""
    # Since time_comparison is now hardcoded to "2020 vs 2025" in the main function,
    # this logic is slightly simplified to just handle the default data.
    if '2010' in time_comparison:
        years = ['2010', '2015', '2020', '2025']
        built_up_area = [550, 650, 790, 915]
        green_cover = [250, 210, 175, 153]
    elif 'Yearly' in time_comparison:
        years = ['2020', '2021', '2022', '2023', '2024', '2025']
        built_up_area = [790, 815, 845, 875, 900, 925]
        green_cover = [175, 170, 165, 160, 155, 150]
    else: # Default 2020 vs 2025
        years = ['2020', '2021', '2022', '2023', '2024', '2025']
        built_up_area = [741, 768, 798, 832, 871, 915]
        green_cover = [189, 182, 174, 168, 161, 153]

    return pd.DataFrame({ 
        'Year': years, 
        'Built-up Area (sq km)': built_up_area, 
        'Green Cover (sq km)': green_cover, 
        'Population (millions)': [round(x * 0.015 + 12.3, 1) for x in built_up_area] # Simple correlation
    })

def get_infrastructure_metrics(analysis_type):
    """Adjusts metrics based on the selected analysis type for context."""
    if analysis_type == "Green Cover Loss":
        return {
            "Traffic Congestion": ("+15%", "vs 2020", "low"),
            "Water Demand": ("+20%", "vs 2020", "low"),
            "Air Quality Index": ("-35%", "vs 2020", "high", "Pollution"),
            "Heat Stress Index": ("+0.8°C", "vs 2020", "high", "Temperature"),
        }
    elif analysis_type == "Building Density":
        return {
            "Traffic Congestion": ("+60%", "vs 2020", "high"),
            "Water Demand": ("+45%", "vs 2020", "high"),
            "Road Capacity Utilization": ("95%", "Avg. Peak", "high", "Roads"),
            "Parking Availability": ("-70%", "vs 2020", "high", "Parking"),
        }
    else: # Default/Land Use Change/Urban Sprawl
        return {
            "Traffic Congestion": ("+45%", "vs 2020", "high"),
            "Water Demand": ("+38%", "vs 2020", "high"),
            "Power Consumption": ("+52%", "vs 2020", "high", "Power"),
            "Waste Generation": ("+41%", "vs 2020", "high", "Waste"),
        }

# --- Main Application Function ---

def create_urban_growth_analyzer(stakeholder): 
    st.header("🏙️ Urban Growth & Land Use Analysis (Bengaluru Simulated)") 
    
    # Stakeholder-specific information 
    if stakeholder == "BBMP (City Planning)": 
        st.info("🏛️ **BBMP Focus:** Monitor urban sprawl, manage land use, and plan sustainable development corridors.") 
    elif stakeholder == "Researchers": 
        st.info("🔬 **Research Focus:** Analyze urbanization impacts on environment, climate, and infrastructure resilience.") 
    elif stakeholder == "Citizens": 
        st.info("👥 **Citizen View:** Understand development patterns and resource stress in your neighborhood.") 
    
    # Urban growth analysis controls 
    col1, col2 = st.columns(2) # Changed to 2 columns
    
    # Time comparison is now hardcoded as requested.
    time_comparison = "2020 vs 2025" 

    with col1: 
        analysis_type = st.selectbox( 
            "Analysis Type:", 
            ["Land Use Change", "Urban Sprawl", "Night Lights", "Building Density", "Green Cover Loss"],
            key='analysis_type' # Stored in session_state for dynamic map tiles
        ) 
    
    with col2: # Moved from col3
        data_overlay = st.selectbox( 
            "Overlay Data:", 
            ["Population Density", "Infrastructure", "Transport Networks", "Zoning Plans"] 
        ) 
    
    st.markdown("---")

    # --- Urban Growth Map ---
    st.subheader(f"🗺️ {analysis_type} Map Visualized ({time_comparison})") 
    
    growth_map = create_base_map() 
    development_zones = get_growth_zones()
    
    # Dynamic Map Styling Logic
    if analysis_type == 'Night Lights':
        # Simulate bright night light areas with large, bright markers
        color_map = {'established': 'yellow', 'tech_hub': 'white', 'expanding': 'red', 'residential': 'orange'}
        title_metric = 'Light Intensity'
    elif analysis_type == 'Green Cover Loss':
        # Simulate loss: higher growth = higher loss
        color_map = {'established': 'green', 'tech_hub': 'orange', 'expanding': 'red', 'residential': 'darkred'}
        title_metric = 'Green Loss %'
    elif analysis_type == 'Building Density':
        # Simulate high density areas
        color_map = {'established': 'gray', 'tech_hub': 'purple', 'expanding': 'red', 'residential': 'blue'}
        title_metric = 'Density Score'
    else: # Land Use Change / Urban Sprawl
        color_map = {'established': 'green', 'tech_hub': 'yellow', 'expanding': 'red', 'residential': 'orange'}
        title_metric = 'Growth Rate %'

    
    # Add development zone markers 
    for zone in development_zones: 
        growth_rate = zone['base_growth']
        
        # Adjust growth rate slightly for visual difference based on time comparison
        if '2010' in time_comparison:
            simulated_value = growth_rate * 1.2 # Show higher value over long period
        elif 'Yearly' in time_comparison:
            simulated_value = growth_rate * 0.5 # Show smaller change over short period
        else:
            simulated_value = growth_rate
            
        # Determine status and color
        if simulated_value < 5: 
            status = 'Stable/Consolidated' 
        elif simulated_value < 10: 
            status = 'Moderate Development' 
        elif simulated_value < 15: 
            status = 'High Sprawl' 
        else: 
            status = 'Rapid Expansion' 
        
        color = color_map.get(zone['type'], 'gray')
        
        # Marker size based on simulated value
        radius = 8 + (simulated_value / 3) 
        
        folium.CircleMarker( 
            location=[zone['lat'], zone['lon']], 
            radius=radius, 
            popup=f""" 
            <b>{zone['zone']}</b><br> 
            {title_metric}: {simulated_value:.1f}<br> 
            Status: {status}<br> 
            Type: {zone['type'].replace('_', ' ').title()} 
            """, 
            color=color, 
            fillColor=color, 
            fillOpacity=0.7, 
            weight=2 
        ).add_to(growth_map) 
    
    # Add transport infrastructure (Overlay Data simulation) 
    if data_overlay in ["Infrastructure", "Transport Networks"]:
        transport_lines = [ 
            # Metro lines - Purple, Green, Blue
            [[12.9716, 77.5946], [12.9698, 77.7500]],
            [[13.0827, 77.5946], [12.8456, 77.6636]],
            [[12.9141, 77.6101], [12.9833, 77.6167]]
        ] 
        
        for i, line in enumerate(transport_lines): 
            colors = ['#8A2BE2', '#3CB371', '#1E90FF'] 
            folium.PolyLine( 
                locations=line, 
                color=colors[i], 
                weight=4, 
                opacity=0.8, 
                popup=f"Metro Line {i+1} ({['Purple', 'Green', 'Blue'][i]})" 
            ).add_to(growth_map) 

    st_folium(growth_map, width=700, height=500, key="urban_map") 
    
    st.markdown("---")

    # --- Urban Growth Statistics and Charts ---
    col1, col2 = st.columns(2) 
    
    with col1: 
        st.subheader("📊 Zone Growth Statistics") 
        growth_stats_df = pd.DataFrame([
            {
                'Zone': zone['zone'], 
                'Growth Rate (%)': round(zone['base_growth'], 1), 
                'New Buildings': int(100 * zone['base_growth'] * np.random.uniform(0.9, 1.1)),
                'Population Change': f"+{int(500 * zone['base_growth'] * np.random.uniform(0.9, 1.1)):,}", 
                'Development Type': zone['type'].replace('_', ' ').title()
            } for zone in development_zones
        ]).sort_values(by='Growth Rate (%)', ascending=False).reset_index(drop=True)
        st.dataframe(growth_stats_df, use_container_width=True) 
    
    with col2: 
        st.subheader("📈 Area vs Green Cover Trend") 
        # Create development trend chart 
        development_data = get_simulated_trend_data(time_comparison)
        
        fig = px.line(development_data, 
                      x='Year', 
                      y=['Built-up Area (sq km)', 'Green Cover (sq km)', 'Population (millions)'], 
                      title=f'{analysis_type} Trend over Time ({time_comparison})', 
                      labels={'value': 'Value', 'variable': 'Metric'},
                      color_discrete_map={
                          'Built-up Area (sq km)': 'red', 
                          'Green Cover (sq km)': 'green', 
                          'Population (millions)': 'blue'
                      }) 
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True) 
    
    st.markdown("---")

    # --- Infrastructure strain analysis (Dynamically adjusted) ---
    st.subheader(f"🚧 Infrastructure Assessment ({analysis_type} Impact)") 
    metrics = get_infrastructure_metrics(analysis_type)
    
    col1_metrics, col2_metrics, col3_metrics = st.columns(3) 
    
    # Helper to display metrics based on the dictionary structure
    metric_keys = list(metrics.keys())
    
    with col1_metrics: 
        st.metric(metric_keys[0], metrics[metric_keys[0]][0], metrics[metric_keys[0]][1]) 
        st.metric(metric_keys[1], metrics[metric_keys[1]][0], metrics[metric_keys[1]][1]) 
    
    with col2_metrics: 
        if len(metric_keys) > 2:
            st.metric(metric_keys[2], metrics[metric_keys[2]][0], metrics[metric_keys[2]][1]) 
        if len(metric_keys) > 3:
            st.metric(metric_keys[3], metrics[metric_keys[3]][0], metrics[metric_keys[3]][1]) 
        
    with col3_metrics:
        # Placeholder for dynamic visual indicator
        impact = metrics[metric_keys[0]][2]
        st.markdown(f"**Overall Impact:** {'🔴 High' if impact == 'high' else '🟠 Moderate'}")
        st.caption("Impact levels are derived from the current analysis type.")


    # --- Development hotspots ---
    st.subheader("🔥 Development Hotspots & Critical Areas") 
    
    # Adjust hotspot table slightly based on the analysis type
    if analysis_type == 'Green Cover Loss':
        impact_col = 'Vulnerability to Heat Island'
        impact_data = ['High', 'Moderate', 'Very High', 'High', 'High', 'Moderate']
    elif analysis_type == 'Night Lights':
        impact_col = 'Light Pollution Index'
        impact_data = ['7.5/10', '6.2/10', '8.9/10', '7.0/10', '8.5/10', '5.5/10']
    else:
        impact_col = 'Environmental Impact'
        impact_data = ['High', 'Moderate', 'Very High', 'High', 'High', 'Moderate']


    hotspots_df = pd.DataFrame({ 
        'Hotspot Area': ['Aerospace Park', 'Kempegowda International Airport Area', 'Outer Ring Road Corridor', 
                         'Hosur Road Extension', 'Sarjapur Road', 'Tumkur Road'], 
        'Development Intensity': ['Very High', 'High', 'Very High', 'High', 'Very High', 'Moderate'], 
        'Primary Driver': ['IT/Aerospace', 'Airport Connectivity', 'IT Companies', 'Industrial Growth', 'Residential/IT', 'Residential'], 
        'Infrastructure Readiness': ['Moderate', 'Good', 'Poor', 'Moderate', 'Poor', 'Good'], 
        impact_col: impact_data
    }) 
    
    st.dataframe(hotspots_df, use_container_width=True) 
    
    st.markdown("---")
    
    # --- Predictions and recommendations (Stakeholder-specific, unchanged) ---
    st.subheader("🔮 Growth Projections & Recommendations") 
    
    if stakeholder == "BBMP (City Planning)": 
        st.markdown(""" 
        **2030 Projections:** - Urban area will expand by additional 180 sq km 
        - Population will reach $18.2$ million ($+2.6$ million) 
        - Green cover may decrease to $135$ sq km without intervention 
        
        **Immediate Actions Needed:** - Implement zoning restrictions in rapidly expanding areas like Yelahanka and Bannerghatta 
        - Fast-track Metro Phase 3 to decentralize growth and reduce sprawl pressure 
        - Mandate $30\%$ green space and rainwater harvesting in all new developments 
        """) 
    elif stakeholder == "Researchers": 
        st.markdown(""" 
        **Research Insights:** - Urban heat island effect increasing by $0.3^{\circ}C$ per year due to land use changes. 
        - $65\%$ of perimeter agricultural land has been converted in outer areas over the last decade. 
        - Infrastructure lag is causing an estimated $40\%$ efficiency loss in resource distribution. 
        
        **Study Recommendations:** - Monitor satellite data for real-time sprawl detection metrics. 
        - Implement smart growth models from international cities (e.g., Singapore/Copenhagen) for urban density. 
        - Study and protect biodiversity corridors and lake buffer zones critical for ecosystem resilience. 
        """) 
    elif stakeholder == "Citizens": 
        st.markdown(""" 
        **What This Means for You:** - New residential areas (Bannerghatta, Yelahanka) may face increased water and power shortages. 
        - Traffic congestion will worsen significantly on key corridors without immediate public transport expansion. 
        - Property values continue rising fastest in high-growth, expanding areas. 
        
        **How to Help:** - Support and advocate for public transport initiatives and last-mile connectivity. 
        - Choose eco-friendly housing developments and participate in local tree-planting drives. 
        - Report unauthorized constructions and infrastructure issues through the BBMP citizen app. 
        """) 

# --- Streamlit Main Block ---

if 'analysis_type' not in st.session_state:
    st.session_state['analysis_type'] = 'Land Use Change'

st.sidebar.title("Urban Dashboard Controls")
selected_stakeholder = st.sidebar.radio(
    "Select Stakeholder View:",
    ["BBMP (City Planning)", "Researchers", "Citizens"]
)

st.sidebar.info("This is a simulated dashboard using hard-coded data to demonstrate feature functionality across all analysis options.")

create_urban_growth_analyzer(selected_stakeholder)
