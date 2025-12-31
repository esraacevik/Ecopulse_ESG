"""
Qwen ML Dashboard AI Service
Her ML sekmesi için özel AI önerileri ve analizler
"""
from typing import Dict, Any, Optional, List
from app.services.qwen_service import QwenESGContentGenerator
import json

class QwenMLAdvisor:
    """ML Dashboard sekmeleri için AI danışmanı"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:1234"):
        """
        ML Advisor başlat
        
        Args:
            base_url: LM Studio API endpoint
        """
        self.qwen = QwenESGContentGenerator(base_url=base_url)
        
        # Her sekme için özel system prompt
        self.system_prompts = {
            'net_zero': """Sen bir Net Zero ve karbon azaltım stratejileri uzmanısın.
Türkçe yazıyorsun ve şirketlere pratik, uygulanabilir öneriler sunuyorsun.

Odak noktaların:
- Teknoloji önerileri (yenilenebilir enerji, enerji verimliliği)
- Operasyonel iyileştirmeler
- Yatırım öncelikleri
- Risk yönetimi
- SBTi uyumlu stratejiler
- Finansal analiz ve ROI

Yazı stilinde:
- Markdown kullanma, sadece düz metin
- Pratik ve uygulanabilir öneriler
- Sayısal verilerle destekle
- Önceliklendirme yap
- Türkçe karakterleri doğru kullan""",
            
            'benchmark': """Sen bir sektör analizi ve benchmark uzmanısın.
Türkçe yazıyorsun ve şirketlere sektörel karşılaştırma ve iyileştirme önerileri sunuyorsun.

Odak noktaların:
- Sektörel pozisyon analizi
- Best practice örnekleri
- Rekabet avantajı stratejileri
- Sektörel trendler
- İyileştirme fırsatları
- Risk değerlendirmesi

Yazı stilinde:
- Markdown kullanma, sadece düz metin
- Veri odaklı analiz
- Karşılaştırmalı değerlendirme
- Türkçe karakterleri doğru kullan""",
            
            'anomaly': """Sen bir veri analizi ve anomali çözümleme uzmanısın.
Türkçe yazıyorsun ve enerji tüketimi anomalilerini analiz edip çözüm önerileri sunuyorsun.

Odak noktaların:
- Anomali nedenlerini açıklama
- Sistem arıza tespiti
- Operasyonel sorunlar
- Önleyici önlemler
- İzleme stratejileri
- Acil müdahale planları

Yazı stilinde:
- Markdown kullanma, sadece düz metin
- Teknik ama anlaşılır dil
- Pratik çözümler
- Türkçe karakterleri doğru kullan""",
            
            'forecast': """Sen bir enerji yönetimi ve tahmin optimizasyonu uzmanısın.
Türkçe yazıyorsun ve enerji tüketimi tahminlerine dayalı tasarruf önerileri sunuyorsun.

Odak noktaların:
- Enerji tasarruf fırsatları
- Yük yönetimi stratejileri
- Verimlilik iyileştirmeleri
- Talep yönetimi
- Maliyet optimizasyonu
- Sürdürülebilirlik hedefleri

Yazı stilinde:
- Markdown kullanma, sadece düz metin
- Sayısal hedeflerle destekle
- Uygulanabilir öneriler
- Türkçe karakterleri doğru kullan""",
            
            'overview': """Sen bir ESG ve sürdürülebilirlik stratejisi uzmanısın.
Türkçe yazıyorsun ve şirketlere kapsamlı ESG önerileri sunuyorsun.

Odak noktaların:
- Genel ESG performans değerlendirmesi
- Stratejik öncelikler
- Entegre yaklaşımlar
- Risk ve fırsat analizi
- Paydaş yönetimi
- Uzun vadeli hedefler

Yazı stilinde:
- Markdown kullanma, sadece düz metin
- Holistik bakış açısı
- Stratejik öneriler
- Türkçe karakterleri doğru kullan"""
        }
    
    def generate_net_zero_recommendations(
        self,
        company_name: str,
        current_emissions: Dict[str, float],
        target_year: int,
        base_year: int,
        reduction_target: float,
        milestones: Optional[List[Dict]] = None,
        investment: Optional[Dict] = None
    ) -> str:
        """
        Net Zero için detaylı öneriler üret
        
        Args:
            company_name: Şirket adı
            current_emissions: Mevcut emisyonlar (scope1, scope2, scope3)
            target_year: Hedef yıl
            base_year: Baz yıl
            reduction_target: Azaltım hedefi (%)
            milestones: Kilometre taşları
            investment: Yatırım bilgileri
            
        Returns:
            AI önerileri metni
        """
        context = {
            'company': company_name,
            'current_emissions': current_emissions,
            'target_year': target_year,
            'base_year': base_year,
            'reduction_target': reduction_target,
            'milestones': milestones or [],
            'investment': investment or {}
        }
        
        prompt = f"""Aşağıdaki bilgilere dayanarak {company_name} şirketi için detaylı Net Zero azaltım stratejileri ve önerileri sun:

Mevcut Durum:
- Scope 1: {current_emissions.get('scope1', 0):,.0f} ton CO2e
- Scope 2: {current_emissions.get('scope2', 0):,.0f} ton CO2e
- Scope 3: {current_emissions.get('scope3', 0):,.0f} ton CO2e
- Toplam: {sum(current_emissions.values()):,.0f} ton CO2e

Hedef:
- Baz Yıl: {base_year}
- Hedef Yıl: {target_year}
- Azaltım Hedefi: %{reduction_target:.1f}

Lütfen şunları içeren kapsamlı bir strateji sun:
1. Teknoloji önerileri (yenilenebilir enerji, enerji verimliliği teknolojileri)
2. Operasyonel iyileştirmeler (süreç optimizasyonu, atık azaltma)
3. Scope bazlı öncelikli aksiyonlar
4. Yatırım öncelikleri ve ROI analizi
5. Risk yönetimi ve alternatif senaryolar
6. İzleme ve raporlama önerileri

Her öneriyi somut, uygulanabilir ve sayısal hedeflerle destekle. Minimum 500 kelime yaz."""
        
        return self.qwen.generate_content(
            prompt=prompt,
            context=context,
            max_tokens=3000,
            temperature=0.7,
            min_words=500
        )
    
    def generate_benchmark_insights(
        self,
        company_name: str,
        sector: str,
        company_metrics: Dict[str, float],
        sector_average: Dict[str, float],
        percentile: float
    ) -> str:
        """
        Sektör benchmark için AI analizi
        
        Args:
            company_name: Şirket adı
            sector: Sektör adı
            company_metrics: Şirket metrikleri
            sector_average: Sektör ortalaması
            percentile: Şirketin yüzdelik dilimi
            
        Returns:
            AI analizi metni
        """
        context = {
            'company': company_name,
            'sector': sector,
            'company_metrics': company_metrics,
            'sector_average': sector_average,
            'percentile': percentile
        }
        
        prompt = f"""Aşağıdaki sektör benchmark verilerine dayanarak {company_name} şirketi için detaylı analiz ve öneriler sun:

Sektör: {sector}
Şirket Pozisyonu: {percentile:.0f}. yüzdelik dilim

Şirket Metrikleri:
{json.dumps(company_metrics, indent=2, ensure_ascii=False)}

Sektör Ortalaması:
{json.dumps(sector_average, indent=2, ensure_ascii=False)}

Lütfen şunları içeren kapsamlı bir analiz sun:
1. Sektörel pozisyon değerlendirmesi
2. Güçlü yönler ve iyileştirme alanları
3. Best practice örnekleri ve öğrenilecek dersler
4. Rekabet avantajı stratejileri
5. Sektörel trendler ve gelecek beklentileri
6. Öncelikli iyileştirme önerileri

Minimum 400 kelime yaz."""
        
        return self.qwen.generate_content(
            prompt=prompt,
            context=context,
            max_tokens=2500,
            temperature=0.7,
            min_words=400
        )
    
    def generate_anomaly_analysis(
        self,
        anomaly_count: int,
        anomaly_indices: List[int],
        data_summary: Dict[str, Any],
        anomaly_details: Optional[List[Dict]] = None
    ) -> str:
        """
        Anomali tespiti için AI analizi ve çözüm önerileri
        
        Args:
            anomaly_count: Anomali sayısı
            anomaly_indices: Anomali indeksleri
            data_summary: Veri özeti (toplam satır, ortalama, min, max)
            anomaly_details: Anomali detayları (zaman, değer vb.)
            
        Returns:
            AI analizi metni
        """
        context = {
            'anomaly_count': anomaly_count,
            'anomaly_indices': anomaly_indices,
            'data_summary': data_summary,
            'anomaly_details': anomaly_details or []
        }
        
        prompt = f"""Aşağıdaki anomali tespiti sonuçlarına dayanarak detaylı analiz ve çözüm önerileri sun:

Tespit Edilen Anomaliler:
- Toplam Anomali Sayısı: {anomaly_count}
- Veri Seti: {data_summary.get('total_samples', 0)} satır
- Anomali Oranı: {(anomaly_count / data_summary.get('total_samples', 1) * 100):.1f}%

Veri Özeti:
- Ortalama Güç: {data_summary.get('avg_power', 0):.1f} kW
- Minimum: {data_summary.get('min_power', 0):.1f} kW
- Maksimum: {data_summary.get('max_power', 0):.1f} kW

Lütfen şunları içeren kapsamlı bir analiz sun:
1. Anomali nedenlerinin olası açıklamaları (sistem arızası, operasyonel sorunlar, ölçüm hataları)
2. Anomali tiplerinin analizi (yüksek/düşük değerler, spike'lar, persistent anomaliler)
3. Acil müdahale önerileri
4. Önleyici önlemler ve izleme stratejileri
5. Sistem iyileştirme önerileri
6. Bakım ve kalibrasyon önerileri

Minimum 400 kelime yaz."""
        
        return self.qwen.generate_content(
            prompt=prompt,
            context=context,
            max_tokens=2500,
            temperature=0.7,
            min_words=400
        )
    
    def generate_forecast_recommendations(
        self,
        forecast_summary: Dict[str, Any],
        current_consumption: Optional[float] = None,
        location: Optional[str] = None
    ) -> str:
        """
        Tüketim tahmini için AI önerileri
        
        Args:
            forecast_summary: Tahmin özeti (ortalama, toplam, CO2 vb.)
            current_consumption: Mevcut tüketim
            location: Lokasyon
            
        Returns:
            AI önerileri metni
        """
        context = {
            'forecast_summary': forecast_summary,
            'current_consumption': current_consumption,
            'location': location
        }
        
        prompt = f"""Aşağıdaki enerji tüketimi tahminlerine dayanarak detaylı tasarruf ve optimizasyon önerileri sun:

Tahmin Özeti:
- Ortalama Güç: {forecast_summary.get('avg_power', 0):.1f} kW
- Toplam Enerji: {forecast_summary.get('total_kwh', 0):,.0f} kWh
- Tahmini CO2: {forecast_summary.get('co2_ton', 0):.2f} ton CO2e
- Tahmin Süresi: {forecast_summary.get('forecast_hours', 0)} saat
{f'- Lokasyon: {location}' if location else ''}
{f'- Mevcut Tüketim: {current_consumption:.1f} kW' if current_consumption else ''}

Lütfen şunları içeren kapsamlı öneriler sun:
1. Enerji tasarruf fırsatları (kısa ve uzun vadeli)
2. Yük yönetimi stratejileri (peak shaving, load shifting)
3. Verimlilik iyileştirmeleri (ekipman, sistem optimizasyonu)
4. Talep yönetimi önerileri
5. Maliyet optimizasyonu stratejileri
6. Sürdürülebilirlik hedeflerine katkı
7. Teknoloji yatırım önerileri (akıllı sayaçlar, IoT sensörler)

Her öneriyi somut ve uygulanabilir şekilde sun. Minimum 400 kelime yaz."""
        
        return self.qwen.generate_content(
            prompt=prompt,
            context=context,
            max_tokens=2500,
            temperature=0.7,
            min_words=400
        )
    
    def generate_overview_insights(
        self,
        company_name: str,
        esg_summary: Dict[str, Any],
        ml_results: Optional[Dict] = None
    ) -> str:
        """
        Genel bakış için AI önerileri
        
        Args:
            company_name: Şirket adı
            esg_summary: ESG özeti
            ml_results: ML analiz sonuçları
            
        Returns:
            AI önerileri metni
        """
        context = {
            'company': company_name,
            'esg_summary': esg_summary,
            'ml_results': ml_results or {}
        }
        
        prompt = f"""Aşağıdaki ESG ve ML analiz sonuçlarına dayanarak {company_name} şirketi için kapsamlı stratejik öneriler sun:

ESG Özeti:
{json.dumps(esg_summary, indent=2, ensure_ascii=False)}

ML Analiz Sonuçları:
{json.dumps(ml_results, indent=2, ensure_ascii=False) if ml_results else 'Henüz ML analizi yapılmamış'}

Lütfen şunları içeren holistik bir değerlendirme sun:
1. Genel ESG performans değerlendirmesi
2. Stratejik öncelikler ve hedefler
3. Entegre yaklaşımlar (çevresel, sosyal, yönetişim)
4. Risk ve fırsat analizi
5. Paydaş yönetimi önerileri
6. Uzun vadeli sürdürülebilirlik stratejisi
7. İyileştirme yol haritası

Minimum 500 kelime yaz."""
        
        return self.qwen.generate_content(
            prompt=prompt,
            context=context,
            max_tokens=3000,
            temperature=0.7,
            min_words=500
        )

