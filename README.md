# 🌿 ECOLOGIA

**AI-Powered Carbon Footprint Calculator & ESG Reporting Platform**

---

## 📋 İçindekiler

- [Kurulum](#kurulum)
- [Çalıştırma](#çalıştırma)
- [Proje Yapısı](#proje-yapısı)
- [API Endpoints](#api-endpoints)
- [Özellikler](#özellikler)
- [Teknolojiler](#teknolojiler)

---

## 🚀 Kurulum

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

Backend için `.env` dosyası oluşturun:

```env
CLIMATIQ_API_KEY=your_climatiq_api_key
GEMINI_API_KEY=your_gemini_api_key
```

---

## ▶️ Çalıştırma

### Backend (Port 8000)

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Port 3000)

```bash
cd frontend
npm run dev
```

### Erişim

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 📁 Proje Yapısı

```
ecologia/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # Ana uygulama
│   │   ├── config.py          # Ayarlar
│   │   ├── api/v1/            # API Endpoints
│   │   │   ├── emission.py    # Emisyon hesaplama
│   │   │   ├── report.py      # PDF rapor
│   │   │   ├── ai.py          # AI chat
│   │   │   ├── activity.py    # Aktivite DB
│   │   │   └── upload.py      # Dosya yükleme
│   │   ├── services/          # İş mantığı
│   │   │   ├── climatiq_service.py
│   │   │   ├── hybrid_calculator.py
│   │   │   ├── gemini_service.py
│   │   │   └── report_generator.py
│   │   └── models/
│   │       └── schemas.py     # Pydantic modelleri
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
│   │   │   └── ReportGenerator.tsx   # PDF oluştur
│   │   └── services/
│   │       └── api.ts         # API client
│   ├── package.json
│   └── tailwind.config.js
│
├── scope1_data.json           # Scope 1 emission factors
├── scope2_data.json           # Scope 2 emission factors
├── scope3_data.json           # Scope 3 emission factors
├── test_upload_*.csv          # Test dosyaları
├── esg_report_*.pdf           # Örnek raporlar
├── MIGRATION_STATUS.md        # Geçiş durumu
└── README.md                  # Bu dosya
```

---

## 🔌 API Endpoints

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/api/v1/emission/calculate` | POST | Emisyon hesapla |
| `/api/v1/report/generate` | POST | PDF rapor oluştur |
| `/api/v1/ai/chat` | POST | AI sohbet |
| `/api/v1/activity/search` | GET | Aktivite ara |
| `/api/v1/upload/parse` | POST | Dosya parse |
| `/api/v1/upload/extract-emissions` | POST | Emisyon çıkar |

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

**© 2025 ECOLOGIA - ESG Carbon Calculator**
