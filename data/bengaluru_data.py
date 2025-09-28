import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_bengaluru_coordinates():
    """Return the center coordinates of Bengaluru"""
    return [12.9716, 77.5946]

def get_sample_locations():
    """Return sample locations for map markers"""
    return [
        {
            'name': 'Bellandur Lake',
            'lat': 12.9361,
            'lon': 77.6747,
            'type': 'Water Body - Critical',
            'color': 'red'
        },
        {
            'name': 'Cubbon Park',
            'lat': 12.9762,
            'lon': 77.5993,
            'type': 'Green Space - Good',
            'color': 'green'
        },
        {
            'name': 'Electronic City Air Station',
            'lat': 12.8398,
            'lon': 77.6595,
            'type': 'Air Quality Monitor',
            'color': 'orange'
        },
        {
            'name': 'Silk Board Junction',
            'lat': 12.9173,
            'lon': 77.6226,
            'type': 'Traffic Pollution Hotspot',
            'color': 'darkred'
        },
        {
            'name': 'Ulsoor Lake',
            'lat': 12.9813,
            'lon': 77.6081,
            'type': 'Water Body - Moderate',
            'color': 'blue'
        }
    ]

def get_temperature_grid():
    """Generate temperature monitoring grid points across Bengaluru"""
    grid_points = []
    
    # Define different area types and their characteristics
    area_types = {
        'urban_core': {'lat_range': (12.95, 13.00), 'lon_range': (77.55, 77.65)},
        'residential': {'lat_range': (12.90, 12.95), 'lon_range': (77.60, 77.70)},
        'industrial': {'lat_range': (12.85, 12.95), 'lon_range': (77.65, 77.75)},
        'green': {'lat_range': (12.95, 13.05), 'lon_range': (77.50, 77.60)},
        'suburban': {'lat_range': (12.80, 12.90), 'lon_range': (77.45, 77.55)}
    }
    
    for area_type, bounds in area_types.items():
        # Generate 20 random points for each area type
        for _ in range(20):
            lat = np.random.uniform(bounds['lat_range'][0], bounds['lat_range'][1])
            lon = np.random.uniform(bounds['lon_range'][0], bounds['lon_range'][1])
            
            grid_points.append({
                'lat': lat,
                'lon': lon,
                'area_type': area_type
            })
    
    return grid_points

def get_lake_locations():
    """Return major lakes in Bengaluru with health data"""
    return [
        {
            'name': 'Bellandur Lake',
            'lat': 12.9361,
            'lon': 77.6747,
            'area_hectares': 361,
            'health_score': 3.2,
            'pollution_level': 'High'
        },
        {
            'name': 'Varthur Lake',
            'lat': 12.9467,
            'lon': 77.7411,
            'area_hectares': 220,
            'health_score': 4.1,
            'pollution_level': 'High'
        },
        {
            'name': 'Ulsoor Lake',
            'lat': 12.9813,
            'lon': 77.6081,
            'area_hectares': 50,
            'health_score': 6.8,
            'pollution_level': 'Moderate'
        },
        {
            'name': 'Sankey Tank',
            'lat': 12.9716,
            'lon': 77.5714,
            'area_hectares': 15,
            'health_score': 7.5,
            'pollution_level': 'Low'
        },
        {
            'name': 'Hebbal Lake',
            'lat': 13.0358,
            'lon': 77.5970,
            'area_hectares': 75,
            'health_score': 5.9,
            'pollution_level': 'Moderate'
        },
        {
            'name': 'Agara Lake',
            'lat': 12.9361,
            'lon': 77.6388,
            'area_hectares': 80,
            'health_score': 4.7,
            'pollution_level': 'High'
        }
    ]

def get_air_quality_stations():
    """Return air quality monitoring stations with current data"""
    stations = [
        {
            'name': 'City Railway Station',
            'lat': 12.9716,
            'lon': 77.5946,
            'aqi': 156,
            'pm25': 68,
            'pm10': 98,
            'no2': 45,
            'station_type': 'Urban Traffic'
        },
        {
            'name': 'Hebbal',
            'lat': 13.0358,
            'lon': 77.5970,
            'aqi': 132,
            'pm25': 52,
            'pm10': 76,
            'no2': 38,
            'station_type': 'Residential'
        },
        {
            'name': 'BTM Layout',
            'lat': 12.9165,
            'lon': 77.6101,
            'aqi': 178,
            'pm25': 89,
            'pm10': 125,
            'no2': 52,
            'station_type': 'Commercial'
        },
        {
            'name': 'Silk Board',
            'lat': 12.9173,
            'lon': 77.6226,
            'aqi': 203,
            'pm25': 112,
            'pm10': 156,
            'no2': 67,
            'station_type': 'Traffic Junction'
        },
        {
            'name': 'Whitefield',
            'lat': 12.9698,
            'lon': 77.7500,
            'aqi': 145,
            'pm25': 58,
            'pm10': 82,
            'no2': 41,
            'station_type': 'IT Hub'
        },
        {
            'name': 'Electronic City',
            'lat': 12.8398,
            'lon': 77.6595,
            'aqi': 189,
            'pm25': 94,
            'pm10': 134,
            'no2': 58,
            'station_type': 'Industrial'
        }
    ]
    
    return stations

def get_historical_environmental_data():
    """Generate historical environmental data for trends"""
    dates = pd.date_range(start=datetime.now() - timedelta(days=365), end=datetime.now(), freq='D')
    
    # Generate seasonal temperature pattern
    seasonal_temp = 30 + 5 * np.sin(2 * np.pi * np.arange(len(dates)) / 365) + np.random.normal(0, 2, len(dates))
    
    # Generate AQI with seasonal and random variations
    seasonal_aqi = 120 + 40 * np.sin(2 * np.pi * np.arange(len(dates)) / 365 + np.pi) + np.random.normal(0, 20, len(dates))
    seasonal_aqi = np.clip(seasonal_aqi, 50, 300)  # Realistic AQI range
    
    # Water quality with monsoon effects
    monsoon_effect = np.where((np.arange(len(dates)) % 365 > 150) & (np.arange(len(dates)) % 365 < 250), -1, 0)
    water_quality = 6 + monsoon_effect + np.random.normal(0, 0.5, len(dates))
    water_quality = np.clip(water_quality, 2, 10)
    
    return pd.DataFrame({
        'date': dates,
        'temperature': seasonal_temp,
        'aqi': seasonal_aqi,
        'water_quality': water_quality,
        'green_cover': 20 - 0.01 * np.arange(len(dates)) + np.random.normal(0, 0.1, len(dates))  # Declining trend
    })
