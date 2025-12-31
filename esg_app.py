"""
ESG Carbon Calculator & Report Generator
Streamlit uygulaması - Climatiq API + RAG LLM ile ESG raporu oluşturma
"""

import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Optional imports
try:
    from climatiq_calculator import ClimatiqCalculator, EmissionResult
    from esg_report_generator import ESG_Report_Generator
    from activity_database import ActivityDatabase
    from esg_analyzer_hf import ESGAnalyzer  # NEW: Hugging Face ESG Analyzer
    from external_data_sources import DataGovIntegration  # NEW: Data.gov API
    # Try Groq-based RAG first, fallback to simple
    try:
        from rag_system_groq import ESG_RAG_Groq as ESGAssistant
        RAG_TYPE = "groq"
    except (ImportError, ValueError):
        from rag_system_simple import SimpleESGAssistant as ESGAssistant
        RAG_TYPE = "simple"
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    RAG_TYPE = None
    print(f"Bazı modüller yüklenemedi: {e}")

# Load environment
load_dotenv()

# Sayfa yapılandırması
st.set_page_config(
    page_title="ESG Carbon Calculator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2E7D32;
    }
    .stButton>button {
        background-color: #2E7D32;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Ana başlık
st.markdown('<h1 class="main-header">🌍 ESG Carbon Calculator</h1>', unsafe_allow_html=True)
st.markdown("**AI-Powered Carbon Footprint Calculation & ESG Reporting**")
st.divider()

# Sidebar - Menü
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3930/3930169.png", width=100)
    st.title("📊 Menü")

    menu = st.radio(
        "Bölüm Seçin:",
        ["🏠 Ana Sayfa", "📝 Veri Girişi", "🔍 Activity DB", "📊 Hesaplama", "📄 ESG Raporu", "📊 Rapor Analizi", "🤖 AI Asistan", "ℹ️ Hakkında"]
    )

    st.divider()

    # API Status
    api_key = os.getenv('CLIMATIQ_API_KEY')
    if api_key:
        st.success("✅ API Bağlantısı: Aktif")
    else:
        st.error("❌ API Anahtarı bulunamadı")

    # Hybrid Calculator Status (NEW!)
    if MODULES_AVAILABLE:
        try:
            from hybrid_calculator import HybridEmissionCalculator
            calc = HybridEmissionCalculator()
            sources = calc.get_source_info()

            # Climatiq durumu
            if sources['climatiq']['available']:
                st.success("✅ Climatiq API: Aktif")
            else:
                st.info("ℹ️ Climatiq API: Pasif")

            # EPA durumu
            if sources['epa']['available']:
                st.success("✅ Data.gov EPA: Aktif")
                st.caption("Hibrit sistem (Climatiq + EPA)")
        except:
            st.warning("⚠️ Hibrit sistem: Devre Dışı")

    st.divider()
    st.caption("© 2025 ESG Carbon Calculator")

# ==================== ANA SAYFA ====================
if menu == "🏠 Ana Sayfa":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📊 Toplam Emission Factor", "277,011", delta="Climatiq Database")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🌍 Desteklenen Ülke", "200+", delta="Global Coverage")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🤖 AI Model", "RAG + LLM", delta="Akıllı Raporlama")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Hızlı Başlangıç
    st.subheader("🚀 Hızlı Başlangıç")

    st.markdown("""
    ### Bu uygulama ile neler yapabilirsiniz?

    1. **📝 Veri Girişi:** Şirketinizin karbon emisyon verilerini girin
       - Elektrik tüketimi (otomatik CO2 tahmini ✨)
       - Yakıt kullanımı (EPA faktörleri ✨)
       - Ulaşım verileri
       - PDF/Excel/CSV dosya yükleme (OCR desteği)

    2. **📊 Otomatik Hesaplama:** Climatiq API + Data.gov ile anlık CO2e hesaplama
       - Scope 1, 2, 3 emisyonları
       - EPA emisyon faktörleri (ücretsiz)
       - Kategori bazlı raporlama
       - Trend analizi

    3. **📄 ESG Raporu Oluşturma:** Profesyonel ESG raporu
       - PDF formatında rapor
       - Grafikler ve görselleştirmeler
       - GRI standardına uyumlu

    4. **🤖 AI Asistan:** RAG tabanlı akıllı asistan
       - ESG sorularınızı cevaplayın
       - Öneriler alın
       - Benchmark karşılaştırmaları

    5. **🌍 External Data Sources:** ✨ YENİ!
       - Data.gov EPA emisyon faktörleri (ücretsiz)
       - Otomatik CO2 hesaplama
       - Gerçek zamanlı tahminler
    """)

    st.info("👈 Sol menüden başlamak için bir bölüm seçin!")

# ==================== VERİ GİRİŞİ ====================
elif menu == "📝 Veri Girişi":
    st.header("📝 Emisyon Verisi Girişi")

    # Session state'de veri saklama
    if 'emission_data' not in st.session_state:
        st.session_state.emission_data = []

    # Hybrid Calculator integration (Climatiq + EPA)
    if 'hybrid_calc' not in st.session_state and MODULES_AVAILABLE:
        try:
            from hybrid_calculator import HybridEmissionCalculator
            st.session_state.hybrid_calc = HybridEmissionCalculator()
            # Backward compatibility
            if hasattr(st.session_state.hybrid_calc, 'datagov'):
                st.session_state.datagov = st.session_state.hybrid_calc.datagov
        except Exception as e:
            st.session_state.hybrid_calc = None
            # Fallback to EPA only
            try:
                st.session_state.datagov = DataGovIntegration()
            except:
                st.session_state.datagov = None

    tab1, tab2, tab3, tab4 = st.tabs(["⚡ Enerji", "🚗 Ulaşım", "🏭 Diğer", "📎 Dosya Yükle"])

    # TAB 1: ENERJİ
    with tab1:
        st.subheader("Enerji Tüketimi")

        col1, col2 = st.columns(2)

        with col1:
            electricity = st.number_input("Elektrik Tüketimi (kWh)", min_value=0.0, value=0.0, step=100.0)
            natural_gas = st.number_input("Doğalgaz Tüketimi (m³)", min_value=0.0, value=0.0, step=10.0)

        with col2:
            region = st.selectbox("Bölge", ["TR", "US", "GB", "DE", "FR", "GLOBAL"])
            period = st.selectbox("Dönem", ["Aylık", "Yıllık", "Çeyrek"])

        # Otomatik CO2 tahmini (Hibrit: Climatiq + EPA)
        if (st.session_state.get('hybrid_calc') or st.session_state.get('datagov')) and (electricity > 0 or natural_gas > 0):
            st.divider()
            st.markdown("### 📊 Tahmini CO2 Emisyonu")

            total_co2_kg = 0
            sources_used = []

            # Elektrik hesaplama
            if electricity > 0:
                if st.session_state.get('hybrid_calc'):
                    result = st.session_state.hybrid_calc.calculate_emission(
                        "electricity", electricity, "kWh", region
                    )
                    co2_elec = result["co2_kg"]
                    source = result["source"].upper()
                    confidence = result["confidence"]

                    # Kaynak badge
                    if source == "CLIMATIQ":
                        badge = "🔵 Climatiq API"
                        color = "blue"
                    elif source == "EPA":
                        badge = "🟢 Data.gov EPA"
                        color = "green"
                    else:
                        badge = "⚪ Manuel"
                        color = "gray"

                    total_co2_kg += co2_elec
                    sources_used.append(source)

                    st.info(f"⚡ Elektrik: **{co2_elec:,.2f} kg CO2e** ({co2_elec/1000:.2f} ton) - Scope 2\n\n📌 Kaynak: **{badge}** | Güven: **{confidence}**")
                else:
                    # Fallback to EPA only
                    factor_elec = st.session_state.datagov.get_emission_factor("electricity")
                    if factor_elec:
                        co2_elec = electricity * factor_elec
                        total_co2_kg += co2_elec
                        sources_used.append("EPA")
                        st.info(f"⚡ Elektrik: **{co2_elec:,.2f} kg CO2e** ({co2_elec/1000:.2f} ton) - Scope 2\n\n📌 Kaynak: **🟢 Data.gov EPA**")

            # Doğalgaz hesaplama
            if natural_gas > 0:
                if st.session_state.get('hybrid_calc'):
                    result = st.session_state.hybrid_calc.calculate_emission(
                        "natural_gas", natural_gas, "m3", region
                    )
                    co2_gas = result["co2_kg"]
                    source = result["source"].upper()
                    confidence = result["confidence"]

                    # Kaynak badge
                    if source == "CLIMATIQ":
                        badge = "🔵 Climatiq API"
                    elif source == "EPA":
                        badge = "🟢 Data.gov EPA"
                    else:
                        badge = "⚪ Manuel"

                    total_co2_kg += co2_gas
                    sources_used.append(source)

                    st.info(f"🔥 Doğalgaz: **{co2_gas:,.2f} kg CO2e** ({co2_gas/1000:.2f} ton) - Scope 1\n\n📌 Kaynak: **{badge}** | Güven: **{confidence}**")
                else:
                    # Fallback to EPA only
                    factor_gas = st.session_state.datagov.get_emission_factor("natural_gas")
                    if factor_gas:
                        co2_gas = natural_gas * factor_gas
                        total_co2_kg += co2_gas
                        sources_used.append("EPA")
                        st.info(f"🔥 Doğalgaz: **{co2_gas:,.2f} kg CO2e** ({co2_gas/1000:.2f} ton) - Scope 1\n\n📌 Kaynak: **🟢 Data.gov EPA**")

            # Toplam
            if total_co2_kg > 0:
                st.success(f"🌍 **Toplam Tahmini:** {total_co2_kg:,.2f} kg CO2e (**{total_co2_kg/1000:.2f} ton**)")

                # Kaynak özeti
                unique_sources = list(set(sources_used))
                if len(unique_sources) == 1:
                    st.caption(f"ℹ️ Tüm hesaplamalar **{unique_sources[0]}** ile yapıldı")
                else:
                    st.caption(f"ℹ️ Hibrit hesaplama: {', '.join(unique_sources)}")

        if st.button("➕ Enerji Verisi Ekle", key="add_energy"):
            if electricity > 0 or natural_gas > 0:
                entry = {
                    "category": "Enerji",
                    "electricity_kwh": electricity,
                    "natural_gas_m3": natural_gas,
                    "region": region,
                    "period": period,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.emission_data.append(entry)
                st.success(f"✅ Veri eklendi! Toplam {len(st.session_state.emission_data)} kayıt.")

    # TAB 2: ULAŞIM
    with tab2:
        st.subheader("Ulaşım Emisyonları")

        col1, col2 = st.columns(2)

        with col1:
            vehicle_km = st.number_input("Araç Yolculuğu (km)", min_value=0.0, value=0.0, step=100.0)
            fuel_type = st.selectbox("Yakıt Tipi", ["Benzin", "Dizel", "Elektrikli"])
            fuel_litre = st.number_input("veya Yakıt Tüketimi (litre)", min_value=0.0, value=0.0, step=10.0, help="Eğer yakıt tüketimi biliyorsanız")

        with col2:
            flight_km = st.number_input("Uçak Yolculuğu (km)", min_value=0.0, value=0.0, step=100.0)
            flight_class = st.selectbox("Sınıf", ["Ekonomi", "Business", "First Class"])

        # Otomatik CO2 tahmini (yakıt tüketimi için - Hibrit)
        if (st.session_state.get('hybrid_calc') or st.session_state.get('datagov')) and fuel_litre > 0:
            st.divider()
            st.markdown("### 📊 Tahmini CO2 Emisyonu")

            fuel_key = fuel_type.lower()
            if fuel_key == "benzin":
                fuel_key = "petrol"

            if st.session_state.get('hybrid_calc'):
                result = st.session_state.hybrid_calc.calculate_emission(
                    fuel_key, fuel_litre, "litre", region="TR"
                )
                co2_kg = result["co2_kg"]
                source = result["source"].upper()
                confidence = result["confidence"]

                # Kaynak badge
                if source == "CLIMATIQ":
                    badge = "🔵 Climatiq API"
                elif source == "EPA":
                    badge = "🟢 Data.gov EPA"
                else:
                    badge = "⚪ Manuel"

                st.info(f"🚗 {fuel_type}: **{co2_kg:,.2f} kg CO2e** ({co2_kg/1000:.2f} ton) - Scope 1\n\n📌 Kaynak: **{badge}** | Güven: **{confidence}**")
            else:
                # Fallback to EPA only
                factor = st.session_state.datagov.get_emission_factor(fuel_key)
                if factor:
                    co2_kg = fuel_litre * factor
                    st.info(f"🚗 {fuel_type}: **{co2_kg:,.2f} kg CO2e** ({co2_kg/1000:.2f} ton) - Scope 1\n\n📌 Kaynak: **🟢 Data.gov EPA**")

        if st.button("➕ Ulaşım Verisi Ekle", key="add_transport"):
            if vehicle_km > 0 or flight_km > 0:
                entry = {
                    "category": "Ulaşım",
                    "vehicle_km": vehicle_km,
                    "fuel_type": fuel_type,
                    "flight_km": flight_km,
                    "flight_class": flight_class,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.emission_data.append(entry)
                st.success(f"✅ Veri eklendi! Toplam {len(st.session_state.emission_data)} kayıt.")

    # TAB 3: DİĞER
    with tab3:
        st.subheader("Diğer Emisyonlar")

        col1, col2 = st.columns(2)

        with col1:
            waste_kg = st.number_input("Atık (kg)", min_value=0.0, value=0.0, step=10.0)
            water_l = st.number_input("Su Tüketimi (litre)", min_value=0.0, value=0.0, step=100.0)

        with col2:
            custom_activity = st.text_input("Özel Aktivite (opsiyonel)")
            custom_value = st.number_input("Miktar", min_value=0.0, value=0.0, step=1.0)

        if st.button("➕ Diğer Veri Ekle", key="add_other"):
            if waste_kg > 0 or water_l > 0 or custom_value > 0:
                entry = {
                    "category": "Diğer",
                    "waste_kg": waste_kg,
                    "water_l": water_l,
                    "custom_activity": custom_activity,
                    "custom_value": custom_value,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.emission_data.append(entry)
                st.success(f"✅ Veri eklendi! Toplam {len(st.session_state.emission_data)} kayıt.")

    # TAB 4: DOSYA YÜKLE
    with tab4:
        st.subheader("📎 PDF/Excel/CSV Dosya Yükle")

        st.info("""
        **Desteklenen Formatlar:**
        - 📄 PDF (ESG raporları, faturalar) - Normal ve taranmış
        - 📊 Excel (.xlsx, .xls)
        - 📋 CSV dosyaları
        - 🖼️ Görüntüler (.png, .jpg, .jpeg, .tiff, .bmp) - OCR ile

        **Ne Çıkarılır?**
        - Elektrik, doğalgaz, yakıt tüketimi
        - Scope 1/2/3 emisyon değerleri
        - Tablolardan yapılandırılmış veri
        - Taranmış belgelerden OCR ile metin
        """)

        # OCR language selection
        col1, col2 = st.columns([3, 1])
        with col1:
            ocr_enabled = st.checkbox("🔍 OCR Kullan (taranmış belgeler için)", value=False)
        with col2:
            if ocr_enabled:
                ocr_language = st.selectbox("Dil", ["eng", "tur", "eng+tur"], index=2)

        uploaded_file = st.file_uploader(
            "Dosya Seçin",
            type=['pdf', 'xlsx', 'xls', 'csv', 'png', 'jpg', 'jpeg', 'tiff', 'bmp'],
            help="PDF, Excel, CSV veya görüntü formatında dosya yükleyin"
        )

        if uploaded_file is not None:
            st.success(f"✅ Dosya yüklendi: {uploaded_file.name}")

            # Dosya bilgileri
            file_details = {
                "Dosya Adı": uploaded_file.name,
                "Dosya Tipi": uploaded_file.type,
                "Dosya Boyutu": f"{uploaded_file.size / 1024:.2f} KB"
            }
            st.json(file_details)

            # Veri çıkarma butonu
            if st.button("🔍 Veriyi Çıkar ve İşle", type="primary"):
                try:
                    from data_extractor import DataExtractor
                    import os

                    # Dosya uzantısını al
                    file_ext = os.path.splitext(uploaded_file.name)[1].lower()

                    # OCR gerekli mi kontrol et
                    if ocr_enabled or file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                        from ocr_extractor import OCRExtractor

                        with st.spinner("OCR ile dosya işleniyor... (Bu biraz zaman alabilir)"):
                            ocr = OCRExtractor()

                            if not ocr.ocr_available:
                                st.error("❌ OCR kütüphaneleri kurulu değil!")
                                st.info("""
                                **Kurulum Adımları:**
                                1. `pip install pytesseract pillow pdf2image`
                                2. Tesseract binary indir: https://github.com/UB-Mannheim/tesseract/wiki
                                3. Poppler (PDF için): https://github.com/oschwartz10612/poppler-windows/releases/
                                """)
                                result = {"success": False, "error": "OCR kütüphaneleri kurulu değil"}
                            else:
                                language = ocr_language if ocr_enabled else 'eng+tur'

                                # Görüntü dosyası mı?
                                if file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                                    # Görüntüden OCR
                                    ocr_result = ocr.extract_from_image(uploaded_file, language=language)

                                    if ocr_result["success"]:
                                        # OCR metnini data_extractor ile parse et
                                        extractor = DataExtractor()
                                        extracted_data = extractor._parse_emission_text(ocr_result["text"])

                                        result = {
                                            "success": True,
                                            "data": extracted_data,
                                            "raw_text": ocr_result["text"],
                                            "tables": [],
                                            "ocr_confidence": ocr_result.get("confidence", 0)
                                        }
                                    else:
                                        result = ocr_result

                                # PDF dosyası mı?
                                elif file_ext == '.pdf':
                                    # Taranmış PDF'den OCR
                                    ocr_result = ocr.extract_from_scanned_pdf(uploaded_file, language=language)

                                    if ocr_result["success"]:
                                        # OCR metnini data_extractor ile parse et
                                        extractor = DataExtractor()
                                        extracted_data = extractor._parse_emission_text(ocr_result["text"])

                                        result = {
                                            "success": True,
                                            "data": extracted_data,
                                            "raw_text": ocr_result["text"],
                                            "tables": [],
                                            "ocr_confidence": ocr_result.get("confidence", 0),
                                            "ocr_pages": ocr_result.get("pages", [])
                                        }
                                    else:
                                        result = ocr_result
                                else:
                                    result = {"success": False, "error": "OCR sadece görüntü ve PDF dosyaları için kullanılabilir"}

                    else:
                        # Normal extraction (OCR olmadan)
                        with st.spinner("Dosya işleniyor..."):
                            extractor = DataExtractor()
                            result = extractor.extract_from_file(uploaded_file)

                    if result["success"]:
                        st.success(f"✅ {len(result['data'])} adet veri çıkarıldı!")

                        # OCR güven skorunu göster
                        if "ocr_confidence" in result:
                            confidence_pct = result["ocr_confidence"] * 100
                            if confidence_pct >= 80:
                                st.info(f"🎯 OCR Güven Skoru: {confidence_pct:.1f}% (Yüksek)")
                            elif confidence_pct >= 60:
                                st.warning(f"⚠️ OCR Güven Skoru: {confidence_pct:.1f}% (Orta)")
                            else:
                                st.error(f"❌ OCR Güven Skoru: {confidence_pct:.1f}% (Düşük - manuel kontrol edin)")

                        # OCR sayfa detaylarını göster
                        if "ocr_pages" in result and result["ocr_pages"]:
                            with st.expander(f"📄 OCR Sayfa Detayları ({len(result['ocr_pages'])} sayfa)"):
                                for page in result["ocr_pages"]:
                                    st.write(f"**Sayfa {page['page_number']}** - Güven: {page['confidence']*100:.1f}%")
                                    st.text_area(
                                        f"Sayfa {page['page_number']} Metni",
                                        page['text'][:500] + ("..." if len(page['text']) > 500 else ""),
                                        height=100,
                                        key=f"page_{page['page_number']}"
                                    )

                        # Çıkarılan verileri göster
                        if result["data"]:
                            st.subheader("📊 Çıkarılan Veriler:")

                            for idx, item in enumerate(result["data"], 1):
                                with st.expander(f"{idx}. {item['category']} - {item['amount']} {item['unit']}"):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write(f"**Kategori:** {item['category']}")
                                        st.write(f"**Miktar:** {item['amount']}")
                                        st.write(f"**Birim:** {item['unit']}")
                                    with col2:
                                        st.write(f"**Scope:** {item.get('scope', 'Unknown')}")
                                        st.write(f"**Kaynak:** {item.get('source', 'N/A')}")
                                        st.write(f"**Güven:** {item.get('confidence', 0)*100:.0f}%")

                            # Verileri session'a ekle
                            if st.button("✅ Tüm Verileri Ekle", key="add_extracted_data"):
                                for item in result["data"]:
                                    st.session_state.emission_data.append(item)
                                st.success(f"✅ {len(result['data'])} veri emission_data'ya eklendi!")
                                st.rerun()

                        # Ham metin (PDF için)
                        if result["raw_text"]:
                            with st.expander("📄 Ham Metin (PDF)"):
                                st.text_area("PDF İçeriği", result["raw_text"], height=200)

                        # Tablolar (Excel/CSV için)
                        if result["tables"]:
                            with st.expander("📊 Tablolar"):
                                for idx, table in enumerate(result["tables"], 1):
                                    st.write(f"**Tablo {idx}:**")
                                    st.dataframe(table)

                    else:
                        st.error(f"❌ Hata: {result['error']}")

                except ImportError as e:
                    st.error(f"❌ Gerekli kütüphane eksik: {str(e)}")
                    st.info("Çözüm: `pip install PyPDF2 openpyxl` komutunu çalıştırın")
                except Exception as e:
                    st.error(f"❌ Beklenmeyen hata: {str(e)}")

            st.divider()

            # Örnek template indirme
            st.subheader("📥 Örnek Template")
            st.info("Verilerinizi Excel template'ine girip yükleyebilirsiniz.")

            # Örnek CSV oluştur
            example_csv = """Kategori,Miktar,Birim,Scope
Elektrik,15000,kWh,Scope 2
Doğalgaz,500,m³,Scope 1
Araç Yakıtı,200,litre,Scope 1
İş Seyahati,5000,km,Scope 3"""

            st.download_button(
                label="📥 Örnek CSV İndir",
                data=example_csv,
                file_name="emission_data_template.csv",
                mime="text/csv"
            )

    # Girilen verileri göster
    st.divider()
    st.subheader("📋 Girilen Veriler")

    if len(st.session_state.emission_data) > 0:
        # Veritabanından eklenen verilerin miktarını girme
        for idx, entry in enumerate(st.session_state.emission_data):
            if 'activity_id' in entry and entry.get('amount', 0) == 0:
                with st.expander(f"⚠️ Miktar Girilmedi: {entry.get('activity_name', 'Bilinmeyen')[:50]}"):
                    st.caption(f"Unit: {entry.get('unit', 'N/A')}")

                    new_amount = st.number_input(
                        f"Miktar ({entry.get('unit', 'N/A')})",
                        min_value=0.0,
                        value=0.0,
                        step=1.0,
                        key=f"amount_input_{idx}"
                    )

                    if st.button(f"💾 Kaydet", key=f"save_amount_{idx}"):
                        st.session_state.emission_data[idx]['amount'] = new_amount
                        # Eğer unit_type yoksa, varsayılan olarak Energy ekle
                        if 'unit_type' not in st.session_state.emission_data[idx]:
                            st.session_state.emission_data[idx]['unit_type'] = 'Energy'
                        st.success(f"✅ Miktar güncellendi: {new_amount} {entry.get('unit', '')}")
                        st.rerun()

        # Tüm verileri göster
        st.json(st.session_state.emission_data)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Tüm Verileri Sil"):
                st.session_state.emission_data = []
                st.rerun()

        with col2:
            if st.button("💾 Verileri Kaydet (JSON)"):
                with open('emission_data_input.json', 'w', encoding='utf-8') as f:
                    json.dump(st.session_state.emission_data, f, indent=2, ensure_ascii=False)
                st.success("✅ Veriler kaydedildi: emission_data_input.json")
    else:
        st.info("Henüz veri girilmedi. Yukarıdaki sekmelerden veri ekleyin.")

# ==================== ACTIVITY DATABASE ====================
elif menu == "🔍 Activity DB":
    st.header("🔍 Emission Factor Veritabanı")

    if not MODULES_AVAILABLE:
        st.error("Activity Database modülü yüklenemedi.")
    else:
        # Database'i yükle
        if 'activity_db' not in st.session_state:
            with st.spinner("268,000+ emission factor yükleniyor..."):
                st.session_state.activity_db = ActivityDatabase()

        db = st.session_state.activity_db

        # İstatistikler
        stats = db.get_stats()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Toplam Factor", f"{stats['total']:,}")
        with col2:
            st.metric("Scope 1", f"{stats['scope1']:,}")
        with col3:
            st.metric("Scope 2", f"{stats['scope2']:,}")
        with col4:
            st.metric("Scope 3", f"{stats['scope3']:,}")

        st.divider()

        # Arama ve filtreleme
        st.subheader("🔍 Activity Ara")

        col1, col2, col3 = st.columns(3)

        with col1:
            search_query = st.text_input("Arama (İngilizce)", placeholder="örn: electricity, gas, flight")
            scope_filter = st.selectbox("Scope Filtresi", ["Tümü", "1", "2", "3"])

        with col2:
            categories = ["Tümü"] + db.get_categories()
            category_filter = st.selectbox("Kategori", categories)

        with col3:
            regions = ["Tümü"] + db.get_regions()[:20]  # İlk 20 bölge
            region_filter = st.selectbox("Bölge", regions)

        # Arama yap
        if st.button("🔍 Ara", type="primary") or search_query:
            scope_param = None if scope_filter == "Tümü" else scope_filter
            category_param = None if category_filter == "Tümü" else category_filter
            region_param = None if region_filter == "Tümü" else region_filter

            results = db.search_activities(
                query=search_query,
                scope=scope_param,
                category=category_param,
                region=region_param,
                limit=100
            )

            st.success(f"✅ {len(results)} sonuç bulundu!")

            if results:
                # Sonuçları göster
                for i, activity in enumerate(results[:20], 1):  # İlk 20'yi göster
                    with st.expander(f"{i}. {activity['name'][:80]} - Scope {activity['scopes'][0]}"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"**Activity ID:** `{activity['activity_id']}`")
                            st.markdown(f"**Kategori:** {activity.get('category', 'N/A')}")
                            st.markdown(f"**Bölge:** {activity.get('region', 'N/A')} ({activity.get('region_name', 'N/A')})")
                            st.markdown(f"**Unit:** {activity.get('unit', 'N/A')}")

                        with col2:
                            st.markdown(f"**Kaynak:** {activity.get('source', 'N/A')}")
                            st.markdown(f"**Yıl:** {activity.get('year', 'N/A')}")
                            st.markdown(f"**Scope:** {', '.join([str(s) for s in activity.get('scopes', [])])}")

                        # Açıklama
                        if activity.get('description'):
                            st.caption(f"**Açıklama:** {activity['description'][:200]}...")

                        # Veri girişine ekle butonu
                        if st.button(f"➕ Veri Girişine Ekle", key=f"add_{activity['id']}"):
                            if 'emission_data' not in st.session_state:
                                st.session_state.emission_data = []

                            entry = {
                                "category": "Veritabanından",
                                "activity_id": activity['activity_id'],
                                "activity_name": activity['name'],
                                "unit": activity.get('unit', 'unknown'),
                                "unit_type": activity.get('unit_type', 'Energy'),  # Energy, Distance, Weight, Volume, Money
                                "region": activity.get('region', 'GLOBAL'),
                                "scope": activity.get('scopes', ['Unknown'])[0],
                                "amount": 0.0,  # Kullanıcı sonra girer
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                            }

                            st.session_state.emission_data.append(entry)
                            st.success(f"✅ '{activity['name'][:40]}...' veri girişine eklendi!")
                            st.info("→ 'Veri Girişi' sekmesinden miktarı girebilirsiniz")

                if len(results) > 20:
                    st.info(f"İlk 20 sonuç gösteriliyor. Toplam {len(results)} sonuç bulundu. Daha spesifik arama yapın.")

        # Popüler aktiviteler
        st.divider()
        st.subheader("⭐ Popüler Aktiviteler")

        popular = db.get_popular_activities(top_n=10)

        for i, activity in enumerate(popular, 1):
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.text(f"{i}. {activity['name'][:60]}")

            with col2:
                st.caption(f"Scope {activity.get('scopes', ['?'])[0]}")

            with col3:
                if st.button("➕", key=f"popular_{activity['id']}"):
                    if 'emission_data' not in st.session_state:
                        st.session_state.emission_data = []

                    entry = {
                        "category": "Popüler",
                        "activity_id": activity['activity_id'],
                        "activity_name": activity['name'],
                        "unit": activity.get('unit', 'unknown'),
                        "unit_type": activity.get('unit_type', 'Energy'),  # Energy, Distance, Weight, Volume, Money
                        "region": activity.get('region', 'GLOBAL'),
                        "scope": activity.get('scopes', ['Unknown'])[0],
                        "amount": 0.0,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }

                    st.session_state.emission_data.append(entry)
                    st.success("✅ Eklendi!")

# ==================== HESAPLAMA ====================
elif menu == "📊 Hesaplama":
    st.header("📊 CO2e Hesaplama")

    if not MODULES_AVAILABLE:
        st.error("Climatiq Calculator modülü yüklenemedi. Lütfen requirements kurulumunu kontrol edin.")
    elif 'emission_data' not in st.session_state or len(st.session_state.emission_data) == 0:
        st.warning("Henüz veri girilmedi. Lütfen 'Veri Girişi' sekmesinden veri ekleyin.")
    else:
        st.success(f"✅ {len(st.session_state.emission_data)} adet veri bulundu!")

        if st.button("🔄 Hesaplama Yap", type="primary"):
            with st.spinner("Climatiq API ile hesaplama yapılıyor..."):

                # Calculator oluştur
                calc = ClimatiqCalculator()

                # Hesaplama yap
                results = calc.calculate_batch(st.session_state.emission_data)

                if results:
                    # Session'a kaydet
                    st.session_state.calculation_results = results

                    # Scope özeti
                    scope_summary = calc.summarize_by_scope(results)
                    st.session_state.scope_summary = scope_summary

                    st.success(f"✅ Hesaplama tamamlandı! {len(results)} aktivite işlendi.")
                else:
                    st.error("Hesaplama yapılamadı. API hatası olabilir.")

        # Sonuçları göster
        if 'calculation_results' in st.session_state and st.session_state.calculation_results:
            st.divider()
            st.subheader("📊 Hesaplama Sonuçları")

            results = st.session_state.calculation_results

            # Özet metrikler
            col1, col2, col3 = st.columns(3)

            total_co2e = sum([r.co2e_ton for r in results])

            with col1:
                st.metric("Toplam Emisyon", f"{total_co2e:.2f} ton CO2e",
                         delta=f"{len(results)} aktivite")

            with col2:
                scope1_total = sum([r.co2e_ton for r in results if "Scope 1" in r.scope])
                st.metric("Scope 1", f"{scope1_total:.2f} ton CO2e")

            with col3:
                scope2_total = sum([r.co2e_ton for r in results if "Scope 2" in r.scope])
                st.metric("Scope 2", f"{scope2_total:.2f} ton CO2e")

            # Detaylı tablo
            st.subheader("Detaylı Sonuçlar")

            import pandas as pd

            df = pd.DataFrame([
                {
                    "Aktivite": r.activity_name[:40],
                    "Miktar": f"{r.amount:.1f} {r.unit}",
                    "CO2e (kg)": f"{r.co2e_kg:.2f}",
                    "CO2e (ton)": f"{r.co2e_ton:.4f}",
                    "Scope": r.scope,
                    "Kaynak": r.source
                }
                for r in results
            ])

            st.dataframe(df, use_container_width=True)

            # Scope dağılımı
            if 'scope_summary' in st.session_state:
                st.divider()
                st.subheader("Scope Dağılımı")

                scope_summary = st.session_state.scope_summary

                # Pasta grafik için hazırla
                scope_data = {k: v for k, v in scope_summary.items() if v > 0}

                if scope_data:
                    import matplotlib.pyplot as plt

                    fig, ax = plt.subplots(figsize=(8, 5))

                    colors_list = ['#2E7D32', '#66BB6A', '#A5D6A7', '#C8E6C9']
                    explode = [0.05] * len(scope_data)

                    ax.pie(
                        scope_data.values(),
                        labels=scope_data.keys(),
                        autopct='%1.1f%%',
                        startangle=90,
                        colors=colors_list,
                        explode=explode
                    )

                    ax.set_title('Scope Bazında Emisyon Dağılımı', fontsize=14, fontweight='bold')

                    st.pyplot(fig)

            # Export butonu
            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                if st.button("💾 Sonuçları JSON Olarak Kaydet"):
                    result_data = [
                        {
                            "activity": r.activity_name,
                            "amount": r.amount,
                            "unit": r.unit,
                            "co2e_kg": r.co2e_kg,
                            "co2e_ton": r.co2e_ton,
                            "scope": r.scope,
                            "category": r.category,
                            "region": r.region,
                            "source": r.source,
                            "year": r.year
                        }
                        for r in results
                    ]

                    with open('emission_results.json', 'w', encoding='utf-8') as f:
                        json.dump(result_data, f, indent=2, ensure_ascii=False)

                    st.success("✅ Kaydedildi: emission_results.json")

            with col2:
                st.info("PDF rapor için 'ESG Raporu' sekmesine gidin →")

# ==================== ESG RAPORU ====================
elif menu == "📄 ESG Raporu":
    st.header("📄 ESG Raporu Oluştur")

    if not MODULES_AVAILABLE:
        st.error("ESG Report Generator modülü yüklenemedi. Lütfen requirements kurulumunu kontrol edin.")
    elif 'calculation_results' not in st.session_state or not st.session_state.calculation_results:
        st.warning("Önce hesaplama yapmalısınız. '📊 Hesaplama' sekmesine gidin.")
    else:
        st.success("✅ Hesaplama sonuçları bulundu!")

        # Şirket bilgileri
        st.subheader("🏢 Şirket Bilgileri")

        col1, col2 = st.columns(2)

        with col1:
            company_name = st.text_input("Şirket Adı", value="Örnek Şirket A.Ş.")
            reporting_period = st.selectbox(
                "Raporlama Dönemi",
                ["2024 Yıllık", "2024 Q1", "2024 Q2", "2024 Q3", "2024 Q4", "2023 Yıllık"]
            )

        with col2:
            report_title = st.text_input("Rapor Başlığı", value="ESG Karbon Ayak İzi Raporu")
            gri_compliance = st.checkbox("GRI 305 Uyumlu", value=True)

        # Özet önizleme
        st.divider()
        st.subheader("📊 Rapor Özeti")

        results = st.session_state.calculation_results
        scope_summary = st.session_state.get('scope_summary', {})

        col1, col2, col3, col4 = st.columns(4)

        total_emissions = sum([r.co2e_ton for r in results])

        with col1:
            st.metric("Toplam Emisyon", f"{total_emissions:.2f} ton CO2e")

        with col2:
            st.metric("Aktivite Sayısı", f"{len(results)}")

        with col3:
            scope1 = scope_summary.get("Scope 1", 0)
            st.metric("Scope 1", f"{scope1:.2f} ton")

        with col4:
            scope2 = scope_summary.get("Scope 2", 0)
            st.metric("Scope 2", f"{scope2:.2f} ton")

        # PDF oluştur
        st.divider()
        st.subheader("📄 PDF Rapor Oluştur")

        if st.button("📥 PDF Raporu İndir", type="primary"):
            with st.spinner("PDF raporu oluşturuluyor..."):
                try:
                    # Generator oluştur
                    generator = ESG_Report_Generator(
                        company_name=company_name,
                        reporting_period=reporting_period
                    )

                    # PDF oluştur
                    filename = f"esg_report_{company_name.replace(' ', '_')}_{reporting_period.replace(' ', '_')}.pdf"
                    generator.generate_report(
                        results=results,
                        scope_summary=scope_summary,
                        filename=filename
                    )

                    st.success(f"✅ PDF raporu oluşturuldu: {filename}")

                    # İndir butonu
                    with open(filename, "rb") as pdf_file:
                        pdf_bytes = pdf_file.read()

                        st.download_button(
                            label="📥 PDF'i İndir",
                            data=pdf_bytes,
                            file_name=filename,
                            mime="application/pdf"
                        )

                except Exception as e:
                    st.error(f"PDF oluşturulurken hata: {str(e)}")
                    st.code(str(e))

        # Rapor içeriği önizleme
        st.divider()

        with st.expander("📋 Rapor İçeriği Önizleme"):
            st.markdown(f"""
            ## {company_name}
            ### {report_title}

            **Raporlama Dönemi:** {reporting_period}

            **GRI Uyumluluk:** {"✅ GRI 305: Emisyonlar" if gri_compliance else "❌"}

            ---

            ### 1. Yönetici Özeti

            {company_name} için {reporting_period} döneminde gerçekleştirilen karbon ayak izi
            analizi sonuçları bu raporda sunulmaktadır.

            **Toplam GHG Emisyonu:** {total_emissions:.2f} ton CO2e

            ---

            ### 2. Emisyon Özeti (Scope Bazında)

            | Scope | Emisyon (ton CO2e) | Oran (%) |
            |-------|-------------------|----------|
            """)

            for scope, value in scope_summary.items():
                if value > 0:
                    percentage = (value / total_emissions * 100) if total_emissions > 0 else 0
                    st.markdown(f"| {scope} | {value:.2f} | {percentage:.1f}% |")

            st.markdown(f"| **TOPLAM** | **{total_emissions:.2f}** | **100%** |")

            st.markdown("""
            ---

            ### 3. Detaylı Emisyon Verileri

            Tüm aktiviteler, miktarlar, CO2e değerleri ve kaynaklar PDF raporunda yer almaktadır.

            ### 4. Metodoloji

            - **Hesaplama Standardı:** GHG Protocol
            - **Emission Factor Kaynağı:** Climatiq API
            - **Veri Kalitesi:** Birincil veri
            - **Konsolidasyon:** Operasyonel Kontrol
            """)

# ==================== RAPOR ANALİZİ (HUGGING FACE) ====================
elif menu == "📊 Rapor Analizi":
    st.header("📊 AI ile ESG Rapor Analizi")
    st.markdown("**Hugging Face ESG modelleri ile PDF/metin analizi**")

    if not MODULES_AVAILABLE:
        st.error("ESG Analyzer modülü yüklenemedi.")
    else:
        # Analyzer oluştur
        if 'esg_analyzer' not in st.session_state:
            st.session_state.esg_analyzer = ESGAnalyzer()

        analyzer = st.session_state.esg_analyzer

        st.divider()

        # Tab: PDF Upload vs Metin Girişi
        tab1, tab2 = st.tabs(["📄 PDF Yükle", "📝 Metin Analizi"])

        # TAB 1: PDF Upload
        with tab1:
            st.subheader("PDF ESG Raporu Yükle")

            uploaded_file = st.file_uploader(
                "ESG raporunu yükleyin (PDF)",
                type=['pdf'],
                help="Şirket ESG raporu, sürdürülebilirlik raporu, karbon ayak izi raporu vb."
            )

            if uploaded_file:
                # Geçici dosyaya kaydet
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                st.success(f"✅ Dosya yüklendi: {uploaded_file.name}")

                if st.button("🔍 PDF'i Analiz Et", type="primary"):
                    with st.spinner("PDF analiz ediliyor (Hugging Face ESG modeli)..."):
                        results = analyzer.analyze_pdf(tmp_path)

                        if "error" in results:
                            st.error(f"❌ Hata: {results['error']}")
                            if "PyPDF2" in results['error']:
                                st.info("📦 Kurulum: `pip install PyPDF2`")
                        else:
                            # Session'a kaydet
                            st.session_state.analysis_results = results

                            st.success("✅ Analiz tamamlandı!")

                # Temizlik
                try:
                    import os
                    if 'tmp_path' in locals():
                        os.unlink(tmp_path)
                except:
                    pass

        # TAB 2: Text Analysis
        with tab2:
            st.subheader("Metin Analizi")

            text_input = st.text_area(
                "ESG metni girin:",
                height=200,
                placeholder="Örnek:\nScope 1 Emissions: 1,234 ton CO2e\nScope 2 Emissions: 2,500 tonnes CO2\nScope 3 Emissions: 15,000 ton CO2e"
            )

            if st.button("🔍 Metni Analiz Et", type="primary"):
                if text_input.strip():
                    with st.spinner("Metin analiz ediliyor..."):
                        results = analyzer.analyze_text(text_input)
                        st.session_state.analysis_results = results
                        st.success("✅ Analiz tamamlandı!")
                else:
                    st.warning("Lütfen analiz edilecek metin girin.")

        # Sonuçları göster
        if 'analysis_results' in st.session_state:
            st.divider()
            st.subheader("📊 Analiz Sonuçları")

            results = st.session_state.analysis_results

            # Özet
            st.markdown(results.get("summary", ""))

            st.divider()

            # Detaylı Sonuçlar
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🎯 Scope Tespiti")
                scopes = results.get("scope_detection", {})

                for scope, detected in scopes.items():
                    status = "✅ Tespit Edildi" if detected else "❌ Tespit Edilemedi"
                    st.write(f"**{scope.upper()}:** {status}")

            with col2:
                st.markdown("### 📈 ESG Kategorileri")
                esg = results.get("esg_classification", {})

                for category, score in esg.items():
                    percentage = score * 100 if score <= 1 else score
                    st.metric(category, f"{percentage:.1f}%")

            # Emisyon Değerleri
            st.divider()
            st.markdown("### 💨 Bulunan Emisyon Değerleri")

            emissions = results.get("emission_values", [])

            if emissions:
                import pandas as pd

                df = pd.DataFrame([
                    {
                        "Değer": f"{e['value']:,.2f}",
                        "Birim": e['unit'],
                        "Bağlam": e['context'][:80]
                    }
                    for e in emissions
                ])

                st.dataframe(df, use_container_width=True)
            else:
                st.info("Metinde emisyon değeri tespit edilemedi.")

            # Risk Skoru
            st.divider()
            risk = results.get("risk_score", 0)

            col1, col2, col3 = st.columns([1, 2, 1])

            with col2:
                st.markdown("### 🎯 ESG Risk Skoru")

                # Progress bar
                if risk < 30:
                    color = "green"
                    level = "Düşük Risk"
                elif risk < 60:
                    color = "orange"
                    level = "Orta Risk"
                else:
                    color = "red"
                    level = "Yüksek Risk"

                st.progress(risk / 100)
                st.markdown(f"<h2 style='text-align: center; color: {color};'>{risk}/100 - {level}</h2>", unsafe_allow_html=True)

                st.caption("""
                **Risk Skorlama:**
                - Scope tespiti eksiklikleri
                - Emisyon verisi eksikliği
                - ESG kategorilerinde dengesizlik
                """)

# ==================== AI ASISTAN ====================
elif menu == "🤖 AI Asistan":
    st.header("🤖 ESG AI Asistan")

    st.info("💡 ESG konularında bilgi almak için aşağıdaki soruları sorabilirsiniz!")

    # AI asistan kur
    if 'ai_assistant' not in st.session_state:
        try:
            st.session_state.ai_assistant = ESGAssistant()
            if RAG_TYPE == "groq":
                st.success("✅ AI Asistan hazır! (Groq LLM - Mixtral-8x7B)")
            else:
                st.success("✅ AI Asistan hazır! (Basit mod - keyword matching)")
        except Exception as e:
            st.session_state.ai_assistant = None
            st.warning(f"AI asistan yüklenemedi: {e}")

    # Örnek sorular
    st.subheader("📚 Örnek Sorular")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        - Scope 1 emisyonları nedir?
        - Scope 2 emisyonları nedir?
        - Scope 3 emisyonları nedir?
        - GRI 305 standardı nedir?
        """)

    with col2:
        st.markdown("""
        - Net Zero hedefi nedir?
        - Carbon offsetting nedir?
        - GHG Protocol nedir?
        - CDP nedir?
        """)

    st.divider()

    # Soru-cevap alanı
    st.subheader("💬 Soru Sorun")

    user_question = st.text_input("ESG hakkında sorunuz:", placeholder="Örn: Scope 1 nedir?")

    if st.button("🔍 Sor", type="primary"):
        if user_question:
            if st.session_state.ai_assistant:
                with st.spinner("Cevap aranıyor..."):
                    answer = st.session_state.ai_assistant.ask(user_question)

                    st.success("✅ Cevap bulundu!")

                    st.markdown("### Cevap:")
                    st.markdown(answer)
            else:
                st.error("AI asistan yüklenemedi. Lütfen kurulumu kontrol edin.")
        else:
            st.warning("Lütfen bir soru girin.")

    # Sohbet geçmişi
    st.divider()

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if st.session_state.chat_history:
        st.subheader("📜 Sohbet Geçmişi")

        for idx, chat in enumerate(st.session_state.chat_history[-5:]):  # Son 5 soru
            with st.expander(f"❓ {chat['question'][:50]}...", expanded=(idx == len(st.session_state.chat_history[-5:]) - 1)):
                st.markdown(f"**Soru:** {chat['question']}")
                st.markdown(f"**Cevap:** {chat['answer'][:500]}...")

    # RAG sistemi hakkında
    st.divider()

    with st.expander("ℹ️ AI Asistan Hakkında"):
        if RAG_TYPE == "groq":
            st.markdown("""
            ### ESG AI Asistan - Groq LLM

            **Aktif Model:** Mixtral-8x7B (Groq API)

            ✅ **Özellikler:**
            - Gerçek LLM ile akıllı cevaplar
            - Mükemmel Türkçe destek
            - Çok hızlı yanıt (saniyeler)
            - 14,400 ücretsiz istek/gün

            **Bilgi Tabanı:**
            - GHG Protocol (Scope 1, 2, 3)
            - GRI 305 Standardı
            - Karbon muhasebesi metodolojileri
            - ESG raporlama kılavuzları
            - Emisyon azaltma stratejileri

            **API Key Almak İçin:**
            1. https://console.groq.com adresine gidin
            2. Ücretsiz hesap açın (Google ile giriş)
            3. API Keys > Create API Key
            4. .env dosyasına ekleyin: `GROQ_API_KEY=gsk_...`
            """)
        else:
            st.markdown("""
            ### ESG AI Asistan - Basit Mod

            **Aktif Mod:** Keyword Matching (LLM yok)

            **Groq LLM için (ÜCRETSİZ):**
            ```bash
            pip install groq
            # .env dosyasına GROQ_API_KEY ekleyin
            ```

            **Bilgi Tabanı:**
            - Scope 1, 2, 3 tanımları
            - GRI standardları
            - Net Zero ve carbon offsetting
            - GHG Protocol
            - CDP
            """)

# ==================== HAKKINDA ====================
elif menu == "ℹ️ Hakkında":
    st.header("ℹ️ Hakkında")

    st.markdown("""
    ## ESG Carbon Calculator & Report Generator

    **Versiyon:** 1.0.0
    **Teknolojiler:**
    - 🌐 **Frontend:** Streamlit
    - 📊 **API:** Climatiq Emission Factors API
    - 🤖 **AI:** LangChain + RAG + HuggingFace LLM
    - 💾 **Vector DB:** ChromaDB
    - 📄 **PDF:** ReportLab

    ### Özellikler:
    - ✅ 277,000+ emission factor veritabanı
    - ✅ Otomatik CO2e hesaplama
    - ✅ Scope 1, 2, 3 kategorilendirme
    - ✅ AI destekli ESG raporu
    - ✅ RAG tabanlı akıllı asistan

    ### Kaynaklar:
    - [Climatiq API](https://www.climatiq.io)
    - [GRI Standards](https://www.globalreporting.org)
    - [GHG Protocol](https://ghgprotocol.org)

    ---
    © 2025 - ESG Carbon Calculator
    """)

# Footer
st.divider()
st.caption("Powered by Climatiq API | Built with Streamlit & ❤️")
