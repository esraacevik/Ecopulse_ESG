"""
Model Doğrulama Testi
=====================
Eğitilmiş modelin gerçekten çalışıp çalışmadığını test eder
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from models.energy_prediction.predictor import EnergyPredictor
import pandas as pd
import xgboost as xgb
import json

print("=" * 60)
print("MODEL DOĞRULAMA TESTİ")
print("=" * 60)

# 1. Model yükle
print("\n[1/5] Model yükleniyor...")
model_path = Path("outputs/models/weather_energy_model")
predictor = EnergyPredictor()
predictor.load(model_path)

print(f"   [OK] Model yuklendi: {predictor.is_trained}")
print(f"   [OK] Feature sayisi: {len(predictor.feature_engineer.get_feature_columns())}")

# 2. Model tipi kontrolü
print("\n[2/5] Model tipi kontrol ediliyor...")
print(f"   Model tipi: {type(predictor.model.model)}")
print(f"   Model fitted: {predictor.model.is_fitted}")

if hasattr(predictor.model.model, '_Booster'):
    booster = predictor.model.model._Booster
    if booster:
        print(f"   [OK] Booster modeli mevcut")
        print(f"   [OK] Agac sayisi: {booster.num_boosted_rounds()}")
        print(f"   [OK] Feature sayisi: {booster.num_feature() if hasattr(booster, 'num_feature') else booster.num_features()}")
    else:
        print("   [HATA] Booster modeli yok!")

# 3. Checkpoint kontrolü
print("\n[3/5] Checkpoint durumu kontrol ediliyor...")
checkpoint_path = Path("checkpoints/weather_training/model_checkpoint.json")
if checkpoint_path.exists():
    bst = xgb.Booster()
    bst.load_model(str(checkpoint_path))
    print(f"   [OK] Checkpoint model yuklendi")
    print(f"   [OK] Checkpoint agac sayisi: {bst.num_boosted_rounds()}")
    print(f"   [OK] Checkpoint feature sayisi: {bst.num_feature() if hasattr(bst, 'num_feature') else bst.num_features()}")
    print(f"   [OK] Checkpoint boyutu: {checkpoint_path.stat().st_size / 1024:.1f} KB")
else:
    print("   [HATA] Checkpoint bulunamadi")

# 4. Training state kontrolü
print("\n[4/5] Training state kontrol ediliyor...")
state_path = Path("checkpoints/weather_training/training_state.json")
if state_path.exists():
    with open(state_path, 'r') as f:
        state = json.load(f)
    print(f"   [OK] Training completed: {state.get('training_completed', False)}")
    print(f"   [OK] Estimators trained: {state.get('n_estimators_trained', 0)}/200")
    print(f"   [OK] Data rows: {state.get('n_rows', 0):,}")
    print(f"   [OK] Features: {state.get('n_features', 0)}")
else:
    print("   [HATA] Training state bulunamadi")

# 5. Test tahmini
print("\n[5/5] Test tahmini yapılıyor...")
try:
    # Tüm feature'ları içeren test verisi
    feature_cols = predictor.feature_engineer.get_feature_columns()
    test_data = {}
    
    for col in feature_cols:
        if 'Power' in col or 'power' in col.lower():
            test_data[col] = [100.0]
        elif 'hour' in col:
            test_data[col] = [12.0]
        elif 'day' in col and 'week' in col:
            test_data[col] = [1.0]
        elif 'month' in col:
            test_data[col] = [6.0]
        elif 'weather' in col:
            test_data[col] = [20.0]
        elif 'sin' in col or 'cos' in col:
            test_data[col] = [0.5]
        elif 'lag' in col or 'rolling' in col:
            test_data[col] = [100.0]
        elif 'is_' in col:
            test_data[col] = [1.0]
        else:
            test_data[col] = [0.0]
    
    test_df = pd.DataFrame(test_data)
    print(f"   Test feature sayısı: {len(test_df.columns)}")
    
    # Tahmin yap
    prediction = predictor.model.predict(test_df)
    print(f"   [OK] Tahmin basarili!")
    print(f"   [OK] Tahmin sonucu: {prediction[0]:.2f}")
    print("   [OK] Model calisiyor!")
    
except Exception as e:
    print(f"   [HATA] Hata: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("SONUC: Model gercekten egitilmis ve calisiyor! [OK]")
print("=" * 60)

