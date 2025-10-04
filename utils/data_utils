import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import numpy as np

def get_bengaluru_coordinates() -> Tuple[float, float]:
    """Get Bengaluru city center coordinates"""
    return 12.9716, 77.5946

def calculate_metrics(weather_data: Optional[Dict], air_quality_data: Optional[Dict], nasa_data: Optional[Dict] = None) -> Dict:
    """Calculate derived climate metrics"""
    metrics = {}
    
    if weather_data:
        temp = weather_data.get('temperature_2m', 25)
        humidity = weather_data.get('relative_humidity_2m', 50)
        
        # Heat index calculation
        metrics['heat_index'] = calculate_heat_index(temp, humidity)
        
        # Comfort index (0-100 scale)
        metrics['comfort_index'] = calculate_comfort_index(temp, humidity)
        
        # Lake health estimation based on temperature and humidity
        metrics['lake_health_estimate'] = min(100, max(0, humidity + (30 - temp) * 2))
    
    if air_quality_data:
        pm25 = air_quality_data.get('pm2_5', 25)
        pm10 = air_quality_data.get('pm10', 50)
        
        # Air Quality Index calculation (simplified)
        metrics['aqi_estimate'] = calculate_simple_aqi(pm25, pm10)
        
        # Health risk assessment
        metrics['health_risk'] = assess_health_risk(pm25, pm10)
    
    return metrics

def calculate_heat_index(temperature: float, humidity: float) -> float:
    """Calculate heat index from temperature and humidity"""
    if temperature < 27:  # Not meaningful below 27°C
        return temperature
    
    # Simplified heat index formula
    hi = (
        -8.78469475556 + 1.61139411 * temperature + 2.33854883889 * humidity +
        -0.14611605 * temperature * humidity + -0.012308094 * temperature**2 +
        -0.0164248277778 * humidity**2 + 0.002211732 * temperature**2 * humidity +
        0.00072546 * temperature * humidity**2 + -0.000003582 * temperature**2 * humidity**2
    )
    
    return round(hi, 1)

def calculate_comfort_index(temperature: float, humidity: float) -> float:
    """Calculate comfort index (0-100)"""
    # Optimal comfort: 20-26°C, 40-60% humidity
    temp_comfort = max(0, 100 - abs(temperature - 23) * 10)
    humidity_comfort = max(0, 100 - abs(humidity - 50) * 2)
    
    return round((temp_comfort + humidity_comfort) / 2, 1)

def calculate_simple_aqi(pm25: float, pm10: float) -> float:
    """Calculate simplified Air Quality Index"""
    # Simplified AQI calculation based on PM values
    aqi_pm25 = (pm25 / 25) * 50  # Scale PM2.5 to 0-200 range
    aqi_pm10 = (pm10 / 50) * 50  # Scale PM10 to 0-200 range
    
    return round(max(aqi_pm25, aqi_pm10), 1)

def assess_health_risk(pm25: float, pm10: float) -> str:
    """Assess health risk based on PM values"""
    max_pm = max(pm25 / 25, pm10 / 50)  # Normalize to WHO guidelines
    
    if max_pm <= 1:
        return "Low"
    elif max_pm <= 2:
        return "Moderate"
    elif max_pm <= 3:
        return "High"
    else:
        return "Very High"

def generate_time_series_data(base_value: float, days: int = 30, variation: float = 0.1) -> pd.DataFrame:
    """Generate synthetic time series data for visualization"""
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), end=datetime.now(), freq='D')
    
    # Add random variation and trend
    values = []
    for i in range(len(dates)):
        trend = base_value + (i * 0.01)  # Small upward trend
        noise = np.random.normal(0, base_value * variation)
        values.append(max(0, trend + noise))
    
    return pd.DataFrame({'date': dates, 'value': values})

def get_bengaluru_districts() -> List[Dict]:
    """Get Bengaluru districts with coordinates"""
    return [
        {"name": "Koramangala", "lat": 12.9352, "lon": 77.6245, "type": "residential"},
        {"name": "Indiranagar", "lat": 12.9719, "lon": 77.6412, "type": "commercial"},
        {"name": "Whitefield", "lat": 12.9698, "lon": 77.7500, "type": "it_hub"},
        {"name": "Electronic City", "lat": 12.8456, "lon": 77.6611, "type": "it_hub"},
        {"name": "Jayanagar", "lat": 12.9254, "lon": 77.5831, "type": "residential"},
        {"name": "Malleshwaram", "lat": 13.0039, "lon": 77.5731, "type": "residential"},
        {"name": "JP Nagar", "lat": 12.9081, "lon": 77.5831, "type": "residential"},
        {"name": "BTM Layout", "lat": 12.9165, "lon": 77.6101, "type": "residential"}
    ]

def get_major_lakes() -> List[Dict]:
    """Get major lakes in Bengaluru with metadata"""
    return [
        {
            "name": "Bellandur Lake",
            "lat": 12.9259,
            "lon": 77.6759,
            "area_hectares": 361,
            "pollution_sources": ["sewage", "industrial_waste"],
            "health_score": 45
        },
        {
            "name": "Ulsoor Lake",
            "lat": 12.9759,
            "lon": 77.6259,
            "area_hectares": 50,
            "pollution_sources": ["urban_runoff"],
            "health_score": 78
        },
        {
            "name": "Sankey Tank",
            "lat": 12.9912,
            "lon": 77.5672,
            "area_hectares": 15,
            "pollution_sources": [],
            "health_score": 82
        },
        {
            "name": "Hebbal Lake",
            "lat": 13.0359,
            "lon": 77.5972,
            "area_hectares": 72,
            "pollution_sources": ["sewage"],
            "health_score": 67
        },
        {
            "name": "Madivala Lake",
            "lat": 12.9254,
            "lon": 77.6231,
            "area_hectares": 114,
            "pollution_sources": ["sewage", "urban_runoff"],
            "health_score": 59
        }
    ]

def format_number_with_units(value: float, unit: str) -> str:
    """Format numbers with appropriate units and precision"""
    if unit == "temperature":
        return f"{value:.1f}°C"
    elif unit == "percentage":
        return f"{value:.1f}%"
    elif unit == "pm":
        return f"{value:.1f} μg/m³"
    elif unit == "area":
        return f"{value:.1f} km²"
    elif unit == "index":
        return f"{value:.0f}"
    else:
        return f"{value:.2f} {unit}"

def calculate_trend_direction(current: float, previous: float) -> str:
    """Calculate trend direction and return emoji"""
    if current > previous * 1.05:  # 5% increase threshold
        return "↗️ Increasing"
    elif current < previous * 0.95:  # 5% decrease threshold
        return "↘️ Decreasing"
    else:
        return "→ Stable"

def get_stakeholder_priorities(stakeholder: str) -> List[str]:
    """Get priority metrics for each stakeholder"""
    priorities = {
        "Citizens": ["air_quality", "temperature", "uv_index", "comfort_index"],
        "BBMP (City Planning)": ["urban_growth", "heat_islands", "green_cover", "development_pressure"],
        "BWSSB (Water Board)": ["lake_health", "water_quality", "rainfall", "groundwater"],
        "BESCOM (Electricity)": ["temperature", "heat_index", "cooling_demand", "peak_load"],
        "Parks Department": ["green_cover", "vegetation_health", "park_usage", "urban_canopy"],
        "Researchers": ["all_metrics", "trends", "correlations", "climate_patterns"]
    }
    
    return priorities.get(stakeholder, ["temperature", "air_quality"])

def filter_data_by_stakeholder(data: Dict, stakeholder: str) -> Dict:
    """Filter data based on stakeholder priorities"""
    priorities = get_stakeholder_priorities(stakeholder)
    
    if "all_metrics" in priorities:
        return data
    
    filtered_data = {}
    for key, value in data.items():
        if any(priority in key.lower() for priority in priorities):
            filtered_data[key] = value
    
    return filtered_data if filtered_data else data
