"""
Energy Prediction Feature Engineering
======================================

Enerji tahmini için özellik mühendisliği.
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Tuple
from pathlib import Path
from datetime import date

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    # Fallback: simple progress function
    def tqdm(iterable, desc="", total=None):
        if total is None:
            total = len(iterable) if hasattr(iterable, '__len__') else None
        if total:
            print(f"{desc}... ({total} items)")
        return iterable

from utils.feature_utils import (
    create_time_features,
    create_lag_features,
    create_rolling_features,
    create_cyclical_features,
    create_degree_days
)

try:
    from services.weather_service import WeatherService
    WEATHER_AVAILABLE = True
except ImportError:
    WEATHER_AVAILABLE = False
    WeatherService = None


class EnergyFeatureEngineer:
    """Enerji tahmini için feature engineering"""
    
    def __init__(
        self,
        target_column: str = "total_power",
        date_column: str = "Time",
        lag_hours: List[int] = [1, 2, 3, 6, 12, 24, 48, 168],
        rolling_windows: List[int] = [6, 12, 24, 48, 168],
        include_cyclical: bool = True,
        include_weather: bool = True,
        location: str = "Istanbul,TR",
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ):
        """
        Args:
            target_column: Hedef kolon (tahmin edilecek)
            date_column: Tarih kolonu
            lag_hours: Lag saatleri
            rolling_windows: Rolling window boyutları
            include_cyclical: Döngüsel features (sin/cos)
            include_weather: Hava durumu features
            location: Location name for weather (e.g., "Istanbul,TR")
            lat: Latitude (optional)
            lon: Longitude (optional)
        """
        self.target_column = target_column
        self.date_column = date_column
        self.lag_hours = lag_hours
        self.rolling_windows = rolling_windows
        self.include_cyclical = include_cyclical
        self.include_weather = include_weather and WEATHER_AVAILABLE
        self.location = location
        self.lat = lat
        self.lon = lon
        
        self.feature_columns = []
        
        # Initialize weather service if needed
        if self.include_weather:
            try:
                self.weather_service = WeatherService(verbose=False)
            except Exception as e:
                print(f"Warning: Weather service not available: {e}")
                self.include_weather = False
                self.weather_service = None
        else:
            self.weather_service = None
    
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Feature'ları oluştur
        
        Args:
            df: Ham DataFrame
        
        Returns:
            Feature'lı DataFrame
        """
        df = df.copy()
        
        # Tarih kolonunu kontrol et
        if self.date_column not in df.columns:
            raise ValueError(f"Date column not found: {self.date_column}")
        
        df[self.date_column] = pd.to_datetime(df[self.date_column])
        df = df.sort_values(self.date_column).reset_index(drop=True)
        
        # 1. Zaman features
        print("1/5 Zaman features oluşturuluyor...")
        df = create_time_features(df, self.date_column)
        
        # 2. Döngüsel features
        if self.include_cyclical:
            print("2/5 Döngüsel features oluşturuluyor...")
            df = create_cyclical_features(df, "hour", 24)
            df = create_cyclical_features(df, "day_of_week", 7)
            df = create_cyclical_features(df, "month", 12)
        
        # 3. Lag features
        print("3/5 Lag features oluşturuluyor...")
        df = create_lag_features(df, self.target_column, self.lag_hours)
        
        # 4. Rolling features
        print("4/5 Rolling features oluşturuluyor...")
        df = create_rolling_features(
            df, 
            self.target_column, 
            self.rolling_windows,
            functions=["mean", "std", "min", "max"]
        )
        
        # 5. Weather features
        if self.include_weather:
            print("5/6 Weather features oluşturuluyor...")
            df = self._add_weather_features(df)
        else:
            print("5/6 Weather features atlanıyor...")
        
        # 6. Ek features
        print("6/6 Ek features oluşturuluyor...")
        df = self._create_additional_features(df)
        
        # Feature kolonlarını kaydet
        self._save_feature_columns(df)
        
        # inf değerlerini NaN'e çevir
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # NaN'leri temizle (lag/rolling kaynaklı)
        initial_len = len(df)
        df = df.dropna()
        print(f"NaN temizliği: {initial_len} -> {len(df)} satır")
        
        return df
    
    def _add_weather_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Weather features ekle - OPTIMIZED: Batch processing ile hızlı
        
        Args:
            df: DataFrame with date column
        
        Returns:
            DataFrame with weather features
        """
        if not self.include_weather or self.weather_service is None:
            return df
        
        df = df.copy()
        
        # Extract dates
        df['_date'] = pd.to_datetime(df[self.date_column]).dt.date
        
        # Get date range
        min_date = df['_date'].min()
        max_date = df['_date'].max()
        
        print(f"  -> Weather features için tarih aralığı: {min_date} - {max_date}")
        print(f"  -> Toplam {len(df):,} satır için weather features oluşturuluyor...")
        
        # OPTIMIZATION: Toplu weather verisi çek (tek seferde tüm tarih aralığı)
        try:
            # World Weather Repository'den toplu veri çek
            if hasattr(self.weather_service, 'weather_repo') and self.weather_service.weather_repo:
                print("  -> World Weather Repository'den toplu veri yükleniyor...")
                
                # Location formatını düzelt (Istanbul,TR -> Istanbul)
                location_name = self.location.split(',')[0].strip() if ',' in self.location else self.location
                country_name = self.location.split(',')[1].strip() if ',' in self.location else None
                
                # Tüm tarih aralığı için weather verisi çek
                weather_df = self.weather_service.weather_repo.get_historical_weather(
                    location_name,
                    min_date,
                    max_date,
                    country=country_name,
                    lat=self.lat,
                    lon=self.lon
                )
                
                if len(weather_df) > 0:
                    print(f"  -> {len(weather_df):,} weather kaydı bulundu")
                    
                    # Weather DataFrame'i hazırla
                    weather_df['_date'] = pd.to_datetime(weather_df['last_updated']).dt.date
                    
                    # Temperature ve diğer değerleri hazırla
                    weather_df['temperature_celsius'] = pd.to_numeric(
                        weather_df.get('temperature_celsius', 20.0), errors='coerce'
                    ).fillna(20.0)
                    
                    weather_df['humidity'] = pd.to_numeric(
                        weather_df.get('humidity', 50.0), errors='coerce'
                    ).fillna(50.0)
                    
                    weather_df['pressure_mb'] = pd.to_numeric(
                        weather_df.get('pressure_mb', 1013.0), errors='coerce'
                    ).fillna(1013.0)
                    
                    # Wind speed (kph -> m/s)
                    wind_kph = pd.to_numeric(
                        weather_df.get('wind_kph', 0), errors='coerce'
                    ).fillna(0.0)
                    weather_df['wind_speed_ms'] = wind_kph / 3.6
                    
                    weather_df['cloudiness'] = pd.to_numeric(
                        weather_df.get('cloud', 0), errors='coerce'
                    ).fillna(0.0)
                    
                    # Degree days hesapla
                    weather_df['heating_degree_days'] = (18.0 - weather_df['temperature_celsius']).clip(lower=0)
                    weather_df['cooling_degree_days'] = (weather_df['temperature_celsius'] - 24.0).clip(lower=0)
                    
                    # Her tarih için en yakın kaydı seç (günlük ortalama)
                    weather_daily = weather_df.groupby('_date').agg({
                        'temperature_celsius': 'mean',
                        'humidity': 'mean',
                        'pressure_mb': 'mean',
                        'wind_speed_ms': 'mean',
                        'cloudiness': 'mean',
                        'heating_degree_days': 'mean',
                        'cooling_degree_days': 'mean'
                    }).reset_index()
                    
                    print(f"  -> {len(weather_daily):,} unique tarih için weather features hazırlandı")
                    
                    # Merge: Her satır için tarihine göre weather features ekle
                    df = df.merge(
                        weather_daily[['_date', 'temperature_celsius', 'humidity', 'pressure_mb', 
                                      'wind_speed_ms', 'cloudiness', 'heating_degree_days', 'cooling_degree_days']],
                        on='_date',
                        how='left'
                    )
                    
                    # Eksik tarihler için default değerler
                    missing_mask = df['temperature_celsius'].isna()
                    if missing_mask.sum() > 0:
                        print(f"  -> {missing_mask.sum():,} satır için weather verisi bulunamadı, default değerler kullanılıyor")
                        df.loc[missing_mask, 'temperature_celsius'] = 20.0
                        df.loc[missing_mask, 'humidity'] = 50.0
                        df.loc[missing_mask, 'pressure_mb'] = 1013.0
                        df.loc[missing_mask, 'wind_speed_ms'] = 0.0
                        df.loc[missing_mask, 'cloudiness'] = 0.0
                        df.loc[missing_mask, 'heating_degree_days'] = 0.0
                        df.loc[missing_mask, 'cooling_degree_days'] = 0.0
                    
                    # Column isimlerini weather_ prefix ile değiştir
                    weather_cols = ['temperature_celsius', 'humidity', 'pressure_mb', 
                                   'wind_speed_ms', 'cloudiness', 'heating_degree_days', 'cooling_degree_days']
                    rename_dict = {col: f'weather_{col}' for col in weather_cols}
                    df = df.rename(columns=rename_dict)
                    
                    # Geçici _date kolonunu sil
                    df = df.drop(columns=['_date'])
                    
                    print(f"  -> Weather features başarıyla eklendi!")
                    return df
                else:
                    print("  -> Weather verisi bulunamadı, default değerler kullanılıyor")
            else:
                print("  -> Weather repository bulunamadı, default değerler kullanılıyor")
        except Exception as e:
            print(f"  -> Weather batch processing hatası: {e}")
            print("  -> Fallback: Default değerler kullanılıyor")
        
        # Fallback: Default değerler (optimizasyon başarısız olursa)
        default_features = {
            'weather_temperature_celsius': 20.0,
            'weather_humidity': 50.0,
            'weather_pressure_mb': 1013.0,
            'weather_wind_speed_ms': 0.0,
            'weather_cloudiness': 0.0,
            'weather_heating_degree_days': 0.0,
            'weather_cooling_degree_days': 0.0
        }
        
        for col, val in default_features.items():
            df[col] = val
        
        # Geçici _date kolonunu sil (varsa)
        if '_date' in df.columns:
            df = df.drop(columns=['_date'])
        
        return df
    
    def _create_additional_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ek features oluştur"""
        
        # İş günü mü?
        df["is_business_hour"] = (
            (df["hour"] >= 9) & 
            (df["hour"] <= 18) & 
            (df["is_weekend"] == 0)
        ).astype(int)
        
        # Pik saat mi?
        df["is_peak_hour"] = (
            ((df["hour"] >= 8) & (df["hour"] <= 11)) |
            ((df["hour"] >= 17) & (df["hour"] <= 20))
        ).astype(int)
        
        # Gece mi?
        df["is_night"] = (
            (df["hour"] >= 22) | (df["hour"] <= 6)
        ).astype(int)
        
        # Değişim oranları
        if self.target_column in df.columns:
            df["power_change_1h"] = df[self.target_column].diff(1)
            df["power_change_24h"] = df[self.target_column].diff(24)
            df["power_pct_change_1h"] = df[self.target_column].pct_change(1)
        
        # Önceki gün aynı saat
        if f"{self.target_column}_lag_24" in df.columns:
            df["same_hour_yesterday"] = df[f"{self.target_column}_lag_24"]
        
        # Önceki hafta aynı saat
        if f"{self.target_column}_lag_168" in df.columns:
            df["same_hour_last_week"] = df[f"{self.target_column}_lag_168"]
        
        return df
    
    def _save_feature_columns(self, df: pd.DataFrame):
        """Feature kolon isimlerini kaydet"""
        exclude_cols = [
            self.date_column, 
            self.target_column, 
            "source_file"
        ]
        
        self.feature_columns = [
            col for col in df.columns 
            if col not in exclude_cols
            and df[col].dtype in [np.float64, np.int64, float, int]
        ]
    
    def get_feature_columns(self) -> List[str]:
        """Feature kolon isimlerini döndür"""
        return self.feature_columns
    
    def get_X_y(
        self, 
        df: pd.DataFrame, 
        feature_cols: Optional[List[str]] = None
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        X (features) ve y (target) ayır
        
        Args:
            df: Feature'lı DataFrame
            feature_cols: Kullanılacak feature kolonları
        
        Returns:
            (X, y) tuple
        """
        if feature_cols is None:
            feature_cols = self.feature_columns
        
        X = df[feature_cols].copy()
        y = df[self.target_column].copy()
        
        return X, y
    
    def create_forecast_features(
        self,
        last_data: pd.DataFrame,
        forecast_hours: int = 24
    ) -> pd.DataFrame:
        """
        Tahmin için gelecek feature'ları oluştur
        
        Args:
            last_data: Son bilinen veriler
            forecast_hours: Tahmin edilecek saat sayısı
        
        Returns:
            Tahmin için feature DataFrame
        """
        # Son tarihi al
        last_date = last_data[self.date_column].max()
        
        # Gelecek tarihler
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(hours=1),
            periods=forecast_hours,
            freq="H"
        )
        
        # Boş DataFrame
        forecast_df = pd.DataFrame({self.date_column: future_dates})
        
        # Zaman features
        forecast_df = create_time_features(forecast_df, self.date_column)
        
        # Döngüsel features
        if self.include_cyclical:
            forecast_df = create_cyclical_features(forecast_df, "hour", 24)
            forecast_df = create_cyclical_features(forecast_df, "day_of_week", 7)
            forecast_df = create_cyclical_features(forecast_df, "month", 12)
        
        # İş günü/pik saat features
        forecast_df["is_business_hour"] = (
            (forecast_df["hour"] >= 9) & 
            (forecast_df["hour"] <= 18) & 
            (forecast_df["is_weekend"] == 0)
        ).astype(int)
        
        forecast_df["is_peak_hour"] = (
            ((forecast_df["hour"] >= 8) & (forecast_df["hour"] <= 11)) |
            ((forecast_df["hour"] >= 17) & (forecast_df["hour"] <= 20))
        ).astype(int)
        
        forecast_df["is_night"] = (
            (forecast_df["hour"] >= 22) | (forecast_df["hour"] <= 6)
        ).astype(int)
        
        # Lag features için son değerleri kullan
        for lag in self.lag_hours:
            col_name = f"{self.target_column}_lag_{lag}"
            if lag <= len(last_data):
                # Son lag kadar veriyi al
                forecast_df[col_name] = last_data[self.target_column].iloc[-lag]
            else:
                forecast_df[col_name] = last_data[self.target_column].mean()
        
        # Rolling features için son değerleri kullan
        for window in self.rolling_windows:
            for func in ["mean", "std", "min", "max"]:
                col_name = f"{self.target_column}_rolling_{func}_{window}"
                if window <= len(last_data):
                    if func == "mean":
                        val = last_data[self.target_column].iloc[-window:].mean()
                    elif func == "std":
                        val = last_data[self.target_column].iloc[-window:].std()
                    elif func == "min":
                        val = last_data[self.target_column].iloc[-window:].min()
                    elif func == "max":
                        val = last_data[self.target_column].iloc[-window:].max()
                    forecast_df[col_name] = val
                else:
                    forecast_df[col_name] = last_data[self.target_column].mean()
        
        # Weather features for forecast
        if self.include_weather and self.weather_service is not None:
            try:
                # Try to get forecast from OpenWeather API
                forecast_weather = self.weather_service.get_forecast(
                    self.location,
                    days=min(5, (forecast_hours // 24) + 1),
                    lat=self.lat,
                    lon=self.lon
                )
                
                # Map forecast to hourly
                forecast_dates = pd.to_datetime(forecast_df[self.date_column])
                weather_features_list = []
                
                for forecast_date in forecast_dates:
                    # Find closest forecast entry
                    closest = None
                    min_diff = float('inf')
                    
                    for item in forecast_weather.get("forecasts", []):
                        item_time = pd.to_datetime(item["datetime"])
                        diff = abs((forecast_date - item_time).total_seconds())
                        if diff < min_diff:
                            min_diff = diff
                            closest = item
                    
                    if closest:
                        temp = closest["temperature_celsius"]
                        weather_features_list.append({
                            "weather_temperature_celsius": temp,
                            "weather_humidity": closest["humidity"],
                            "weather_pressure_mb": closest["pressure_mb"],
                            "weather_wind_speed_ms": closest.get("wind_speed_ms", 0),
                            "weather_cloudiness": closest.get("cloudiness", 0),
                            "weather_heating_degree_days": max(0, 18.0 - temp),
                            "weather_cooling_degree_days": max(0, temp - 24.0)
                        })
                    else:
                        # Fallback
                        weather_features_list.append({
                            "weather_temperature_celsius": 20.0,
                            "weather_humidity": 50.0,
                            "weather_pressure_mb": 1013.0,
                            "weather_wind_speed_ms": 0.0,
                            "weather_cloudiness": 0.0,
                            "weather_heating_degree_days": 0.0,
                            "weather_cooling_degree_days": 0.0
                        })
                
                weather_df = pd.DataFrame(weather_features_list)
                forecast_df = pd.concat([forecast_df, weather_df], axis=1)
                
            except Exception as e:
                # Fallback: use historical averages or defaults
                print(f"  Warning: Weather forecast failed: {e}, using defaults")
                for col in ["weather_temperature_celsius", "weather_humidity", "weather_pressure_mb",
                           "weather_wind_speed_ms", "weather_cloudiness", 
                           "weather_heating_degree_days", "weather_cooling_degree_days"]:
                    forecast_df[col] = 20.0 if "temperature" in col else (50.0 if "humidity" in col else (1013.0 if "pressure" in col else 0.0))
        
        # Eksik kolonları 0 ile doldur
        for col in self.feature_columns:
            if col not in forecast_df.columns:
                forecast_df[col] = 0
        
        return forecast_df


# Test
if __name__ == "__main__":
    from data_loader import EnergyDataLoader
    
    # Veri yükle
    loader = EnergyDataLoader(verbose=True)
    df = loader.get_sample_data(5000)
    
    # Feature engineering
    engineer = EnergyFeatureEngineer(
        target_column="total_power",
        date_column="Time"
    )
    
    df_features = engineer.fit_transform(df)
    
    print(f"\nOrijinal kolonlar: {len(df.columns)}")
    print(f"Feature sonrası kolonlar: {len(df_features.columns)}")
    print(f"Feature sayısı: {len(engineer.get_feature_columns())}")
    
    # X, y ayır
    X, y = engineer.get_X_y(df_features)
    print(f"\nX shape: {X.shape}")
    print(f"y shape: {y.shape}")

