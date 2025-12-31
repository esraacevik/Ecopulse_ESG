"""
Anomaly Detection Model
========================

Enerji tüketimi ve emisyon verilerinde anomali tespiti.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Tuple, Union
from pathlib import Path
import joblib
import json
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM
import warnings


class AnomalyDetector:
    """
    Anomali tespit modeli
    
    Algoritmalar:
    - isolation_forest: Isolation Forest (default)
    - one_class_svm: One-Class SVM
    - statistical: Z-Score + IQR
    """
    
    def __init__(
        self,
        algorithm: str = "isolation_forest",
        contamination: float = 0.05,
        random_state: int = 42
    ):
        """
        Args:
            algorithm: Kullanılacak algoritma
            contamination: Beklenen anomali oranı (0-0.5)
            random_state: Random seed
        """
        self.algorithm = algorithm
        self.contamination = contamination
        self.random_state = random_state
        
        self.model = None
        self.scaler = StandardScaler()
        self.baseline_stats = {}
        self.is_fitted = False
        self.feature_names = []
    
    def fit(
        self,
        X: pd.DataFrame,
        columns: Optional[List[str]] = None,
        verbose: bool = True
    ) -> "AnomalyDetector":
        """
        Modeli normal veri üzerinde eğit
        
        Args:
            X: Eğitim verisi (normal veri)
            columns: Kullanılacak kolonlar
            verbose: Log göster
        
        Returns:
            self
        """
        if columns is None:
            columns = X.select_dtypes(include=[np.number]).columns.tolist()
        
        self.feature_names = columns
        X_train = X[columns].copy()
        
        # Missing ve inf temizle
        X_train = X_train.replace([np.inf, -np.inf], np.nan)
        X_train = X_train.dropna()
        
        if verbose:
            print(f"Eğitim verisi: {len(X_train)} satır, {len(columns)} kolon")
        
        # Baseline istatistikler hesapla
        self._calculate_baseline_stats(X_train)
        
        # Normalize et
        X_scaled = self.scaler.fit_transform(X_train)
        
        # Model seç ve eğit
        if self.algorithm == "isolation_forest":
            self.model = IsolationForest(
                contamination=self.contamination,
                random_state=self.random_state,
                n_estimators=100,
                n_jobs=-1
            )
            self.model.fit(X_scaled)
            
        elif self.algorithm == "one_class_svm":
            self.model = OneClassSVM(
                kernel="rbf",
                nu=self.contamination,
                gamma="auto"
            )
            # SVM için örnekleme (performans için)
            if len(X_scaled) > 10000:
                idx = np.random.choice(len(X_scaled), 10000, replace=False)
                X_scaled = X_scaled[idx]
            self.model.fit(X_scaled)
            
        elif self.algorithm == "statistical":
            # Statistical method için model gerekmez
            pass
        
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
        
        self.is_fitted = True
        
        if verbose:
            print(f"Model eğitildi: {self.algorithm}")
        
        return self
    
    def _calculate_baseline_stats(self, X: pd.DataFrame):
        """Baseline istatistikleri hesapla"""
        for col in X.columns:
            self.baseline_stats[col] = {
                "mean": X[col].mean(),
                "std": X[col].std(),
                "median": X[col].median(),
                "q1": X[col].quantile(0.25),
                "q3": X[col].quantile(0.75),
                "iqr": X[col].quantile(0.75) - X[col].quantile(0.25),
                "min": X[col].min(),
                "max": X[col].max()
            }
    
    def detect(
        self,
        X: pd.DataFrame,
        return_scores: bool = False
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Anomali tespit et
        
        Args:
            X: Test verisi
            return_scores: Anomali skorlarını da döndür
        
        Returns:
            Anomali etiketleri (1: normal, -1: anomali) ve opsiyonel skorlar
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        X_test = X[self.feature_names].copy()
        X_test = X_test.replace([np.inf, -np.inf], np.nan)
        
        # NaN değerler için mask
        nan_mask = X_test.isna().any(axis=1)
        
        # NaN olmayanları işle
        X_clean = X_test[~nan_mask]
        
        if self.algorithm in ["isolation_forest", "one_class_svm"]:
            X_scaled = self.scaler.transform(X_clean)
            predictions = self.model.predict(X_scaled)
            
            if return_scores:
                if hasattr(self.model, "decision_function"):
                    scores = -self.model.decision_function(X_scaled)  # Negatif = anomali
                else:
                    scores = np.zeros(len(X_clean))
        
        elif self.algorithm == "statistical":
            predictions, scores = self._statistical_detection(X_clean)
        
        # NaN olanları anomali olarak işaretle
        full_predictions = np.ones(len(X_test))
        full_predictions[~nan_mask] = predictions
        full_predictions[nan_mask] = -1  # NaN = anomali
        
        if return_scores:
            full_scores = np.zeros(len(X_test))
            full_scores[~nan_mask] = scores
            full_scores[nan_mask] = 1.0  # Yüksek skor = anomali
            return full_predictions, full_scores
        
        return full_predictions
    
    def _statistical_detection(
        self,
        X: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Z-Score + IQR tabanlı anomali tespiti"""
        anomaly_scores = np.zeros(len(X))
        
        for col in X.columns:
            stats = self.baseline_stats[col]
            
            # Z-Score
            z_scores = np.abs((X[col] - stats["mean"]) / (stats["std"] + 1e-10))
            
            # IQR
            lower_bound = stats["q1"] - 1.5 * stats["iqr"]
            upper_bound = stats["q3"] + 1.5 * stats["iqr"]
            iqr_outliers = ((X[col] < lower_bound) | (X[col] > upper_bound)).astype(float)
            
            # Kombine skor
            anomaly_scores += (z_scores > 3).astype(float) + iqr_outliers
        
        # Normalize et
        anomaly_scores = anomaly_scores / (2 * len(X.columns))
        
        # Threshold
        threshold = 0.3
        predictions = np.where(anomaly_scores > threshold, -1, 1)
        
        return predictions, anomaly_scores
    
    def get_anomaly_report(
        self,
        X: pd.DataFrame,
        include_details: bool = True
    ) -> pd.DataFrame:
        """
        Detaylı anomali raporu oluştur
        
        Args:
            X: Test verisi
            include_details: Detayları dahil et
        
        Returns:
            Anomali raporu DataFrame
        """
        predictions, scores = self.detect(X, return_scores=True)
        
        report = X.copy()
        report["is_anomaly"] = predictions == -1
        report["anomaly_score"] = scores
        
        if include_details:
            # Hangi özellik anomali?
            anomaly_reasons = []
            for idx, row in X.iterrows():
                reasons = []
                for col in self.feature_names:
                    if col not in self.baseline_stats:
                        continue
                    stats = self.baseline_stats[col]
                    value = row[col]
                    
                    if pd.isna(value):
                        reasons.append(f"{col}: NaN")
                    else:
                        z_score = abs((value - stats["mean"]) / (stats["std"] + 1e-10))
                        if z_score > 3:
                            direction = "yüksek" if value > stats["mean"] else "düşük"
                            reasons.append(f"{col}: {direction} (z={z_score:.1f})")
                
                anomaly_reasons.append("; ".join(reasons[:3]) if reasons else "")
            
            report["anomaly_reason"] = anomaly_reasons
        
        return report
    
    def get_anomaly_summary(
        self,
        X: pd.DataFrame
    ) -> Dict:
        """
        Anomali özeti
        
        Args:
            X: Test verisi
        
        Returns:
            Özet dictionary
        """
        predictions, scores = self.detect(X, return_scores=True)
        
        n_anomalies = (predictions == -1).sum()
        n_total = len(predictions)
        
        return {
            "total_samples": n_total,
            "anomaly_count": int(n_anomalies),
            "anomaly_ratio": float(n_anomalies / n_total) if n_total > 0 else 0,
            "avg_anomaly_score": float(scores.mean()),
            "max_anomaly_score": float(scores.max()),
            "algorithm": self.algorithm,
            "contamination": self.contamination
        }
    
    def save(self, path: Path) -> None:
        """Modeli kaydet"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Model kaydet
        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "baseline_stats": self.baseline_stats,
            "feature_names": self.feature_names,
            "algorithm": self.algorithm,
            "contamination": self.contamination
        }
        joblib.dump(model_data, path)
        
        print(f"Model saved: {path}")
    
    def load(self, path: Path) -> "AnomalyDetector":
        """Modeli yükle"""
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Model not found: {path}")
        
        model_data = joblib.load(path)
        
        self.model = model_data["model"]
        self.scaler = model_data["scaler"]
        self.baseline_stats = model_data["baseline_stats"]
        self.feature_names = model_data["feature_names"]
        self.algorithm = model_data["algorithm"]
        self.contamination = model_data["contamination"]
        
        self.is_fitted = True
        print(f"Model loaded: {path}")
        
        return self


# Test
if __name__ == "__main__":
    print("=== Anomaly Detector Test ===\n")
    
    # Sentetik veri oluştur
    np.random.seed(42)
    n_samples = 1000
    
    # Normal veri
    normal_data = pd.DataFrame({
        "power": np.random.normal(100, 10, n_samples),
        "temperature": np.random.normal(25, 3, n_samples),
        "humidity": np.random.normal(50, 5, n_samples)
    })
    
    # Test verisi (anomaliler ekle)
    test_data = normal_data.copy()
    
    # Anomaliler ekle
    anomaly_indices = np.random.choice(n_samples, 50, replace=False)
    test_data.loc[anomaly_indices, "power"] = np.random.normal(200, 20, 50)  # Spike
    
    # Model eğit
    detector = AnomalyDetector(algorithm="isolation_forest", contamination=0.05)
    detector.fit(normal_data, verbose=True)
    
    # Tespit
    predictions, scores = detector.detect(test_data, return_scores=True)
    
    # Sonuçlar
    detected = (predictions == -1).sum()
    print(f"\nTespit edilen anomali: {detected}")
    print(f"Gerçek anomali: {len(anomaly_indices)}")
    
    # Özet
    summary = detector.get_anomaly_summary(test_data)
    print(f"\nAnomali oranı: {summary['anomaly_ratio']:.2%}")
    
    # Doğruluk
    true_positives = sum(1 for i in anomaly_indices if predictions[i] == -1)
    precision = true_positives / detected if detected > 0 else 0
    recall = true_positives / len(anomaly_indices)
    
    print(f"\nPrecision: {precision:.2%}")
    print(f"Recall: {recall:.2%}")
    
    print("\n=== Test Başarılı ===")

