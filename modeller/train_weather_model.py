"""
Weather-Enabled Energy Prediction Model Training
=================================================

Tam eğitim scripti - checkpoint desteği ile
"""

import sys
import json
import pickle
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).resolve().parent))

from models.energy_prediction.predictor import EnergyPredictor
from models.energy_prediction.data_loader import EnergyDataLoader

print("=" * 60)
print("WEATHER-ENABLED ENERGY PREDICTION MODEL TRAINING")
print("=" * 60)

# Checkpoint ayarları
CHECKPOINT_DIR = Path(__file__).parent / "checkpoints" / "weather_training"
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_DATA = CHECKPOINT_DIR / "data_checkpoint.pkl"
CHECKPOINT_FEATURES = CHECKPOINT_DIR / "features_checkpoint.parquet"
CHECKPOINT_STATE = CHECKPOINT_DIR / "training_state.json"
CHECKPOINT_MODEL = CHECKPOINT_DIR / "model_checkpoint.json"

# Tam veri mi örnek mi?
USE_FULL_DATA = True  # True: 3.1M satır, False: 10K satır (test)
RESUME_FROM_CHECKPOINT = True  # Checkpoint'ten devam et

# Checkpoint kontrolü
def load_checkpoint_state():
    """Checkpoint state'i yükle"""
    if CHECKPOINT_STATE.exists() and RESUME_FROM_CHECKPOINT:
        with open(CHECKPOINT_STATE, 'r') as f:
            return json.load(f)
    return None

def save_checkpoint_state(state):
    """Checkpoint state'i kaydet"""
    with open(CHECKPOINT_STATE, 'w') as f:
        json.dump(state, f, indent=2)

# 1. Veri yükleme (checkpoint kontrolü ile)
print("\n[1/6] Veri yükleme kontrolü...")
checkpoint_state = load_checkpoint_state()

if checkpoint_state and checkpoint_state.get("data_loaded") and RESUME_FROM_CHECKPOINT:
    print("   -> Checkpoint'ten veri yükleniyor...")
    try:
        import pandas as pd
        df = pd.read_pickle(CHECKPOINT_DATA)
        print(f"   -> {len(df):,} satır checkpoint'ten yüklendi")
    except Exception as e:
        print(f"   -> Checkpoint yüklenemedi: {e}, yeni veri yükleniyor...")
        checkpoint_state = None

if checkpoint_state is None or not checkpoint_state.get("data_loaded"):
    print("   -> Yeni veri yükleniyor...")
    loader = EnergyDataLoader(verbose=True)
    
    if USE_FULL_DATA:
        print("   -> TAM VERİ yükleniyor (bu işlem uzun sürebilir)...")
        df = loader.load_building_energy_dataset()  # Tüm yıllar (2016-2021)
        print(f"   -> {len(df):,} satır yüklendi (TAM VERİ)")
    else:
        print("   -> Örnek veri yükleniyor (hızlı test için)...")
        df = loader.get_sample_data(10000)
        print(f"   -> {len(df):,} satır yüklendi (ÖRNEK)")
    
    # Veri checkpoint'i kaydet
    print("   -> Veri checkpoint'i kaydediliyor...")
    df.to_pickle(CHECKPOINT_DATA)
    save_checkpoint_state({"data_loaded": True, "n_rows": len(df), "timestamp": datetime.now().isoformat()})
    print("   -> Veri checkpoint'i kaydedildi")

# 2. Predictor oluştur (weather enabled)
print("\n[2/6] Predictor oluşturuluyor (weather features aktif)...")
predictor = EnergyPredictor(
    algorithm="xgboost",
    location="Istanbul,TR",
    include_weather=True,
    model_params={
        "n_estimators": 200,
        "max_depth": 6,
        "learning_rate": 0.1
    }
)
print(f"   -> Location: {predictor.location}")
print(f"   -> Weather features: {predictor.include_weather}")

# 3. Feature Engineering (checkpoint kontrolü ile)
print("\n[3/6] Feature engineering kontrolü...")
checkpoint_state = load_checkpoint_state()

if checkpoint_state and checkpoint_state.get("features_created") and RESUME_FROM_CHECKPOINT:
    print("   -> Checkpoint'ten feature'lar yükleniyor...")
    try:
        import pandas as pd
        df_features = pd.read_parquet(CHECKPOINT_FEATURES)
        print(f"   -> {len(df_features):,} satır feature checkpoint'ten yüklendi")
        # Feature engineer state'i restore et
        feature_cols = checkpoint_state.get("feature_columns", [])
        if feature_cols:
            predictor.feature_engineer.feature_columns = feature_cols
    except Exception as e:
        print(f"   -> Feature checkpoint yüklenemedi: {e}, yeni feature'lar oluşturuluyor...")
        checkpoint_state = None

if checkpoint_state is None or not checkpoint_state.get("features_created"):
    print("   -> Feature engineering başlıyor...")
    # Preprocessing
    df = predictor.loader.preprocess_building_data(df)
    
    # Feature engineering
    df_features = predictor.feature_engineer.fit_transform(df)
    feature_cols = predictor.feature_engineer.get_feature_columns()
    
    print(f"   -> {len(feature_cols)} feature oluşturuldu")
    
    # Feature checkpoint'i kaydet
    print("   -> Feature checkpoint'i kaydediliyor...")
    df_features.to_parquet(CHECKPOINT_FEATURES, index=False)
    checkpoint_state = load_checkpoint_state() or {}
    checkpoint_state.update({
        "features_created": True,
        "feature_columns": feature_cols,
        "n_features": len(feature_cols),
        "timestamp": datetime.now().isoformat()
    })
    save_checkpoint_state(checkpoint_state)
    print("   -> Feature checkpoint'i kaydedildi")

# 4. Train/Val split
print("\n[4/6] Train/Val split...")
n = len(df_features)
val_size = int(n * 0.15)
train_df = df_features.iloc[:-val_size]
val_df = df_features.iloc[-val_size:]

X_train, y_train = predictor.feature_engineer.get_X_y(train_df)
X_val, y_val = predictor.feature_engineer.get_X_y(val_df)

print(f"   -> Train: {len(X_train)}, Val: {len(X_val)}")

# 5. Model eğitimi (checkpoint kontrolü ile)
print("\n[5/6] Model eğitimi başlıyor...")
if USE_FULL_DATA:
    print("   (TAM VERİ ile eğitim - bu işlem 30-60 dakika sürebilir)")

# XGBoost checkpoint callback tanımla (hem checkpoint hem yeni eğitim için)
import xgboost as xgb
from xgboost.callback import TrainingCallback

class CheckpointCallback(TrainingCallback):
    """XGBoost checkpoint callback"""
    def __init__(self, checkpoint_path, checkpoint_state_func):
        self.checkpoint_path = checkpoint_path
        self.checkpoint_state_func = checkpoint_state_func
    
    def after_iteration(self, model, epoch, evals_log):
        """Her iterasyondan sonra checkpoint kaydet"""
        try:
            model.save_model(str(self.checkpoint_path))
            checkpoint_state = self.checkpoint_state_func() or {}
            checkpoint_state.update({
                "model_training_started": True,
                "n_estimators_trained": epoch + 1,
                "last_checkpoint": datetime.now().isoformat()
            })
            save_checkpoint_state(checkpoint_state)
        except Exception as e:
            print(f"  -> Checkpoint kaydetme hatası: {e}")
        return False  # Training devam etsin

# Checkpoint callback'i oluştur
checkpoint_callback = CheckpointCallback(CHECKPOINT_MODEL, load_checkpoint_state)

# XGBoost checkpoint desteği
checkpoint_state = load_checkpoint_state()
model_checkpoint_exists = CHECKPOINT_MODEL.exists() and checkpoint_state and checkpoint_state.get("model_training_started")

if model_checkpoint_exists and RESUME_FROM_CHECKPOINT:
    print("   -> Checkpoint'ten model eğitimi devam ediyor...")
    try:
        # XGBoost model checkpoint'ten yükle
        bst = xgb.Booster()
        bst.load_model(str(CHECKPOINT_MODEL))
        
        # Eğitime devam et
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dval = xgb.DMatrix(X_val, label=y_val)
        
        # Kalan iterasyonları eğit
        remaining_iters = 200 - checkpoint_state.get("n_estimators_trained", 0)
        if remaining_iters > 0:
            print(f"   -> Kalan {remaining_iters} iterasyon eğitiliyor...")
            bst = xgb.train(
                predictor.model.default_params,
                dtrain,
                num_boost_round=remaining_iters,
                evals=[(dtrain, 'train'), (dval, 'val')],
                xgb_model=bst,
                callbacks=[checkpoint_callback],
                verbose_eval=10
            )
            bst.save_model(str(CHECKPOINT_MODEL))
        
        # Model'i predictor'a yükle (XGBRegressor wrapper ile)
        predictor.model.model = xgb.XGBRegressor(**predictor.model.default_params)
        predictor.model.model._Booster = bst
        predictor.model.model._le = None
        predictor.model.model._classes = None
        predictor.model.is_fitted = True
        predictor.model.feature_names = X_train.columns.tolist()
        
        # Predictor state'i güncelle
        predictor.is_trained = True
        
        print("   -> Model checkpoint'ten yüklendi ve eğitim tamamlandı")
    except Exception as e:
        print(f"   -> Checkpoint yüklenemedi: {e}, yeni eğitim başlatılıyor...")
        import traceback
        traceback.print_exc()
        model_checkpoint_exists = False

if not model_checkpoint_exists:
    print("   -> Yeni model eğitimi başlatılıyor...")
    
    # XGBoost DMatrix oluştur
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dval = xgb.DMatrix(X_val, label=y_val)
    
    # Eğit (checkpoint_callback zaten tanımlı)
    bst = xgb.train(
        predictor.model.default_params,
        dtrain,
        num_boost_round=200,
        evals=[(dtrain, 'train'), (dval, 'val')],
        callbacks=[checkpoint_callback],
        verbose_eval=10
    )
    
    # Model'i predictor'a yükle
    # XGBoost Booster modelini XGBRegressor'a dönüştür
    predictor.model.model = xgb.XGBRegressor(**predictor.model.default_params)
    predictor.model.model._Booster = bst
    predictor.model.model._le = None  # Label encoder yok
    predictor.model.model._classes = None
    predictor.model.is_fitted = True
    predictor.model.feature_names = X_train.columns.tolist()
    
    # Predictor state'i güncelle
    predictor.is_trained = True

# Validation metrikleri
val_metrics = predictor.model.evaluate(X_val, y_val)
results = {
    "n_samples": len(df),
    "n_features": len(predictor.feature_engineer.get_feature_columns()),
    "trained_at": datetime.now().isoformat(),
    "val_metrics": val_metrics
}

# 6. Sonuçlar
print("\n[6/6] Eğitim tamamlandı!")
print("\n=== Eğitim Sonuçları ===")
print(f"   Örnek sayısı: {results['n_samples']}")
print(f"   Feature sayısı: {results['n_features']}")
print(f"   Eğitim zamanı: {results['trained_at']}")
print("\n=== Validation Metrikleri ===")
for key, value in results['val_metrics'].items():
    print(f"   {key.upper()}: {value:.4f}")

# 7. Feature importance
print("\n[7/7] Feature importance analizi...")
importance = predictor.get_feature_importance()
print("\n=== Top 10 Features ===")
for i, row in importance.head(10).iterrows():
    print(f"   {i+1:2d}. {row['feature']:40s} {row['importance']:.4f}")

# Weather features kontrolü
weather_features = [f for f in importance['feature'] if 'weather' in f]
if weather_features:
    print(f"\n=== Weather Features ({len(weather_features)}) ===")
    for feat in weather_features[:5]:
        imp = importance[importance['feature'] == feat]['importance'].values[0]
        print(f"   - {feat:40s} {imp:.4f}")

# 8. Final model kaydet
print("\n[8/8] Final model kaydediliyor...")
model_path = Path(__file__).parent / "outputs" / "models" / "weather_energy_model"
model_path.mkdir(parents=True, exist_ok=True)
predictor.save(model_path)
print(f"   -> Model kaydedildi: {model_path}")

# Checkpoint state'i güncelle
checkpoint_state = load_checkpoint_state() or {}
checkpoint_state.update({
    "training_completed": True,
    "final_model_path": str(model_path),
    "completion_time": datetime.now().isoformat()
})
save_checkpoint_state(checkpoint_state)

print("\n" + "=" * 60)
print("EĞİTİM TAMAMLANDI!")
print("=" * 60)
print(f"\nCheckpoint klasörü: {CHECKPOINT_DIR}")
print("Eğitim kesilirse, script'i tekrar çalıştırarak checkpoint'ten devam edebilirsiniz.")

