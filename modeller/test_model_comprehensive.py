"""
Kapsamli Model Testi
====================
Modelin gercekten calistigini ve dogru tahmin yaptigini test eder
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from models.energy_prediction.predictor import EnergyPredictor
from models.energy_prediction.data_loader import EnergyDataLoader
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

print("=" * 70)
print("KAPSAMLI MODEL TESTI")
print("=" * 70)

# 1. Model yukle
print("\n[1/7] Model yukleniyor...")
model_path = Path("outputs/models/weather_energy_model")
predictor = EnergyPredictor()
predictor.load(model_path)
print(f"   [OK] Model yuklendi: {predictor.is_trained}")

# 2. Gercek veri yukle (kucuk ornek)
print("\n[2/7] Gercek test verisi yukleniyor...")
loader = EnergyDataLoader(verbose=False)
test_df = loader.get_sample_data(1000)  # 1000 satir test verisi
print(f"   [OK] Test verisi yuklendi: {len(test_df)} satir")

# 3. Feature engineering yap
print("\n[3/7] Feature engineering yapiliyor...")
test_df_processed = loader.preprocess_building_data(test_df)
# Feature engineer zaten fit edilmis, fit_transform kullan (fit kismi atlanir)
test_df_features = predictor.feature_engineer.fit_transform(test_df_processed)
print(f"   [OK] Feature engineering tamamlandi: {len(test_df_features)} satir, {len(predictor.feature_engineer.get_feature_columns())} feature")

# 4. X, y ayir
print("\n[4/7] Veri hazirlaniyor...")
X_test, y_test = predictor.feature_engineer.get_X_y(test_df_features)
print(f"   [OK] X_test: {X_test.shape}, y_test: {y_test.shape}")
print(f"   [OK] y_test ortalama: {y_test.mean():.2f}, std: {y_test.std():.2f}")

# 5. Tahmin yap
print("\n[5/7] Model tahminleri yapiliyor...")
try:
    y_pred = predictor.model.predict(X_test)
    print(f"   [OK] Tahmin basarili: {len(y_pred)} tahmin")
    print(f"   [OK] y_pred ortalama: {y_pred.mean():.2f}, std: {y_pred.std():.2f}")
    print(f"   [OK] y_pred min: {y_pred.min():.2f}, max: {y_pred.max():.2f}")
except Exception as e:
    print(f"   [HATA] Tahmin hatasi: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 6. Metrikleri hesapla
print("\n[6/7] Performans metrikleri hesaplaniyor...")
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

# MAPE
mask = y_test != 0
if mask.sum() > 0:
    mape = np.mean(np.abs((y_test[mask] - y_pred[mask]) / y_test[mask])) * 100
else:
    mape = np.nan

print(f"   [OK] MAE:  {mae:.4f}")
print(f"   [OK] RMSE: {rmse:.4f}")
print(f"   [OK] R2:   {r2:.4f}")
print(f"   [OK] MAPE: {mape:.2f}%")

# 7. Detayli analiz
print("\n[7/7] Detayli analiz...")

# Tahmin vs Gercek karsilastirma
print("\n   Tahmin vs Gercek Karsilastirma (ilk 10):")
comparison = pd.DataFrame({
    'Gercek': y_test.values[:10],
    'Tahmin': y_pred[:10],
    'Fark': np.abs(y_test.values[:10] - y_pred[:10]),
    'Fark %': (np.abs(y_test.values[:10] - y_pred[:10]) / (y_test.values[:10] + 1e-6) * 100)
})
print(comparison.to_string(index=False))

# Istatistikler
print(f"\n   Istatistikler:")
print(f"   - Ortalama mutlak hata: {mae:.4f}")
print(f"   - Maksimum hata: {np.abs(y_test.values - y_pred).max():.4f}")
print(f"   - Hata standart sapmasi: {np.abs(y_test.values - y_pred).std():.4f}")
print(f"   - R2 skoru: {r2:.4f} ({'Cok iyi' if r2 > 0.9 else 'Iyi' if r2 > 0.7 else 'Orta' if r2 > 0.5 else 'Kotu'})")

# Feature importance kontrolu
print(f"\n   Feature Importance (Top 5):")
try:
    importance = predictor.get_feature_importance(top_n=5)
    for idx, row in importance.iterrows():
        print(f"   {idx+1}. {row['feature']:40s} {row['importance']:.4f}")
except Exception as e:
    print(f"   [HATA] Feature importance alinamadi: {e}")

# Sonuc
print("\n" + "=" * 70)
if r2 > 0.9 and mae < 1.0:
    print("SONUC: Model MUKEMMEL calisiyor! [OK]")
    print(f"   - R2 skoru {r2:.4f} ile cok yuksek dogruluk")
    print(f"   - MAE {mae:.4f} ile dusuk hata")
elif r2 > 0.7:
    print("SONUC: Model IYI calisiyor! [OK]")
    print(f"   - R2 skoru {r2:.4f} ile iyi dogruluk")
else:
    print("SONUC: Model calisiyor ama performans dusuk [UYARI]")
    print(f"   - R2 skoru {r2:.4f} ile orta dogruluk")
print("=" * 70)

