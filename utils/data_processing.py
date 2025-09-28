import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def load_environmental_data():
    """Load and process environmental data for the dashboard"""
    
    # Simulate loading data from various sources
    data = {
        'temperature': {
            'current_avg': 32.5,
            'anomaly': 2.1,
            'trend': 'increasing',
            'last_updated': datetime.now().isoformat()
        },
        'air_quality': {
            'aqi_avg': 156,
            'category': 'Unhealthy',
            'primary_pollutant': 'PM2.5',
            'trend': 'worsening',
            'last_updated': datetime.now().isoformat()
        },
        'water_quality': {
            'lake_health_index': 6.2,
            'declining_lakes': ['Bellandur', 'Varthur', 'Agara'],
            'trend': 'declining',
            'last_updated': datetime.now().isoformat()
        },
        'green_cover': {
            'percentage': 18.2,
            'change': -1.3,
            'trend': 'decreasing',
            'last_updated': datetime.now().isoformat()
        },
        'urban_growth': {
            'growth_rate': 12.3,
            'hotspots': ['Yelahanka', 'Bannerghatta', 'Electronic City'],
            'trend': 'rapid expansion',
            'last_updated': datetime.now().isoformat()
        }
    }
    
    return data

def process_satellite_data(raw_data):
    """Process raw satellite data into usable format"""
    # This would normally process actual NASA satellite data
    # For now, we'll simulate the processing
    
    processed_data = {
        'modis_lst': generate_temperature_data(),
        'landsat_ndvi': generate_vegetation_data(),
        'viirs_ntl': generate_nightlights_data(),
        'tropomi_no2': generate_pollution_data()
    }
    
    return processed_data

def generate_temperature_data():
    """Generate simulated temperature data from MODIS LST"""
    # Simulate 30 days of temperature data
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30, freq='D')
    
    # Base temperature with seasonal variation and random noise
    base_temp = 32.0
    seasonal_variation = 3 * np.sin(2 * np.pi * np.arange(30) / 365)
    random_noise = np.random.normal(0, 1.5, 30)
    
    temperatures = base_temp + seasonal_variation + random_noise
    
    return pd.DataFrame({
        'date': dates,
        'temperature': temperatures,
        'anomaly': temperatures - 30.0  # Anomaly from 30°C baseline
    })

def generate_vegetation_data():
    """Generate simulated NDVI vegetation data"""
    # NDVI values typically range from -1 to 1
    # Higher values indicate more vegetation
    
    zones = ['CBD', 'Electronic City', 'Whitefield', 'Koramangala', 'Hebbal', 'Yelahanka']
    
    # Different NDVI values for different zones
    ndvi_values = {
        'CBD': np.random.normal(0.2, 0.05, 30),
        'Electronic City': np.random.normal(0.3, 0.08, 30),
        'Whitefield': np.random.normal(0.4, 0.06, 30),
        'Koramangala': np.random.normal(0.35, 0.07, 30),
        'Hebbal': np.random.normal(0.5, 0.05, 30),
        'Yelahanka': np.random.normal(0.6, 0.04, 30)
    }
    
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30, freq='D')
    
    ndvi_df = pd.DataFrame({'date': dates})
    for zone, values in ndvi_values.items():
        ndvi_df[zone] = np.clip(values, 0, 1)  # Ensure positive values for vegetation
    
    return ndvi_df

def generate_nightlights_data():
    """Generate simulated VIIRS nighttime lights data"""
    # Night lights indicate urban development and activity
    
    zones = ['CBD', 'Electronic City', 'Whitefield', 'Koramangala', 'Hebbal', 'Yelahanka']
    
    # Different brightness levels for different zones (arbitrary units)
    brightness_values = {
        'CBD': np.random.normal(85, 5, 30),
        'Electronic City': np.random.normal(70, 8, 30),
        'Whitefield': np.random.normal(75, 6, 30),
        'Koramangala': np.random.normal(80, 7, 30),
        'Hebbal': np.random.normal(45, 5, 30),
        'Yelahanka': np.random.normal(35, 8, 30)  # Growing area - more variation
    }
    
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30, freq='D')
    
    ntl_df = pd.DataFrame({'date': dates})
    for zone, values in brightness_values.items():
        ntl_df[zone] = np.clip(values, 0, 100)  # Normalize to 0-100 scale
    
    return ntl_df

def generate_pollution_data():
    """Generate simulated TROPOMI pollution data"""
    # NO2 values in molecules/cm²
    
    zones = ['CBD', 'Electronic City', 'Whitefield', 'Koramangala', 'Hebbal', 'Yelahanka']
    
    # Different NO2 levels for different zones
    no2_values = {
        'CBD': np.random.normal(8.5e15, 1e15, 30),        # High traffic
        'Electronic City': np.random.normal(6.2e15, 1.2e15, 30),  # Industrial
        'Whitefield': np.random.normal(5.8e15, 0.8e15, 30),       # IT hub
        'Koramangala': np.random.normal(7.1e15, 0.9e15, 30),      # Commercial
        'Hebbal': np.random.normal(4.5e15, 0.6e15, 30),           # Residential
        'Yelahanka': np.random.normal(3.8e15, 0.7e15, 30)         # Developing
    }
    
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30, freq='D')
    
    no2_df = pd.DataFrame({'date': dates})
    for zone, values in no2_values.items():
        no2_df[zone] = values
    
    return no2_df

def calculate_heat_vulnerability_index(temperature_data, population_data, green_cover_data):
    """Calculate heat vulnerability index for different areas"""
    
    # Normalize inputs to 0-1 scale
    temp_norm = (temperature_data - temperature_data.min()) / (temperature_data.max() - temperature_data.min())
    pop_norm = (population_data - population_data.min()) / (population_data.max() - population_data.min())
    green_norm = 1 - ((green_cover_data - green_cover_data.min()) / (green_cover_data.max() - green_cover_data.min()))
    
    # Weighted combination (temperature: 40%, population: 35%, lack of green: 25%)
    vulnerability_index = 0.4 * temp_norm + 0.35 * pop_norm + 0.25 * green_norm
    
    return vulnerability_index

def calculate_air_quality_index(pm25, pm10, no2, so2, co, o3):
    """Calculate comprehensive Air Quality Index"""
    
    # Standard AQI breakpoints and calculations
    # This is a simplified version - actual AQI calculation is more complex
    
    def get_aqi_from_pm25(concentration):
        if concentration <= 12.0:
            return linear_interpolation(concentration, 0, 12.0, 0, 50)
        elif concentration <= 35.4:
            return linear_interpolation(concentration, 12.1, 35.4, 51, 100)
        elif concentration <= 55.4:
            return linear_interpolation(concentration, 35.5, 55.4, 101, 150)
        elif concentration <= 150.4:
            return linear_interpolation(concentration, 55.5, 150.4, 151, 200)
        elif concentration <= 250.4:
            return linear_interpolation(concentration, 150.5, 250.4, 201, 300)
        else:
            return 301
    
    aqi_pm25 = get_aqi_from_pm25(pm25)
    
    # Return the highest AQI among all pollutants
    return int(aqi_pm25)

def linear_interpolation(x, x1, x2, y1, y2):
    """Linear interpolation for AQI calculation"""
    return ((y2 - y1) / (x2 - x1)) * (x - x1) + y1

def analyze_water_quality_trends(water_data, timeframe_days=30):
    """Analyze water quality trends over specified timeframe"""
    
    # Calculate trends for each water body
    trends = {}
    
    for lake in water_data.columns:
        if lake != 'date':
            recent_data = water_data[lake].tail(timeframe_days)
            
            # Calculate trend using linear regression
            x = np.arange(len(recent_data))
            slope = np.polyfit(x, recent_data, 1)[0]
            
            if slope > 0.1:
                trend = 'Improving'
            elif slope < -0.1:
                trend = 'Deteriorating'
            else:
                trend = 'Stable'
            
            trends[lake] = {
                'trend': trend,
                'slope': slope,
                'current_quality': recent_data.iloc[-1],
                'change_rate': slope * timeframe_days
            }
    
    return trends

def detect_pollution_hotspots(pollution_data, threshold_percentile=75):
    """Detect pollution hotspots based on threshold"""
    
    hotspots = []
    
    for zone in pollution_data.columns:
        if zone != 'date':
            zone_data = pollution_data[zone]
            threshold = np.percentile(zone_data, threshold_percentile)
            
            if zone_data.iloc[-1] > threshold:
                hotspots.append({
                    'zone': zone,
                    'current_level': zone_data.iloc[-1],
                    'threshold': threshold,
                    'severity': 'High' if zone_data.iloc[-1] > np.percentile(zone_data, 90) else 'Moderate'
                })
    
    return hotspots

def export_data_to_json(data, filename):
    """Export processed data to JSON format"""
    
    # Convert numpy arrays and pandas objects to JSON serializable format
    json_data = convert_to_json_serializable(data)
    
    with open(filename, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    return filename

def convert_to_json_serializable(obj):
    """Convert data structures to JSON serializable format"""
    
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    elif isinstance(obj, pd.Series):
        return obj.to_list()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    else:
        return obj

def validate_environmental_data(data):
    """Validate environmental data for consistency and realistic ranges"""
    
    validation_results = {
        'valid': True,
        'warnings': [],
        'errors': []
    }
    
    # Temperature validation
    if 'temperature' in data:
        temp_data = data['temperature']
        if isinstance(temp_data, dict) and 'current_avg' in temp_data:
            temp = temp_data['current_avg']
            if temp < 15 or temp > 50:
                validation_results['warnings'].append(f"Temperature {temp}°C is outside typical range for Bengaluru")
    
    # AQI validation
    if 'air_quality' in data:
        aqi_data = data['air_quality']
        if isinstance(aqi_data, dict) and 'aqi_avg' in aqi_data:
            aqi = aqi_data['aqi_avg']
            if aqi < 0 or aqi > 500:
                validation_results['errors'].append(f"AQI value {aqi} is outside valid range (0-500)")
                validation_results['valid'] = False
    
    # Water quality validation
    if 'water_quality' in data:
        water_data = data['water_quality']
        if isinstance(water_data, dict) and 'lake_health_index' in water_data:
            health_index = water_data['lake_health_index']
            if health_index < 0 or health_index > 10:
                validation_results['errors'].append(f"Lake health index {health_index} is outside valid range (0-10)")
                validation_results['valid'] = False
    
    return validation_results
