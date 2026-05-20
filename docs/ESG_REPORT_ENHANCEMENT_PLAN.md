# 📊 ESG Rapor Geliştirme Planı

## 🎯 Mevcut Durum Analizi

### Sorunlar:
1. **Statik İçerik**: Raporlar çok standart, açıklama yok
2. **Kısa Metinler**: Yönetici özeti 3-4 cümle, metodoloji çok basit
3. **Analiz Eksikliği**: Veriler var ama yorum/analiz yok
4. **Görselleştirme**: Sadece pasta grafiği
5. **Tema/Şema Yok**: Standart PDF formatı, profesyonel görünüm yok
6. **AI Kullanımı Yok**: Gemini var ama rapor üretiminde kullanılmıyor

### Mevcut Sistem:
- ReportLab ile PDF oluşturma
- Gemini API entegre (sadece chat için)
- ML sonuçları ekleniyor ama açıklanmıyor
- Basit tablolar ve grafikler

---

## 🤖 API Seçimi: Gemini vs Ollama/DeepSeek

### **ÖNERİ: Gemini API (Mevcut)**

**Neden Gemini?**
- ✅ Zaten entegre, ekstra setup yok
- ✅ Ücretsiz tier yeterli (60 RPM)
- ✅ Türkçe desteği mükemmel
- ✅ Uzun context (1M token)
- ✅ Rapor kalitesi yüksek
- ✅ API stabilitesi iyi

**Ollama/DeepSeek-R1-8B Alternatifi:**
- ❌ Local setup gerekiyor
- ❌ Türkçe kalitesi belirsiz
- ❌ Context window küçük (8B model)
- ✅ Ücretsiz, offline çalışır
- ✅ API limit yok

**Karar:** Gemini kullan, Ollama'yı fallback olarak ekle

---

## 📋 Geliştirme Planı - PROFESYONEL ESG RAPOR FORMATI

### **HEDEF: 10-15 Sayfa, Gerçek ESG Rapor Formatı**

---

### **FAZE 1: AI İçerik Üretimi (Detaylı & Uzun)**

#### 1.1 Yönetici Özeti Geliştirme
- **Mevcut:** 3-4 cümle statik metin
- **Yeni:** 
  - Gemini ile dinamik, detaylı özet (**800-1200 kelime, 2-3 sayfa**)
  - Şirket performansı kapsamlı analizi
  - Scope bazında detaylı yorumlar ve karşılaştırmalar
  - Trend analizi (varsa önceki dönem) + grafik
  - Öncelikli aksiyon önerileri (detaylı, ROI ile)
  - KPI dashboard (büyük sayılar, görsel kartlar)
  - Stratejik öneriler ve yol haritası özeti

#### 1.2 Metodoloji Detaylandırma
- **Mevcut:** 6 madde, kısa açıklamalar
- **Yeni:**
  - Her metodoloji bölümü için **400-600 kelime açıklama**
  - Kullanılan standartların detaylı açıklaması (GRI, GHG Protocol, ISO 14064)
  - Veri kalitesi değerlendirmesi (skor, güvenilirlik)
  - Belirsizlik analizi (istatistiksel)
  - Sınırlamalar ve varsayımlar (detaylı liste)
  - Hesaplama metodolojisi (formüller, örnekler)
  - **Toplam: 2-3 sayfa metodoloji**

#### 1.3 Analiz Bölümleri Ekleme (Kapsamlı)
- **Yeni Bölümler:**
  - **Performans Analizi** (2-3 sayfa): 
    - Scope bazında detaylı yorum (her scope için 500-700 kelime)
    - Trend analizi ve grafikler
    - Kritik aktivite analizi (top 10 aktivite)
    - Kategori bazında karşılaştırma
    - Yıllık karşılaştırma (varsa)
  
  - **Kritik Aktivite Analizi** (1-2 sayfa):
    - En yüksek emisyonlu 10 aktivite
    - Her aktivite için detaylı açıklama (AI ile)
    - İyileştirme potansiyeli analizi
    - ROI tahminleri
  
  - **İyileştirme Önerileri** (2-3 sayfa):
    - AI ile önerilen 8-12 aksiyon
    - Her aksiyon için: açıklama, ROI, uygulama süresi, öncelik
    - Uygulama planı (timeline)
    - Yatırım gereksinimleri
    - Beklenen emisyon azaltımı
  
  - **Risk ve Fırsatlar** (1-2 sayfa):
    - ESG risk analizi (kategorize edilmiş)
    - Fırsat değerlendirmesi
    - Stratejik öneriler
    - Regülasyon uyumluluğu
  
  - **Benchmark Yorumu** (1 sayfa):
    - ML benchmark sonuçlarının detaylı açıklaması
    - Sektör karşılaştırması görselleştirmesi
    - Performans değerlendirmesi
  
  - **Net Zero Yol Haritası** (1-2 sayfa):
    - ML target sonuçlarının stratejik analizi
    - Timeline görselleştirmesi
    - Milestone açıklamaları
    - Yatırım planı

#### 1.4 AI Prompt Stratejisi
```python
# Her bölüm için özel prompt'lar:
- Executive Summary: Şirket performansı, öncelikler, öneriler
- Methodology: Teknik detaylar, standartlar, kalite
- Analysis: Veri yorumu, trend, benchmark
- Recommendations: Aksiyon planı, ROI, öncelikler
```

---

### **FAZE 2: Tema ve Şema Tasarımı**

#### 2.1 Profesyonel Tema
- **Renk Paleti:**
  - Ana: #2E7D32 (Forest Green) - mevcut
  - İkincil: #66BB6A, #A5D6A7
  - Vurgu: #1B5E20 (Dark Green)
  - Metin: #212121 (Dark Gray)
  - Arka Plan: #FAFAFA (Light Gray)

#### 2.2 Sayfa Düzeni
- **Kapak Sayfası:**
  - Logo alanı (şirket logosu)
  - Modern tipografi
  - Görsel elementler (yeşil gradient)
  - QR kod (dijital rapor linki)

- **İç Sayfalar:**
  - Header/Footer (sayfa numarası, tarih)
  - Sidebar (içindekiler, navigasyon)
  - Bölüm başlıkları (büyük, vurgulu)
  - Alt başlıklar (hierarşik yapı)

#### 2.3 Görselleştirme İyileştirmeleri (KAPSAMLI)

**Grafik Türleri (Toplam 12-15 grafik):**

1. **Scope Dağılımı Grafikleri:**
   - Pasta grafiği (mevcut, iyileştirilecek)
   - Stacked bar chart (scope x kategori)
   - Donut chart (scope + kategori kombinasyonu)

2. **Trend Analizi:**
   - Line chart (zaman serisi, scope bazında)
   - Area chart (kümülatif emisyon)
   - Yıllık karşılaştırma bar chart

3. **Aktivite Analizi:**
   - Horizontal bar chart (top 10 aktivite)
   - Treemap (aktivite x scope x kategori)
   - Sankey diagram (aktivite → scope → kategori akışı)

4. **Benchmark & Karşılaştırma:**
   - Radar chart (çok boyutlu performans)
   - Box plot (sektör dağılımı)
   - Violin plot (yoğunluk analizi)
   - Benchmark karşılaştırma bar chart

5. **Net Zero Yol Haritası:**
   - Gantt chart (timeline)
   - Waterfall chart (azaltım planı)
   - Progress gauge (hedef ilerleme)

6. **Heatmap & Matris:**
   - Heatmap (aktivite x scope)
   - Correlation matrix (kategori ilişkileri)

**İnfografikler:**
- KPI kartları (4-6 adet, büyük sayılar, ikonlar, renkli)
- Progress bar'lar (hedef ilerleme, % gösterimi)
- Icon'lar (her scope için, modern tasarım)
- Badge'ler (GRI uyumluluk, sertifikalar)
- Timeline (net zero milestones)

**Görselleştirme Kütüphaneleri:**
- Matplotlib (mevcut, temel grafikler)
- Seaborn (istatistiksel grafikler, heatmap)
- Plotly (interaktif grafikler → PNG export)

---

### **FAZE 3: İçerik Yapısı Genişletme**

#### 3.1 Rapor Yapısı (10-15 Sayfa, Detaylı)

**Sayfa Dağılımı:**

1. **Kapak Sayfası** (1 sayfa)
   - Profesyonel tasarım
   - Logo, şirket bilgileri
   - Raporlama dönemi
   - GRI uyumluluk badge
   - QR kod

2. **İçindekiler** (1 sayfa)
   - Tüm bölümler
   - Sayfa numaraları
   - Grafik listesi

3. **Yönetici Özeti** (2-3 sayfa) ⭐ GENİŞLETİLECEK
   - AI ile üretilmiş detaylı özet (800-1200 kelime)
   - KPI dashboard (4-6 kart, görsel)
   - Öncelikli aksiyonlar özeti
   - Stratejik öneriler
   - **Grafikler:** Scope dağılımı (pasta), KPI kartları

4. **Emisyon Özeti** (2 sayfa)
   - Scope tablosu (detaylı, renkli)
   - Scope dağılımı grafikleri (pasta + donut)
   - Kategori bazında dağılım (stacked bar)
   - Trend analizi (line chart, varsa önceki dönem)
   - **Grafikler:** 3-4 adet

5. **Detaylı Emisyon Verileri** (2-3 sayfa)
   - Aktivite tablosu (renkli, kategorize)
   - Top 10 aktivite analizi (horizontal bar chart)
   - Kategori bazında gruplama (treemap)
   - Aktivite x scope heatmap
   - **Grafikler:** 3-4 adet

6. **Performans Analizi** (2-3 sayfa) ⭐ YENİ
   - Scope 1 detaylı analizi (500-700 kelime, AI)
   - Scope 2 detaylı analizi (500-700 kelime, AI)
   - Scope 3 detaylı analizi (500-700 kelime, AI)
   - Trend analizi (area chart)
   - Yıllık karşılaştırma (bar chart, varsa)
   - **Grafikler:** 3-4 adet

7. **Kritik Aktivite Analizi** (1-2 sayfa) ⭐ YENİ
   - Top 10 aktivite detaylı açıklama (AI)
   - Her aktivite için iyileştirme potansiyeli
   - ROI tahminleri tablosu
   - **Grafikler:** Horizontal bar, sankey diagram

8. **Akıllı Analiz Sonuçları** (2 sayfa)
   - ML benchmark detaylı açıklama (AI)
   - Benchmark karşılaştırma grafikleri (radar, box plot)
   - ML target detaylı açıklama (AI)
   - Net zero timeline (Gantt chart)
   - **Grafikler:** 3-4 adet

9. **İyileştirme Önerileri** (2-3 sayfa) ⭐ YENİ
   - 8-12 aksiyon önerisi (AI ile üretilmiş)
   - Her aksiyon için: açıklama, ROI, süre, öncelik
   - Uygulama planı timeline (Gantt chart)
   - Yatırım gereksinimleri tablosu
   - Beklenen azaltım waterfall chart
   - **Grafikler:** 2-3 adet

10. **Risk ve Fırsatlar** (1-2 sayfa) ⭐ YENİ
    - ESG risk analizi (kategorize, AI)
    - Fırsat değerlendirmesi (AI)
    - Stratejik öneriler
    - Risk matrisi görselleştirmesi
    - **Grafikler:** 1-2 adet

11. **Metodoloji** (2-3 sayfa)
    - Detaylandırılmış açıklamalar (her bölüm 400-600 kelime)
    - Standartlar ve referanslar (GRI, GHG Protocol, ISO)
    - Veri kalitesi değerlendirmesi
    - Belirsizlik analizi
    - Hesaplama formülleri

12. **Ekler** (1 sayfa)
    - Glossar (terimler sözlüğü)
    - Referanslar
    - İletişim bilgileri
    - Rapor versiyonu

**TOPLAM: 10-15 sayfa, 12-15 grafik, AI ile üretilmiş detaylı içerikler**

---

### **FAZE 4: Teknik İyileştirmeler**

#### 4.1 Gemini Entegrasyonu
```python
class ESGReportContentGenerator:
    """AI ile rapor içeriği üretir"""
    
    def generate_executive_summary(self, data):
        """Yönetici özeti üret"""
        
    def generate_analysis(self, scope_data, ml_results):
        """Performans analizi üret"""
        
    def generate_recommendations(self, emissions, benchmark):
        """İyileştirme önerileri üret"""
        
    def generate_risk_assessment(self, data):
        """Risk analizi üret"""
```

#### 4.2 Ollama Fallback (Opsiyonel)
- Gemini başarısız olursa Ollama kullan
- Local model: DeepSeek-R1-8B veya Llama 3.1
- API endpoint: `http://localhost:11434`

#### 4.3 Caching Stratejisi
- Aynı veri için aynı içerik üretilmesin
- Cache key: `company_name + period + data_hash`
- Cache süresi: 7 gün

#### 4.4 Hata Yönetimi
- Gemini API limit aşımı → Fallback
- API hatası → Statik içerik + uyarı
- Timeout → Async timeout handling

---

## 🎨 Tasarım Örnekleri

### Kapak Sayfası:
```
┌─────────────────────────────────────┐
│  [LOGO]                             │
│                                     │
│  ŞİRKET ADI                         │
│                                     │
│  ESG KARBON AYAK İZİ RAPORU         │
│                                     │
│  Raporlama Dönemi: 2024 Yıllık      │
│  Rapor Tarihi: 29.12.2024           │
│                                     │
│  [GRI 305 Uyumlu]                   │
│                                     │
│  [QR KOD]                           │
└─────────────────────────────────────┘
```

### İç Sayfa Düzeni:
```
┌─────────────────────────────────────┐
│  Header: Şirket Adı | Sayfa 1       │
├─────────────────────────────────────┤
│                                     │
│  1. YÖNETİCİ ÖZETİ                  │
│                                     │
│  [AI ile üretilmiş 300-500 kelime]  │
│                                     │
│  ┌─────────┬─────────┬─────────┐   │
│  │ KPI 1   │ KPI 2   │ KPI 3   │   │
│  └─────────┴─────────┴─────────┘   │
│                                     │
│  [Grafik: Scope Dağılımı]           │
│                                     │
├─────────────────────────────────────┤
│  Footer: © 2024 | ecologia.ai       │
└─────────────────────────────────────┘
```

---

## 📊 İçerik Örnekleri

### Yönetici Özeti (AI ile üretilecek):
```
[Şirket Adı] için 2024 yıllık döneminde gerçekleştirilen karbon 
ayak izi analizi sonuçları, şirketin sürdürülebilirlik performansına 
ilişkin önemli bulgular ortaya koymaktadır.

Toplam GHG emisyonu 1,234.56 ton CO2e olarak hesaplanmış olup, 
bu değer sektör ortalamasının %15 altındadır. Emisyonların %65'i 
Scope 2 (elektrik tüketimi) kaynaklıdır, bu da enerji verimliliği 
çalışmalarına öncelik verilmesi gerektiğini göstermektedir.

Scope 1 emisyonları toplamın %25'ini oluşturmakta ve öncelikli 
olarak ulaşım kaynaklı emisyonların azaltılması önerilmektedir. 
Scope 3 emisyonları henüz kapsamlı olarak ölçülmemiş olup, 
gelecek dönemlerde değer zinciri analizinin genişletilmesi 
planlanmaktadır.

Şirket, SBTi (Science Based Targets initiative) kriterlerine 
uygun olarak 2030 yılına kadar %50 emisyon azaltımı hedeflemektedir. 
Bu hedefe ulaşmak için önerilen aksiyonlar:
- Enerji verimliliği iyileştirmeleri (ROI: 2.5 yıl)
- Yenilenebilir enerji geçişi (ROI: 5 yıl)
- Ulaşım optimizasyonu (ROI: 1.5 yıl)
```

### Performans Analizi (AI ile üretilecek):
```
Scope 1 Emisyonları Analizi:
[Detaylı yorum, trend analizi, kritik aktiviteler, öneriler]

Scope 2 Emisyonları Analizi:
[Detaylı yorum, enerji kaynakları, verimlilik, öneriler]

Scope 3 Emisyonları Analizi:
[Detaylı yorum, değer zinciri, tedarikçi analizi, öneriler]
```

---

## 🚀 Uygulama Adımları

### Adım 1: Gemini Content Generator
- `ESGReportContentGenerator` class'ı oluştur
- Her bölüm için prompt template'leri hazırla
- Test et (küçük veri seti ile)

### Adım 2: Tema Geliştirme
- ReportLab tema sistemini genişlet
- Yeni stiller ekle
- Kapak sayfası tasarla

### Adım 3: Görselleştirme (KAPSAMLI)
- 12-15 grafik fonksiyonu oluştur
  - Matplotlib (temel grafikler)
  - Seaborn (istatistiksel, heatmap)
  - Plotly (interaktif → PNG export)
- Her grafik için özel styling (tema uyumlu)
- İnfografik elementler (KPI kartları, progress bar'lar)
- Grafik cache mekanizması (aynı veri için tekrar üretme)

### Adım 4: Rapor Yapısı
- Yeni bölümleri ekle
- AI içerikleri entegre et
- Test et

### Adım 5: Ollama Fallback (Opsiyonel)
- Ollama client ekle
- Fallback mekanizması
- Test et

---

## ⚙️ Teknik Detaylar

### Gemini API Kullanımı:
```python
# Mevcut: gemini_service.py
# Genişletilecek: ESGReportContentGenerator

from app.services.gemini_service import GeminiESGAssistant

class ESGReportContentGenerator:
    def __init__(self):
        self.gemini = GeminiESGAssistant()
    
    def generate_section(self, section_type, data, context):
        prompt = self._build_prompt(section_type, data, context)
        return self.gemini.answer_question(prompt)
```

### Ollama Fallback:
```python
import requests

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.model = "deepseek-r1:8b"  # veya "llama3.1:8b"
    
    def generate(self, prompt):
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": prompt}
        )
        return response.json()["response"]
```

---

## 📈 Beklenen Sonuçlar

### Öncesi:
- 5-6 sayfa, basit içerik
- Statik metinler
- Sadece tablolar

### Sonrası:
- **10-15 sayfa**, zengin içerik
- **12-15 profesyonel grafik** (matplotlib, seaborn, plotly)
- **AI ile üretilmiş detaylı analizler** (her bölüm 400-1200 kelime)
- **Profesyonel tema** ve görselleştirmeler
- **Gerçek ESG rapor formatı** (GRI uyumlu)
- Stratejik öneriler ve yol haritası
- Kapsamlı metodoloji ve analizler

---

## 🎯 Öncelik Sırası

1. **Yüksek Öncelik:**
   - Gemini ile içerik üretimi
   - Yönetici özeti genişletme
   - Performans analizi bölümü

2. **Orta Öncelik:**
   - Tema iyileştirme
   - Görselleştirme genişletme
   - İyileştirme önerileri bölümü

3. **Düşük Öncelik:**
   - Ollama fallback
   - Risk analizi bölümü
   - Ek görselleştirmeler

---

## 💡 Öneriler

1. **Gemini API kullan** - Zaten var, kaliteli, Türkçe mükemmel, uzun context
2. **Ollama'yı fallback olarak ekle** - API limit durumunda
3. **İçerik üretimini async yap** - Hız için (paralel bölüm üretimi)
4. **Cache mekanizması ekle** - Aynı veri için tekrar üretme (hem AI hem grafik)
5. **Modüler yapı** - Her bölüm bağımsız üretilebilsin
6. **Grafik üretimini optimize et** - Matplotlib backend'i optimize, DPI ayarı
7. **İçerik kalitesi kontrolü** - AI üretilen içerikler için minimum kelime sayısı
8. **Template sistemi** - Her bölüm için prompt template'leri, tutarlılık için

---

## ✅ Onay Bekleniyor

Bu planı onaylarsanız, önce Gemini ile içerik üretimini başlatırız.

