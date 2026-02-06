"""
Weather API Tool with REAL API integration (FREE - no key required)
"""
import requests
import time
from typing import Dict, Any
from .base_tool import BaseTool
from config import Config
from utils import retry_on_failure, format_response

class WeatherTool(BaseTool):
    """Tool for weather API operations"""
    
    def __init__(self):
        super().__init__(
            name="weather_tool",
            description="Get current weather using real weather API"
        )
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute weather API call"""
        
        cache_key = self.get_cache_key(**kwargs)
        cached_result = self.get_cached_result(cache_key)
        if cached_result:
            cached_result["cached"] = True
            return cached_result
        
        city = kwargs.get("city", "London")
        
        print(f"[WeatherTool] Getting weather for: {city}")
        
        try:
            # Use Open-Meteo FREE API (no key required)
            # First, get coordinates for the city
            geocode_url = f"https://geocoding-api.open-meteo.com/v1/search"
            geocode_params = {
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            }
            
            geocode_response = requests.get(
                geocode_url,
                params=geocode_params,
                timeout=Config.REQUEST_TIMEOUT
            )
            
            if geocode_response.status_code == 200:
                geocode_data = geocode_response.json()
                
                if geocode_data.get("results"):
                    location = geocode_data["results"][0]
                    latitude = location["latitude"]
                    longitude = location["longitude"]
                    country = location.get("country", "")
                    region = location.get("admin1", "")
                    
                    # Get current weather
                    weather_url = f"{Config.WEATHER_API_BASE}/forecast"
                    weather_params = {
                        "latitude": latitude,
                        "longitude": longitude,
                        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m",
                        "timezone": "auto"
                    }
                    
                    weather_response = requests.get(
                        weather_url,
                        params=weather_params,
                        timeout=Config.REQUEST_TIMEOUT
                    )
                    
                    if weather_response.status_code == 200:
                        weather_data = weather_response.json()
                        current = weather_data.get("current", {})
                        
                        # Map weather code to human-readable condition
                        weather_condition = self._get_weather_condition(current.get("weather_code", 0))
                        
                        result = format_response({
                            "city": city,
                            "country": country,
                            "region": region,
                            "latitude": latitude,
                            "longitude": longitude,
                            "temperature": current.get("temperature_2m", 0),
                            "feels_like": current.get("apparent_temperature", 0),
                            "humidity": current.get("relative_humidity_2m", 0),
                            "weather_code": current.get("weather_code", 0),
                            "condition": weather_condition,
                            "wind_speed": current.get("wind_speed_10m", 0),
                            "wind_direction": current.get("wind_direction_10m", 0),
                            "units": {
                                "temperature": "°C",
                                "wind_speed": "km/h"
                            },
                            "source": "open-meteo_api"
                        })
                        
                        self.cache_result(cache_key, result)
                        return result
            
            # If geocoding fails, try with OpenWeatherMap (requires key)
            if Config.OPENWEATHER_API_KEY:
                return self._get_openweather_data(city)
            else:
                return self._get_fallback_data(city)
                
        except Exception as e:
            print(f"Weather API error: {e}")
            return self._get_fallback_data(city)
    
    def _get_weather_condition(self, code: int) -> str:
        """Convert WMO weather code to condition"""
        # WMO Weather interpretation codes (WW)
        condition_map = {
            0: "Clear sky",
            1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
            80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
        }
        return condition_map.get(code, "Unknown")
    
    def _get_openweather_data(self, city: str) -> Dict[str, Any]:
        """Get weather data from OpenWeatherMap (requires API key)"""
        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": city,
                "appid": Config.OPENWEATHER_API_KEY,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=Config.REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                return format_response({
                    "city": data["name"],
                    "country": data["sys"]["country"],
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "condition": data["weather"][0]["main"],
                    "description": data["weather"][0]["description"],
                    "wind_speed": data["wind"]["speed"],
                    "pressure": data["main"]["pressure"],
                    "source": "openweathermap_api"
                })
        except:
            pass
        
        return self._get_fallback_data(city)
    
    def _get_fallback_data(self, city: str) -> Dict[str, Any]:
        """Fallback weather data"""
        print(f"[WeatherTool] Using fallback data for: {city}")
        
        # Mock weather data
        weather_data = {
            "Tokyo": {"temp": 25.5, "condition": "Clear sky", "humidity": 60, "wind": 12.3},
            "London": {"temp": 14.0, "condition": "Overcast", "humidity": 85, "wind": 15.2},
            "New York": {"temp": 22.0, "condition": "Partly cloudy", "humidity": 55, "wind": 8.7},
            "Paris": {"temp": 19.5, "condition": "Light drizzle", "humidity": 70, "wind": 10.5},
            "Berlin": {"temp": 16.0, "condition": "Moderate rain", "humidity": 75, "wind": 12.8},
            "Mumbai": {"temp": 32.0, "condition": "Clear sky", "humidity": 80, "wind": 6.5},
            "Sydney": {"temp": 24.5, "condition": "Sunny", "humidity": 65, "wind": 14.2}
        }
        
        data = weather_data.get(city.title(), {"temp": 20.0, "condition": "Unknown", "humidity": 50, "wind": 10.0})
        
        return format_response({
            "city": city,
            "temperature": data["temp"],
            "feels_like": data["temp"],
            "humidity": data["humidity"],
            "condition": data["condition"],
            "wind_speed": data["wind"],
            "source": "fallback_data",
            "note": "Using fallback data (API unavailable)"
        })
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate parameters"""
        return "city" in kwargs