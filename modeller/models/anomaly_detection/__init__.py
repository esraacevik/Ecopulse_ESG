"""
Anomaly Detection Model
=======================

Olağandışı enerji tüketimi veya emisyon değerlerini tespit eder.

Algoritmalar:
- Isolation Forest: Outlier detection
- One-Class SVM: Novelty detection
- Autoencoder: Reconstruction error
- Statistical: Z-Score, IQR

Anomali Türleri:
- spike: Ani yükseliş
- drop: Ani düşüş
- trend_deviation: Trend sapması
- seasonal_anomaly: Mevsimsel anomali

Kullanım:
    from models.anomaly_detection import AnomalyDetector
    
    detector = AnomalyDetector(algorithm="isolation_forest")
    detector.fit(normal_data)
    anomalies = detector.detect(test_data)
"""

__all__ = [
    "AnomalyDetector",
    "IsolationForestDetector",
    "AutoencoderDetector",
    "StatisticalDetector"
]

