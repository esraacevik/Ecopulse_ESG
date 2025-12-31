# 🔍 Anomali Tespiti Test Verileri

Bu klasörde anomali tespiti için 2 farklı test veri seti bulunmaktadır.

## 📊 Veri Setleri

### 1. `anomali_veri_spike.csv` - Spike (Ani Yükseliş) Anomalileri

**Özellikler:**
- 240 satır (10 günlük saatlik veri)
- Normal enerji tüketim pattern'i
- 3 adet **spike anomali** (ani yükselişler):
  - Satır 50: ~3.5x normal değer
  - Satır 120: ~3.5x normal değer
  - Satır 180: ~3.5x normal değer

**Kullanım Senaryosu:**
- Arıza durumları
- Beklenmedik yük artışları
- Ölçüm hataları

**Beklenen Sonuç:**
- 3 anomali tespit edilmeli
- Anomali oranı: ~1.25%

### 2. `anomali_veri_persistent.csv` - Persistent (Sürekli) Anomalileri

**Özellikler:**
- 240 satır (10 günlük saatlik veri)
- Normal enerji tüketim pattern'i
- 3 adet **anomali grubu**:
  - Satır 80-87: 8 saatlik düşük değerler (~%85 düşüş)
  - Satır 160-167: 8 saatlik yüksek değerler (~%180 artış)
  - Satır 50, 120, 180, 200, 220, 230, 235, 238: 8 adet spike anomali (~3.5x normal değer)

**Kullanım Senaryosu:**
- Uzun süreli arıza durumları
- Sistem bakımı
- Sürekli anormal çalışma
- Ani yükselişler

**Beklenen Sonuç:**
- 24 anomali tespit edilmeli (8 düşük + 8 yüksek + 8 spike)
- Anomali oranı: ~10%

## 📋 Veri Formatı

Her iki dosya da aynı formatı kullanır:

```csv
Time,total_power,HVAC_Actual_kW,Chiller_Power_kW,Humidifier_power_kW,HV_light_Power_kW,PowerkW,PV_panels_power_kW,Battery_system_power
2024-01-01 00:00:00,145.2,48.5,25.3,2.1,12.5,35.8,0.0,0.0
...
```

**Kolonlar:**
- `Time`: Tarih/saat (datetime formatı)
- `total_power`: Toplam güç tüketimi (kW)
- `HVAC_Actual_kW`: HVAC gücü
- `Chiller_Power_kW`: Chiller gücü
- `Humidifier_power_kW`: Nemlendirici gücü
- `HV_light_Power_kW`: Aydınlatma gücü
- `PowerkW`: Genel güç
- `PV_panels_power_kW`: Güneş paneli gücü
- `Battery_system_power`: Batarya sistemi gücü

## 🚀 Kullanım

1. **Frontend'de:**
   - ML Dashboard → Anomali Tespiti sekmesine git
   - CSV dosyasını yükle
   - "Analiz Et" butonuna bas
   - Anomali sonuçlarını görüntüle

2. **API ile:**
   ```python
   import pandas as pd
   import requests
   
   df = pd.read_csv('anomali_veri_spike.csv')
   response = requests.post('http://localhost:8000/api/v1/ml/anomaly', json={
       'data': df.to_dict('records'),
       'contamination': 0.1
   })
   ```

## 📝 Notlar

- Her iki veri seti de gerçekçi enerji tüketim pattern'leri içerir
- Anomaliler kasıtlı olarak eklenmiştir
- Normal değerler: 100-250 kW aralığında
- Anomali değerler: Normal değerlerin 0.15x - 3.5x aralığında

