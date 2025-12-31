"""
OpenWeather API Client
======================

Client for OpenWeather API with caching and rate limiting.
"""

import os
import requests
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json


class OpenWeatherClient:
    """OpenWeather API client with caching"""
    
    def __init__(self, api_key: Optional[str] = None, cache_ttl_hours: int = 1):
        """
        Initialize OpenWeather client
        
        Args:
            api_key: OpenWeather API key (if None, tries to read from file or env)
            cache_ttl_hours: Cache TTL in hours
        """
        self.api_key = api_key or self._load_api_key()
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.cache: Dict[str, Tuple[Dict, datetime]] = {}
        
        if not self.api_key:
            raise ValueError("OpenWeather API key not found. Please set OPENWEATHER_API_KEY or provide api_key parameter.")
    
    def _load_api_key(self) -> Optional[str]:
        """Load API key from file or environment"""
        # Try environment variable first
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if api_key:
            return api_key
        
        # Try reading from file
        api_key_file = Path(__file__).parent.parent.parent.parent / "yeni_veri_setleri" / "openweatherapi"
        if api_key_file.exists():
            try:
                with open(api_key_file, "r") as f:
                    return f.read().strip()
            except Exception:
                pass
        
        return None
    
    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """Generate cache key"""
        return f"{endpoint}:{json.dumps(params, sort_keys=True)}"
    
    def _is_cache_valid(self, cache_time: datetime) -> bool:
        """Check if cache entry is still valid"""
        return datetime.now() - cache_time < self.cache_ttl
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Get data from cache if valid"""
        if cache_key in self.cache:
            data, cache_time = self.cache[cache_key]
            if self._is_cache_valid(cache_time):
                return data
            else:
                del self.cache[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save data to cache"""
        self.cache[cache_key] = (data, datetime.now())
    
    def get_current_weather(
        self,
        location: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict:
        """
        Get current weather for a location
        
        Args:
            location: City name (e.g., "Istanbul,TR")
            lat: Latitude (optional, for more precise location)
            lon: Longitude (optional, for more precise location)
        
        Returns:
            Weather data dictionary
        """
        # Build query
        if lat is not None and lon is not None:
            query = f"lat={lat}&lon={lon}"
        else:
            query = f"q={location}"
        
        cache_key = self._get_cache_key("current", {"location": location, "lat": lat, "lon": lon})
        
        # Check cache
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        # API call
        url = f"{self.base_url}/weather"
        params = {
            "appid": self.api_key,
            "units": "metric"  # Celsius
        }
        
        if lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon
        else:
            params["q"] = location
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant fields
            result = {
                "temperature_celsius": data["main"]["temp"],
                "feels_like_celsius": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure_mb": data["main"]["pressure"],
                "wind_speed_ms": data.get("wind", {}).get("speed", 0),
                "wind_degree": data.get("wind", {}).get("deg", 0),
                "cloudiness": data.get("clouds", {}).get("all", 0),
                "visibility_m": data.get("visibility", 10000),
                "uv_index": None,  # Requires One Call API
                "condition": data["weather"][0]["main"],
                "condition_description": data["weather"][0]["description"],
                "timestamp": datetime.now().isoformat(),
                "location": location,
                "lat": data["coord"]["lat"],
                "lon": data["coord"]["lon"]
            }
            
            # Air quality (if available in response)
            if "air_quality" in data:
                result["air_quality"] = data["air_quality"]
            
            # Cache result
            self._save_to_cache(cache_key, result)
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenWeather API error: {str(e)}")
    
    def get_forecast(
        self,
        location: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        days: int = 5
    ) -> Dict:
        """
        Get weather forecast
        
        Args:
            location: City name
            lat: Latitude
            lon: Longitude
            days: Number of days (max 5 for free tier)
        
        Returns:
            Forecast data dictionary
        """
        if days > 5:
            days = 5  # Free tier limit
        
        # Build query
        if lat is not None and lon is not None:
            query = f"lat={lat}&lon={lon}"
        else:
            query = f"q={location}"
        
        cache_key = self._get_cache_key("forecast", {"location": location, "lat": lat, "lon": lon, "days": days})
        
        # Check cache
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        # API call
        url = f"{self.base_url}/forecast"
        params = {
            "appid": self.api_key,
            "units": "metric",
            "cnt": days * 8  # 3-hour intervals, 8 per day
        }
        
        if lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon
        else:
            params["q"] = location
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Process forecast list
            forecasts = []
            for item in data.get("list", []):
                forecasts.append({
                    "datetime": datetime.fromtimestamp(item["dt"]).isoformat(),
                    "temperature_celsius": item["main"]["temp"],
                    "feels_like_celsius": item["main"]["feels_like"],
                    "humidity": item["main"]["humidity"],
                    "pressure_mb": item["main"]["pressure"],
                    "wind_speed_ms": item.get("wind", {}).get("speed", 0),
                    "cloudiness": item.get("clouds", {}).get("all", 0),
                    "condition": item["weather"][0]["main"],
                    "condition_description": item["weather"][0]["description"]
                })
            
            result = {
                "location": location,
                "lat": data["city"]["coord"]["lat"],
                "lon": data["city"]["coord"]["lon"],
                "forecasts": forecasts,
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache result
            self._save_to_cache(cache_key, result)
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenWeather API forecast error: {str(e)}")
    
    def get_weather_features(
        self,
        location: str,
        date: Optional[datetime] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict:
        """
        Get weather features for ML model
        
        Args:
            location: City name
            date: Date for weather (if None, current)
            lat: Latitude
            lon: Longitude
        
        Returns:
            Weather features dictionary
        """
        if date is None or date.date() == datetime.now().date():
            # Current weather
            weather = self.get_current_weather(location, lat, lon)
        else:
            # For historical data, we'd need to use World Weather Repo
            # For now, return current weather as fallback
            weather = self.get_current_weather(location, lat, lon)
        
        # Calculate degree days
        temp = weather["temperature_celsius"]
        hdd = max(0, 18.0 - temp)  # Heating degree days (base 18°C)
        cdd = max(0, temp - 24.0)  # Cooling degree days (base 24°C)
        
        return {
            "temperature_celsius": temp,
            "humidity": weather["humidity"],
            "pressure_mb": weather["pressure_mb"],
            "wind_speed_ms": weather.get("wind_speed_ms", 0),
            "cloudiness": weather.get("cloudiness", 0),
            "heating_degree_days": hdd,
            "cooling_degree_days": cdd,
            "air_quality_index": weather.get("air_quality", {}).get("us-epa-index", None) if isinstance(weather.get("air_quality"), dict) else None
        }

