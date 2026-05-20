# 🌿 ECOLOGIA

**AI-Powered Carbon Footprint Calculator & ESG Reporting Platform**

> **Proje kök dizini:** `ESG_project/`  
> Kurulum ve çalıştırma komutlarının tamamı bu klasörün içinden çalıştırılmalıdır.  
> (Üst klasör `Ecopulse_ESG/` yalnızca sarmalayıcıdır; GitHub reposu için `ESG_project/` içeriğini kök olarak kullanın.)

Bu depo, ECOLOGIA sürdürülebilirlik ve ESG platformunun teknik uygulamasını içerir.

---

## 📖 Proje Dokümantasyonu

Projenin stratejik vizyonu, pazar analizi, SWOT, yol haritası, bütçe planı ve iş modeli gibi **ayrıntılı bilgiler** için üst dizindeki analiz dokümanına bakın:

📄 **[Proje_Analizi.md](../Proje_Analizi.md)** — *EcoPulse: Kapsamlı Proje Analizi ve Strateji Dokümanı*

Bu dosya; problem tanımı, önerilen çözüm mimarisi, hedef kitle, SMART hedefler, riskler, KPI'lar ve gelecek yol haritası dahil olmak üzere projeyle ilgili kapsamlı ve ayrıntılı bilgiler sunar. Teknik kurulum ve API kullanımı için bu README'yi, ürün ve strateji detayları için **Proje_Analizi.md** dosyasını kullanın.

---



## 📋 İçindekiler

- [Proje Dokümantasyonu](#-proje-dokümantasyonu)
- [ECHO! Ekibi](#-echo-ekibi)
- [Kurulum](#kurulum)
- [Çalıştırma](#çalıştırma)
- [Proje Yapısı](#proje-yapısı)
- [API Endpoints](#api-endpoints)
- [Özellikler](#özellikler)
- [Teknolojiler](#teknolojiler)

---

##  Kurulum

### Gereksinimler
- Python 3.10+
- Node.js 18+
- npm veya yarn

### 1. Backend Kurulumu

```bash
cd backend
pip install -r requirements.txt
```

### 2. Frontend Kurulumu

```bash
cd frontend
npm install
```

### 3. Environment Variables

`backend/.env` dosyası oluşturun (backend bu dizinden çalıştırıldığında okunur):

```env
CLIMATIQ_API_KEY=your_climatiq_api_key
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
```

---

## ▶️ Çalıştırma

Tüm komutlar **proje kökünden** (`ESG_project/`) başlar.

### Backend (Port 8000)

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Alternatif:

```bash
cd backend
python run.py
```

### Frontend (Port 3000)

```bash
cd frontend
npm run dev
```

### Streamlit (opsiyonel legacy UI)

Proje kökünden:

```bash
streamlit run streamlit/esg_app.py
```

### Yardımcı scriptler

```bash
# Veri dosyalarını doğrula (GitHub klonundan sonra önerilir)
powershell -ExecutionPolicy Bypass -File scripts/setup_data.ps1

# Önbellek temizle
powershell -ExecutionPolicy Bypass -File scripts/clear_cache.ps1

# Veri analizi (data/summary.json kullanır)
python scripts/analyze_data.py
```

### Erişim

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 📁 Proje Yapısı

```
ESG_project/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # Ana uygulama
│   │   ├── config.py          # Ayarlar
│   │   ├── api/v1/            # API Endpoints
│   │   │   ├── emission.py    # Emisyon hesaplama
│   │   │   ├── report.py      # PDF rapor
│   │   │   ├── ai.py          # AI chat
│   │   │   ├── activity.py    # Aktivite DB
│   │   │   ├── analyzer.py    # ESG analiz & OCR
│   │   │   └── upload.py      # Dosya yükleme
│   │   ├── services/          # İş mantığı
│   │   │   ├── climatiq_service.py
│   │   │   ├── hybrid_calculator.py
│   │   │   ├── activity_database.py
│   │   │   ├── gemini_service.py
│   │   │   └── report_generator.py
│   │   └── models/
│   │       └── schemas.py     # Pydantic modeller
│   ├── requirements.txt
│   └── run.py
│
├── frontend/                   # Next.js Frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx       # Ana sayfa
│   │   │   ├── layout.tsx     # Root layout
│   │   │   └── globals.css    # Global stiller
│   │   ├── components/
│   │   │   ├── EmissionForm.tsx      # Veri giriş
│   │   │   ├── ResultsDisplay.tsx    # Sonuçlar
│   │   │   ├── ActivitySearch.tsx    # DB arama
│   │   │   ├── AIChat.tsx            # AI sohbet
│   │   │   ├── FileUpload.tsx        # Dosya yükle
│   │   │   ├── ReportGenerator.tsx   # PDF oluştur
│   │   │   ├── ReportHistory.tsx     # Rapor geçmişi
│   │   │   ├── MLDashboard.tsx       # ML paneli
│   │   │   ├── ESGAnalyzer.tsx       # ESG analiz
│   │   │   ├── InvoiceScanner.tsx    # Fatura tarama
│   │   │   └── HintPanel.tsx         # İpucu paneli
│   │   └── services/
│   │       └── api.ts         # API client
│   ├── package.json
│   └── tailwind.config.js
│
├── streamlit/                  # Streamlit uygulaması (legacy UI)
│   ├── esg_app.py             # Ana Streamlit uygulaması
│   ├── climatiq_calculator.py
│   ├── esg_report_generator.py
│   ├── activity_database.py
│   ├── hybrid_calculator.py
│   ├── data_extractor.py
│   ├── esg_analyzer_hf.py
│   └── external_data_sources.py
│
├── modeller/                   # ML modelleri ve eğitim
│   ├── api/                   # ML API route'ları
│   ├── models/                # Anomali, tahmin, benchmark vb.
│   ├── services/              # Hava durumu servisleri
│   ├── outputs/               # Eğitilmiş model çıktıları
│   └── requirements.txt
│
├── data/                       # Emisyon faktörü verileri (tüm JSON burada)
│   ├── scope1_data.json       # Zorunlu
│   ├── scope2_data.json       # Zorunlu
│   ├── summary.json           # Zorunlu
│   ├── emission_data_input.json
│   └── scope3_data.json       # Opsiyonel (yoksa Scope 3 listesi boş kalır)
│
├── scripts/                    # Yardımcı scriptler
│   ├── setup_data.ps1         # Veri doğrulama / eski kök JSON temizliği
│   ├── clear_cache.ps1        # Önbellek temizleme
│   ├── analyze_data.py
│   └── emission_calculator.py
│
├── docs/                       # Geliştirme planları ve dokümantasyon
│   ├── DURUM_VE_GELISTIRME_PLANI.md
│   ├── GELISTIRME_PLANI.md
│   ├── GELISTIRME_TAMAMLANDI.md
│   ├── ESG_REPORT_ENHANCEMENT_PLAN.md
│   ├── REPORT_STREAMING_PLAN.md
│   └── MODEL_KULLANIMI.md
│
├── test/                       # Test verileri ve örnek faturalar
├── output/                     # Oluşturulan PDF raporlar (API çıktısı)
├── legacy/                     # Kullanılmayan / arşiv dosyalar
│   └── activity_database.py   # Eski backend kopyası
│
├── CHANGELOG.md
└── README.md                  # Bu dosya
```

> **Veri notu:** Backend ve Streamlit `data/` klasöründen okur. GitHub klonundan sonra `scripts/setup_data.ps1` çalıştırın. `scope3_data.json` isteğe bağlıdır; yoksa uygulama Scope 1 ve 2 ile çalışmaya devam eder.

---

## 🔌 API Endpoints

Tam liste: http://localhost:8000/docs

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/api/v1/emission/calculate` | POST | Emisyon hesapla |
| `/api/v1/emission/sources` | GET | Veri kaynakları |
| `/api/v1/report/generate` | POST | PDF rapor oluştur |
| `/api/v1/report/generate-stream` | POST | Akışlı PDF rapor |
| `/api/v1/report/list` | GET | Rapor listesi |
| `/api/v1/report/download/{filename}` | GET | Rapor indir |
| `/api/v1/ai/chat` | POST | AI sohbet |
| `/api/v1/activity/search` | GET | Aktivite ara |
| `/api/v1/activity/popular` | GET | Popüler aktiviteler |
| `/api/v1/upload/parse` | POST | Dosya parse |
| `/api/v1/upload/extract-emissions` | POST | Emisyon çıkar |
| `/api/v1/analyzer/text` | POST | Metin ESG analizi |
| `/api/v1/analyzer/pdf` | POST | PDF ESG analizi |
| `/api/v1/analyzer/invoice` | POST | Fatura analizi |
| `/api/v1/ml/forecast` | POST | Enerji tahmini (ML) |
| `/api/v1/ml/anomaly` | POST | Anomali tespiti (ML) |
| `/api/v1/ml/benchmark` | POST | Sektör kıyaslaması (ML) |

---

## ✨ Özellikler

### 📝 Emisyon Hesaplama
- Elektrik, Doğalgaz, Dizel, Benzin, LPG, Kömür
- Su ve Atık tüketimi
- Araç ve Uçak yolculuğu
- 277,000+ emisyon faktörü

### 📊 Sonuç Görüntüleme
- Scope 1, 2, 3 dağılımı
- Bar chart görselleştirme
- JSON/CSV export

### 🔍 Aktivite Veritabanı
- Arama ve filtreleme
- Otomatik tamamlama
- Calculator'a aktarma

### 📄 PDF Rapor
- GRI 305 uyumlu
- Şirket bilgileri
- Profesyonel format

### 🤖 AI Asistan
- Gemini entegrasyonu
- ESG uzmanlığı
- Örnek sorular

### 📎 Dosya Yükleme
- CSV/Excel desteği
- Otomatik sütun algılama
- Toplu hesaplama

---

## 🛠️ Teknolojiler

### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Framer Motion
- Axios

### Backend
- FastAPI
- Python 3.10
- Pydantic
- ReportLab (PDF)
- Pandas

### External APIs
- Climatiq API (emisyon faktörleri)
- Google Gemini (AI chat)
- Data.gov EPA (fallback)

---

## 📊 Standartlar

- GHG Protocol
- GRI 305
- TCFD
- CDP

---

## 📄 Lisans

Bu proje özel kullanım içindir.

---

**© 2025 ECOLOGIA — ESG Carbon Calculator**  
## 👥 ECHO! Ekibi

Bu proje **ECHO!** ekibi tarafından geliştirilmiştir.

| Üye |
|-----|
| ESRA ÇEVİK |
| İBRAHİM KUTAY ŞAHİN |
| HAZAL PARLAK |
| FATİH KADİM |
| EMİR KAYA |

---
