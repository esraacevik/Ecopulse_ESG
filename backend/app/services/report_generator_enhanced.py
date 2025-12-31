"""
ESG PDF Report Generator (Enhanced with Qwen AI)
GRI standardına uygun, AI ile zenginleştirilmiş ESG raporu oluşturur
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

# Add parent directory to path for imports
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir.parent))

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

# UTF-8 encoding helper
def clean_text_for_pdf(text: str) -> str:
    """PDF için metni temizle (UTF-8, markdown temizleme)"""
    if not text:
        return ""
    
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

class ESG_Report_Generator_Enhanced:
    """ESG PDF Rapor Oluşturucu (Qwen AI ile zenginleştirilmiş)"""

    def __init__(self, company_name: str, reporting_period: str, use_ai: bool = True, progress_callback: Optional[Callable] = None):
        """
        Args:
            company_name: Şirket adı
            reporting_period: Raporlama dönemi
            use_ai: AI içerik üretimi kullan (Qwen)
            progress_callback: İlerleme callback'i (status: str) -> None
        """
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
                # Test connection
                if not self.content_generator.qwen.test_connection():
                    print("[UYARI] LM Studio bağlantısı başarısız, AI içerik üretimi devre dışı")
                    self.use_ai = False
            except Exception as e:
                print(f"[UYARI] AI content generator başlatılamadı: {e}")
                self.use_ai = False

    def _create_custom_styles(self):
        """Özel stilleri oluştur"""
        # Başlık stili
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontName=FONT_BOLD,
            fontSize=24,
            textColor=colors.HexColor('#2E7D32'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        # Alt başlık
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontName=FONT_BOLD,
            fontSize=16,
            textColor=colors.HexColor('#2E7D32'),
            spaceAfter=12,
            spaceBefore=12
        ))

        # Normal metin - Türkçe destekli, justified
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontName=FONT_NAME,
            fontSize=10,
            alignment=TA_JUSTIFY,
            leading=14
        ))

        # Body text (uzun metinler için)
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontName=FONT_NAME,
            fontSize=10,
            alignment=TA_JUSTIFY,
            leading=14,
            spaceAfter=6
        ))

    def _update_progress(self, message: str):
        """Progress callback'i çağır"""
        if self.progress_callback:
            self.progress_callback(message)
        print(f"[PROGRESS] {message}")

    def _create_pie_chart(self, scope_summary: dict) -> io.BytesIO:
        """Scope dağılımı pasta grafiği oluştur"""
        data = {k: v for k, v in scope_summary.items() if v > 0}
        if not data:
            return None

        plt.style.use('seaborn-v0_8-darkgrid')
        fig, ax = plt.subplots(figsize=(8, 6))
        
        colors_list = ['#2E7D32', '#66BB6A', '#A5D6A7', '#C8E6C9', '#E8F5E9']
        explode = [0.05] * len(data)

        wedges, texts, autotexts = ax.pie(
            data.values(),
            labels=data.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=colors_list[:len(data)],
            explode=explode,
            textprops={'fontsize': 11, 'fontweight': 'bold'}
        )

        ax.set_title('Scope Bazında Emisyon Dağılımı', fontsize=14, fontweight='bold', pad=20)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf

    def generate_report(
        self, 
        results: List[EmissionResult], 
        scope_summary: dict, 
        filename: str = "esg_report.pdf", 
        ml_results: dict = None
    ):
        """
        ESG raporu oluştur (AI ile zenginleştirilmiş)
        
        Args:
            results: EmissionResult listesi
            scope_summary: Scope özeti (dict)
            filename: PDF dosya adı
            ml_results: ML analiz sonuçları (benchmark, target vb.)
        """
        self._update_progress("Rapor oluşturma başlatılıyor...")

        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        story = []
        total_emissions = sum(scope_summary.values())

        # ==================== KAPAK SAYFASI ====================
        self._update_progress("Kapak sayfası oluşturuluyor...")
        story.append(Spacer(1, 3*cm))
        title = Paragraph(f"<b>{self.company_name}</b>", self.styles['CustomTitle'])
        story.append(title)
        subtitle = Paragraph("ESG Karbon Ayak İzi Raporu", self.styles['CustomHeading'])
        story.append(subtitle)
        story.append(Spacer(1, 1*cm))
        
        period_text = Paragraph(
            f"<b>Raporlama Dönemi:</b> {self.reporting_period}",
            self.styles['CustomNormal']
        )
        story.append(period_text)
        
        date_text = Paragraph(
            f"<b>Rapor Tarihi:</b> {datetime.now().strftime('%d.%m.%Y')}",
            self.styles['CustomNormal']
        )
        story.append(date_text)
        story.append(Spacer(1, 2*cm))
        
        gri_text = Paragraph(
            "<i>Bu rapor GRI 305: Emisyonlar standardına uygun hazırlanmıştır.</i>",
            self.styles['CustomNormal']
        )
        story.append(gri_text)
        story.append(PageBreak())

        # ==================== AI İÇERİK ÜRETİMİ ====================
        ai_sections = {}
        if self.use_ai:
            self._update_progress("AI ile içerik üretimi başlatılıyor...")
            
            # Results'ı dict formatına çevir
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
                self._update_progress("AI içerik üretimi tamamlandı")
            except Exception as e:
                print(f"[HATA] AI içerik üretimi başarısız: {e}")
                self._update_progress("AI içerik üretimi başarısız, statik içerik kullanılıyor")
                ai_sections = {}
        else:
            self._update_progress("AI içerik üretimi devre dışı, statik içerik kullanılıyor")

        # ==================== YÖNETİCİ ÖZETİ ====================
        self._update_progress("Yönetici özeti ekleniyor...")
        story.append(Paragraph("1. Yönetici Özeti", self.styles['CustomHeading']))
        
        if ai_sections.get('executive_summary'):
            # AI ile üretilmiş içerik
            exec_text = clean_text_for_pdf(ai_sections['executive_summary'])
            # Paragraflara böl
            for para in exec_text.split('\n\n'):
                if para.strip():
                    story.append(Paragraph(para.strip(), self.styles['CustomBody']))
                    story.append(Spacer(1, 0.3*cm))
        else:
            # Statik içerik (fallback)
            executive_summary = f"""
            <b>{self.company_name}</b> için {self.reporting_period} döneminde gerçekleştirilen karbon ayak izi
            analizi sonuçları bu raporda sunulmaktadır.

            <br/><br/>

            <b>Toplam GHG Emisyonu:</b> {total_emissions:.2f} ton CO2e

            <br/><br/>

            Emisyonlarımız GHG Protocol metodolojisi kullanılarak hesaplanmış olup, Scope 1, 2 ve 3 kategorilerinde
            raporlanmıştır. Hesaplamalar Climatiq API emission factor veritabanı kullanılarak yapılmıştır.
            """
            story.append(Paragraph(executive_summary, self.styles['CustomNormal']))
        
        story.append(Spacer(1, 1*cm))

        # ==================== EMİSYON ÖZETİ ====================
        self._update_progress("Emisyon özeti ekleniyor...")
        story.append(PageBreak())
        story.append(Paragraph("2. Emisyon Özeti (Scope Bazında)", self.styles['CustomHeading']))

        table_data = [['Scope', 'Emisyon (ton CO2e)', 'Oran (%)']]
        for scope, value in scope_summary.items():
            if value > 0:
                percentage = (value / total_emissions * 100) if total_emissions > 0 else 0
                table_data.append([scope, f"{value:.2f}", f"{percentage:.1f}%"])
        table_data.append(['TOPLAM', f"{total_emissions:.2f}", "100%"])

        table = Table(table_data, colWidths=[5*cm, 4*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#A5D6A7')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, -1), (-1, -1), FONT_BOLD),
        ]))
        story.append(table)
        story.append(Spacer(1, 1*cm))

        # Pasta grafiği
        chart_buf = self._create_pie_chart(scope_summary)
        if chart_buf:
            img = Image(chart_buf, width=12*cm, height=9*cm)
            story.append(img)
            story.append(Spacer(1, 1*cm))

        story.append(PageBreak())

        # ==================== PERFORMANS ANALİZİ ====================
        if any(ai_sections.get(f'performance_{s.lower().replace(" ", "_")}') for s in scope_summary.keys() if scope_summary[s] > 0):
            self._update_progress("Performans analizi ekleniyor...")
            story.append(Paragraph("3. Performans Analizi", self.styles['CustomHeading']))
            
            for scope, value in scope_summary.items():
                if value > 0:
                    key = f'performance_{scope.lower().replace(" ", "_")}'
                    if ai_sections.get(key):
                        story.append(Paragraph(f"3.{list(scope_summary.keys()).index(scope)+1} {scope} Emisyonları Analizi", self.styles['CustomNormal']))
                        story.append(Spacer(1, 0.3*cm))
                        
                        analysis_text = clean_text_for_pdf(ai_sections[key])
                        for para in analysis_text.split('\n\n'):
                            if para.strip():
                                story.append(Paragraph(para.strip(), self.styles['CustomBody']))
                                story.append(Spacer(1, 0.3*cm))
                        story.append(Spacer(1, 0.5*cm))
            
            story.append(PageBreak())

        # ==================== DETAYLI EMİSYON VERİLERİ ====================
        self._update_progress("Detaylı emisyon verileri ekleniyor...")
        story.append(Paragraph("4. Detaylı Emisyon Verileri", self.styles['CustomHeading']))

        detail_table_data = [['Aktivite', 'Miktar', 'Birim', 'CO2e (kg)', 'Scope', 'Kaynak']]
        for result in results:
            detail_table_data.append([
                result.activity_name[:30],
                f"{result.amount:.1f}",
                result.unit,
                f"{result.co2e_kg:.2f}",
                result.scope,
                result.source
            ])

        detail_table = Table(detail_table_data, colWidths=[5*cm, 2*cm, 2*cm, 2.5*cm, 2*cm, 2.5*cm])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(detail_table)
        story.append(Spacer(1, 1*cm))

        # ==================== KRİTİK AKTİVİTE ANALİZİ ====================
        if ai_sections.get('critical_activities'):
            self._update_progress("Kritik aktivite analizi ekleniyor...")
            story.append(PageBreak())
            story.append(Paragraph("5. Kritik Aktivite Analizi", self.styles['CustomHeading']))
            
            critical_text = clean_text_for_pdf(ai_sections['critical_activities'])
            for para in critical_text.split('\n\n'):
                if para.strip():
                    story.append(Paragraph(para.strip(), self.styles['CustomBody']))
                    story.append(Spacer(1, 0.3*cm))
            story.append(PageBreak())

        # ==================== İYİLEŞTİRME ÖNERİLERİ ====================
        if ai_sections.get('recommendations'):
            self._update_progress("İyileştirme önerileri ekleniyor...")
            story.append(Paragraph("6. İyileştirme Önerileri", self.styles['CustomHeading']))
            
            rec_text = clean_text_for_pdf(ai_sections['recommendations'])
            for para in rec_text.split('\n\n'):
                if para.strip():
                    story.append(Paragraph(para.strip(), self.styles['CustomBody']))
                    story.append(Spacer(1, 0.3*cm))
            story.append(PageBreak())

        # ==================== RİSK ANALİZİ ====================
        if ai_sections.get('risk_assessment'):
            self._update_progress("Risk analizi ekleniyor...")
            story.append(Paragraph("7. Risk ve Fırsatlar", self.styles['CustomHeading']))
            
            risk_text = clean_text_for_pdf(ai_sections['risk_assessment'])
            for para in risk_text.split('\n\n'):
                if para.strip():
                    story.append(Paragraph(para.strip(), self.styles['CustomBody']))
                    story.append(Spacer(1, 0.3*cm))
            story.append(PageBreak())

        # ==================== ML ANALİZ SONUÇLARI ====================
        if ml_results:
            self._update_progress("ML analiz sonuçları ekleniyor...")
            section_num = "8" if ai_sections else "5"
            story.append(Paragraph(f"{section_num}. Akıllı Analiz Sonuçları", self.styles['CustomHeading']))
            
            if ml_results.get('benchmark'):
                benchmark = ml_results['benchmark']
                story.append(Paragraph(f"<b>{section_num}.1 Sektör Karşılaştırması</b>", self.styles['CustomNormal']))
                story.append(Spacer(1, 0.3*cm))
                
                if benchmark.get('success') and benchmark.get('metrics'):
                    metrics = benchmark['metrics']
                    benchmark_text = f"""
                    <b>Sektör:</b> {benchmark.get('sector', 'Belirtilmemiş')}<br/>
                    <b>Şirket Yoğunluğu:</b> {metrics.get('company_intensity', 0):.4f} kg CO2e/USD<br/>
                    <b>Sektör Ortalaması:</b> {metrics.get('sector_intensity', 0):.4f} kg CO2e/USD<br/>
                    <b>Performans Oranı:</b> {metrics.get('ratio', 0):.2f}x<br/>
                    <b>Sektör İçi Sıralama:</b> En iyi %{100 - metrics.get('percentile', 50)}<br/>
                    <b>Rating:</b> {metrics.get('rating', 'N/A')}
                    """
                    story.append(Paragraph(benchmark_text, self.styles['CustomNormal']))
                    
                    if benchmark.get('interpretation'):
                        story.append(Spacer(1, 0.3*cm))
                        story.append(Paragraph(f"<i>{benchmark['interpretation']}</i>", self.styles['CustomNormal']))
                
                story.append(Spacer(1, 0.5*cm))
            
            if ml_results.get('target'):
                target = ml_results['target']
                story.append(Paragraph(f"<b>{section_num}.2 Net Zero Yol Haritası</b>", self.styles['CustomNormal']))
                story.append(Spacer(1, 0.3*cm))
                
                if target.get('success') and target.get('summary'):
                    summary = target['summary']
                    target_text = f"""
                    <b>Mevcut Emisyon:</b> {summary.get('current_emissions', 0):,.0f} ton CO2e<br/>
                    <b>Hedef Yıl:</b> {summary.get('target_year', 2030)}<br/>
                    <b>Hedef Emisyon:</b> {summary.get('target_emissions', 0):,.0f} ton CO2e<br/>
                    <b>Toplam Azaltım:</b> {summary.get('total_reduction', 'N/A')}<br/>
                    <b>SBTi Uyumlu:</b> {'Evet' if summary.get('sbti_aligned') else 'Hayır'}
                    """
                    story.append(Paragraph(target_text, self.styles['CustomNormal']))
                
                if target.get('milestones'):
                    story.append(Spacer(1, 0.3*cm))
                    milestone_data = [['Yıl', 'Hedef (ton)', 'Azaltım']]
                    for ms in target['milestones']:
                        milestone_data.append([
                            str(ms.get('year', '')),
                            f"{ms.get('target', 0):,.0f}",
                            ms.get('reduction', '')
                        ])
                    
                    ms_table = Table(milestone_data, colWidths=[3*cm, 4*cm, 3*cm])
                    ms_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ]))
                    story.append(ms_table)
                
                story.append(Spacer(1, 0.5*cm))
            
            story.append(PageBreak())

        # ==================== METODOLOJI ====================
        self._update_progress("Metodoloji bölümü ekleniyor...")
        section_num = "9" if (ai_sections and ml_results) else ("8" if (ai_sections or ml_results) else "5")
        story.append(Paragraph(f"{section_num}. Metodoloji", self.styles['CustomHeading']))

        if ai_sections.get('methodology'):
            # AI ile üretilmiş metodoloji
            method_text = clean_text_for_pdf(ai_sections['methodology'])
            for para in method_text.split('\n\n'):
                if para.strip():
                    story.append(Paragraph(para.strip(), self.styles['CustomBody']))
                    story.append(Spacer(1, 0.3*cm))
        else:
            # Statik metodoloji (fallback)
            methodology = f"""
            <b>{section_num}.1 Hesaplama Standardı:</b> GHG Protocol Corporate Accounting and Reporting Standard

            <br/><br/>

            <b>{section_num}.2 Emission Factor Kaynağı:</b> Climatiq API (80+ global veri kaynağı)

            <br/><br/>

            <b>{section_num}.3 Hesaplama Formülü:</b><br/>
            CO2e = Aktivite Verisi x Emission Factor

            <br/><br/>

            <b>{section_num}.4 Scope Tanımları:</b><br/>
            - <b>Scope 1:</b> Doğrudan emisyonlar (şirket kontrolündeki kaynaklar)<br/>
            - <b>Scope 2:</b> Dolaylı enerji emisyonları (satın alınan elektrik, ısı, buhar)<br/>
            - <b>Scope 3:</b> Diğer dolaylı emisyonlar (değer zinciri)

            <br/><br/>

            <b>{section_num}.5 Konsolidasyon Yaklaşımı:</b> Operasyonel Kontrol

            <br/><br/>

            <b>{section_num}.6 Veri Kalitesi:</b> Birincil veri (ölçüm ve faturalar)
            """
            story.append(Paragraph(methodology, self.styles['CustomNormal']))

        # ==================== PDF OLUŞTUR ====================
        self._update_progress("PDF oluşturuluyor...")
        doc.build(story)
        self._update_progress("Rapor oluşturma tamamlandı!")

        print(f"[OK] ESG Raporu oluşturuldu: {filename}")
        return filename

