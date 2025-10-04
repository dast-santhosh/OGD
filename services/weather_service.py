import requests
import os
from typing import Dict, Optional, List
from datetime import datetime, timedelta

class WeatherService:
    """Service for Open-Meteo API integration"""
    
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1"
        
    def get_current_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """Get current weather conditions"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m", 
                    "apparent_temperature",
                    "weather_code",
                    "wind_speed_10m",
                    "wind_direction_10m"
                ],
                "timezone": "Asia/Kolkata"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            current = data.get("current", {})
            
            return {
                "temperature_2m": current.get("temperature_2m"),
                "relative_humidity_2m": current.get("relative_humidity_2m"),
                "apparent_temperature": current.get("apparent_temperature"),
                "weather_code": current.get("weather_code"),
                "wind_speed_10m": current.get("wind_speed_10m"),
                "wind_direction_10m": current.get("wind_direction_10m"),
                "timestamp": current.get("time"),
                "location": {"lat": lat, "lon": lon}
            }
            
        except requests.RequestException as e:
            print(f"Weather API error: {str(e)}")
            return None
    
    def get_air_quality(self, lat: float, lon: float) -> Optional[Dict]:
        """Get current air quality data"""
        try:
            url = f"{self.base_url}/air-quality"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone",
                "timezone": "Asia/Kolkata"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            current = data.get("current", {})
            
            return {
                "pm10": current.get("pm10"),
                "pm2_5": current.get("pm2_5"),
                "carbon_monoxide": current.get("carbon_monoxide"),
                "nitrogen_dioxide": current.get("nitrogen_dioxide"),
                "sulphur_dioxide": current.get("sulphur_dioxide"),
                "ozone": current.get("ozone"),
                "timestamp": current.get("time"),
                "location": {"lat": lat, "lon": lon}
            }
            
        except requests.RequestException as e:
            print(f"Air quality API error: {str(e)}")
            return None
    
    def get_weather_forecast(self, lat: float, lon: float, days: int = 7) -> Optional[Dict]:
        """Get weather forecast"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "wind_speed_10m_max",
                    "weather_code"
                ],
                "forecast_days": days,
                "timezone": "Asia/Kolkata"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            daily = data.get("daily", {})
            
            return {
                "daily_forecast": daily,
                "location": {"lat": lat, "lon": lon},
                "forecast_days": days
            }
            
        except requests.RequestException as e:
            print(f"Forecast API error: {str(e)}")
            return None
    
    def get_historical_weather(self, lat: float, lon: float, start_date: str, end_date: str) -> Optional[Dict]:
        """Get historical weather data"""
        try:
            url = f"{self.base_url}/historical-weather"
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date,
                "end_date": end_date,
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min", 
                    "precipitation_sum"
                ],
                "timezone": "Asia/Kolkata"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            print(f"Historical weather API error: {str(e)}")
            return None
    
    def calculate_heat_index(self, temperature: float, humidity: float) -> float:
        """Calculate heat index from temperature and humidity"""
        if temperature < 27:  # Heat index not meaningful below 80°F (27°C)
            return temperature
        
        # Simplified heat index calculation for Celsius
        hi = (
            -8.784695 + 
            1.61139411 * temperature +
            2.338549 * humidity -
            0.14611605 * temperature * humidity -
            0.012308094 * temperature**2 -
            0.016424828 * humidity**2 +
            0.002211732 * temperature**2 * humidity +
            0.00072546 * temperature * humidity**2 -
            0.000003582 * temperature**2 * humidity**2
        )
        
        return round(hi, 1)
    
    def get_uv_index(self, lat: float, lon: float) -> Optional[Dict]:
        """Get UV index data"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "daily": ["uv_index_max"],
                "forecast_days": 1,
                "timezone": "Asia/Kolkata"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            daily = data.get("daily", {})
            uv_max = daily.get("uv_index_max", [0])[0] if daily.get("uv_index_max") else 0
            
            return {
                "uv_index": uv_max,
                "risk_level": self._get_uv_risk_level(uv_max),
                "timestamp": datetime.now().isoformat()
            }
            
        except requests.RequestException as e:
            print(f"UV index API error: {str(e)}")
            return None
    
    def _get_uv_risk_level(self, uv_index: float) -> str:
        """Convert UV index to risk level"""
        if uv_index <= 2:
            return "Low"
        elif uv_index <= 5:
            return "Moderate"
        elif uv_index <= 7:
            return "High"
        elif uv_index <= 10:
            return "Very High"
        else:
            return "Extreme"
