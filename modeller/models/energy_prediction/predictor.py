"""
Energy Predictor - Main Interface
==================================

Enerji tüketimi tahmini için ana arayüz.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Union
from pathlib import Path
from datetime import datetime

from .data_loader import EnergyDataLoader
from .feature_engineer import EnergyFeatureEngineer
from .xgboost_model import XGBoostEnergyPredictor


class EnergyPredictor:
    """
    Enerji tüketimi tahmin sistemi
    
    Kullanım:
        predictor = EnergyPredictor()
        predictor.train(data)
        predictions = predictor.predict(future_hours=24)
    """
    
    def __init__(
        self,
        algorithm: str = "xgboost",
        target_column: str = "total_power",
        date_column: str = "Time",
        model_params: Optional[Dict] = None,
        location: str = "Istanbul,TR",
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        include_weather: bool = True
    ):
        """
        Args:
            algorithm: Kullanılacak algoritma ("xgboost", "prophet", "lstm")
            target_column: Tahmin edilecek kolon
            date_column: Tarih kolonu
            model_params: Model parametreleri
            location: Location name for weather (e.g., "Istanbul,TR")
            lat: Latitude (optional)
            lon: Longitude (optional)
            include_weather: Include weather features
        """
        self.algorithm = algorithm
        self.target_column = target_column
        self.date_column = date_column
        self.model_params = model_params or {}
        self.location = location
        self.lat = lat
        self.lon = lon
        self.include_weather = include_weather
        
        # Bileşenler
        self.loader = EnergyDataLoader(verbose=False)
        self.feature_engineer = EnergyFeatureEngineer(
            target_column=target_column,
            date_column=date_column,
            location=location,
            lat=lat,
            lon=lon,
            include_weather=include_weather
        )
        
        # Model
        if algorithm == "xgboost":
            self.model = XGBoostEnergyPredictor(**self.model_params)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        # State
        self.is_trained = False
        self.last_data = None
        self.training_history = {}
    
    def train(
        self,
        data: Union[pd.DataFrame, str],
        val_ratio: float = 0.15,
        verbose: bool = True
    ) -> Dict:
        """
        Modeli eğit
        
        Args:
            data: DataFrame veya dosya yolu
            val_ratio: Validation oranı
            verbose: Log göster
        
        Returns:
            Eğitim sonuçları
        """
        if verbose:
            print("=== Energy Predictor Training ===\n")
        
        # 1. Veri yükle
        if isinstance(data, str):
            df = pd.read_csv(data)
        else:
            df = data.copy()
        
        if verbose:
            print(f"1. Veri yüklendi: {len(df)} satır")
        
        # 2. Preprocessing
        df = self.loader.preprocess_building_data(df)
        
        # 3. Feature engineering
        if verbose:
            print("\n2. Feature engineering...")
        df_features = self.feature_engineer.fit_transform(df)
        
        if verbose:
            print(f"   -> {len(self.feature_engineer.get_feature_columns())} feature oluşturuldu")
        
        # 4. Train/Val split
        n = len(df_features)
        val_size = int(n * val_ratio)
        train_df = df_features.iloc[:-val_size]
        val_df = df_features.iloc[-val_size:]
        
        if verbose:
            print(f"\n3. Train: {len(train_df)}, Val: {len(val_df)}")
        
        # X, y ayır
        X_train, y_train = self.feature_engineer.get_X_y(train_df)
        X_val, y_val = self.feature_engineer.get_X_y(val_df)
        
        # 5. Model eğit
        if verbose:
            print("\n4. Model eğitiliyor...")
            try:
                from tqdm import tqdm
                # XGBoost doesn't have built-in tqdm, but we can show progress
                print("   Eğitim devam ediyor... (XGBoost progress)")
            except:
                pass
        
        self.model.fit(X_train, y_train, X_val, y_val, verbose=verbose)
        
        # 6. Değerlendirme
        val_metrics = self.model.evaluate(X_val, y_val)
        
        if verbose:
            print("\n=== Validation Metrics ===")
            for key, value in val_metrics.items():
                print(f"   {key}: {value:.4f}")
        
        # State güncelle
        self.is_trained = True
        self.last_data = df_features.tail(200)  # Son 200 satırı sakla (tahmin için)
        
        self.training_history = {
            "trained_at": datetime.now().isoformat(),
            "n_samples": len(df),
            "n_features": len(self.feature_engineer.get_feature_columns()),
            "val_metrics": val_metrics
        }
        
        return self.training_history
    
    def predict(
        self,
        future_hours: int = 24,
        return_features: bool = False
    ) -> Union[pd.DataFrame, tuple]:
        """
        Gelecek tahminleri yap
        
        Args:
            future_hours: Tahmin edilecek saat sayısı
            return_features: Feature'ları da döndür
        
        Returns:
            Tahmin DataFrame veya (tahmin, features) tuple
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        # Tahmin için feature'lar oluştur
        forecast_features = self.feature_engineer.create_forecast_features(
            self.last_data,
            forecast_hours=future_hours
        )
        
        # Feature kolonlarını al
        feature_cols = self.feature_engineer.get_feature_columns()
        X_forecast = forecast_features[feature_cols]
        
        # Tahmin yap
        predictions = self.model.predict(X_forecast)
        
        # Sonuç DataFrame
        result = pd.DataFrame({
            self.date_column: forecast_features[self.date_column],
            "predicted_power": predictions
        })
        
        if return_features:
            return result, forecast_features
        
        return result
    
    def predict_on_data(self, data: pd.DataFrame) -> np.ndarray:
        """
        Mevcut veri üzerinde tahmin yap
        
        Args:
            data: Feature'lı DataFrame
        
        Returns:
            Tahminler
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        feature_cols = self.feature_engineer.get_feature_columns()
        X = data[feature_cols]
        
        return self.model.predict(X)
    
    def get_feature_importance(self, top_n: int = 20) -> pd.DataFrame:
        """Feature importance döndür"""
        if not self.is_trained and not (hasattr(self.model, 'is_fitted') and self.model.is_fitted):
            raise ValueError("Model not trained.")
        
        return self.model.get_feature_importance().head(top_n)
    
    def save(self, path: Union[str, Path]) -> None:
        """
        Tüm sistemi kaydet
        
        Args:
            path: Kayıt klasörü
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Model kaydet
        self.model.save(path / "model.pkl")
        
        # Feature engineer state kaydet (feature names)
        import json
        config = {
            "algorithm": self.algorithm,
            "target_column": self.target_column,
            "date_column": self.date_column,
            "feature_columns": self.feature_engineer.get_feature_columns(),
            "training_history": self.training_history
        }
        
        with open(path / "config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"Predictor saved to: {path}")
    
    def load(self, path: Union[str, Path]) -> "EnergyPredictor":
        """
        Sistemi yükle
        
        Args:
            path: Yükleme klasörü
        
        Returns:
            self
        """
        path = Path(path)
        
        # Config yükle
        import json
        with open(path / "config.json", "r") as f:
            config = json.load(f)
        
        self.algorithm = config["algorithm"]
        self.target_column = config["target_column"]
        self.date_column = config["date_column"]
        self.feature_engineer.feature_columns = config["feature_columns"]
        self.training_history = config.get("training_history", {})
        
        # Model yükle
        self.model.load(path / "model.pkl")
        
        self.is_trained = True
        print(f"Predictor loaded from: {path}")
        
        return self


# Quick test
if __name__ == "__main__":
    print("=== Energy Predictor Quick Test ===\n")
    
    # Veri yükle
    loader = EnergyDataLoader(verbose=True)
    df = loader.get_sample_data(3000)
    
    # Predictor oluştur ve eğit
    predictor = EnergyPredictor(algorithm="xgboost")
    results = predictor.train(df, verbose=True)
    
    # Gelecek tahminleri
    print("\n=== 24 Saatlik Tahmin ===")
    forecast = predictor.predict(future_hours=24)
    print(forecast.head(10))
    
    # Feature importance
    print("\n=== Top 10 Features ===")
    print(predictor.get_feature_importance(10))
    
    print("\n=== Test Başarılı ===")

