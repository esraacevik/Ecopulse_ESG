# 📊 YENİ VERİ SETLERİ ENTEGRASYON PLANI

**Tarih:** 30 Aralık 2024  
**Versiyon:** 2.0  
**Durum:** 📋 PLANLAMA AŞAMASI (Implementasyona geçilmeyecek)

---

## 🎯 GENEL STRATEJİ

### Mevcut Sistem Durumu
- ✅ 4 ML Model aktif (Energy Prediction, Anomaly Detection, Sector Benchmark, Target Recommendation)
- ✅ OpenWeather API key mevcut (`88bd2e8030f58139bedfc2bd85e939c7`)
- ✅ World Weather Repository CSV mevcut (29MB, günlük güncellenen)
- ✅ Hibrit emisyon hesaplama sistemi (Climatiq + EPA)

### Entegrasyon Hedefleri
1. **Weather Data Integration** - OpenWeather API + World Weather Repository
2. **Enhanced Energy Prediction** - Weather features ile model iyileştirme
3. **Real-time Weather Features** - Canlı hava durumu entegrasyonu
4. **Historical Weather Analysis** - Geçmiş hava durumu korelasyonu
5. **Air Quality Integration** - Hava kalitesi → Emisyon korelasyonu

---

## 📦 VERİ SETLERİ KATEGORİZASYONU

### ⭐⭐⭐ BİRİNCİL ÖNCELİK (Hemen Entegre Edilmeli)

| Veri Seti | Dosya | Kullanım Amacı | Entegrasyon Yeri | Öncelik |
|-----------|-------|----------------|------------------|---------|
| **World Weather Repository** | `GlobalWeatherRepository.csv` | Historical weather data | Energy Prediction Model | 🔥 YÜKSEK |
| **OpenWeather API** | API Key mevcut | Real-time weather | Energy Prediction + Frontend | 🔥 YÜKSEK |
| **US EIA Hourly** | `data/*.csv` (90 dosya) | Time series training | Energy Prediction Model | 🔥 YÜKSEK |
| **Supply Chain GHG Factors** | `SupplyChainGHGEmissionFactors_v1.3.0_NAICS_CO2e_USD2022.csv` | Sector benchmarking | Sector Benchmark Model | 🔥 YÜKSEK |
| **Corporate Environmental Impact** | `final_raw_sample_0_percent.csv` | Company ESG scores | Sector Benchmark + Target Recommendation | 🔥 YÜKSEK |
| **Ember** | `yearly_full_release_long_format.csv` | Country electricity trends | Energy Prediction + Sector Benchmark | 🔥 YÜKSEK |

### ⭐⭐ İKİNCİL ÖNCELİK (Yararlı - Sonraki Faz)

| Veri Seti | Dosya | Kullanım Amacı | Entegrasyon Yeri | Öncelik |
|-----------|-------|----------------|------------------|---------|
| **EPA eGRID** | `egrid2023_data_rev2.xlsx` | Regional emission factors | Hybrid Calculator | ⚡ ORTA |
| **EPA Vehicle Fuel Economy** | `vehicles.csv` | Transportation emissions | Scope 3 Calculator | ⚡ ORTA |
| **NYC Building Energy** | `NYC_Building_Energy_*.csv` | Building benchmarks | Anomaly Detection | ⚡ ORTA |
| **Building Energy Benchmarking** | `Building_Energy_Benchmarking_Data_*.csv` | Building patterns | Energy Prediction | ⚡ ORTA |
| **RECS** | `recs2015_public_v4.csv` | Residential patterns | Energy Prediction | ⚡ ORTA |
| **Monthly Energy by Sector** | `Table_1.1_Primary_Energy_Overview.xlsx` | Sector trends | Energy Prediction | ⚡ ORTA |

### ⭐ ÜÇÜNCÜL ÖNCELİK (Opsiyonel - Gelecek)

| Veri Seti | Kullanım Amacı | Öncelik |
|-----------|----------------|---------|
| **ASHRAE Thermal Comfort** | HVAC optimization | 🔵 DÜŞÜK |
| **Occupancy Detection** | Building occupancy patterns | 🔵 DÜŞÜK |
| **eVED** | Vehicle energy patterns | 🔵 DÜŞÜK |
| **CBECS** | Commercial building energy | 🔵 DÜŞÜK |
| **Chicago Energy Benchmarking** | Regional benchmarks | 🔵 DÜŞÜK |

---

## 🌤️ WEATHER DATA ENTEGRASYONU (ÖNCELİKLİ)

### 1. OpenWeather API + World Weather Repository Hibrit Yaklaşımı

#### Strateji
```
┌─────────────────────────────────────────────────────────┐
│  WEATHER DATA SOURCE SELECTION                          │
└─────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────────┐         ┌──────────────────────┐
│ OpenWeather API   │         │ World Weather Repo   │
│ (Real-time)       │         │ (Historical)         │
│                   │         │                      │
│ ✅ Current data   │         │ ✅ Historical data    │
│ ✅ Forecast       │         │ ✅ Daily updates      │
│ ✅ Air quality    │         │ ✅ Global coverage   │
│ ❌ Historical     │         │ ❌ No forecast        │
│    (ücretli)      │         │                      │
└───────────────────┘         └──────────────────────┘
        │                               │
        └───────────────┬───────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │  Weather Service      │
            │  (Unified Interface)  │
            └───────────────────────┘
```

#### Kullanım Senaryoları

**A. Real-time Weather (OpenWeather API)**
- **Kullanım:** Canlı hava durumu verisi
- **Yer:** Frontend dashboard, Energy Prediction API
- **Özellikler:**
  - Current temperature, humidity, pressure
  - Air quality (CO, Ozone, NO2, SO2, PM2.5, PM10)
  - Weather forecast (5 gün)
  - UV index, wind speed

**B. Historical Weather (World Weather Repository)**
- **Kullanım:** Geçmiş hava durumu analizi
- **Yer:** ML Model training, Historical correlation
- **Özellikler:**
  - Historical temperature, humidity, pressure
  - Historical air quality data
  - Global coverage (200+ countries)
  - Daily updates (CSV format)

**C. Hybrid Approach (İkisini Birlikte)**
- **Training:** World Weather Repository (historical)
- **Prediction:** OpenWeather API (real-time)
- **Fallback:** World Weather Repository (API limit aşımında)

### 2. Weather Service Implementation Plan

#### Dosya Yapısı
```
modeller/
├── services/
│   ├── __init__.py
│   ├── weather_service.py          # Unified weather interface
│   ├── openweather_client.py       # OpenWeather API client
│   └── weather_repo_loader.py      # World Weather CSV loader
├── utils/
│   └── weather_utils.py            # Weather feature engineering
```

#### Weather Service API
```python
class WeatherService:
    """
    Unified weather data service
    - Real-time: OpenWeather API
    - Historical: World Weather Repository
    """
    
    def get_current_weather(
        self, 
        location: str, 
        lat: float = None, 
        lon: float = None
    ) -> Dict:
        """Get current weather (OpenWeather API)"""
        
    def get_historical_weather(
        self,
        location: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """Get historical weather (World Weather Repository)"""
        
    def get_weather_features(
        self,
        location: str,
        date: str
    ) -> Dict:
        """Get weather features for ML model"""
        # Returns: temperature, humidity, pressure, 
        #          cooling_degree_days, heating_degree_days,
        #          air_quality_index
```

### 3. Energy Prediction Model Entegrasyonu

#### Mevcut Durum
- ✅ XGBoost modeli eğitilmiş
- ✅ Time features, lag features, rolling features mevcut
- ❌ Weather features **YOK** (planlanmış ama implement edilmemiş)

#### Yapılacaklar

**A. Feature Engineering Güncellemesi**
```python
# modeller/models/energy_prediction/feature_engineer.py

class EnergyFeatureEngineer:
    def __init__(self, include_weather: bool = True):
        self.include_weather = include_weather
        self.weather_service = WeatherService()  # YENİ
    
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        # Mevcut features
        df = create_time_features(df)
        df = create_lag_features(df)
        df = create_rolling_features(df)
        
        # YENİ: Weather features
        if self.include_weather:
            df = self._add_weather_features(df)
        
        return df
    
    def _add_weather_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add weather features from OpenWeather API or World Weather Repo"""
        # 1. Location bilgisi al (user input veya default)
        # 2. Her tarih için weather data çek
        # 3. Temperature, humidity, pressure ekle
        # 4. Cooling/Heating degree days hesapla
        # 5. Air quality index ekle
        pass
```

**B. Model Retraining**
- Weather features ile model yeniden eğitilecek
- Feature importance analizi yapılacak
- Weather features'ın model performansına etkisi ölçülecek

### 4. Frontend Entegrasyonu

#### Yeni Özellikler

**A. Weather Dashboard Widget**
- **Yer:** Energy Prediction sekmesi
- **İçerik:**
  - Current weather (location-based)
  - Weather forecast (5 gün)
  - Air quality index
  - Weather impact on energy consumption

**B. Historical Weather Analysis**
- **Yer:** Energy Prediction sekmesi
- **İçerik:**
  - Historical temperature vs energy consumption chart
  - Correlation analysis
  - Seasonal patterns

---

## 📈 ENERGY PREDICTION MODEL İYİLEŞTİRMELERİ

### 1. US EIA Hourly Electricity Consumption

#### Veri Seti Özellikleri
- **90 CSV dosyası** (Balancing authorities, Regions, U.S)
- **Hourly data** (time series)
- **Geographic coverage:** US regions, states, balancing authorities

#### Kullanım Planı

**A. Model Training Data**
```python
# modeller/models/energy_prediction/data_loader.py

class EnergyDataLoader:
    def load_eia_data(self, region: str = "US48") -> pd.DataFrame:
        """
        Load US EIA hourly electricity consumption
        
        Args:
            region: "US48", "CAL", "TEX", "NY", etc.
        
        Returns:
            DataFrame with columns: [timestamp, consumption_mwh, ...]
        """
        path = f"yeni_veri_setleri/US EIA hourly electiricty consumption/data/{region}.csv"
        # Load and preprocess
```

**B. Multi-Region Training**
- Farklı bölgelerden veri yükle
- Model genelleştirme yeteneğini artır
- Regional patterns öğren

**C. Feature Engineering**
- Regional features ekle
- Time zone features
- Regional weather correlation

### 2. Building Energy Dataset (Mevcut + Yeni)

#### Mevcut Durum
- ✅ `buildingenergydataset` kullanılıyor (2016-2021)
- ✅ 5 CSV dosyası (1-5.data_*.csv)

#### Yeni Veri Setleri

**A. NYC Building Energy Data**
- **Dosya:** `NYC_Building_Energy_and_Water_Data_*.csv`
- **Kullanım:** Building-level benchmarks
- **Entegrasyon:** Anomaly Detection model

**B. Building Energy Benchmarking Data**
- **Dosya:** `Building_Energy_Benchmarking_Data_*.csv`
- **Kullanım:** Building type patterns
- **Entegrasyon:** Energy Prediction model

**C. Chicago Energy Benchmarking**
- **Dosya:** `Chicago_Energy_Benchmarking_*.csv`
- **Kullanım:** Regional building patterns
- **Entegrasyon:** Sector Benchmark model

### 3. Residential Energy Consumption Survey (RECS)

#### Kullanım Planı
- **Amaç:** Residential energy consumption patterns
- **Entegrasyon:** Energy Prediction model (residential buildings için)
- **Features:**
  - Household characteristics
  - Building type
  - Energy consumption patterns
  - Regional differences

---

## 🏢 SECTOR BENCHMARK MODEL İYİLEŞTİRMELERİ

### 1. Supply Chain GHG Emission Factors (NAICS)

#### Mevcut Durum
- ✅ Model mevcut ve çalışıyor
- ✅ NAICS kodları ile sektör eşleştirme yapılıyor

#### İyileştirmeler

**A. Daha Detaylı Sektör Eşleştirme**
- **Dosya:** `SupplyChainGHGEmissionFactors_v1.3.0_NAICS_CO2e_USD2022.csv`
- **Özellik:** 6-digit NAICS codes (daha detaylı)
- **Kullanım:** Daha hassas sektör eşleştirme

**B. GHG Breakdown**
- **Dosya:** `SupplyChainGHGEmissionFactors_v1.3.0_NAICS_byGHG_USD2022.csv`
- **Özellik:** CO2, CH4, N2O ayrı ayrı
- **Kullanım:** Scope 3 emisyon detaylandırması

### 2. Corporate Environmental Impact

#### Kullanım Planı
- **Amaç:** Şirket bazlı ESG skorları
- **Entegrasyon:** Sector Benchmark + Target Recommendation
- **Features:**
  - Environmental intensity (revenue-based)
  - Environmental intensity (operating income-based)
  - Total environmental cost
  - Industry classification

---

## 🎯 TARGET RECOMMENDATION MODEL İYİLEŞTİRMELERİ

### 1. Ember Global Electricity Data

#### Kullanım Planı
- **Amaç:** Ülke bazlı elektrik trendleri
- **Entegrasyon:** Target Recommendation model
- **Features:**
  - Country renewable energy percentage
  - Electricity demand per capita
  - Clean energy trends
  - Year-over-year changes

### 2. EPA eGRID

#### Kullanım Planı
- **Amaç:** Bölgesel emisyon faktörleri
- **Entegrasyon:** Target Recommendation (region-specific targets)
- **Features:**
  - State-level emission factors
  - Fuel type breakdown
  - Regional renewable energy mix

---

## 🚗 TRANSPORTATION EMISSIONS (YENİ ÖZELLİK)

### EPA Vehicle Fuel Economy

#### Kullanım Planı
- **Amaç:** Scope 3 - Transportation emissions
- **Entegrasyon:** Emission Calculator (yeni kategori)
- **Features:**
  - Vehicle make/model/year
  - Fuel type
  - MPG (city/highway/combined)
  - CO2 emissions per mile
  - GHG score

#### Implementation
```python
# backend/app/services/vehicle_emission_calculator.py

class VehicleEmissionCalculator:
    def __init__(self):
        self.vehicle_db = pd.read_csv("yeni_veri_setleri/EPA Vehicle Fuel Economy/vehicles.csv")
    
    def calculate_emission(
        self,
        make: str,
        model: str,
        year: int,
        distance_miles: float
    ) -> Dict:
        """
        Calculate CO2 emissions for vehicle travel
        
        Returns:
            {
                "co2_kg": float,
                "mpg": float,
                "fuel_type": str,
                "ghg_score": int
            }
        """
```

---

## 📊 ANOMALY DETECTION MODEL İYİLEŞTİRMELERİ

### 1. NYC Building Energy Data

#### Kullanım Planı
- **Amaç:** Building-level anomaly detection
- **Entegrasyon:** Anomaly Detection model
- **Features:**
  - Building type
  - Energy consumption patterns
  - Water consumption patterns
  - Building size, age

### 2. Occupancy Detection Dataset

#### Kullanım Planı
- **Amaç:** Occupancy-based anomaly detection
- **Entegrasyon:** Anomaly Detection model (opsiyonel)
- **Features:**
  - Occupancy patterns
  - Energy consumption vs occupancy correlation

---

## 🔧 TEKNİK ENTEGRASYON DETAYLARI

### 1. Veri Yükleme Stratejisi

#### Symlink veya Kopya?
```python
# Seçenek 1: Symlink (disk tasarrufu)
# modeller/data/raw/
#   ├── weather_repo.csv -> ../../yeni_veri_setleri/World Weather Repository/GlobalWeatherRepository.csv
#   ├── eia_data/ -> ../../yeni_veri_setleri/US EIA hourly electiricty consumption/data/
#   └── ...

# Seçenek 2: Kopya (daha güvenli, ama disk kullanır)
# Veri setlerini modeller/data/raw/ altına kopyala
```

**Öneri:** Symlink kullan (disk tasarrufu, tek kaynak)

### 2. API Rate Limiting

#### OpenWeather API Limits
- **Free tier:** 1,000 calls/day
- **Strateji:**
  - Cache mekanizması (Redis veya in-memory)
  - Batch requests
  - Fallback to World Weather Repository

### 3. Data Preprocessing Pipeline

```python
# modeller/utils/data_preprocessing.py

class DataPreprocessor:
    def preprocess_weather_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize weather data"""
        # 1. Remove duplicates
        # 2. Handle missing values
        # 3. Normalize units
        # 4. Create derived features (CDD, HDD)
        pass
    
    def preprocess_eia_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess US EIA hourly data"""
        # 1. Parse timestamps
        # 2. Handle timezone
        # 3. Resample if needed
        # 4. Handle missing values
        pass
```

### 4. Feature Store

```python
# modeller/utils/feature_store.py

class FeatureStore:
    """
    Centralized feature storage and retrieval
    """
    def get_weather_features(
        self,
        location: str,
        date_range: Tuple[str, str]
    ) -> pd.DataFrame:
        """Get weather features from cache or API"""
        pass
    
    def get_sector_features(
        self,
        naics_code: str
    ) -> Dict:
        """Get sector emission factors"""
        pass
```

---

## 📅 UYGULAMA PLANI (PRIORITY ORDER)

### Faz 1: Weather Integration (1-2 hafta)
1. ✅ Weather Service oluştur (OpenWeather + World Weather Repo)
2. ✅ Energy Prediction model'e weather features ekle
3. ✅ Model retraining (weather features ile)
4. ✅ Frontend weather widget ekle

### Faz 2: US EIA Data Integration (1 hafta)
1. ✅ US EIA data loader oluştur
2. ✅ Multi-region training data hazırla
3. ✅ Model retraining (EIA data ile)

### Faz 3: Sector Benchmark İyileştirmeleri (1 hafta)
1. ✅ NAICS 6-digit eşleştirme
2. ✅ Corporate Environmental Impact entegrasyonu
3. ✅ Ember data entegrasyonu

### Faz 4: Transportation Emissions (1 hafta)
1. ✅ Vehicle Emission Calculator oluştur
2. ✅ Emission Calculator'a entegre et
3. ✅ Frontend UI ekle

### Faz 5: Anomaly Detection İyileştirmeleri (1 hafta)
1. ✅ NYC Building Data entegrasyonu
2. ✅ Building-level anomaly detection
3. ✅ Model retraining

---

## 🎯 BEKLENEN FAYDALAR

### 1. Model Performansı
- **Energy Prediction:** Weather features ile %10-15 daha iyi tahmin
- **Anomaly Detection:** Building-level data ile daha hassas tespit
- **Sector Benchmark:** Daha detaylı sektör eşleştirme

### 2. Kullanıcı Deneyimi
- **Real-time weather** bilgisi
- **Weather impact** görselleştirmesi
- **Transportation emissions** hesaplama
- **Daha detaylı sektör karşılaştırması**

### 3. Sistem Yetenekleri
- **Global weather coverage** (200+ countries)
- **Historical weather analysis**
- **Air quality integration**
- **Multi-region energy patterns**

---

## ⚠️ RİSKLER VE ÇÖZÜMLER

### Risk 1: OpenWeather API Rate Limiting
- **Çözüm:** Cache mekanizması + World Weather Repository fallback

### Risk 2: Büyük Veri Setleri (29MB+ CSV)
- **Çözüm:** Lazy loading, chunk processing, database storage

### Risk 3: Veri Güncelliği
- **Çözüm:** World Weather Repository günlük güncelleniyor, cron job ile sync

### Risk 4: API Key Güvenliği
- **Çözüm:** Environment variables, backend-only access

---

## 📝 SONUÇ

Bu plan, mevcut ECOLOGIA sistemine **25+ yeni veri setini** entegre etmek için kapsamlı bir yol haritası sunmaktadır. Öncelik **Weather Data Integration** ve **Energy Prediction Model İyileştirmeleri** üzerinedir.

**Sıradaki Adım:** Kullanıcı onayından sonra Faz 1 (Weather Integration) ile başlanacak.

---

**Not:** Bu plan sadece planlama amaçlıdır. Implementasyona geçilmeden önce kullanıcı onayı alınacaktır.

