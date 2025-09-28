import folium
from data.bengaluru_data import get_bengaluru_coordinates

def create_base_map():
    """Create a base Folium map centered on Bengaluru"""
    center_coords = get_bengaluru_coordinates()
    
    # Create base map
    m = folium.Map(
        location=center_coords,
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Add additional tile layers
    folium.TileLayer(
        tiles='CartoDB positron',
        name='Light Mode',
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='CartoDB dark_matter',
        name='Dark Mode',
        control=True
    ).add_to(m)
    
    # Add satellite view
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        control=True
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

def add_heat_layer(map_obj, heat_data, name="Heat Layer"):
    """Add a heat map layer to the map"""
    from folium.plugins import HeatMap
    
    HeatMap(
        heat_data,
        name=name,
        radius=15,
        blur=10,
        gradient={
            0.0: 'blue',
            0.3: 'green',
            0.5: 'yellow', 
            0.7: 'orange',
            1.0: 'red'
        }
    ).add_to(map_obj)
    
    return map_obj

def add_marker_cluster(map_obj, markers_data, name="Markers"):
    """Add a cluster of markers to the map"""
    from folium.plugins import MarkerCluster
    
    marker_cluster = MarkerCluster(name=name).add_to(map_obj)
    
    for marker in markers_data:
        folium.Marker(
            location=[marker['lat'], marker['lon']],
            popup=marker.get('popup', ''),
            tooltip=marker.get('tooltip', ''),
            icon=folium.Icon(
                color=marker.get('color', 'blue'),
                icon=marker.get('icon', 'info-sign')
            )
        ).add_to(marker_cluster)
    
    return map_obj

def add_choropleth_layer(map_obj, geojson_data, data_column, name="Choropleth"):
    """Add a choropleth layer to the map"""
    folium.Choropleth(
        geo_data=geojson_data,
        name=name,
        data=data_column,
        columns=['id', 'value'],
        key_on='feature.id',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=name
    ).add_to(map_obj)
    
    return map_obj

def add_circle_markers(map_obj, locations, name="Circle Markers"):
    """Add circle markers to represent data points"""
    for location in locations:
        folium.CircleMarker(
            location=[location['lat'], location['lon']],
            radius=location.get('radius', 10),
            popup=location.get('popup', ''),
            color=location.get('color', 'blue'),
            fillColor=location.get('fillColor', location.get('color', 'blue')),
            fillOpacity=location.get('fillOpacity', 0.7),
            weight=location.get('weight', 2)
        ).add_to(map_obj)
    
    return map_obj

def add_polygon_layer(map_obj, polygons_data, name="Polygons"):
    """Add polygon overlays to the map"""
    for polygon in polygons_data:
        folium.Polygon(
            locations=polygon['coordinates'],
            popup=polygon.get('popup', ''),
            color=polygon.get('color', 'blue'),
            fillColor=polygon.get('fillColor', polygon.get('color', 'blue')),
            fillOpacity=polygon.get('fillOpacity', 0.3),
            weight=polygon.get('weight', 2)
        ).add_to(map_obj)
    
    return map_obj

def add_search_functionality(map_obj):
    """Add search functionality to the map"""
    from folium.plugins import Search
    
    # Note: This requires additional setup with search data
    # For now, we'll add a simple geocoder
    from folium.plugins import Geocoder
    
    Geocoder().add_to(map_obj)
    
    return map_obj

def add_fullscreen_button(map_obj):
    """Add fullscreen functionality to the map"""
    from folium.plugins import Fullscreen
    
    Fullscreen().add_to(map_obj)
    
    return map_obj

def add_minimap(map_obj):
    """Add a mini map for navigation"""
    from folium.plugins import MiniMap
    
    minimap = MiniMap(toggle_display=True)
    map_obj.add_child(minimap)
    
    return map_obj

def add_measurement_tool(map_obj):
    """Add measurement tool for distances"""
    from folium.plugins import MeasureControl
    
    MeasureControl().add_to(map_obj)
    
    return map_obj

def create_legend_html(legend_items):
    """Create HTML legend for the map"""
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4>Legend</h4>
    '''
    
    for item in legend_items:
        legend_html += f'''
        <p><span style="color:{item['color']};">●</span> {item['label']}</p>
        '''
    
    legend_html += '</div>'
    
    return legend_html

def add_legend(map_obj, legend_items):
    """Add a legend to the map"""
    legend_html = create_legend_html(legend_items)
    map_obj.get_root().html.add_child(folium.Element(legend_html))
    
    return map_obj
