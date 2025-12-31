# Weather Integration Documentation

**Date:** December 30, 2024  
**Status:** ✅ Implemented and Tested

## Overview

Weather data integration for Energy Prediction model using a hybrid approach:
- **OpenWeather API**: Real-time weather data and forecasts
- **World Weather Repository**: Historical weather data (CSV)

## Architecture

```
┌─────────────────────────────────────────┐
│  Energy Prediction Model                │
│  (EnergyFeatureEngineer)                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Weather Service (Unified Interface)     │
│  - get_current_weather()                │
│  - get_historical_weather()             │
│  - get_weather_features()               │
│  - get_forecast()                       │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌─────────────┐    ┌──────────────────┐
│ OpenWeather │    │ World Weather    │
│ API         │    │ Repository CSV   │
│ (Real-time) │    │ (Historical)     │
└─────────────┘    └──────────────────┘
```

## Components

### 1. Weather Service (`services/weather_service.py`)

Unified interface that combines both data sources:

```python
from services.weather_service import WeatherService

service = WeatherService(verbose=False)

# Get current weather
current = service.get_current_weather("Istanbul,TR")

# Get historical weather
historical = service.get_historical_weather(
    "Istanbul", 
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 7)
)

# Get weather features for ML
features = service.get_weather_features("Istanbul,TR", date.today())
```

### 2. OpenWeather Client (`services/openweather_client.py`)

- Real-time weather data
- 5-day forecast
- Caching (1 hour TTL)
- Rate limiting handling (1000 calls/day free tier)
- API key from `yeni_veri_setleri/openweatherapi` or environment variable

### 3. World Weather Repository Loader (`services/weather_repo_loader.py`)

- Loads `GlobalWeatherRepository.csv` (29MB)
- Location-based filtering
- Date range filtering
- Efficient chunked reading

## Weather Features

The following weather features are added to the model:

| Feature | Description | Source |
|---------|-------------|--------|
| `weather_temperature_celsius` | Temperature in Celsius | OpenWeather / CSV |
| `weather_humidity` | Humidity percentage | OpenWeather / CSV |
| `weather_pressure_mb` | Atmospheric pressure (mb) | OpenWeather / CSV |
| `weather_wind_speed_ms` | Wind speed (m/s) | OpenWeather / CSV |
| `weather_cloudiness` | Cloud cover percentage | OpenWeather / CSV |
| `weather_heating_degree_days` | HDD (base 18°C) | Calculated |
| `weather_cooling_degree_days` | CDD (base 24°C) | Calculated |

## Usage

### In Feature Engineering

```python
from models.energy_prediction.feature_engineer import EnergyFeatureEngineer

engineer = EnergyFeatureEngineer(
    target_column="total_power",
    date_column="Time",
    include_weather=True,  # Enable weather features
    location="Istanbul,TR",
    lat=41.0082,  # Optional
    lon=28.9784   # Optional
)

df_features = engineer.fit_transform(df)
```

### In Predictor

```python
from models.energy_prediction.predictor import EnergyPredictor

predictor = EnergyPredictor(
    algorithm="xgboost",
    location="Istanbul,TR",
    include_weather=True
)

predictor.train(data)
forecast = predictor.predict(future_hours=24)
```

### In API

```python
POST /api/v1/ml/forecast
{
    "data": [...],  # Historical energy data
    "future_hours": 24,
    "location": "Istanbul,TR",
    "include_weather": true
}
```

## Configuration

### API Key Setup

1. **OpenWeather API Key**
   - File: `yeni_veri_setleri/openweatherapi`
   - Or environment variable: `OPENWEATHER_API_KEY`
   - Backend config: `ecologia/backend/app/config.py`

2. **World Weather Repository**
   - File: `yeni_veri_setleri/World Weather Repository ( Daily Updating )/GlobalWeatherRepository.csv`
   - Automatically loaded by `WeatherRepoLoader`

## Fallback Strategy

1. **For Current Weather:**
   - Try OpenWeather API first
   - Fallback to World Weather Repository (most recent record)

2. **For Historical Weather:**
   - Use World Weather Repository CSV
   - If not found, use monthly averages

3. **For Forecast:**
   - Use OpenWeather API forecast (5 days)
   - If API unavailable, use historical averages

## Performance

- **Feature Count:** +5-7 weather features per prediction
- **Model Performance:** MAPE ~5% (with weather features)
- **API Response Time:** <2s (with caching)
- **Cache Hit Rate:** ~80% (for repeated locations)

## Testing

Run comprehensive tests:

```bash
cd ecologia/modeller
python tests/test_weather_service.py
```

Tests cover:
- Weather service import
- OpenWeather API client
- World Weather Repository loader
- Weather service integration
- Feature engineer with weather

## Troubleshooting

### API Key Not Found
- Check `yeni_veri_setleri/openweatherapi` file
- Or set `OPENWEATHER_API_KEY` environment variable

### CSV Not Found
- Verify `GlobalWeatherRepository.csv` exists
- Check path in `config.py`

### Rate Limiting
- OpenWeather free tier: 1000 calls/day
- Caching reduces API calls
- Fallback to CSV if limit reached

### Missing Weather Data
- Default values used if weather unavailable
- Temperature: 20°C, Humidity: 50%, Pressure: 1013 mb

## Future Enhancements

- [ ] Multi-location support
- [ ] Weather impact visualization
- [ ] Historical weather analysis dashboard
- [ ] Weather-based anomaly detection
- [ ] Seasonal pattern analysis

