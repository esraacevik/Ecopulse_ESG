# Veri dosyaları

Bu klasör, uygulamanın kullandığı emisyon faktörü JSON dosyalarını içerir.

| Dosya | Zorunlu | Açıklama |
|-------|---------|----------|
| `scope1_data.json` | Evet | Scope 1 emisyon faktörleri |
| `scope2_data.json` | Evet | Scope 2 emisyon faktörleri |
| `summary.json` | Evet | Veri seti özet istatistikleri |
| `emission_data_input.json` | Hayır | Streamlit kullanıcı girişi (otomatik oluşabilir) |
| `scope3_data.json` | Hayır | Scope 3 faktörleri (yoksa liste boş kalır) |

Backend ve Streamlit bu klasörden okur. Klon sonrası doğrulama:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup_data.ps1
```
