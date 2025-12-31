# 🤖 Eğitilmiş Model Kullanımı - Detaylı Açıklama

## 📍 Model Nerede Kullanılıyor?

### 1. **Backend API Endpoint'i**
**Dosya**: `ecologia/modeller/api/ml_routes.py`

**Endpoint**: `/api/v1/ml/forecast`

**Nasıl Çalışıyor**:
1. `get_energy_predictor()` fonksiyonu çağrılıyor
2. Önce `load_trained_model()` ile checkpoint'ten model yüklenmeye çalışılıyor
3. Model bulunursa direkt kullanılıyor (eğitim yapılmıyor)
4. Model yoksa veya veri uyumsuzsa yeni eğitim yapılıyor

**Kod Akışı**:
```python
# ml_routes.py - get_energy_predictor()
predictor = load_trained_model(location, include_weather)
if predictor is None:
    # Model yoksa yeni oluştur
    predictor = EnergyPredictor(...)

# ml_routes.py - /forecast endpoint
if predictor.is_trained:
    # Eğitilmiş model varsa direkt tahmin yap
    forecast = predictor.predict(future_hours=request.future_hours)
else:
    # Model yoksa önce eğit
    predictor.train(df, ...)
    forecast = predictor.predict(...)
```

### 2. **Model Yükleme Yolları**

#### A) Final Model (Öncelikli)
**Yol**: `ecologia/modeller/outputs/models/weather_energy_model/`

**Dosyalar**:
- `config.json` - Model konfigürasyonu ve feature listesi
- `model.pkl` - Eğitilmiş XGBoost modeli

**Nasıl Yükleniyor**:
```python
predictor = EnergyPredictor(...)
predictor.load(model_path)  # config.json ve model.pkl'ı yükler
```

#### B) Checkpoint (Yedek)
**Yol**: `ecologia/modeller/checkpoints/weather_training/`

**Dosyalar**:
- `model_checkpoint.json` - XGBoost Booster modeli
- `training_state.json` - Eğitim durumu ve feature listesi

**Nasıl Yükleniyor**:
```python
bst = xgb.Booster()
bst.load_model(str(model_checkpoint))
predictor.model.model._Booster = bst
```

### 3. **Frontend Kullanımı**

**Dosya**: `ecologia/frontend/src/components/MLDashboard.tsx`

**Component**: `EnergyForecast`

**Nasıl Çalışıyor**:
1. Kullanıcı CSV formatında geçmiş veri giriyor
2. "Tahmin Oluştur" butonuna basıyor
3. Frontend `mlAPI.forecast()` çağrısı yapıyor
4. Backend eğitilmiş modeli yüklüyor (checkpoint'ten)
5. Tahmin yapılıyor ve sonuçlar gösteriliyor

**Kod Akışı**:
```typescript
// MLDashboard.tsx - EnergyForecast component
const response = await mlAPI.forecast({
  data: parsedData,  // CSV'den parse edilmiş veri
  location: "Istanbul,TR",
  future_hours: 24,
  include_weather: true
})

// Sonuçlar görselleştiriliyor
setForecast(response)
```

### 4. **Model Özellikleri**

**Eğitildiği Veri**:
- 3.1M satır enerji tüketim verisi
- Weather features dahil (Istanbul,TR için)
- 67 feature (temporal, lag, rolling, weather)

**Model Tipi**: XGBoost Regressor

**Checkpoint Durumu**:
- ✅ Model eğitildi ve kaydedildi
- ✅ Checkpoint'ler oluşturuldu
- ✅ Final model kaydedildi

## 🔄 Model Kullanım Akışı

```
1. Kullanıcı Frontend'de tahmin isteği yapar
   ↓
2. Frontend → Backend API'ye istek gönderir
   POST /api/v1/ml/forecast
   ↓
3. Backend get_energy_predictor() çağırır
   ↓
4. load_trained_model() checkpoint'ten yüklemeyi dener
   ├─ Final model varsa → Yükle (outputs/models/)
   ├─ Checkpoint varsa → Yükle (checkpoints/)
   └─ Yoksa → Yeni oluştur
   ↓
5. Model.is_trained == True ise
   ├─ Direkt tahmin yap
   └─ Sonuçları döndür
   ↓
6. Frontend sonuçları görselleştirir
```

## 📊 Model Performansı

**Eğitim Metrikleri** (checkpoint'ten):
- Feature sayısı: 67
- Eğitim verisi: 3.1M satır
- Weather features: Aktif
- Model tipi: XGBoost

**Kullanım Senaryoları**:
1. ✅ Enerji tüketimi tahmini (24 saat, 1 hafta, 1 ay)
2. ✅ Weather features ile daha doğru tahmin
3. ✅ Geçmiş veriye dayalı gelecek tahmini

## 🎯 Özet

**Model Nerede Kullanılıyor?**
- ✅ Backend: `/api/v1/ml/forecast` endpoint'i
- ✅ Frontend: ML Dashboard → Tüketim Tahmini sekmesi
- ✅ Model checkpoint'ten otomatik yükleniyor
- ✅ Her seferinde eğitilmiyor (performans için)

**Model Dosyaları**:
- Final model: `ecologia/modeller/outputs/models/weather_energy_model/`
- Checkpoint: `ecologia/modeller/checkpoints/weather_training/`

**Kullanım**:
1. Frontend'de CSV veri gir
2. Tahmin oluştur butonuna bas
3. Model otomatik yüklenir ve tahmin yapar

