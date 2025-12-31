"""
Energy Prediction Model Test Script
"""
import sys
sys.path.insert(0, '.')

from models.energy_prediction.data_loader import EnergyDataLoader
from models.energy_prediction.feature_engineer import EnergyFeatureEngineer
from models.energy_prediction.xgboost_model import XGBoostEnergyPredictor

print("=== ENERGY PREDICTION MODEL TEST ===\n")

print("1. Veri yukleniyor...")
loader = EnergyDataLoader(verbose=False)
df = loader.get_sample_data(2000)
print(f"   -> {len(df)} satir yuklendi")

print("\n2. Feature engineering...")
# Test with weather features enabled
engineer = EnergyFeatureEngineer(
    target_column="total_power", 
    date_column="Time",
    include_weather=True,
    location="Istanbul,TR"
)
df_features = engineer.fit_transform(df)
print(f"   -> {len(engineer.get_feature_columns())} feature olusturuldu")
print(f"   -> Weather features: {engineer.include_weather}")

print("\n3. Train/Test split...")
n = len(df_features)
train_df = df_features.iloc[:int(n*0.8)]
test_df = df_features.iloc[int(n*0.8):]

X_train, y_train = engineer.get_X_y(train_df)
X_test, y_test = engineer.get_X_y(test_df)
print(f"   -> Train: {len(X_train)}, Test: {len(X_test)}")

print("\n4. Model egitiliyor...")
model = XGBoostEnergyPredictor(n_estimators=50, max_depth=4)
model.fit(X_train, y_train, verbose=False)

print("\n5. Test degerlendirmesi...")
metrics = model.evaluate(X_test, y_test)
print(f"   MAE:  {metrics['mae']:.2f}")
print(f"   RMSE: {metrics['rmse']:.2f}")
print(f"   R2:   {metrics['r2']:.4f}")
print(f"   MAPE: {metrics['mape']:.2f}%")

print("\n6. Top 5 Features:")
importance = model.get_feature_importance()
for i, row in importance.head(5).iterrows():
    print(f"   {row['feature']}: {row['importance']:.4f}")

print("\n" + "="*40)
if metrics['mape'] < 15:
    print("BASARILI - MAPE < 15%")
else:
    print("Model gelistirilebilir - MAPE yuksek")
print("="*40)

