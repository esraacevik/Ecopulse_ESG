# 🚀 Geliştirme Planı - Detaylı

## 📊 Mevcut Durum Analizi

### ✅ Tamamlananlar
- ESG rapor oluşturma sistemi (AI destekli, streaming)
- Enerji tahmin modeli eğitimi (weather features ile)
- Model checkpoint sistemi
- Frontend timeout ve error handling iyileştirmeleri

### ❌ Eksikler
1. **Model Entegrasyonu**: API her seferinde yeni model eğitiyor, checkpoint kullanmıyor
2. **Rapor Geçmişi**: Oluşturulan raporlar listelenemiyor
3. **Frontend Model Entegrasyonu**: MLDashboard gerçek model tahminlerini göstermiyor
4. **Dashboard Analytics**: Daha fazla görselleştirme ve trend analizi gerekiyor

---

## 🎯 Geliştirme Öncelikleri

### 1️⃣ Model Entegrasyonu (Öncelik: YÜKSEK)
**Durum**: `/api/v1/ml/forecast` endpoint'i her çağrıda yeni model eğitiyor  
**Hedef**: Eğitilmiş checkpoint'ten model yükle, sadece tahmin yap

**Yapılacaklar**:
- [ ] `ml_routes.py` içinde `get_energy_predictor()` fonksiyonunu güncelle
- [ ] Checkpoint'ten model yükleme mantığı ekle
- [ ] Model zaten eğitilmişse tekrar eğitme
- [ ] Model yoksa veya güncel değilse eğit
- [ ] Model cache mekanizması ekle (singleton pattern)

**Dosyalar**:
- `ecologia/modeller/api/ml_routes.py`
- `ecologia/modeller/models/energy_prediction/predictor.py`

**Tahmini Süre**: 2-3 saat

---

### 2️⃣ Rapor Geçmişi Sistemi (Öncelik: ORTA)
**Durum**: Raporlar `ecologia/output/` klasöründe ama liste yok  
**Hedef**: Raporları listele, tekrar indir, sil, filtrele

**Yapılacaklar**:
- [ ] Backend: `/api/v1/report/list` endpoint'i ekle
- [ ] Backend: `/api/v1/report/delete/{filename}` endpoint'i ekle
- [ ] Backend: Rapor metadata'sı (tarih, şirket, dönem) sakla (JSON dosyası)
- [ ] Frontend: Rapor geçmişi sayfası/component'i ekle
- [ ] Frontend: Rapor listesi, arama, filtreleme
- [ ] Frontend: Rapor silme ve indirme butonları

**Dosyalar**:
- `ecologia/backend/app/api/v1/report.py` (yeni endpoint'ler)
- `ecologia/frontend/src/components/ReportHistory.tsx` (yeni component)
- `ecologia/frontend/src/services/api.ts` (yeni API çağrıları)
- `ecologia/frontend/src/app/page.tsx` (yeni tab/sayfa)

**Tahmini Süre**: 4-5 saat

---

### 3️⃣ Frontend Model Entegrasyonu (Öncelik: ORTA)
**Durum**: MLDashboard var ama gerçek model tahminlerini göstermiyor  
**Hedef**: Gerçek veri ile model tahminlerini göster

**Yapılacaklar**:
- [ ] MLDashboard'a gerçek veri yükleme özelliği ekle
- [ ] Model tahmin endpoint'ini çağır
- [ ] Tahmin sonuçlarını görselleştir (grafik)
- [ ] Gerçek vs. tahmin karşılaştırması göster
- [ ] Model performans metrikleri göster (MAE, RMSE, R²)

**Dosyalar**:
- `ecologia/frontend/src/components/MLDashboard.tsx`
- `ecologia/frontend/src/services/api.ts` (forecast endpoint)

**Tahmini Süre**: 3-4 saat

---

### 4️⃣ Dashboard Analytics İyileştirmeleri (Öncelik: DÜŞÜK)
**Durum**: Temel analytics var  
**Hedef**: Daha fazla görselleştirme, trend analizi, karşılaştırmalar

**Yapılacaklar**:
- [ ] Scope bazlı trend grafikleri (aylık/yıllık)
- [ ] Kategori bazlı emisyon dağılımı (pie chart)
- [ ] Yıllık karşılaştırma (önümüzdeki yıl vs. geçen yıl)
- [ ] Hedef vs. gerçekleşen karşılaştırması
- [ ] Export özelliği (CSV, Excel)

**Dosyalar**:
- `ecologia/frontend/src/components/MLDashboard.tsx`
- `ecologia/frontend/src/components/ResultsDisplay.tsx`

**Tahmini Süre**: 4-5 saat

---

## 📋 Detaylı İmplementasyon Planı

### Faz 1: Model Entegrasyonu (1. Öncelik)

#### Adım 1.1: Checkpoint Yükleme Fonksiyonu
```python
# ml_routes.py içinde
def load_trained_model(location: str = "Istanbul,TR") -> Optional[EnergyPredictor]:
    """Eğitilmiş modeli checkpoint'ten yükle"""
    checkpoint_dir = Path(__file__).parent.parent / "checkpoints" / "weather_training"
    model_checkpoint = checkpoint_dir / "model_checkpoint.json"
    
    if not model_checkpoint.exists():
        return None
    
    # Checkpoint'ten yükle
    predictor = EnergyPredictor(...)
    predictor.load_from_checkpoint(checkpoint_dir)
    return predictor
```

#### Adım 1.2: Forecast Endpoint Güncelleme
```python
@router.post("/forecast")
async def generate_forecast(request: ForecastRequest):
    # Önce checkpoint'ten yükle
    predictor = load_trained_model(request.location)
    
    if predictor and predictor.is_trained:
        # Sadece tahmin yap
        forecast = predictor.predict(future_hours=request.future_hours)
    else:
        # Model yoksa eğit (fallback)
        predictor = get_energy_predictor(...)
        predictor.train(...)
        forecast = predictor.predict(...)
```

---

### Faz 2: Rapor Geçmişi Sistemi

#### Adım 2.1: Backend Metadata Sistemi
```python
# report.py içinde
REPORTS_METADATA_FILE = Path("ecologia/output/reports_metadata.json")

def save_report_metadata(filename: str, company_name: str, period: str):
    """Rapor metadata'sını kaydet"""
    metadata = {
        "filename": filename,
        "company_name": company_name,
        "period": period,
        "created_at": datetime.now().isoformat(),
        "file_size": os.path.getsize(filepath)
    }
    # JSON'a ekle
```

#### Adım 2.2: List Endpoint
```python
@router.get("/report/list")
async def list_reports():
    """Oluşturulan raporları listele"""
    output_dir = Path("ecologia/output")
    reports = []
    
    for pdf_file in output_dir.glob("*.pdf"):
        # Metadata'dan bilgileri al
        reports.append({...})
    
    return {"reports": reports}
```

#### Adım 2.3: Frontend Component
```typescript
// ReportHistory.tsx
export default function ReportHistory() {
  const [reports, setReports] = useState([])
  
  useEffect(() => {
    reportAPI.list().then(setReports)
  }, [])
  
  return (
    <div>
      {/* Rapor listesi */}
      {/* Arama, filtreleme */}
      {/* Silme, indirme butonları */}
    </div>
  )
}
```

---

### Faz 3: Frontend Model Entegrasyonu

#### Adım 3.1: MLDashboard Güncelleme
```typescript
// MLDashboard.tsx içinde
const [forecastData, setForecastData] = useState(null)

const handleForecast = async () => {
  const response = await mlAPI.forecast({
    data: historicalData,
    location: "Istanbul,TR",
    future_hours: 24,
    include_weather: true
  })
  setForecastData(response.predictions)
}
```

#### Adım 3.2: Görselleştirme
- Recharts veya Chart.js ile grafik
- Gerçek vs. tahmin karşılaştırması
- Hata metrikleri gösterimi

---

## 🎯 Önerilen Sıralama

1. **Model Entegrasyonu** (1-2 gün)
   - En kritik, performansı doğrudan etkiliyor
   - Kullanıcı deneyimini iyileştiriyor

2. **Rapor Geçmişi** (2-3 gün)
   - Kullanışlı özellik
   - Kullanıcıların raporları tekrar bulmasını sağlıyor

3. **Frontend Model Entegrasyonu** (1-2 gün)
   - MLDashboard'u daha işlevsel hale getiriyor
   - Model tahminlerini görselleştiriyor

4. **Dashboard Analytics** (2-3 gün)
   - Nice-to-have özellikler
   - Daha sonra da yapılabilir

---

## 📝 Notlar

- Model checkpoint yolu: `ecologia/modeller/checkpoints/weather_training/`
- Rapor output yolu: `ecologia/output/`
- Model eğitimi yaklaşık 3.1M satır veri ile yapıldı
- Weather features aktif (Istanbul,TR için)

---

## ✅ Başlangıç

Hangi fazdan başlamak istersin? Önerim: **Faz 1 (Model Entegrasyonu)** - en kritik ve hızlı sonuç veren.

