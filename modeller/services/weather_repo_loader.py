"""
World Weather Repository Loader
================================

Load and filter weather data from GlobalWeatherRepository.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from datetime import datetime, date
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import DATASETS, get_dataset_path


class WeatherRepoLoader:
    """Load historical weather data from World Weather Repository CSV"""
    
    def __init__(self, verbose: bool = False):
        """
        Initialize loader
        
        Args:
            verbose: Print progress messages
        """
        self.verbose = verbose
        self.csv_path = None
        self._data_cache: Optional[pd.DataFrame] = None
        self._load_path()
    
    def _load_path(self):
        """Load CSV file path from config"""
        try:
            base_path = get_dataset_path("world_weather")
            self.csv_path = base_path / DATASETS["world_weather"]["files"]["csv"]
            
            if not self.csv_path.exists():
                raise FileNotFoundError(f"Weather repository CSV not found: {self.csv_path}")
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not load weather repository path: {e}")
            self.csv_path = None
    
    def _load_data(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Load weather data from CSV (with caching)
        
        Args:
            force_reload: Force reload even if cached
        
        Returns:
            Weather DataFrame
        """
        if self.csv_path is None:
            raise ValueError("Weather repository CSV path not configured")
        
        if self._data_cache is not None and not force_reload:
            return self._data_cache
        
        if self.verbose:
            print(f"Loading weather data from: {self.csv_path}")
        
        # Read CSV in chunks (29MB file)
        chunk_size = 10000
        chunks = []
        
        try:
            for chunk in pd.read_csv(self.csv_path, chunksize=chunk_size, low_memory=False):
                chunks.append(chunk)
            
            df = pd.concat(chunks, ignore_index=True)
            
            # Parse date column
            if "last_updated" in df.columns:
                df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
            
            # Clean data
            df = df.dropna(subset=["temperature_celsius", "humidity"])
            
            self._data_cache = df
            
            if self.verbose:
                print(f"Loaded {len(df)} weather records")
            
            return df
            
        except Exception as e:
            raise Exception(f"Error loading weather repository: {str(e)}")
    
    def find_location(
        self,
        location_name: Optional[str] = None,
        country: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        tolerance: float = 0.5
    ) -> pd.DataFrame:
        """
        Find weather data for a location
        
        Args:
            location_name: City name (e.g., "Istanbul")
            country: Country name (e.g., "Turkey")
            lat: Latitude
            lon: Longitude
            tolerance: Location matching tolerance in degrees
        
        Returns:
            Filtered DataFrame
        """
        df = self._load_data()
        
        # Build filter conditions
        conditions = []
        
        if location_name:
            conditions.append(df["location_name"].str.contains(location_name, case=False, na=False))
        
        if country:
            conditions.append(df["country"].str.contains(country, case=False, na=False))
        
        if lat is not None and lon is not None:
            lat_condition = (df["latitude"] >= lat - tolerance) & (df["latitude"] <= lat + tolerance)
            lon_condition = (df["longitude"] >= lon - tolerance) & (df["longitude"] <= lon + tolerance)
            conditions.append(lat_condition & lon_condition)
        
        if conditions:
            mask = conditions[0]
            for cond in conditions[1:]:
                mask = mask & cond
            df = df[mask]
        
        return df
    
    def get_historical_weather(
        self,
        location: str,
        start_date: date,
        end_date: date,
        country: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Get historical weather data for date range
        
        Args:
            location: City name
            start_date: Start date
            end_date: End date
            country: Country name (optional)
            lat: Latitude (optional)
            lon: Longitude (optional)
        
        Returns:
            Historical weather DataFrame
        """
        # Find location
        location_df = self.find_location(location, country, lat, lon)
        
        if len(location_df) == 0:
            raise ValueError(f"No weather data found for location: {location}")
        
        # Filter by date range
        if "last_updated" in location_df.columns:
            mask = (
                (location_df["last_updated"].dt.date >= start_date) &
                (location_df["last_updated"].dt.date <= end_date)
            )
            location_df = location_df[mask]
        
        # Sort by date
        if "last_updated" in location_df.columns:
            location_df = location_df.sort_values("last_updated")
        
        return location_df
    
    def get_weather_features_for_date(
        self,
        location: str,
        target_date: date,
        country: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Optional[Dict]:
        """
        Get weather features for a specific date
        
        Args:
            location: City name
            target_date: Target date
            country: Country name
            lat: Latitude
            lon: Longitude
        
        Returns:
            Weather features dictionary or None if not found
        """
        try:
            df = self.get_historical_weather(
                location, target_date, target_date, country, lat, lon
            )
            
            if len(df) == 0:
                return None
            
            # Get closest record to target date
            record = df.iloc[0]
            
            temp = record.get("temperature_celsius", np.nan)
            if pd.isna(temp):
                return None
            
            # Calculate degree days
            hdd = max(0, 18.0 - temp)
            cdd = max(0, temp - 24.0)
            
            return {
                "temperature_celsius": float(temp),
                "humidity": float(record.get("humidity", 0)),
                "pressure_mb": float(record.get("pressure_mb", 1013.0)),
                "wind_speed_ms": float(record.get("wind_kph", 0)) / 3.6 if "wind_kph" in record else 0.0,
                "cloudiness": float(record.get("cloud", 0)),
                "heating_degree_days": hdd,
                "cooling_degree_days": cdd,
                "air_quality_index": None  # Not always available in CSV
            }
            
        except Exception as e:
            if self.verbose:
                print(f"Error getting weather features: {e}")
            return None
    
    def get_average_weather(
        self,
        location: str,
        start_date: date,
        end_date: date,
        country: Optional[str] = None
    ) -> Dict:
        """
        Get average weather for date range
        
        Args:
            location: City name
            start_date: Start date
            end_date: End date
            country: Country name
        
        Returns:
            Average weather features
        """
        df = self.get_historical_weather(location, start_date, end_date, country)
        
        if len(df) == 0:
            raise ValueError(f"No weather data for {location} in date range")
        
        # Calculate averages
        temp_avg = df["temperature_celsius"].mean()
        humidity_avg = df["humidity"].mean()
        pressure_avg = df.get("pressure_mb", pd.Series([1013.0] * len(df))).mean()
        
        # Average degree days
        hdd_avg = (18.0 - df["temperature_celsius"]).clip(lower=0).mean()
        cdd_avg = (df["temperature_celsius"] - 24.0).clip(lower=0).mean()
        
        return {
            "temperature_celsius": float(temp_avg),
            "humidity": float(humidity_avg),
            "pressure_mb": float(pressure_avg),
            "heating_degree_days": float(hdd_avg),
            "cooling_degree_days": float(cdd_avg)
        }

