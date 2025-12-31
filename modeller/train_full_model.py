"""
Full Energy Prediction Model Training
=====================================

Tam veri setiyle model eğitimi ve kaydetme
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from models.energy_prediction.predictor import EnergyPredictor
from models.energy_prediction.data_loader import EnergyDataLoader
import pandas as pd
from datetime import datetime

print("=" * 60)
print("FULL ENERGY PREDICTION MODEL TRAINING")
print("=" * 60)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 1. Veri yükleme
print("1. Loading data...")
loader = EnergyDataLoader(verbose=True)

# Örnek veri yükle (hızlı eğitim için)
print("   Loading sample data (50,000 rows for faster training)...")
df = loader.get_sample_data(50000)

print(f"   -> Total rows: {len(df)}")

# Preprocessing
print("\n2. Preprocessing...")
df = loader.preprocess_building_data(df)
print(f"   -> After preprocessing: {len(df)} rows")

# 3. Feature Engineering with Weather
print("\n3. Feature Engineering (with weather features)...")
predictor = EnergyPredictor(
    algorithm="xgboost",
    location="Istanbul,TR",
    include_weather=True,
    model_params={
        "n_estimators": 200,
        "max_depth": 8,
        "learning_rate": 0.05
    }
)

# 4. Model Eğitimi
print("\n4. Training model...")
print("   This may take several minutes...")
results = predictor.train(df, val_ratio=0.15, verbose=True)

# 5. Model Kaydetme
print("\n5. Saving model...")
model_dir = Path(__file__).parent / "outputs" / "models" / "energy_prediction"
model_dir.mkdir(parents=True, exist_ok=True)

predictor.save(model_dir)
print(f"   -> Model saved to: {model_dir}")

# 6. Feature Importance
print("\n6. Feature Importance Analysis...")
importance = predictor.get_feature_importance(top_n=20)
print("\n   Top 20 Features:")
for idx, row in importance.iterrows():
    print(f"   {idx+1:2d}. {row['feature']:40s} {row['importance']:.4f}")

# Weather features kontrolü
weather_features = [f for f in importance['feature'] if 'weather' in f.lower()]
if weather_features:
    print(f"\n   Weather features in top 20: {len(weather_features)}")
    for feat in weather_features[:5]:
        print(f"      - {feat}")

# 7. Test Tahmini
print("\n7. Test Prediction...")
forecast = predictor.predict(future_hours=24)
print(f"   -> Forecast generated: {len(forecast)} hours")
print("\n   Sample predictions:")
print(forecast.head(10).to_string())

# 8. Özet
print("\n" + "=" * 60)
print("TRAINING SUMMARY")
print("=" * 60)
print(f"Training Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Data Points: {results['n_samples']:,}")
print(f"Features: {results['n_features']}")
print(f"Validation Metrics:")
for key, value in results['val_metrics'].items():
    print(f"  {key.upper()}: {value:.4f}")
print(f"\nModel Location: {model_dir}")
print("=" * 60)
print("TRAINING COMPLETED SUCCESSFULLY!")
print("=" * 60)

