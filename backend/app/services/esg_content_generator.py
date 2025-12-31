"""
ESG Rapor İçerik Üretici
Qwen3-4B model ile parça parça içerik üretir
"""
from typing import Dict, Any, List, Optional
from app.services.qwen_service import QwenESGContentGenerator
from tqdm import tqdm
import time

class ESGReportContentGenerator:
    """ESG rapor içeriklerini parça parça üretir ve birleştirir"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:1234"):
        """
        Content generator başlat
        
        Args:
            base_url: LM Studio API endpoint
        """
        self.qwen = QwenESGContentGenerator(base_url=base_url)
        self.generated_sections = {}
        
    def generate_executive_summary(
        self, 
        company_name: str,
        reporting_period: str,
        scope_summary: Dict[str, float],
        total_emissions: float,
        ml_results: Optional[Dict] = None,
        progress_callback=None
    ) -> str:
        """
        Yönetici özeti üret (800-1200 kelime)
        
        Args:
            company_name: Şirket adı
            reporting_period: Raporlama dönemi
            scope_summary: Scope özeti
            total_emissions: Toplam emisyon
            ml_results: ML analiz sonuçları
            progress_callback: İlerleme callback'i
            
        Returns:
            Yönetici özeti metni
        """
        if progress_callback:
            progress_callback("Yönetici özeti üretiliyor...")
        
        prompt = f"""
{company_name} için {reporting_period} döneminde gerçekleştirilen karbon ayak izi analizi sonuçlarını 
kapsamlı bir şekilde özetle. 

Rapor şunları içermeli:
1. Şirket performansı genel değerlendirmesi (200-300 kelime)
2. Scope bazında detaylı analiz ve yorumlar (300-400 kelime)
3. Sektör karşılaştırması ve benchmark değerlendirmesi (200-300 kelime)
4. Öncelikli aksiyon önerileri ve stratejik yönlendirmeler (200-300 kelime)

Toplam emisyon: {total_emissions:.2f} ton CO2e
Scope dağılımı: {', '.join([f'{k}: {v:.2f} ton' for k, v in scope_summary.items() if v > 0])}

Lütfen 800-1200 kelime arası, profesyonel, detaylı bir yönetici özeti yaz.
"""
        
        context = {
            'scope_summary': scope_summary,
            'ml_results': ml_results
        }
        
        content = self.qwen.generate_content(
            prompt=prompt,
            context=context,
            max_tokens=2500,
            min_words=800
        )
        
        self.generated_sections['executive_summary'] = content
        return content
    
    def generate_performance_analysis(
        self,
        scope: str,
        scope_value: float,
        total_emissions: float,
        results: List[Dict],
        progress_callback=None
    ) -> str:
        """
        Scope bazında performans analizi üret (500-700 kelime)
        
        Args:
            scope: Scope adı (Scope 1, 2, 3)
            scope_value: Scope emisyon değeri
            total_emissions: Toplam emisyon
            results: Bu scope'a ait aktivite sonuçları
            progress_callback: İlerleme callback'i
            
        Returns:
            Performans analizi metni
        """
        if progress_callback:
            progress_callback(f"{scope} performans analizi üretiliyor...")
        
        # Bu scope'a ait aktiviteleri filtrele
        scope_activities = [r for r in results if r.get('scope') == scope]
        top_activities = sorted(scope_activities, key=lambda x: x.get('co2e_ton', 0), reverse=True)[:5]
        
        prompt = f"""
{scope} emisyonları için detaylı bir performans analizi yaz.

Bilgiler:
- {scope} toplam emisyon: {scope_value:.2f} ton CO2e
- Toplam emisyon içindeki payı: {(scope_value/total_emissions*100):.1f}%
- Aktivite sayısı: {len(scope_activities)}
- En yüksek emisyonlu aktiviteler: {', '.join([a.get('activity_name', 'Unknown')[:30] for a in top_activities[:3]])}

Analiz şunları içermeli:
1. {scope} emisyonlarının genel değerlendirmesi ve önemi (150-200 kelime)
2. Kritik aktivitelerin detaylı analizi (200-250 kelime)
3. İyileştirme potansiyeli ve öneriler (150-250 kelime)

Lütfen 500-700 kelime arası, profesyonel, analitik bir analiz yaz.
"""
        
        context = {
            'results': scope_activities,
            'scope_summary': {scope: scope_value}
        }
        
        content = self.qwen.generate_content(
            prompt=prompt,
            context=context,
            max_tokens=2000,
            min_words=500
        )
        
        self.generated_sections[f'performance_{scope.lower().replace(" ", "_")}'] = content
        return content
    
    def generate_critical_activities_analysis(
        self,
        top_activities: List[Dict],
        progress_callback=None
    ) -> str:
        """
        Kritik aktivite analizi üret
        
        Args:
            top_activities: En yüksek emisyonlu aktiviteler (top 10)
            progress_callback: İlerleme callback'i
            
        Returns:
            Kritik aktivite analizi metni
        """
        if progress_callback:
            progress_callback("Kritik aktivite analizi üretiliyor...")
        
        activities_text = "\n".join([
            f"{i+1}. {act.get('activity_name', 'Unknown')}: {act.get('co2e_ton', 0):.2f} ton CO2e ({act.get('scope', 'Unknown')})"
            for i, act in enumerate(top_activities[:10])
        ])
        
        prompt = f"""
Aşağıdaki en yüksek emisyonlu aktiviteler için detaylı bir analiz yaz:

{activities_text}

Her aktivite için şunları analiz et:
1. Aktivitenin emisyon profili ve önemi
2. İyileştirme potansiyeli
3. Önerilen aksiyonlar ve tahmini ROI

Lütfen kapsamlı, profesyonel bir analiz yaz (toplam 1000-1500 kelime).
"""
        
        context = {
            'results': top_activities
        }
        
        content = self.qwen.generate_content(
            prompt=prompt,
            context=context,
            max_tokens=3000,
            min_words=1000
        )
        
        self.generated_sections['critical_activities'] = content
        return content
    
    def generate_recommendations(
        self,
        scope_summary: Dict[str, float],
        total_emissions: float,
        ml_results: Optional[Dict] = None,
        progress_callback=None
    ) -> str:
        """
        İyileştirme önerileri üret (8-12 aksiyon)
        
        Args:
            scope_summary: Scope özeti
            total_emissions: Toplam emisyon
            ml_results: ML analiz sonuçları
            progress_callback: İlerleme callback'i
            
        Returns:
            İyileştirme önerileri metni
        """
        if progress_callback:
            progress_callback("İyileştirme önerileri üretiliyor...")
        
        prompt = f"""
Toplam {total_emissions:.2f} ton CO2e emisyon için 8-12 adet somut, uygulanabilir iyileştirme önerisi hazırla.

Scope dağılımı:
{chr(10).join([f'- {k}: {v:.2f} ton CO2e ({(v/total_emissions*100):.1f}%)' for k, v in scope_summary.items() if v > 0])}

Her öneri için şunları belirt:
1. Öneri açıklaması
2. Beklenen emisyon azaltımı (ton CO2e)
3. Tahmini ROI ve yatırım gereksinimi
4. Uygulama süresi
5. Öncelik seviyesi (Yüksek/Orta/Düşük)

Lütfen detaylı, uygulanabilir öneriler yaz (toplam 1200-1800 kelime).
"""
        
        context = {
            'scope_summary': scope_summary,
            'ml_results': ml_results
        }
        
        content = self.qwen.generate_content(
            prompt=prompt,
            context=context,
            max_tokens=3500,
            min_words=1200
        )
        
        self.generated_sections['recommendations'] = content
        return content
    
    def generate_risk_assessment(
        self,
        scope_summary: Dict[str, float],
        total_emissions: float,
        progress_callback=None
    ) -> str:
        """
        Risk ve fırsat analizi üret
        
        Args:
            scope_summary: Scope özeti
            total_emissions: Toplam emisyon
            progress_callback: İlerleme callback'i
            
        Returns:
            Risk analizi metni
        """
        if progress_callback:
            progress_callback("Risk analizi üretiliyor...")
        
        prompt = f"""
Toplam {total_emissions:.2f} ton CO2e emisyon için ESG risk ve fırsat analizi yap.

Scope dağılımı:
{chr(10).join([f'- {k}: {v:.2f} ton CO2e' for k, v in scope_summary.items() if v > 0])}

Analiz şunları içermeli:
1. ESG riskleri (regülasyon, fiziksel riskler, geçiş riskleri)
2. Fırsatlar (yeşil finans, verimlilik, rekabet avantajı)
3. Stratejik öneriler

Lütfen kapsamlı bir analiz yaz (800-1200 kelime).
"""
        
        context = {
            'scope_summary': scope_summary
        }
        
        content = self.qwen.generate_content(
            prompt=prompt,
            context=context,
            max_tokens=2500,
            min_words=800
        )
        
        self.generated_sections['risk_assessment'] = content
        return content
    
    def generate_methodology_section(
        self,
        progress_callback=None
    ) -> str:
        """
        Metodoloji bölümü üret (detaylı)
        
        Args:
            progress_callback: İlerleme callback'i
            
        Returns:
            Metodoloji metni
        """
        if progress_callback:
            progress_callback("Metodoloji bölümü üretiliyor...")
        
        prompt = """
ESG karbon ayak izi raporu için detaylı metodoloji bölümü yaz.

Bölüm şunları içermeli:
1. Hesaplama Standardı: GHG Protocol Corporate Accounting and Reporting Standard (400-500 kelime)
2. Emission Factor Kaynağı: Climatiq API ve veri kaynakları (300-400 kelime)
3. Hesaplama Metodolojisi: Formüller ve örnekler (300-400 kelime)
4. Scope Tanımları: Detaylı açıklamalar (400-500 kelime)
5. Veri Kalitesi: Değerlendirme ve sınırlamalar (300-400 kelime)
6. Belirsizlik Analizi: İstatistiksel değerlendirme (200-300 kelime)

Lütfen profesyonel, akademik bir metodoloji bölümü yaz (toplam 2000-2500 kelime).
"""
        
        content = self.qwen.generate_content(
            prompt=prompt,
            max_tokens=5000,
            min_words=2000
        )
        
        self.generated_sections['methodology'] = content
        return content
    
    def generate_all_sections(
        self,
        company_name: str,
        reporting_period: str,
        results: List[Dict],
        scope_summary: Dict[str, float],
        total_emissions: float,
        ml_results: Optional[Dict] = None,
        progress_callback=None
    ) -> Dict[str, str]:
        """
        Tüm bölümleri üret (parça parça)
        
        Args:
            company_name: Şirket adı
            reporting_period: Raporlama dönemi
            results: Emisyon sonuçları
            scope_summary: Scope özeti
            total_emissions: Toplam emisyon
            ml_results: ML analiz sonuçları
            progress_callback: İlerleme callback'i
            
        Returns:
            Tüm bölümlerin dict'i
        """
        all_sections = {}
        
        # 1. Yönetici özeti
        all_sections['executive_summary'] = self.generate_executive_summary(
            company_name, reporting_period, scope_summary, total_emissions, ml_results, progress_callback
        )
        
        # 2. Performans analizleri (her scope için)
        for scope, value in scope_summary.items():
            if value > 0:
                key = f'performance_{scope.lower().replace(" ", "_")}'
                all_sections[key] = self.generate_performance_analysis(
                    scope, value, total_emissions, results, progress_callback
                )
        
        # 3. Kritik aktivite analizi
        top_activities = sorted(results, key=lambda x: x.get('co2e_ton', 0), reverse=True)[:10]
        if top_activities:
            all_sections['critical_activities'] = self.generate_critical_activities_analysis(
                top_activities, progress_callback
            )
        
        # 4. İyileştirme önerileri
        all_sections['recommendations'] = self.generate_recommendations(
            scope_summary, total_emissions, ml_results, progress_callback
        )
        
        # 5. Risk analizi
        all_sections['risk_assessment'] = self.generate_risk_assessment(
            scope_summary, total_emissions, progress_callback
        )
        
        # 6. Metodoloji
        all_sections['methodology'] = self.generate_methodology_section(progress_callback)
        
        return all_sections

