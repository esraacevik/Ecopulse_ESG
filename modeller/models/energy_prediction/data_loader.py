"""
Energy Prediction Data Loader
=============================

Enerji tüketimi verilerini yükler ve birleştirir.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime
import warnings

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config import DATASETS, get_dataset_path


class EnergyDataLoader:
    """Enerji tüketimi verilerini yükleyen sınıf"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.data = None
        
    def _log(self, message: str):
        if self.verbose:
            print(f"[DataLoader] {message}")
    
    def load_building_energy_dataset(
        self,
        years: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Building Energy Dataset yükle (2016-2021)
        
        Args:
            years: Yüklenecek yıllar ["2016_2017", "2018", "2019", "2020", "2021"]
        
        Returns:
            Birleştirilmiş DataFrame
        """
        if years is None:
            years = ["2016_2017", "2018", "2019", "2020", "2021"]
        
        base_path = get_dataset_path("building_energy")
        files = DATASETS["building_energy"]["files"]
        
        dfs = []
        
        for year in years:
            file_key = year
            if year == "2016_2017":
                file_key = "2016_2017"
            elif year == "2018":
                file_key = "2018"
            elif year == "2019":
                file_key = "2019"
            elif year == "2020":
                file_key = "2020"
            elif year == "2021":
                file_key = "2021"
            
            file_path = base_path / files.get(file_key, f"{file_key}.csv")
            
            if not file_path.exists():
                self._log(f"Dosya bulunamadı: {file_path}")
                continue
            
            self._log(f"Yükleniyor: {file_path.name}")
            
            try:
                df = pd.read_csv(file_path)
                df["source_file"] = year
                dfs.append(df)
                self._log(f"  -> {len(df)} satır yüklendi")
            except Exception as e:
                self._log(f"  -> Hata: {e}")
        
        if not dfs:
            raise ValueError("Hiç veri yüklenemedi")
        
        combined = pd.concat(dfs, ignore_index=True)
        self._log(f"Toplam: {len(combined)} satır")
        
        return combined
    
    def load_eia_hourly(
        self,
        regions: Optional[List[str]] = None,
        max_files: int = 10
    ) -> pd.DataFrame:
        """
        US EIA hourly electricity consumption yükle
        
        Args:
            regions: Yüklenecek bölgeler
            max_files: Maksimum dosya sayısı
        
        Returns:
            DataFrame
        """
        base_path = get_dataset_path("eia_hourly")
        data_dir = base_path / "data"
        
        if not data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {data_dir}")
        
        # Dosyaları listele
        csv_files = list(data_dir.glob("*.csv"))[:max_files]
        
        dfs = []
        for file_path in csv_files:
            self._log(f"Yükleniyor: {file_path.name}")
            try:
                df = pd.read_csv(file_path)
                df["region_file"] = file_path.stem
                dfs.append(df)
            except Exception as e:
                self._log(f"  -> Hata: {e}")
        
        if not dfs:
            raise ValueError("Hiç veri yüklenemedi")
        
        combined = pd.concat(dfs, ignore_index=True)
        self._log(f"Toplam: {len(combined)} satır")
        
        return combined
    
    def load_ember_data(
        self,
        countries: Optional[List[str]] = None,
        years: Optional[Tuple[int, int]] = None
    ) -> pd.DataFrame:
        """
        Ember global electricity data yükle
        
        Args:
            countries: Filtre ülkeler
            years: (start_year, end_year)
        
        Returns:
            DataFrame
        """
        file_path = get_dataset_path("ember", "yearly")
        
        self._log(f"Yükleniyor: {file_path.name}")
        df = pd.read_csv(file_path)
        self._log(f"  -> {len(df)} satır yüklendi")
        
        # Filtreleme
        if countries:
            df = df[df["Area"].isin(countries)]
        
        if years:
            df = df[(df["Year"] >= years[0]) & (df["Year"] <= years[1])]
        
        self._log(f"Filtreleme sonrası: {len(df)} satır")
        
        return df
    
    def load_weather_data(self) -> pd.DataFrame:
        """
        World Weather Repository yükle
        
        Returns:
            DataFrame
        """
        file_path = get_dataset_path("world_weather", "csv")
        
        self._log(f"Yükleniyor: {file_path.name}")
        df = pd.read_csv(file_path)
        self._log(f"  -> {len(df)} satır yüklendi")
        
        return df
    
    def preprocess_building_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Building energy verisini ön işle
        
        Args:
            df: Ham DataFrame
        
        Returns:
            İşlenmiş DataFrame
        """
        df = df.copy()
        
        # Time kolonu varsa datetime'a çevir
        if "Time" in df.columns:
            df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
            df = df.dropna(subset=["Time"])
            df = df.sort_values("Time").reset_index(drop=True)
        
        # Kolon isimlerini temizle
        df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace("[", "").str.replace("]", "")
        
        # Sayısal kolonları float'a çevir
        numeric_cols = ["HVAC_Actual_kW", "Chiller_Power_kW", "Power_kW", "PowerkW",
                       "PV_panels_power_kW", "Humidifier_power_kW", "HV_light_Power_kW"]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        # Total power hesapla (yoksa)
        if "total_power" not in df.columns:
            if "PowerkW" in df.columns:
                df["total_power"] = df["PowerkW"]
            elif "Power_kW" in df.columns:
                df["total_power"] = df["Power_kW"]
            elif "HVAC_Actual_kW" in df.columns:
                # HVAC yoksa diğer enerji kolonlarını topla
                df["total_power"] = df["HVAC_Actual_kW"]
            else:
                # Herhangi bir sayısal kolon bul
                for col in df.columns:
                    if df[col].dtype in [np.float64, np.int64] and col != "source_file":
                        df["total_power"] = df[col]
                        break
        
        # Missing değerleri doldur
        df = df.ffill().bfill()
        
        self._log(f"Preprocessing tamamlandı: {len(df)} satır, {len(df.columns)} kolon")
        
        return df
    
    def get_sample_data(self, n_samples: int = 10000) -> pd.DataFrame:
        """
        Test için örnek veri yükle
        
        Args:
            n_samples: Örnek sayısı
        
        Returns:
            Örnek DataFrame
        """
        try:
            df = self.load_building_energy_dataset(years=["2018"])
            df = self.preprocess_building_data(df)
            
            if len(df) > n_samples:
                df = df.sample(n=n_samples, random_state=42).sort_index()
            
            return df
        
        except Exception as e:
            self._log(f"Örnek veri yüklenemedi: {e}")
            # Sentetik veri oluştur
            return self._create_synthetic_data(n_samples)
    
    def _create_synthetic_data(self, n_samples: int) -> pd.DataFrame:
        """Test için sentetik veri oluştur"""
        self._log("Sentetik veri oluşturuluyor...")
        
        np.random.seed(42)
        
        # Zaman serisi oluştur
        dates = pd.date_range(
            start="2020-01-01",
            periods=n_samples,
            freq="H"
        )
        
        # Temel tüketim (günlük pattern)
        hour_effect = np.sin(2 * np.pi * dates.hour / 24) * 20 + 50
        
        # Haftalık pattern
        dow_effect = np.where(dates.dayofweek < 5, 10, -10)
        
        # Mevsimsel pattern
        month_effect = np.sin(2 * np.pi * dates.month / 12) * 15
        
        # Trend
        trend = np.linspace(0, 10, n_samples)
        
        # Gürültü
        noise = np.random.normal(0, 5, n_samples)
        
        # Toplam tüketim
        consumption = hour_effect + dow_effect + month_effect + trend + noise
        consumption = np.maximum(consumption, 0)  # Negatif olamaz
        
        hvac = consumption * 0.4 + np.random.normal(0, 2, n_samples)
        hvac = np.maximum(hvac, 0)
        
        chiller = consumption * 0.2 + np.random.normal(0, 1, n_samples)
        chiller = np.maximum(chiller, 0)
        
        df = pd.DataFrame({
            "Time": dates,
            "Power_kW": consumption,
            "HVAC_Actual_kW": hvac,
            "Chiller_Power_kW": chiller,
            "total_power": consumption,  # Direkt ekle
            "source_file": "synthetic"
        })
        
        self._log(f"Sentetik veri oluşturuldu: {len(df)} satır")
        
        return df


# Test
if __name__ == "__main__":
    loader = EnergyDataLoader(verbose=True)
    
    # Örnek veri yükle
    sample_df = loader.get_sample_data(1000)
    print("\nÖrnek veri:")
    print(sample_df.head())
    print(f"\nKolonlar: {sample_df.columns.tolist()}")

