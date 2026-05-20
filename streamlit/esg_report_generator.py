"""
ESG PDF Report Generator
GRI standardına uygun ESG raporu oluşturur
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from typing import List
import matplotlib.pyplot as plt
import io

from climatiq_calculator import EmissionResult

# Turkce karakter destegi icin font kaydet
try:
    # Windows'ta varsayilan font
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
    FONT_NAME = 'Arial'
    FONT_BOLD = 'Arial-Bold'
except:
    # Fallback - Helvetica (Turkce karakterler olmayabilir)
    FONT_NAME = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'

class ESG_Report_Generator:
    """ESG PDF Rapor Oluşturucu"""

    def __init__(self, company_name: str, reporting_period: str):
        self.company_name = company_name
        self.reporting_period = reporting_period
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

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

        # Normal metin - Turkce destekli
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontName=FONT_NAME,
            fontSize=10
        ))

    def _create_pie_chart(self, scope_summary: dict) -> io.BytesIO:
        """Scope dağılımı pasta grafiği oluştur"""

        # Sadece 0'dan büyük değerleri al
        data = {k: v for k, v in scope_summary.items() if v > 0}

        if not data:
            return None

        fig, ax = plt.subplots(figsize=(6, 4))

        colors_list = ['#2E7D32', '#66BB6A', '#A5D6A7', '#C8E6C9']
        explode = [0.05] * len(data)

        ax.pie(
            data.values(),
            labels=data.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=colors_list,
            explode=explode
        )

        ax.set_title('Scope Bazinda Emisyon Dagilimi', fontsize=14, fontweight='bold')

        # Byte stream'e kaydet
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close()
        buf.seek(0)

        return buf

    def generate_report(self, results: List[EmissionResult], scope_summary: dict, filename: str = "esg_report.pdf"):
        """
        ESG raporu oluştur

        Args:
            results: EmissionResult listesi
            scope_summary: Scope özeti (dict)
            filename: PDF dosya adı
        """

        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        story = []

        # ==================== KAPAK SAYFASI ====================
        story.append(Spacer(1, 3*cm))

        title = Paragraph(f"<b>{self.company_name}</b>", self.styles['CustomTitle'])
        story.append(title)

        subtitle = Paragraph("ESG Karbon Ayak Izi Raporu", self.styles['CustomHeading'])
        story.append(subtitle)

        story.append(Spacer(1, 1*cm))

        period_text = Paragraph(
            f"<b>Raporlama Donemi:</b> {self.reporting_period}",
            self.styles['CustomNormal']
        )
        story.append(period_text)

        date_text = Paragraph(
            f"<b>Rapor Tarihi:</b> {datetime.now().strftime('%d.%m.%Y')}",
            self.styles['CustomNormal']
        )
        story.append(date_text)

        story.append(Spacer(1, 2*cm))

        # GRI uyumlulugu
        gri_text = Paragraph(
            "<i>Bu rapor GRI 305: Emisyonlar standardina uygun hazirlanmistir.</i>",
            self.styles['CustomNormal']
        )
        story.append(gri_text)

        story.append(PageBreak())

        # ==================== YONETICI OZETI ====================
        story.append(Paragraph("1. Yonetici Ozeti", self.styles['CustomHeading']))

        # Toplam emisyon
        total_emissions = sum(scope_summary.values())

        executive_summary = f"""
        <b>{self.company_name}</b> icin {self.reporting_period} doneminde gerceklestirilen karbon ayak izi
        analizi sonuclari bu raporda sunulmaktadir.

        <br/><br/>

        <b>Toplam GHG Emisyonu:</b> {total_emissions:.2f} ton CO2e

        <br/><br/>

        Emisyonlarimiz GHG Protocol metodolojisi kullanilarak hesaplanmis olup, Scope 1, 2 ve 3 kategorilerinde
        raporlanmistir. Hesaplamalar Climatiq API emission factor veritabani kullanilarak yapilmistir.
        """

        story.append(Paragraph(executive_summary, self.styles['CustomNormal']))
        story.append(Spacer(1, 1*cm))

        # ==================== SCOPE OZET TABLOSU ====================
        story.append(Paragraph("2. Emisyon Ozeti (Scope Bazinda)", self.styles['CustomHeading']))

        table_data = [
            ['Scope', 'Emisyon (ton CO2e)', 'Oran (%)']
        ]

        for scope, value in scope_summary.items():
            if value > 0:
                percentage = (value / total_emissions * 100) if total_emissions > 0 else 0
                table_data.append([
                    scope,
                    f"{value:.2f}",
                    f"{percentage:.1f}%"
                ])

        # Toplam satır
        table_data.append(['TOPLAM', f"{total_emissions:.2f}", "100%"])

        table = Table(table_data, colWidths=[5*cm, 4*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#A5D6A7')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))

        story.append(table)
        story.append(Spacer(1, 1*cm))

        # ==================== PASTA GRAFİĞİ ====================
        chart_buf = self._create_pie_chart(scope_summary)

        if chart_buf:
            img = Image(chart_buf, width=12*cm, height=8*cm)
            story.append(img)
            story.append(Spacer(1, 1*cm))

        story.append(PageBreak())

        # ==================== DETAYLI EMISYON TABLOSU ====================
        story.append(Paragraph("3. Detayli Emisyon Verileri", self.styles['CustomHeading']))

        detail_table_data = [
            ['Aktivite', 'Miktar', 'Birim', 'CO2e (kg)', 'Scope', 'Kaynak']
        ]

        for result in results:
            detail_table_data.append([
                result.activity_name[:30],  # Uzun isimleri kısalt
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
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        story.append(detail_table)
        story.append(Spacer(1, 1*cm))

        # ==================== METODOLOJI ====================
        story.append(PageBreak())
        story.append(Paragraph("4. Metodoloji", self.styles['CustomHeading']))

        methodology = """
        <b>4.1 Hesaplama Standardi:</b> GHG Protocol Corporate Accounting and Reporting Standard

        <br/><br/>

        <b>4.2 Emission Factor Kaynagi:</b> Climatiq API (80+ global veri kaynagi)

        <br/><br/>

        <b>4.3 Hesaplama Formulu:</b><br/>
        CO2e = Aktivite Verisi x Emission Factor

        <br/><br/>

        <b>4.4 Scope Tanimlari:</b><br/>
        - <b>Scope 1:</b> Dogrudan emisyonlar (sirket kontrolundeki kaynaklar)<br/>
        - <b>Scope 2:</b> Dolayli enerji emisyonlari (satin alinan elektrik, isi, buhar)<br/>
        - <b>Scope 3:</b> Diger dolayli emisyonlar (deger zinciri)

        <br/><br/>

        <b>4.5 Konsolidasyon Yaklasimi:</b> Operasyonel Kontrol

        <br/><br/>

        <b>4.6 Veri Kalitesi:</b> Birincil veri (olcum ve faturalar)
        """

        story.append(Paragraph(methodology, self.styles['CustomNormal']))

        # ==================== PDF OLUSTUR ====================
        doc.build(story)

        print(f"[OK] ESG Raporu olusturuldu: {filename}")

        return filename

# Test
if __name__ == "__main__":
    from climatiq_calculator import EmissionResult

    # Örnek sonuçlar
    results = [
        EmissionResult(
            activity_name="Elektrik Tüketimi",
            amount=10000,
            unit="kWh",
            co2e_kg=4261.0,
            co2e_ton=4.26,
            scope="Scope 2",
            category="Energy",
            region="TR",
            source="CT",
            year=2021
        ),
        EmissionResult(
            activity_name="Benzinli Araç",
            amount=5000,
            unit="km",
            co2e_kg=925.0,
            co2e_ton=0.93,
            scope="Scope 1",
            category="Transport",
            region="GB",
            source="BEIS",
            year=2022
        )
    ]

    scope_summary = {
        "Scope 1": 0.93,
        "Scope 2": 4.26,
        "Scope 3": 0,
        "Other": 0
    }

    # Rapor oluştur
    generator = ESG_Report_Generator(
        company_name="Örnek Şirket A.Ş.",
        reporting_period="2024 Yıllık"
    )

    generator.generate_report(results, scope_summary, "esg_report_ornek.pdf")
