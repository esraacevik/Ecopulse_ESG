"""
XGBoost Energy Prediction Model
================================

Enerji tüketimi tahmini için XGBoost modeli.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple, List
from pathlib import Path
import joblib
import json
from datetime import datetime

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("Warning: xgboost not installed. Install with: pip install xgboost")

from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))


class XGBoostEnergyPredictor:
    """XGBoost tabanlı enerji tüketimi tahmin modeli"""
    
    def __init__(
        self,
        params: Optional[Dict] = None,
        n_estimators: int = 100,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        early_stopping_rounds: int = 50,
        random_state: int = 42
    ):
        """
        Args:
            params: XGBoost parametreleri (override)
            n_estimators: Ağaç sayısı
            max_depth: Maksimum derinlik
            learning_rate: Öğrenme oranı
            early_stopping_rounds: Early stopping
            random_state: Random seed
        """
        if not XGBOOST_AVAILABLE:
            raise ImportError("xgboost is required. Install with: pip install xgboost")
        
        self.default_params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "learning_rate": learning_rate,
            "min_child_weight": 1,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "objective": "reg:squarederror",
            "random_state": random_state,
            "n_jobs": -1,
            "verbosity": 0
        }
        
        if params:
            self.default_params.update(params)
        
        self.early_stopping_rounds = early_stopping_rounds
        self.model = None
        self.feature_names = None
        self.training_metrics = {}
        self.is_fitted = False
    
    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        verbose: bool = True,
        checkpoint_path: Optional[Path] = None
    ) -> "XGBoostEnergyPredictor":
        """
        Modeli eğit
        
        Args:
            X_train: Eğitim feature'ları
            y_train: Eğitim target'ı
            X_val: Validation feature'ları (opsiyonel)
            y_val: Validation target'ı (opsiyonel)
            verbose: Log göster
            checkpoint_path: Checkpoint dosya yolu (opsiyonel)
        
        Returns:
            self
        """
        self.feature_names = X_train.columns.tolist()
        
        # Checkpoint'ten yükle (varsa)
        if checkpoint_path and Path(checkpoint_path).exists():
            try:
                bst = xgb.Booster()
                bst.load_model(str(checkpoint_path))
                self.model = bst
                self.is_fitted = True
                if verbose:
                    print(f"   -> Model checkpoint'ten yüklendi: {checkpoint_path}")
                return self
            except Exception as e:
                if verbose:
                    print(f"   -> Checkpoint yüklenemedi: {e}, yeni eğitim başlatılıyor...")
        
        # Model oluştur
        self.model = xgb.XGBRegressor(**self.default_params)
        
        # Fit
        if X_val is not None and y_val is not None:
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_train, y_train), (X_val, y_val)],
                verbose=verbose
            )
            
            # Validation metrikleri
            y_val_pred = self.model.predict(X_val)
            self.training_metrics["val_mae"] = mean_absolute_error(y_val, y_val_pred)
            self.training_metrics["val_rmse"] = np.sqrt(mean_squared_error(y_val, y_val_pred))
            self.training_metrics["val_r2"] = r2_score(y_val, y_val_pred)
        else:
            self.model.fit(X_train, y_train, verbose=verbose)
        
        # Training metrikleri
        y_train_pred = self.model.predict(X_train)
        self.training_metrics["train_mae"] = mean_absolute_error(y_train, y_train_pred)
        self.training_metrics["train_rmse"] = np.sqrt(mean_squared_error(y_train, y_train_pred))
        self.training_metrics["train_r2"] = r2_score(y_train, y_train_pred)
        
        self.is_fitted = True
        
        if verbose:
            print("\n=== Training Metrics ===")
            for key, value in self.training_metrics.items():
                print(f"  {key}: {value:.4f}")
        
        return self
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Tahmin yap
        
        Args:
            X: Feature DataFrame
        
        Returns:
            Tahminler
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        # Eğer model Booster ise (xgb.train ile eğitilmişse), DMatrix kullan
        if hasattr(self.model, '_Booster') and self.model._Booster is not None:
            import xgboost as xgb
            dmatrix = xgb.DMatrix(X)
            return self.model._Booster.predict(dmatrix)
        else:
            # Normal XGBRegressor
            return self.model.predict(X)
    
    def evaluate(
        self,
        X_test: pd.DataFrame,
        y_test: pd.Series
    ) -> Dict[str, float]:
        """
        Model değerlendirme
        
        Args:
            X_test: Test feature'ları
            y_test: Test target'ı
        
        Returns:
            Metrikler
        """
        y_pred = self.predict(X_test)
        
        metrics = {
            "mae": mean_absolute_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred)
        }
        
        # MAPE
        mask = y_test != 0
        if mask.sum() > 0:
            metrics["mape"] = np.mean(np.abs((y_test[mask] - y_pred[mask]) / y_test[mask])) * 100
        else:
            metrics["mape"] = np.nan
        
        return metrics
    
    def cross_validate(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_splits: int = 5
    ) -> Dict[str, List[float]]:
        """
        Time series cross-validation
        
        Args:
            X: Feature DataFrame
            y: Target Series
            n_splits: Fold sayısı
        
        Returns:
            CV sonuçları
        """
        tscv = TimeSeriesSplit(n_splits=n_splits)
        
        results = {
            "mae": [],
            "rmse": [],
            "r2": [],
            "mape": []
        }
        
        for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            # Yeni model eğit
            fold_model = xgb.XGBRegressor(**self.default_params)
            fold_model.fit(X_train, y_train, verbose=False)
            
            y_pred = fold_model.predict(X_test)
            
            results["mae"].append(mean_absolute_error(y_test, y_pred))
            results["rmse"].append(np.sqrt(mean_squared_error(y_test, y_pred)))
            results["r2"].append(r2_score(y_test, y_pred))
            
            # MAPE
            mask = y_test != 0
            if mask.sum() > 0:
                mape = np.mean(np.abs((y_test[mask] - y_pred[mask]) / y_test[mask])) * 100
                results["mape"].append(mape)
            
            print(f"Fold {fold+1}: MAE={results['mae'][-1]:.4f}, RMSE={results['rmse'][-1]:.4f}")
        
        # Ortalamalar
        print("\n=== CV Ortalama ===")
        for key, values in results.items():
            print(f"  {key}: {np.mean(values):.4f} (+/- {np.std(values):.4f})")
        
        return results
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Feature importance döndür
        
        Returns:
            Feature importance DataFrame
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted.")
        
        importance = self.model.feature_importances_
        
        return pd.DataFrame({
            "feature": self.feature_names,
            "importance": importance
        }).sort_values("importance", ascending=False).reset_index(drop=True)
    
    def save(self, path: Path) -> None:
        """
        Modeli kaydet
        
        Args:
            path: Kayıt yolu
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Model kaydet
        joblib.dump(self.model, path)
        
        # Metadata kaydet
        metadata = {
            "feature_names": self.feature_names,
            "training_metrics": self.training_metrics,
            "params": self.default_params,
            "saved_at": datetime.now().isoformat()
        }
        
        metadata_path = path.with_suffix(".json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Model saved: {path}")
    
    def load(self, path: Path) -> "XGBoostEnergyPredictor":
        """
        Modeli yükle
        
        Args:
            path: Model yolu
        
        Returns:
            self
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Model not found: {path}")
        
        self.model = joblib.load(path)
        
        # Metadata yükle
        metadata_path = path.with_suffix(".json")
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                self.feature_names = metadata.get("feature_names", [])
                self.training_metrics = metadata.get("training_metrics", {})
        
        self.is_fitted = True
        print(f"Model loaded: {path}")
        
        return self


# Test
if __name__ == "__main__":
    from data_loader import EnergyDataLoader
    from feature_engineer import EnergyFeatureEngineer
    
    print("=== XGBoost Energy Predictor Test ===\n")
    
    # 1. Veri yükle
    print("1. Veri yükleniyor...")
    loader = EnergyDataLoader(verbose=True)
    df = loader.get_sample_data(5000)
    
    # 2. Feature engineering
    print("\n2. Feature engineering...")
    engineer = EnergyFeatureEngineer(
        target_column="total_power",
        date_column="Time"
    )
    df_features = engineer.fit_transform(df)
    
    # 3. Train/Val/Test split
    print("\n3. Train/Val/Test split...")
    n = len(df_features)
    train_end = int(n * 0.7)
    val_end = int(n * 0.85)
    
    train_df = df_features.iloc[:train_end]
    val_df = df_features.iloc[train_end:val_end]
    test_df = df_features.iloc[val_end:]
    
    print(f"  Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
    
    # X, y ayır
    X_train, y_train = engineer.get_X_y(train_df)
    X_val, y_val = engineer.get_X_y(val_df)
    X_test, y_test = engineer.get_X_y(test_df)
    
    # 4. Model eğit
    print("\n4. Model eğitiliyor...")
    model = XGBoostEnergyPredictor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1
    )
    
    model.fit(X_train, y_train, X_val, y_val, verbose=False)
    
    # 5. Test değerlendirme
    print("\n5. Test değerlendirmesi...")
    test_metrics = model.evaluate(X_test, y_test)
    print("\n=== Test Metrics ===")
    for key, value in test_metrics.items():
        print(f"  {key}: {value:.4f}")
    
    # 6. Feature importance
    print("\n6. Top 10 Feature Importance:")
    importance = model.get_feature_importance()
    print(importance.head(10).to_string())
    
    # 7. Model kaydet
    print("\n7. Model kaydediliyor...")
    model_path = Path(__file__).parent / "saved_models" / "xgboost_energy.pkl"
    model.save(model_path)
    
    print("\n=== Test Tamamlandı ===")

