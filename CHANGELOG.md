# 📝 Changelog - ESG Carbon Calculator

## [v2.0.0] - 20 Aralık 2025

### 🎉 Yeni Özellikler

#### 🤖 Groq LLM Entegrasyonu
- **Tamamen ücretsiz AI asistan** eklendi (Groq API)
- Mixtral-8x7B modeli ile güçlendirilmiş ESG soru-cevap
- Mükemmel Türkçe destek
- Saniyeler içinde yanıt
- 14,400 ücretsiz istek/gün limiti

**Dosyalar:**
- ✅ `rag_system_groq.py` - Yeni Groq LLM wrapper
- ✅ `GROQ_SETUP.md` - Detaylı kurulum kılavuzu
- ✅ `requirements_minimal.txt` - Groq paketi eklendi

#### 📱 Streamlit App Güncellemeleri
- AI asistan otomatik Groq/Simple mod seçimi
- Groq aktif olduğunda UI bilgilendirmesi
- Fallback mekanizması (Groq yoksa keyword matching)

**Değişiklikler:**
- ✅ `esg_app.py` - Akıllı RAG seçimi eklendi
- ✅ `.env` - GROQ_API_KEY placeholder eklendi

---

## [v1.1.0] - 19 Aralık 2025

### ✨ Tamamlanan Özellikler

#### 📊 CO2e Hesaplama Sayfası
- Climatiq API entegrasyonu tamamlandı
- Batch hesaplama desteği
- Scope bazlı özet tablolar
- Detaylı sonuç gösterimi

#### 📄 ESG Raporu Sayfası
- GRI 305 uyumlu PDF raporları
- Pie chart ile scope dağılımı
- Şirket bilgileri ve metodoloji
- Download butonu

**Dosyalar:**
- ✅ `esg_report_generator.py` - PDF oluşturucu
- ✅ `climatiq_calculator.py` - API wrapper

---

## [v1.0.0] - 18 Aralık 2025

### 🚀 İlk Versiyon

#### Ana Özellikler
- Streamlit multi-page uygulaması
- Climatiq API entegrasyonu (elektrik)
- Basit AI asistan (keyword matching)
- PDF rapor oluşturma
- Veri girişi ve kaydetme

**Dosyalar:**
- ✅ `esg_app.py` - Ana uygulama
- ✅ `rag_system_simple.py` - Basit asistan
- ✅ `requirements_minimal.txt` - Minimal paketler
- ✅ `requirements_streamlit.txt` - Tam paketler

#### Dokümantasyon
- ✅ `README.md` - Proje açıklaması
- ✅ `INSTALL.md` - Kurulum kılavuzu
- ✅ `QUICKSTART.md` - Hızlı başlangıç
- ✅ `ENHANCEMENT_ROADMAP.md` - Geliştirme planı

---

## 🔄 Karşılaştırma: v1.0 → v2.0

| Özellik | v1.0 | v2.0 |
|---------|------|------|
| **AI Asistan** | Keyword matching | Groq LLM (Mixtral-8x7B) ⭐ |
| **Türkçe Kalitesi** | Basit | Mükemmel |
| **Yanıt Hızı** | Anında | 1-2 saniye |
| **Maliyet** | Ücretsiz | Ücretsiz |
| **Kurulum** | Kolay | Çok kolay |
| **Akıllı Cevaplar** | ❌ | ✅ |

---

## 📅 Planlanan Özellikler

### v2.1.0 (Gelecek)
- [ ] Tüm activity ID'leri (ulaşım, doğalgaz, vb.)
- [ ] Hesaplama sonuçları ile bağlamlı AI sorguları
- [ ] Sohbet geçmişi kaydetme

### v2.2.0
- [ ] Interaktif Plotly dashboardları
- [ ] Zaman serisi analizi
- [ ] Benchmark karşılaştırma

### v3.0.0
- [ ] SQLite veritabanı
- [ ] Multi-user desteği
- [ ] Excel/CSV import
- [ ] Streamlit Cloud deployment

---

## 🐛 Bilinen Sorunlar

### v2.0.0
- ⚠️ Sadece elektrik hesaplamaları çalışıyor
- ⚠️ Araç ve uçak için activity ID'ler güncellenmeli
- ⚠️ Doğalgaz hesaplaması test edilmeli

### v1.x
- ⚠️ ChromaDB kurulum sorunu (Windows C++ compiler)
  - **Çözüm:** FAISS kullanın veya Groq'a geçin

---

## 🔧 Teknik Değişiklikler

### Yeni Bağımlılıklar
```bash
# v2.0.0
groq==0.4.1  # Groq API client
```

### API Entegrasyonları
```
v1.0: Climatiq API
v2.0: Climatiq API + Groq API ⭐
```

### Dosya Yapısı
```
v1.0: 8 Python dosyası, 4 dokümantasyon
v2.0: 9 Python dosyası, 6 dokümantasyon (+GROQ_SETUP.md, +CHANGELOG.md)
```

---

## 📊 İstatistikler

### Kod Metrikleri
- **Toplam satır:** ~2,500+ (Python)
- **Dosya sayısı:** 15+
- **API entegrasyonu:** 2 (Climatiq, Groq)
- **Dokümantasyon:** 6 dosya

### Özellik Kapsamı
- ✅ Veri girişi: %100
- ✅ Hesaplama: %30 (sadece elektrik)
- ✅ PDF rapor: %100
- ✅ AI asistan: %100 ⭐ (v2.0'da tamamlandı)

---

## 🙏 Teşekkürler

**Kullanılan Teknolojiler:**
- [Streamlit](https://streamlit.io/) - Web framework
- [Climatiq](https://climatiq.io/) - Emission factor database
- [Groq](https://groq.com/) - LLM inference ⭐ YENİ
- [ReportLab](https://reportlab.com/) - PDF generation

**Açık Kaynak Toplulukları:**
- Python paketi geliştiricileri
- ESG ve sürdürülebilirlik topluluğu
- Groq Discord topluluğu

---

## 📝 Notlar

### Groq Neden Seçildi?

**Alternatifler değerlendirmesi:**
1. ❌ OpenAI GPT-3.5 - Ücretli (~$1-5/ay)
2. ❌ HuggingFace Local - Kurulum zor, GPU gerekir
3. ❌ Claude API - Ücretli
4. ✅ **Groq API** - Ücretsiz, hızlı, kolay kurulum

**Karar kriterleri:**
- Maliyet: Ücretsiz olmalı
- Türkçe: Mükemmel destek
- Hız: Hızlı yanıt
- Kurulum: Kolay

**Groq kazandı!** 🏆

---

## 🔮 Gelecek Vizyonu

**Hedef:** Türkiye'nin en iyi ücretsiz ESG karbon hesaplama platformu

**Kilometre Taşları:**
- ✅ v1.0 - Temel özellikler (Aralık 2025)
- ✅ v2.0 - AI entegrasyonu (Aralık 2025)
- 🔜 v2.5 - Tam hesaplama desteği (Ocak 2026)
- 🔜 v3.0 - Production deployment (Şubat 2026)

---

**Son güncelleme:** 20 Aralık 2025
