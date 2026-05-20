# ESG Rapor Oluşturma - Streaming Entegrasyon Planı

## 🎯 Amaç
Frontend'de rapor oluşturma sırasında gerçek zamanlı ilerleme göstermek (streaming). Kullanıcı hangi aşamada olduğunu görebilecek.

## 📋 Mevcut Durum

### Backend
- ✅ `report_generator_fixed.py` - Gelişmiş rapor generator (AI destekli)
- ✅ `progress_callback` desteği mevcut
- ✅ `/api/v1/report/generate` endpoint'i var (ama streaming yok)
- ❌ Eski `report_generator.py` kullanılıyor (yeni `report_generator_fixed.py` değil)

### Frontend
- ✅ `ReportGenerator.tsx` component var
- ✅ Basit loading state var
- ❌ Streaming/progress gösterimi yok
- ❌ İlerleme mesajları yok

## 🚀 Planlanan Değişiklikler

### 1. Backend - Streaming Endpoint (SSE)
**Dosya:** `backend/app/api/v1/report.py`

**Yeni Endpoint:**
```python
@router.post("/report/generate-stream")
async def generate_report_stream(request: ReportGenerateRequest):
    """
    Generate ESG PDF report with Server-Sent Events (SSE) streaming
    """
    # FastAPI StreamingResponse kullan
    # report_generator_fixed.py kullan
    # Her progress_callback çağrısında SSE ile mesaj gönder
```

**Özellikler:**
- Server-Sent Events (SSE) kullan
- `report_generator_fixed.py` kullan (yeni versiyon)
- Her `_update_progress` çağrısında frontend'e mesaj gönder
- Progress mesajları: "Kapak sayfası oluşturuluyor...", "Yönetici özeti ekleniyor..." vb.

**Progress Mesaj Formatı:**
```json
{
  "type": "progress",
  "message": "Kapak sayfası oluşturuluyor...",
  "step": "cover",
  "percentage": 10
}
```

**Tamamlanma Mesajı:**
```json
{
  "type": "complete",
  "filename": "esg_report_2024.pdf",
  "file_path": "/path/to/file.pdf"
}
```

### 2. Backend - Schema Güncellemeleri
**Dosya:** `backend/app/models/schemas.py`

**Yeni Schema:**
```python
class ReportProgressMessage(BaseModel):
    type: str  # "progress" | "complete" | "error"
    message: Optional[str] = None
    step: Optional[str] = None  # "cover", "executive_summary", "charts", etc.
    percentage: Optional[int] = None
    filename: Optional[str] = None
    file_path: Optional[str] = None
```

### 3. Frontend - Streaming Client
**Dosya:** `frontend/src/services/api.ts`

**Yeni Fonksiyon:**
```typescript
export const reportAPI = {
  // ... mevcut generate fonksiyonu
  
  generateStream: async (
    data: ReportGenerateRequest,
    onProgress: (message: ReportProgressMessage) => void
  ): Promise<string> => {
    // EventSource veya fetch ile SSE stream oku
    // Her mesajda onProgress callback'i çağır
    // Tamamlanınca filename döndür
  }
}
```

### 4. Frontend - UI Güncellemeleri
**Dosya:** `frontend/src/components/ReportGenerator.tsx`

**Yeni Özellikler:**
- Progress bar (0-100%)
- Adım adım ilerleme gösterimi
- Her adım için checkbox/icon (tamamlandı mı?)
- Gerçek zamanlı mesajlar
- "Kapak sayfası tamamlandı ✓", "Yönetici özeti tamamlandı ✓" gibi

**UI Tasarımı:**
```
┌─────────────────────────────────────┐
│  ESG Rapor Oluşturuluyor...         │
│  ████████████░░░░░░░░  60%          │
│                                     │
│  ✓ Kapak sayfası oluşturuldu       │
│  ✓ Yönetici özeti tamamlandı       │
│  ⏳ Grafikler oluşturuluyor...      │
│  ⏳ AI içerik üretiliyor...         │
│  ⏳ PDF oluşturuluyor...            │
└─────────────────────────────────────┘
```

### 5. Progress Adımları Mapping
**Backend'den gelen mesajlar → Frontend gösterimi:**

| Backend Mesajı | Frontend Adım | Icon |
|---------------|---------------|------|
| "Kapak sayfası oluşturuluyor..." | Kapak Sayfası | ✓ |
| "Yönetici özeti ekleniyor..." | Yönetici Özeti | ✓ |
| "Emisyon özeti ekleniyor..." | Emisyon Özeti | ✓ |
| "Grafikler oluşturuluyor..." | Görselleştirmeler | ✓ |
| "AI ile içerik üretimi başlatılıyor..." | AI İçerik Üretimi | ⏳ |
| "Performans analizi ekleniyor..." | Performans Analizi | ✓ |
| "Kritik aktivite analizi ekleniyor..." | Kritik Analiz | ✓ |
| "İyileştirme önerileri ekleniyor..." | Öneriler | ✓ |
| "Risk analizi ekleniyor..." | Risk Analizi | ✓ |
| "Metodoloji bölümü ekleniyor..." | Metodoloji | ✓ |
| "Kapanış bölümü ekleniyor..." | Kapanış | ✓ |
| "PDF oluşturuluyor..." | PDF Oluşturma | ⏳ |
| "Rapor oluşturma tamamlandı!" | Tamamlandı | ✓ |

## 📁 Dosya Değişiklikleri

### Backend
1. `backend/app/api/v1/report.py`
   - Yeni `/report/generate-stream` endpoint
   - SSE streaming implementasyonu
   - `report_generator_fixed.py` kullanımı

2. `backend/app/models/schemas.py`
   - `ReportProgressMessage` schema eklenecek

### Frontend
1. `frontend/src/services/api.ts`
   - `generateStream` fonksiyonu eklenecek

2. `frontend/src/components/ReportGenerator.tsx`
   - Streaming desteği eklenecek
   - Progress UI eklenecek
   - Adım adım gösterim

## 🔄 İş Akışı

1. Kullanıcı "Rapor Oluştur" butonuna tıklar
2. Frontend `/report/generate-stream` endpoint'ine istek gönderir
3. Backend SSE stream başlatır
4. Backend `report_generator_fixed.py` ile rapor oluşturmaya başlar
5. Her `_update_progress` çağrısında frontend'e mesaj gönderilir
6. Frontend mesajları alır ve UI'da gösterir
7. Rapor tamamlanınca download linki gösterilir

## ⚠️ Dikkat Edilmesi Gerekenler

1. **LM Studio Bağlantısı:** AI içerik üretimi için LM Studio çalışıyor olmalı
2. **Timeout:** Uzun süren işlemler için timeout ayarları
3. **Error Handling:** Hata durumlarında kullanıcıya bilgi verilmeli
4. **Fallback:** AI başarısız olursa fallback içerik kullanılacak (zaten mevcut)

## ✅ Test Senaryoları

1. Normal rapor oluşturma (AI ile)
2. AI olmadan rapor oluşturma (fallback)
3. Hata durumunda kullanıcı bilgilendirmesi
4. Streaming'in düzgün çalışması
5. Progress bar'ın doğru güncellenmesi

## 🎨 UI Örnekleri

### Progress Bar Component
```tsx
<div className="space-y-4">
  <div className="w-full bg-gray-200 rounded-full h-2.5">
    <div 
      className="bg-green-600 h-2.5 rounded-full transition-all duration-300"
      style={{ width: `${percentage}%` }}
    />
  </div>
  
  <div className="space-y-2">
    {steps.map(step => (
      <div key={step.id} className="flex items-center gap-2">
        {step.completed ? (
          <CheckCircle className="w-5 h-5 text-green-600" />
        ) : step.inProgress ? (
          <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
        ) : (
          <Circle className="w-5 h-5 text-gray-400" />
        )}
        <span className={step.completed ? "text-gray-600" : "text-gray-400"}>
          {step.label}
        </span>
      </div>
    ))}
  </div>
</div>
```

## 📝 Notlar

- SSE (Server-Sent Events) kullanılacak (WebSocket yerine, daha basit)
- Mevcut `report_generator_fixed.py` kullanılacak (yeni versiyon)
- Progress mesajları Türkçe olacak
- UI responsive olmalı

