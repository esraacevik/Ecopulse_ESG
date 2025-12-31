"""
ECOLOGIA ML Models Package
==========================

This package contains machine learning models for:
1. Energy Prediction (LSTM, Prophet, XGBoost)
2. Anomaly Detection (Isolation Forest, Autoencoder)
3. Sector Benchmarking (Clustering, Percentile Ranking)
4. Target Recommendation (Scenario Modeling, Optimization)
"""

__version__ = "1.0.0"
__author__ = "ECOLOGIA Team"

from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Data paths
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
FEATURES_DIR = DATA_DIR / "features"

# External data path (relative to project root)
EXTERNAL_DATA_DIR = BASE_DIR.parent.parent / "yeni_veri_setleri"

