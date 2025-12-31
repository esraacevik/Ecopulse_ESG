"""
Test script for model API integration
Tests checkpoint loading and prediction
"""

import sys
import io
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from api.ml_routes import load_trained_model, get_energy_predictor

print("=" * 60)
print("MODEL API INTEGRATION TEST")
print("=" * 60)

# Test 1: Load trained model
print("\n[1/3] Testing load_trained_model()...")
try:
    predictor = load_trained_model(location="Istanbul,TR", include_weather=True)
    if predictor:
        print(f"   [OK] Model loaded successfully")
        print(f"   [OK] is_trained: {predictor.is_trained}")
        if hasattr(predictor, 'feature_engineer') and hasattr(predictor.feature_engineer, 'feature_columns'):
            print(f"   [OK] Features: {len(predictor.feature_engineer.feature_columns)}")
    else:
        print("   [FAIL] No trained model found")
except Exception as e:
    print(f"   [ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Get predictor (should use cached if available)
print("\n[2/3] Testing get_energy_predictor()...")
try:
    predictor = get_energy_predictor(location="Istanbul,TR", include_weather=True)
    print(f"   [OK] Predictor obtained")
    print(f"   [OK] is_trained: {predictor.is_trained}")
except Exception as e:
    print(f"   [ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Prediction (if model is trained)
print("\n[3/3] Testing prediction...")
try:
    predictor = get_energy_predictor(location="Istanbul,TR", include_weather=True)
    if predictor.is_trained:
        # Try to predict (needs last_data)
        if predictor.last_data is not None and len(predictor.last_data) > 0:
            forecast = predictor.predict(future_hours=24)
            print(f"   [OK] Prediction successful")
            print(f"   [OK] Forecast length: {len(forecast)}")
            print(f"   [OK] Sample prediction:")
            print(forecast.head(3).to_string())
        else:
            print("   [WARN] Model trained but no last_data available")
            print("   [WARN] Prediction requires historical data")
    else:
        print("   [WARN] Model not trained, skipping prediction test")
except Exception as e:
    print(f"   [ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)

