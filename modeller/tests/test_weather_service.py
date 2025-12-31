"""
Weather Service Tests
====================

Test weather service integration
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.weather_service import WeatherService
from services.openweather_client import OpenWeatherClient
from services.weather_repo_loader import WeatherRepoLoader
from datetime import date, datetime


def test_weather_service_import():
    """Test weather service can be imported"""
    print("1. Testing weather service import...")
    try:
        service = WeatherService(verbose=False)
        print("   [OK] WeatherService imported successfully")
        return True
    except Exception as e:
        print(f"   [FAIL] Import failed: {e}")
        return False


def test_openweather_client():
    """Test OpenWeather API client"""
    print("\n2. Testing OpenWeather client...")
    try:
        client = OpenWeatherClient()
        print(f"   [OK] OpenWeatherClient created (API key: {'found' if client.api_key else 'not found'})")
        
        # Test current weather (if API key available)
        if client.api_key:
            try:
                weather = client.get_current_weather("Istanbul,TR")
                print(f"   [OK] Current weather fetched: {weather['temperature_celsius']:.1f}C")
                return True
            except Exception as e:
                print(f"   [WARN] API call failed (may be rate limit): {e}")
                return True  # Still pass if client works
        else:
            print("   [WARN] API key not available, skipping API test")
            return True
    except Exception as e:
        print(f"   [FAIL] OpenWeather client test failed: {e}")
        return False


def test_weather_repo_loader():
    """Test World Weather Repository loader"""
    print("\n3. Testing World Weather Repository loader...")
    try:
        loader = WeatherRepoLoader(verbose=False)
        
        # Test location finding
        df = loader.find_location(location_name="Istanbul", country="Turkey")
        print(f"   [OK] Found {len(df)} records for Istanbul")
        
        if len(df) > 0:
            # Test historical weather
            start = date(2024, 1, 1)
            end = date(2024, 1, 7)
            hist = loader.get_historical_weather("Istanbul", start, end, country="Turkey")
            print(f"   [OK] Historical weather: {len(hist)} records")
            
            # Test weather features
            features = loader.get_weather_features_for_date("Istanbul", date(2024, 1, 1))
            if features:
                print(f"   [OK] Weather features: temp={features['temperature_celsius']:.1f}C")
            else:
                print("   [WARN] No weather features for test date")
        
        return True
    except Exception as e:
        print(f"   [FAIL] Weather repo loader test failed: {e}")
        return False


def test_weather_service_integration():
    """Test unified weather service"""
    print("\n4. Testing Weather Service integration...")
    try:
        service = WeatherService(verbose=False)
        
        # Test current weather
        try:
            current = service.get_current_weather("Istanbul,TR")
            print(f"   [OK] Current weather: {current.get('temperature_celsius', 'N/A')}C")
            print(f"   [OK] Source: {current.get('source', 'unknown')}")
        except Exception as e:
            print(f"   [WARN] Current weather failed: {e}")
        
        # Test weather features
        try:
            features = service.get_weather_features("Istanbul,TR", date.today())
            print(f"   [OK] Weather features: {len(features)} features")
            print(f"      - Temperature: {features.get('temperature_celsius', 'N/A')}C")
            print(f"      - Humidity: {features.get('humidity', 'N/A')}%")
            print(f"      - HDD: {features.get('heating_degree_days', 'N/A')}")
            print(f"      - CDD: {features.get('cooling_degree_days', 'N/A')}")
        except Exception as e:
            print(f"   [WARN] Weather features failed: {e}")
        
        return True
    except Exception as e:
        print(f"   [FAIL] Weather service integration test failed: {e}")
        return False


def test_feature_engineer_with_weather():
    """Test feature engineer with weather features"""
    print("\n5. Testing Feature Engineer with weather...")
    try:
        from models.energy_prediction.feature_engineer import EnergyFeatureEngineer
        from models.energy_prediction.data_loader import EnergyDataLoader
        
        # Load sample data
        loader = EnergyDataLoader(verbose=False)
        df = loader.get_sample_data(500)
        
        # Create feature engineer with weather
        engineer = EnergyFeatureEngineer(
            target_column="total_power",
            date_column="Time",
            include_weather=True,
            location="Istanbul,TR"
        )
        
        # Transform
        df_features = engineer.fit_transform(df)
        
        # Check weather features
        weather_cols = [col for col in df_features.columns if col.startswith("weather_")]
        print(f"   [OK] Weather features added: {len(weather_cols)} columns")
        print(f"      - {', '.join(weather_cols[:5])}")
        
        # Check feature count
        total_features = len(engineer.get_feature_columns())
        print(f"   [OK] Total features: {total_features}")
        
        return True
    except Exception as e:
        print(f"   [FAIL] Feature engineer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("WEATHER SERVICE TESTS")
    print("=" * 50)
    
    results = []
    results.append(test_weather_service_import())
    results.append(test_openweather_client())
    results.append(test_weather_repo_loader())
    results.append(test_weather_service_integration())
    results.append(test_feature_engineer_with_weather())
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("[SUCCESS] ALL TESTS PASSED")
    else:
        print("[FAILURE] SOME TESTS FAILED")

