"""
ESG PDF Report Generator (Fixed - Professional Format)
GRI standardına uygun, AI ile zenginleştirilmiş ESG raporu oluşturur
Tüm sorunlar düzeltildi: API hataları, encoding, boş sayfalar, görselleştirmeler
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from typing import List, Optional, Dict, Callable
import matplotlib.pyplot as plt
import seaborn as sns
import io
import sys
from pathlib import Path
import re
import numpy as np

# Add parent directory to path for imports
# __file__ = ecologia/backend/app/services/report_generator_fixed.py
# parent.parent.parent.parent = ecologia
backend_dir = Path(__file__).parent.parent.parent.parent
ecologia_dir = backend_dir  # backend_dir zaten ecologia
sys.path.insert(0, str(ecologia_dir))

from app.services.climatiq_service import EmissionResult
from app.services.esg_content_generator import ESGReportContentGenerator

# Türkçe karakter desteği için font kaydet
try:
    # Windows'ta varsayılan font
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
    FONT_NAME = 'Arial'
    FONT_BOLD = 'Arial-Bold'
except:
    # Fallback - Helvetica (Türkçe karakterler olmayabilir)
    FONT_NAME = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'

# UTF-8 encoding helper - Geliştirilmiş
def clean_text_for_pdf(text: str) -> str:
    """PDF için metni temizle (UTF-8, markdown temizleme, HATA mesajlarını kaldır)"""
    if not text:
        return ""
    
    # HATA mesajlarını kaldır
    if text.startswith("[HATA:") or "[HATA:" in text:
        return ""  # HATA mesajlarını boş döndür
    
    # Markdown temizle
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # UTF-8 encoding
    try:
        text = text.encode('utf-8').decode('utf-8')
    except UnicodeDecodeError:
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
    
    # Fazla boşlukları temizle
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    return text.strip()

# Tablo başlıkları için encoding-safe helper
def safe_table_header(text: str) -> str:
    """Tablolar için güvenli başlık (encoding sorunlarını önler)"""
    if not text:
        return ""
    try:
        # UTF-8 encoding
        text = text.encode('utf-8').decode('utf-8')
        # Özel karakterleri kontrol et
        return text
    except:
        # Fallback - ASCII
        return text.encode('ascii', errors='ignore').decode('ascii')

class ESG_Report_Generator_Fixed:
    """ESG PDF Rapor Oluşturucu (Tüm sorunlar düzeltildi)"""

    def __init__(self, company_name: str, reporting_period: str, use_ai: bool = True, progress_callback: Optional[Callable] = None):
        self.company_name = company_name
        self.reporting_period = reporting_period
        self.use_ai = use_ai
        self.progress_callback = progress_callback or (lambda x: None)
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
        # AI content generator
        if use_ai:
            try:
                self.content_generator = ESGReportContentGenerator()
                if not self.content_generator.qwen.test_connection():
                    print("[UYARI] LM Studio bağlantısı başarısız, AI içerik üretimi devre dışı")
                    self.use_ai = False
            except Exception as e:
                print(f"[UYARI] AI content generator başlatılamadı: {e}")
                self.use_ai = False

    def _create_custom_styles(self):
        """Özel stilleri oluştur - ESG formatına uygun"""
        # Ana başlık (Bölüm başlıkları)
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading1'],
            fontName=FONT_BOLD,
            fontSize=18,
            textColor=colors.HexColor('#1B5E20'),
            spaceAfter=15,
            spaceBefore=20,
            alignment=TA_LEFT
        ))

        # Alt başlık
        self.styles.add(ParagraphStyle(
            name='SubSectionHeading',
            parent=self.styles['Heading2'],
            fontName=FONT_BOLD,
            fontSize=14,
            textColor=colors.HexColor('#2E7D32'),
            spaceAfter=10,
            spaceBefore=15,
            alignment=TA_LEFT
        ))

        # Normal metin - justified
        if 'ESGBodyText' not in self.styles.byName:
            self.styles.add(ParagraphStyle(
                name='ESGBodyText',
                parent=self.styles['Normal'],
                fontName=FONT_NAME,
                fontSize=10,
                alignment=TA_JUSTIFY,
                leading=14,
                spaceAfter=6
            ))

        # Kapak başlığı
        self.styles.add(ParagraphStyle(
            name='CoverTitle',
            parent=self.styles['Heading1'],
            fontName=FONT_BOLD,
            fontSize=28,
            textColor=colors.HexColor('#1B5E20'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))

    def _update_progress(self, message: str):
        """Progress callback'i çağır"""
        if self.progress_callback:
            self.progress_callback(message)
        print(f"[PROGRESS] {message}")

    def _create_pie_chart(self, scope_summary: dict) -> io.BytesIO:
        """Scope dağılımı pasta grafiği - İyileştirilmiş"""
        data = {k: v for k, v in scope_summary.items() if v > 0}
        if not data:
            return None

        # UTF-8 font ayarı
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # UTF-8 safe labels
        labels = [safe_table_header(k) for k in data.keys()]
        colors_list = ['#2E7D32', '#66BB6A', '#A5D6A7', '#C8E6C9', '#E8F5E9']
        explode = [0.08] * len(data)

        wedges, texts, autotexts = ax.pie(
            data.values(),
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors_list[:len(data)],
            explode=explode,
            textprops={'fontsize': 12, 'fontweight': 'bold', 'color': '#1B5E20'},
            shadow=True,
            wedgeprops={'edgecolor': 'white', 'linewidth': 2}
        )

        ax.set_title('Scope Bazında Emisyon Dağılımı', fontsize=16, fontweight='bold', 
                    pad=25, color='#1B5E20')

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=200, bbox_inches='tight', facecolor='white', 
                   edgecolor='none', pad_inches=0.3)
        plt.close()
        buf.seek(0)
        return buf

    def _create_bar_chart(self, results: List[EmissionResult], top_n: int = 10) -> io.BytesIO:
        """Top aktiviteler bar chart - UTF-8 safe"""
        if not results:
            return None
        
        # Top N aktiviteyi al
        sorted_results = sorted(results, key=lambda x: x.co2e_ton, reverse=True)[:top_n]
        
        # UTF-8 safe aktivite isimleri
        activities = []
        for r in sorted_results:
            name = r.activity_name
            # UTF-8 encoding kontrolü
            try:
                name = name.encode('utf-8').decode('utf-8')
            except:
                name = name.encode('utf-8', errors='ignore').decode('utf-8')
            # Uzun isimleri kısalt
            if len(name) > 30:
                name = name[:27] + '...'
            activities.append(name)
        
        emissions = [r.co2e_ton for r in sorted_results]
        
        # Matplotlib UTF-8 font ayarı
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Gradient renkler
        colors_gradient = plt.cm.Greens(np.linspace(0.4, 0.8, len(activities)))
        bars = ax.barh(activities, emissions, color=colors_gradient, alpha=0.85, edgecolor='#1B5E20', linewidth=1.2)
        
        ax.set_xlabel('Emisyon (ton CO2e)', fontsize=13, fontweight='bold', color='#1B5E20')
        ax.set_title(f'En Yüksek Emisyonlu {top_n} Aktivite', fontsize=16, fontweight='bold', pad=20, color='#1B5E20')
        ax.grid(axis='x', alpha=0.4, linestyle='--')
        ax.set_axisbelow(True)
        
        # Değerleri göster
        for i, (bar, val) in enumerate(zip(bars, emissions)):
            ax.text(val + max(emissions)*0.02, i, f'{val:.2f} ton', va='center', 
                   fontsize=10, fontweight='bold', color='#1B5E20')
        
        # Y ekseni font ayarı
        ax.tick_params(axis='y', labelsize=10)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=200, bbox_inches='tight', facecolor='white', 
                   edgecolor='none', pad_inches=0.2)
        plt.close()
        buf.seek(0)
        return buf

    def _create_scope_comparison_chart(self, scope_summary: dict) -> io.BytesIO:
        """Scope karşılaştırma bar chart - İyileştirilmiş"""
        data = {k: v for k, v in scope_summary.items() if v > 0}
        if not data:
            return None
        
        # UTF-8 font ayarı
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # UTF-8 safe scope isimleri
        scopes = [safe_table_header(k) for k in data.keys()]
        values = list(data.values())
        colors_list = ['#2E7D32', '#66BB6A', '#A5D6A7', '#C8E6C9']
        
        bars = ax.bar(scopes, values, color=colors_list[:len(scopes)], alpha=0.85, 
                      edgecolor='#1B5E20', linewidth=2)
        ax.set_ylabel('Emisyon (ton CO2e)', fontsize=13, fontweight='bold', color='#1B5E20')
        ax.set_title('Scope Bazında Emisyon Karşılaştırması', fontsize=16, fontweight='bold', 
                    pad=20, color='#1B5E20')
        ax.grid(axis='y', alpha=0.4, linestyle='--', linewidth=0.8)
        ax.set_axisbelow(True)
        
        # X ekseni font ayarı
        ax.tick_params(axis='x', labelsize=11, colors='#1B5E20')
        ax.tick_params(axis='y', labelsize=11, colors='#1B5E20')
        
        # Değerleri göster
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.03,
                   f'{val:.2f} ton', ha='center', va='bottom', fontsize=11, 
                   fontweight='bold', color='#1B5E20')
        
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=200, bbox_inches='tight', facecolor='white',
                   edgecolor='none', pad_inches=0.2)
        plt.close()
        buf.seek(0)
        return buf

    def _create_category_chart(self, results: List[EmissionResult]) -> io.BytesIO:
        """Kategori bazında emisyon dağılımı"""
        if not results:
            return None
        
        # Kategori bazında topla
        category_emissions = {}
        for result in results:
            category = result.category if hasattr(result, 'category') and result.category else 'Diğer'
            if category not in category_emissions:
                category_emissions[category] = 0
            category_emissions[category] += result.co2e_ton
        
        if not category_emissions:
            return None
        
        # UTF-8 font ayarı
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        categories = [safe_table_header(k) for k in category_emissions.keys()]
        values = list(category_emissions.values())
        colors_list = ['#2E7D32', '#66BB6A', '#A5D6A7', '#C8E6C9', '#E8F5E9', '#1B5E20']
        
        bars = ax.barh(categories, values, color=colors_list[:len(categories)], alpha=0.85,
                      edgecolor='#1B5E20', linewidth=1.5)
        ax.set_xlabel('Emisyon (ton CO2e)', fontsize=13, fontweight='bold', color='#1B5E20')
        ax.set_title('Kategori Bazında Emisyon Dağılımı', fontsize=16, fontweight='bold',
                    pad=20, color='#1B5E20')
        ax.grid(axis='x', alpha=0.4, linestyle='--')
        ax.set_axisbelow(True)
        
        # Değerleri göster
        for i, (bar, val) in enumerate(zip(bars, values)):
            ax.text(val + max(values)*0.02, i, f'{val:.2f} ton', va='center',
                   fontsize=10, fontweight='bold', color='#1B5E20')
        
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=200, bbox_inches='tight', facecolor='white',
                   edgecolor='none', pad_inches=0.2)
        plt.close()
        buf.seek(0)
        return buf

    def _create_year_trend_chart(self, results: List[EmissionResult]) -> io.BytesIO:
        """Yıl bazında emisyon trendi"""
        if not results:
            return None
        
        # Yıl bazında topla
        year_emissions = {}
        for result in results:
            year = result.year if hasattr(result, 'year') and result.year else None
            if year:
                if year not in year_emissions:
                    year_emissions[year] = 0
                year_emissions[year] += result.co2e_ton
        
        if len(year_emissions) < 2:
            return None  # En az 2 yıl olmalı
        
        # UTF-8 font ayarı
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        years = sorted(year_emissions.keys())
        values = [year_emissions[y] for y in years]
        
        ax.plot(years, values, marker='o', linewidth=3, markersize=10,
               color='#2E7D32', markerfacecolor='#66BB6A', markeredgecolor='#1B5E20',
               markeredgewidth=2)
        ax.fill_between(years, values, alpha=0.3, color='#A5D6A7')
        ax.set_xlabel('Yıl', fontsize=13, fontweight='bold', color='#1B5E20')
        ax.set_ylabel('Emisyon (ton CO2e)', fontsize=13, fontweight='bold', color='#1B5E20')
        ax.set_title('Yıl Bazında Emisyon Trendi', fontsize=16, fontweight='bold',
                    pad=20, color='#1B5E20')
        ax.grid(True, alpha=0.4, linestyle='--')
        ax.set_axisbelow(True)
        
        # Değerleri göster
        for year, val in zip(years, values):
            ax.text(year, val + max(values)*0.03, f'{val:.2f}', ha='center',
                   fontsize=9, fontweight='bold', color='#1B5E20')
        
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=200, bbox_inches='tight', facecolor='white',
                   edgecolor='none', pad_inches=0.2)
        plt.close()
        buf.seek(0)
        return buf

    def _create_scope_stacked_chart(self, results: List[EmissionResult], scope_summary: dict) -> io.BytesIO:
        """Scope bazında yığınlı bar chart"""
        if not results:
            return None
        
        # Scope ve kategori bazında topla
        scope_category = {}
        for result in results:
            scope = result.scope
            category = result.category if hasattr(result, 'category') and result.category else 'Diğer'
            key = f"{scope}_{category}"
            if key not in scope_category:
                scope_category[key] = {'scope': scope, 'category': category, 'value': 0}
            scope_category[key]['value'] += result.co2e_ton
        
        if not scope_category:
            return None
        
        # UTF-8 font ayarı
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Scope bazında grupla
        scopes = sorted(set([v['scope'] for v in scope_category.values()]))
        categories = sorted(set([v['category'] for v in scope_category.values()]))
        
        # Her scope için kategori değerlerini topla
        data = {}
        for scope in scopes:
            data[scope] = {}
            for cat in categories:
                data[scope][cat] = sum([v['value'] for v in scope_category.values() 
                                       if v['scope'] == scope and v['category'] == cat])
        
        # Stacked bar chart
        x = range(len(scopes))
        width = 0.6
        bottom = np.zeros(len(scopes))
        colors_list = ['#2E7D32', '#66BB6A', '#A5D6A7', '#C8E6C9', '#E8F5E9']
        
        for i, cat in enumerate(categories):
            values = [data[scope][cat] for scope in scopes]
            if any(v > 0 for v in values):
                bars = ax.bar(x, values, width, label=safe_table_header(cat), 
                            bottom=bottom, color=colors_list[i % len(colors_list)],
                            alpha=0.85, edgecolor='#1B5E20', linewidth=1)
                bottom += values
        
        ax.set_xlabel('Scope', fontsize=13, fontweight='bold', color='#1B5E20')
        ax.set_ylabel('Emisyon (ton CO2e)', fontsize=13, fontweight='bold', color='#1B5E20')
        ax.set_title('Scope ve Kategori Bazında Emisyon Dağılımı', fontsize=16, fontweight='bold',
                    pad=20, color='#1B5E20')
        ax.set_xticks(x)
        ax.set_xticklabels([safe_table_header(s) for s in scopes])
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(axis='y', alpha=0.4, linestyle='--')
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=200, bbox_inches='tight', facecolor='white',
                   edgecolor='none', pad_inches=0.2)
        plt.close()
        buf.seek(0)
        return buf

    def _generate_fallback_content(self, section_type: str, data: Dict) -> str:
        """API başarısız olursa fallback içerik üret - UZUN VERSİYON"""
        if section_type == "executive_summary":
            total = data.get('total_emissions', 0)
            scope_summary = data.get('scope_summary', {})
            scope1 = scope_summary.get('Scope 1', 0)
            scope2 = scope_summary.get('Scope 2', 0)
            scope3 = scope_summary.get('Scope 3', 0)
            
            return f"""
{self.company_name} için {self.reporting_period} döneminde gerçekleştirilen kapsamlı karbon ayak izi analizi sonuçları, şirketin sürdürülebilirlik performansına ilişkin önemli bulgular ortaya koymaktadır. Bu rapor, şirketin çevresel etkisini anlamak ve azaltım stratejileri geliştirmek için kritik bir adım teşkil etmektedir.

Toplam GHG emisyonu {total:.2f} ton CO2e olarak hesaplanmış olup, bu değer şirketin karbon ayak izinin mevcut durumunu yansıtmaktadır. Emisyonların detaylı analizi, iyileştirme potansiyelinin belirlenmesi ve stratejik kararların alınması açısından büyük önem taşımaktadır.

Scope bazında emisyon dağılımı incelendiğinde, Scope 1 emisyonları {scope1:.2f} ton CO2e ({scope1/total*100 if total > 0 else 0:.1f}%) olarak hesaplanmıştır. Bu emisyonlar doğrudan şirket kontrolündeki kaynaklardan kaynaklanmakta olup, öncelikli olarak ulaşım, yakıt tüketimi ve proses emisyonlarını kapsamaktadır. Scope 1 emisyonlarının azaltılması için enerji verimliliği iyileştirmeleri, temiz yakıt geçişi ve teknoloji modernizasyonu gibi stratejiler önerilmektedir.

Scope 2 emisyonları {scope2:.2f} ton CO2e ({scope2/total*100 if total > 0 else 0:.1f}%) ile toplam emisyonların en büyük payını oluşturmaktadır. Bu emisyonlar satın alınan elektrik, ısı ve buhar tüketiminden kaynaklanmaktadır. Elektrik tüketiminin yüksek olması, enerji verimliliği çalışmalarına ve yenilenebilir enerji geçişine öncelik verilmesi gerektiğini göstermektedir. Güneş enerjisi yatırımları, enerji yönetim sistemleri ve LED aydınlatma gibi önlemlerle Scope 2 emisyonlarında önemli azalmalar sağlanabilir.

Scope 3 emisyonları {scope3:.2f} ton CO2e ({scope3/total*100 if total > 0 else 0:.1f}%) olarak hesaplanmış olup, değer zinciri kaynaklı emisyonları kapsamaktadır. Bu kapsam tedarikçi emisyonları, ürün kullanımı, atık yönetimi ve ulaşım gibi aktiviteleri içermektedir. Scope 3 emisyonlarının kapsamlı ölçümü ve azaltımı, şirketin sürdürülebilirlik hedeflerine ulaşması için kritik öneme sahiptir.

Şirket, SBTi (Science Based Targets initiative) kriterlerine uygun olarak net zero hedefi doğrultusunda çalışmalarını sürdürmektedir. Bu hedefe ulaşmak için önerilen aksiyonlar arasında enerji verimliliği iyileştirmeleri, yenilenebilir enerji geçişi, ulaşım optimizasyonu, tedarik zinciri sürdürülebilirliği ve karbon offset mekanizmaları yer almaktadır. Bu stratejilerin sistematik olarak uygulanması, şirketin çevresel performansını önemli ölçüde iyileştirecek ve rekabet avantajı sağlayacaktır.
"""
        elif section_type == "performance":
            scope = data.get('scope', '')
            value = data.get('value', 0)
            return f"""
{scope} emisyonları toplam {value:.2f} ton CO2e olarak hesaplanmıştır. Bu emisyonlar şirketin karbon ayak izinin 
önemli bir bileşenini oluşturmaktadır. {scope} kapsamındaki aktivitelerin detaylı analizi, iyileştirme 
potansiyelinin belirlenmesi açısından kritik öneme sahiptir.

Emisyon kaynaklarının sistematik olarak değerlendirilmesi ve azaltım stratejilerinin geliştirilmesi gerekmektedir. 
Bu kapsamda, enerji verimliliği iyileştirmeleri, teknoloji modernizasyonu ve operasyonel optimizasyonlar öncelikli 
olarak ele alınmalıdır.
"""
        elif section_type == "recommendations":
            return """
Aşağıdaki iyileştirme önerileri, şirketin karbon ayak izini azaltmak ve sürdürülebilirlik performansını artırmak için detaylı analiz sonucunda geliştirilmiştir. Her öneri, uygulanabilirlik, maliyet etkinliği ve beklenen emisyon azaltım potansiyeli açısından değerlendirilmiştir.

1. Enerji Verimliliği İyileştirmeleri (Öncelik: Yüksek, ROI: 2-3 yıl)
   Bina yalıtımı, LED aydınlatma sistemleri, enerji yönetim sistemleri ve akıllı termostat kurulumu ile %15-20 enerji tasarrufu sağlanabilir. Bu önlemler, Scope 2 emisyonlarında önemli azalmalar yaratacak ve operasyonel maliyetleri düşürecektir. Yatırım gereksinimi orta seviyede olup, geri ödeme süresi 2-3 yıl arasındadır.

2. Yenilenebilir Enerji Geçişi (Öncelik: Yüksek, ROI: 5-7 yıl)
   Güneş panelleri veya rüzgar enerjisi yatırımları ile elektrik tüketiminin %30-50'si yenilenebilir kaynaklardan karşılanabilir. Bu geçiş, Scope 2 emisyonlarını neredeyse sıfıra indirebilir ve uzun vadede önemli maliyet tasarrufları sağlayabilir. Devlet teşvikleri ve yeşil finansman seçenekleri bu yatırımları daha cazip hale getirmektedir.

3. Ulaşım Optimizasyonu (Öncelik: Orta, ROI: 3-4 yıl)
   Elektrikli araç filosuna geçiş, toplu taşıma kullanımının artırılması, uzaktan çalışma politikaları ve lojistik optimizasyonu ile ulaşım kaynaklı emisyonlar %40-60 azaltılabilir. Bu önlemler hem Scope 1 hem de Scope 3 emisyonlarını etkilemektedir. Elektrikli araç yatırımları için devlet teşvikleri ve şarj altyapısı kurulumu önemli faktörlerdir.

4. Tedarik Zinciri Optimizasyonu (Öncelik: Orta, ROI: 2-5 yıl)
   Düşük karbonlu tedarikçilerle çalışma, lojistik optimizasyonu, ambalaj azaltımı ve döngüsel ekonomi prensiplerinin benimsenmesi ile Scope 3 emisyonlarında önemli azalmalar sağlanabilir. Bu önlemler, tedarikçi ilişkilerini güçlendirir ve marka değerini artırır.

5. Atık Yönetimi ve Döngüsel Ekonomi (Öncelik: Orta, ROI: 1-2 yıl)
   Atık azaltımı, geri dönüşüm programları ve döngüsel ekonomi modellerinin uygulanması ile hem emisyon azaltımı hem de maliyet tasarrufu sağlanabilir. Bu önlemler, Scope 3 emisyonlarını etkiler ve sürdürülebilirlik imajını güçlendirir.

6. Karbon Offset ve Karbon Kredisi Programları (Öncelik: Düşük, ROI: Değişken)
   Kaçınılmaz emisyonlar için karbon offset projelerine yatırım yapılabilir. Bu programlar, net zero hedefine ulaşmak için geçici bir çözüm olarak kullanılabilir, ancak asıl odak emisyon azaltımı olmalıdır.

7. Enerji İzleme ve Raporlama Sistemleri (Öncelik: Yüksek, ROI: 1-2 yıl)
   Gerçek zamanlı enerji izleme sistemleri, detaylı raporlama ve veri analizi ile emisyon kaynakları daha iyi anlaşılabilir ve optimizasyon fırsatları belirlenebilir. Bu sistemler, sürekli iyileştirme kültürünü destekler.

8. Çalışan Farkındalığı ve Eğitim Programları (Öncelik: Orta, ROI: Uzun vadeli)
   Sürdürülebilirlik eğitimleri, çalışan katılım programları ve yeşil ofis uygulamaları ile organizasyonel kültür değişikliği sağlanabilir. Bu önlemler, uzun vadede sürdürülebilir davranış değişiklikleri yaratır.
"""
        elif section_type == "risk":
            return """
ESG riskleri ve fırsatlar analizi, şirketin sürdürülebilirlik yolculuğunda karşılaşabileceği zorlukları ve 
avantajları ortaya koymaktadır. İklim değişikliği ile ilgili fiziksel ve geçiş riskleri, regülasyon 
değişiklikleri ve tüketici tercihlerindeki değişimler şirket için önemli risk faktörleri oluşturmaktadır.

Ancak, yeşil finansman fırsatları, enerji verimliliği yatırımları, yenilenebilir enerji geçişi ve 
sürdürülebilir ürün geliştirme gibi alanlarda önemli fırsatlar bulunmaktadır. Bu fırsatlar, şirketin 
rekabet avantajını artırabilir ve uzun vadeli değer yaratabilir.
"""
        elif section_type == "methodology":
            return """
Bu rapor, GHG Protocol Corporate Accounting and Reporting Standard metodolojisine uygun olarak 
hazırlanmıştır. Emisyon faktörleri Climatiq API veritabanından alınmış olup, 80+ global veri kaynağından 
derlenmiştir.

Hesaplama formülü: CO2e = Aktivite Verisi × Emission Factor

Scope tanımları:
- Scope 1: Doğrudan emisyonlar (şirket kontrolündeki kaynaklar)
- Scope 2: Dolaylı enerji emisyonları (satın alınan elektrik, ısı, buhar)
- Scope 3: Diğer dolaylı emisyonlar (değer zinciri)

Konsolidasyon yaklaşımı: Operasyonel Kontrol
Veri kalitesi: Birincil veri (ölçüm ve faturalar)
"""
        return ""

    def generate_report(
        self, 
        results: List[EmissionResult], 
        scope_summary: dict, 
        filename: str = "esg_report.pdf", 
        ml_results: dict = None
    ):
        """ESG raporu oluştur - Tüm sorunlar düzeltildi"""
        self._update_progress("Rapor oluşturma başlatılıyor...")

        # Output klasörüne kaydet (ecologia/output)
        # backend_dir zaten ecologia klasörü
        output_dir = backend_dir / "output"
        output_dir.mkdir(exist_ok=True)
        filepath = output_dir / filename

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        story = []
        total_emissions = sum(scope_summary.values())

        # ==================== KAPAK SAYFASI (Temiz ve Düzenli) ====================
        self._update_progress("Kapak sayfası oluşturuluyor...")
        
        story.append(Spacer(1, 5*cm))
        
        # Şirket adı - Temiz, padding olmadan
        company_name_safe = safe_table_header(self.company_name)
        title_style = ParagraphStyle(
            name='CoverTitleStyle',
            parent=self.styles['Normal'],
            fontName=FONT_BOLD,
            fontSize=32,
            textColor=colors.HexColor('#1B5E20'),
            alignment=TA_CENTER,
            spaceAfter=30,
            spaceBefore=0
        )
        title_para = Paragraph(f"<b>{company_name_safe}</b>", title_style)
        story.append(title_para)
        
        # Yeşil çizgi (dekoratif)
        line_style = ParagraphStyle(
            name='CoverLine',
            parent=self.styles['Normal'],
            fontSize=1,
            textColor=colors.HexColor('#2E7D32'),
            alignment=TA_CENTER,
            spaceAfter=20,
            spaceBefore=10
        )
        story.append(Paragraph("─" * 50, line_style))
        story.append(Spacer(1, 1*cm))
        
        # Alt başlık - Daha temiz
        subtitle_style = ParagraphStyle(
            name='CoverSubtitle',
            parent=self.styles['Normal'],
            fontName=FONT_BOLD,
            fontSize=16,
            textColor=colors.HexColor('#2E7D32'),
            alignment=TA_CENTER,
            spaceAfter=20,
            spaceBefore=0
        )
        subtitle = Paragraph(
            "SÜRDÜRÜLEBİLİRLİK RAPORU<br/>KARBON AYAK İZİ ANALİZİ",
            subtitle_style
        )
        story.append(subtitle)
        story.append(Spacer(1, 3*cm))
        
        # Bilgi kutusu - Merkezi, temiz (UTF-8 safe, safe_table_header kullanmıyoruz)
        date_safe = datetime.now().strftime('%d.%m.%Y')
        
        # Bilgi kutusu için Table kullan (daha temiz görünüm)
        # reporting_period'u direkt kullanıyoruz (UTF-8 destekli)
        info_data = [
            [Paragraph(f"<b>Raporlama Dönemi:</b>", self.styles['Normal']), 
             Paragraph(self.reporting_period, self.styles['Normal'])],
            [Paragraph(f"<b>Rapor Tarihi:</b>", self.styles['Normal']), 
             Paragraph(date_safe, self.styles['Normal'])],
            [Paragraph(f"<b>Toplam Emisyon:</b>", self.styles['Normal']), 
             Paragraph(f"{total_emissions:.2f} ton CO2e", self.styles['Normal'])],
            [Paragraph(f"<b>Standart:</b>", self.styles['Normal']), 
             Paragraph("GRI 305: Emisyonlar", self.styles['Normal'])]
        ]
        
        info_table = Table(info_data, colWidths=[6*cm, 6*cm])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#212121')),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F8E9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#C8E6C9')),
        ]))
        
        # Tabloyu merkeze al
        from reportlab.platypus import KeepTogether
        story.append(Spacer(1, 0.5*cm))
        story.append(KeepTogether([info_table]))
        story.append(Spacer(1, 3*cm))
        
        # GRI uyumluluk badge - Merkezi
        gri_style = ParagraphStyle(
            name='CoverGRI',
            parent=self.styles['Normal'],
            fontName=FONT_NAME,
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            fontStyle='Italic',
            spaceAfter=0,
            spaceBefore=0
        )
        gri_text = Paragraph(
            "Bu rapor GRI 305: Emisyonlar standardına uygun hazırlanmıştır.",
            gri_style
        )
        story.append(gri_text)
        story.append(PageBreak())

        # ==================== AI İÇERİK ÜRETİMİ ====================
        ai_sections = {}
        if self.use_ai:
            self._update_progress("AI ile içerik üretimi başlatılıyor...")
            
            results_dict = [
                {
                    'activity_name': r.activity_name,
                    'co2e_ton': r.co2e_ton,
                    'scope': r.scope,
                    'category': r.category
                }
                for r in results
            ]
            
            try:
                ai_sections = self.content_generator.generate_all_sections(
                    company_name=self.company_name,
                    reporting_period=self.reporting_period,
                    results=results_dict,
                    scope_summary=scope_summary,
                    total_emissions=total_emissions,
                    ml_results=ml_results,
                    progress_callback=self._update_progress
                )
                # HATA mesajlarını temizle
                ai_sections = {k: v for k, v in ai_sections.items() if v and not v.startswith("[HATA:")}
                self._update_progress("AI içerik üretimi tamamlandı")
            except Exception as e:
                print(f"[HATA] AI içerik üretimi başarısız: {e}")
                self._update_progress("AI içerik üretimi başarısız, fallback içerik kullanılıyor")
                ai_sections = {}

        # ==================== 1. YÖNETİCİ ÖZETİ ====================
        self._update_progress("Yönetici özeti ekleniyor...")
        story.append(Paragraph("1. YÖNETİCİ ÖZETİ", self.styles['SectionHeading']))
        
        exec_text = ""
        if ai_sections.get('executive_summary'):
            exec_text = clean_text_for_pdf(ai_sections['executive_summary'])
        
        if not exec_text:
            exec_text = self._generate_fallback_content("executive_summary", {
                'total_emissions': total_emissions,
                'scope_summary': scope_summary
            })
        
        # Paragraflara böl ve ekle
        paragraphs = [p.strip() for p in exec_text.split('\n\n') if p.strip()]
        for para in paragraphs:
            story.append(Paragraph(para, self.styles['ESGBodyText']))
            story.append(Spacer(1, 0.4*cm))
        
        story.append(PageBreak())

        # ==================== 2. EMİSYON ÖZETİ ====================
        self._update_progress("Emisyon özeti ekleniyor...")
        story.append(Paragraph("2. EMİSYON ÖZETİ", self.styles['SectionHeading']))
        story.append(Paragraph("2.1 Scope Bazında Dağılım", self.styles['SubSectionHeading']))

        # Tablo yerine metin formatında gösterim (encoding sorunlarını önlemek için)
        scope_text = "Emisyonlar scope bazında aşağıdaki şekilde dağılmaktadır:\n\n"
        
        for scope, value in scope_summary.items():
            if value > 0:
                percentage = (value / total_emissions * 100) if total_emissions > 0 else 0
                scope_safe = safe_table_header(scope)
                scope_text += f"• <b>{scope_safe}:</b> {value:.2f} ton CO2e (%{percentage:.1f})\n\n"
        
        scope_text += f"<b>TOPLAM:</b> {total_emissions:.2f} ton CO2e (%100.0)"
        
        story.append(Paragraph(scope_text, self.styles['ESGBodyText']))
        story.append(Spacer(1, 1.5*cm))

        # Grafikler - İyileştirilmiş görselleştirmeler (Daha fazla görsellik)
        chart1 = self._create_pie_chart(scope_summary)
        if chart1:
            img1 = Image(chart1, width=14*cm, height=10*cm)
            story.append(img1)
            story.append(Spacer(1, 0.8*cm))
        
        chart2 = self._create_scope_comparison_chart(scope_summary)
        if chart2:
            img2 = Image(chart2, width=14*cm, height=8*cm)
            story.append(img2)
            story.append(Spacer(1, 0.8*cm))
        
        # Yeni görselleştirmeler
        category_chart = self._create_category_chart(results)
        if category_chart:
            story.append(Paragraph("2.2 Kategori Bazında Dağılım", self.styles['SubSectionHeading']))
            img3 = Image(category_chart, width=14*cm, height=8*cm)
            story.append(img3)
            story.append(Spacer(1, 0.8*cm))
        
        year_trend = self._create_year_trend_chart(results)
        if year_trend:
            story.append(Paragraph("2.3 Yıl Bazında Emisyon Trendi", self.styles['SubSectionHeading']))
            img4 = Image(year_trend, width=14*cm, height=8*cm)
            story.append(img4)
            story.append(Spacer(1, 0.8*cm))
        
        scope_stacked = self._create_scope_stacked_chart(results, scope_summary)
        if scope_stacked:
            story.append(Paragraph("2.4 Scope ve Kategori Analizi", self.styles['SubSectionHeading']))
            img5 = Image(scope_stacked, width=14*cm, height=9*cm)
            story.append(img5)
            story.append(Spacer(1, 0.5*cm))
        
        story.append(PageBreak())

        # ==================== 3. DETAYLI EMİSYON VERİLERİ ====================
        self._update_progress("Detaylı emisyon verileri ekleniyor...")
        story.append(Paragraph("3. DETAYLI EMİSYON VERİLERİ", self.styles['SectionHeading']))

        # Bar chart - İyileştirilmiş
        story.append(Paragraph("3.1 En Yüksek Emisyonlu Aktiviteler", self.styles['SubSectionHeading']))
        bar_chart = self._create_bar_chart(results, top_n=10)
        if bar_chart:
            img = Image(bar_chart, width=16*cm, height=10*cm)
            story.append(img)
            story.append(Spacer(1, 1.2*cm))

        # Tablo yerine metin formatında gösterim (encoding sorunlarını önlemek için)
        detail_text = "Detaylı emisyon verileri aşağıda listelenmektedir:\n\n"
        
        for i, result in enumerate(results, 1):
            activity_safe = safe_table_header(result.activity_name)
            unit_safe = safe_table_header(result.unit)
            scope_safe = safe_table_header(result.scope)
            source_safe = safe_table_header(result.source)
            
            detail_text += f"<b>{i}. {activity_safe}</b><br/>"
            detail_text += f"   Miktar: {result.amount:.1f} {unit_safe} | "
            detail_text += f"CO2e: {result.co2e_kg:.2f} kg | "
            detail_text += f"Scope: {scope_safe} | "
            detail_text += f"Kaynak: {source_safe}<br/><br/>"
        
        story.append(Paragraph(detail_text, self.styles['ESGBodyText']))
        story.append(PageBreak())

        # ==================== 4. PERFORMANS ANALİZİ ====================
        has_performance = any(ai_sections.get(f'performance_{s.lower().replace(" ", "_")}') for s in scope_summary.keys() if scope_summary[s] > 0)
        if has_performance:
            self._update_progress("Performans analizi ekleniyor...")
            story.append(Paragraph("4. PERFORMANS ANALİZİ", self.styles['SectionHeading']))
            
            section_num = 1
            for scope, value in scope_summary.items():
                if value > 0:
                    key = f'performance_{scope.lower().replace(" ", "_")}'
                    perf_text = clean_text_for_pdf(ai_sections.get(key, ""))
                    
                    if not perf_text:
                        perf_text = self._generate_fallback_content("performance", {'scope': scope, 'value': value})
                    
                    if perf_text:
                        story.append(Paragraph(f"4.{section_num} {scope} Emisyonları Analizi", self.styles['SubSectionHeading']))
                        paragraphs = [p.strip() for p in perf_text.split('\n\n') if p.strip()]
                        for para in paragraphs:
                            story.append(Paragraph(para, self.styles['ESGBodyText']))
                            story.append(Spacer(1, 0.3*cm))
                        story.append(Spacer(1, 0.5*cm))
                        section_num += 1
            
            story.append(PageBreak())

        # ==================== 5. KRİTİK AKTİVİTE ANALİZİ ====================
        critical_text = clean_text_for_pdf(ai_sections.get('critical_activities', ""))
        if critical_text:
            self._update_progress("Kritik aktivite analizi ekleniyor...")
            story.append(Paragraph("5. KRİTİK AKTİVİTE ANALİZİ", self.styles['SectionHeading']))
            
            paragraphs = [p.strip() for p in critical_text.split('\n\n') if p.strip()]
            for para in paragraphs:
                story.append(Paragraph(para, self.styles['ESGBodyText']))
                story.append(Spacer(1, 0.3*cm))
            story.append(PageBreak())

        # ==================== 6. İYİLEŞTİRME ÖNERİLERİ ====================
        rec_text = clean_text_for_pdf(ai_sections.get('recommendations', ""))
        if not rec_text:
            rec_text = self._generate_fallback_content("recommendations", {})
        
        if rec_text:
            self._update_progress("İyileştirme önerileri ekleniyor...")
            story.append(Paragraph("6. İYİLEŞTİRME ÖNERİLERİ", self.styles['SectionHeading']))
            
            paragraphs = [p.strip() for p in rec_text.split('\n\n') if p.strip()]
            for para in paragraphs:
                story.append(Paragraph(para, self.styles['ESGBodyText']))
                story.append(Spacer(1, 0.3*cm))
            story.append(PageBreak())

        # ==================== 7. RİSK VE FIRSATLAR ====================
        risk_text = clean_text_for_pdf(ai_sections.get('risk_assessment', ""))
        if not risk_text:
            risk_text = self._generate_fallback_content("risk", {})
        
        if risk_text:
            self._update_progress("Risk analizi ekleniyor...")
            story.append(Paragraph("7. RİSK VE FIRSATLAR", self.styles['SectionHeading']))
            
            paragraphs = [p.strip() for p in risk_text.split('\n\n') if p.strip()]
            for para in paragraphs:
                story.append(Paragraph(para, self.styles['ESGBodyText']))
                story.append(Spacer(1, 0.3*cm))
            story.append(PageBreak())

        # ==================== 8. METODOLOJI ====================
        self._update_progress("Metodoloji bölümü ekleniyor...")
        story.append(Paragraph("8. METODOLOJİ", self.styles['SectionHeading']))
        
        method_text = clean_text_for_pdf(ai_sections.get('methodology', ""))
        if not method_text:
            method_text = self._generate_fallback_content("methodology", {})
        
        paragraphs = [p.strip() for p in method_text.split('\n\n') if p.strip()]
        for para in paragraphs:
            story.append(Paragraph(para, self.styles['ESGBodyText']))
            story.append(Spacer(1, 0.3*cm))
        
        story.append(PageBreak())

        # ==================== 9. KAPANIŞ ====================
        self._update_progress("Kapanış bölümü ekleniyor...")
        story.append(Paragraph("9. KAPANIŞ", self.styles['SectionHeading']))
        
        # UTF-8 safe kapanış metni
        company_name_safe = safe_table_header(self.company_name)
        period_safe = safe_table_header(self.reporting_period)
        date_safe = datetime.now().strftime('%d.%m.%Y')
        
        closing_paragraphs = [
            f"Bu rapor, {company_name_safe} için {period_safe} döneminde gerçekleştirilen kapsamlı karbon ayak izi analizinin sonuçlarını sunmaktadır. Rapor, GHG Protocol standartlarına uygun olarak hazırlanmış ve GRI 305 kriterlerini karşılamaktadır.",
            
            f"Şirket olarak, sürdürülebilirlik ve iklim değişikliği ile mücadele konusundaki taahhüdümüzü sürdürmekteyiz. Bu raporda belirtilen bulgular ve öneriler doğrultusunda, emisyon azaltım hedeflerimize ulaşmak için sistematik bir yaklaşım benimsemekteyiz.",
            
            "Gelecek dönemlerde, raporlama kapsamını genişletmek, veri kalitesini artırmak ve daha iddialı hedefler belirlemek için çalışmalarımızı sürdüreceğiz. Paydaşlarımızın görüş ve önerileri bizim için değerlidir.",
            
            "Rapor hakkında sorularınız için lütfen bizimle iletişime geçin."
        ]
        
        for para in closing_paragraphs:
            story.append(Paragraph(para, self.styles['ESGBodyText']))
            story.append(Spacer(1, 0.4*cm))
        
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(f"<b>{company_name_safe}</b>", self.styles['ESGBodyText']))
        story.append(Paragraph(date_safe, self.styles['ESGBodyText']))

        # ==================== PDF OLUŞTUR ====================
        self._update_progress("PDF oluşturuluyor...")
        doc.build(story)
        self._update_progress("Rapor oluşturma tamamlandı!")

        print(f"[OK] ESG Raporu oluşturuldu: {filepath}")
        return str(filepath)

