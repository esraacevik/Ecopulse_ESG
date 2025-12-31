"""
Unified Weather Service
=======================

Combines OpenWeather API (real-time) and World Weather Repository (historical)
"""

from typing import Dict, Optional
from datetime import datetime, date, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from .openweather_client import OpenWeatherClient
from .weather_repo_loader import WeatherRepoLoader


class WeatherService:
    """
    Unified weather service combining OpenWeather API and World Weather Repository
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        use_cache: bool = True,
        verbose: bool = False
    ):
        """
        Initialize weather service
        
        Args:
            api_key: OpenWeather API key (optional, will try to load automatically)
            use_cache: Enable caching
            verbose: Print debug messages
        """
        self.verbose = verbose
        self.openweather = OpenWeatherClient(api_key=api_key) if api_key or self._has_api_key() else None
        self.weather_repo = WeatherRepoLoader(verbose=verbose)
        self.use_cache = use_cache
    
    def _has_api_key(self) -> bool:
        """Check if API key is available"""
        try:
            client = OpenWeatherClient()
            return client.api_key is not None
        except:
            return False
    
    def _log(self, message: str):
        """Log message if verbose"""
        if self.verbose:
            print(f"[WeatherService] {message}")
    
    def get_current_weather(
        self,
        location: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict:
        """
        Get current weather (prefers OpenWeather API, falls back to CSV)
        
        Args:
            location: City name (e.g., "Istanbul,TR")
            lat: Latitude
            lon: Longitude
        
        Returns:
            Current weather data
        """
        # Try OpenWeather API first
        if self.openweather:
            try:
                self._log(f"Fetching current weather from OpenWeather API for {location}")
                return self.openweather.get_current_weather(location, lat, lon)
            except Exception as e:
                self._log(f"OpenWeather API failed: {e}, falling back to CSV")
        
        # Fallback to CSV (most recent record)
        self._log(f"Using World Weather Repository for {location}")
        try:
            df = self.weather_repo.find_location(
                location_name=location.split(",")[0] if "," in location else location,
                lat=lat,
                lon=lon
            )
            
            if len(df) == 0:
                raise ValueError(f"No weather data found for {location}")
            
            # Get most recent record
            if "last_updated" in df.columns:
                df = df.sort_values("last_updated", ascending=False)
            
            record = df.iloc[0]
            
            temp = record.get("temperature_celsius", 20.0)
            hdd = max(0, 18.0 - temp)
            cdd = max(0, temp - 24.0)
            
            return {
                "temperature_celsius": float(temp),
                "humidity": float(record.get("humidity", 50)),
                "pressure_mb": float(record.get("pressure_mb", 1013.0)),
                "wind_speed_ms": float(record.get("wind_kph", 0)) / 3.6 if "wind_kph" in record else 0.0,
                "cloudiness": float(record.get("cloud", 0)),
                "heating_degree_days": hdd,
                "cooling_degree_days": cdd,
                "location": location,
                "timestamp": record.get("last_updated", datetime.now()).isoformat() if "last_updated" in record else datetime.now().isoformat(),
                "source": "world_weather_repo"
            }
        except Exception as e:
            raise Exception(f"Failed to get current weather: {str(e)}")
    
    def get_historical_weather(
        self,
        location: str,
        start_date: date,
        end_date: date,
        country: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict:
        """
        Get historical weather data (uses World Weather Repository)
        
        Args:
            location: City name
            start_date: Start date
            end_date: End date
            country: Country name
            lat: Latitude
            lon: Longitude
        
        Returns:
            Historical weather data
        """
        self._log(f"Fetching historical weather for {location} from {start_date} to {end_date}")
        
        try:
            df = self.weather_repo.get_historical_weather(
                location, start_date, end_date, country, lat, lon
            )
            
            # Convert to list of records
            records = []
            for _, row in df.iterrows():
                temp = row.get("temperature_celsius", 20.0)
                records.append({
                    "date": row.get("last_updated", datetime.now()).date().isoformat() if "last_updated" in row else None,
                    "temperature_celsius": float(temp),
                    "humidity": float(row.get("humidity", 50)),
                    "pressure_mb": float(row.get("pressure_mb", 1013.0)),
                    "heating_degree_days": max(0, 18.0 - temp),
                    "cooling_degree_days": max(0, temp - 24.0)
                })
            
            return {
                "location": location,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "records": records,
                "count": len(records),
                "source": "world_weather_repo"
            }
        except Exception as e:
            raise Exception(f"Failed to get historical weather: {str(e)}")
    
    def get_weather_features(
        self,
        location: str,
        target_date: Optional[date] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict:
        """
        Get weather features for ML model
        
        Args:
            location: City name
            target_date: Target date (if None, current)
            lat: Latitude
            lon: Longitude
        
        Returns:
            Weather features dictionary
        """
        if target_date is None or target_date == date.today():
            # Current weather
            if self.openweather:
                try:
                    return self.openweather.get_weather_features(location, datetime.now(), lat, lon)
                except:
                    pass
            
            # Fallback to CSV
            current = self.get_current_weather(location, lat, lon)
            return {
                "temperature_celsius": current["temperature_celsius"],
                "humidity": current["humidity"],
                "pressure_mb": current["pressure_mb"],
                "wind_speed_ms": current.get("wind_speed_ms", 0),
                "cloudiness": current.get("cloudiness", 0),
                "heating_degree_days": current.get("heating_degree_days", 0),
                "cooling_degree_days": current.get("cooling_degree_days", 0),
                "air_quality_index": current.get("air_quality_index")
            }
        else:
            # Historical weather from CSV
            features = self.weather_repo.get_weather_features_for_date(
                location, target_date, lat=lat, lon=lon
            )
            
            if features is None:
                # Fallback to average
                try:
                    # Get average for month
                    start = date(target_date.year, target_date.month, 1)
                    if target_date.month == 12:
                        end = date(target_date.year + 1, 1, 1) - timedelta(days=1)
                    else:
                        end = date(target_date.year, target_date.month + 1, 1) - timedelta(days=1)
                    
                    return self.weather_repo.get_average_weather(location, start, end)
                except:
                    # Ultimate fallback
                    return {
                        "temperature_celsius": 20.0,
                        "humidity": 50.0,
                        "pressure_mb": 1013.0,
                        "heating_degree_days": 0.0,
                        "cooling_degree_days": 0.0
                    }
            
            return features
    
    def get_forecast(
        self,
        location: str,
        days: int = 5,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict:
        """
        Get weather forecast (OpenWeather API only)
        
        Args:
            location: City name
            days: Number of days (max 5)
            lat: Latitude
            lon: Longitude
        
        Returns:
            Forecast data
        """
        if not self.openweather:
            raise ValueError("OpenWeather API not available for forecast")
        
        return self.openweather.get_forecast(location, lat, lon, days)

