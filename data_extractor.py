"""
Data Extractor - PDF/Excel/CSV veri çıkarma modülü
OCR, Table extraction, NER ile otomatik veri çıkarma
"""

import os
import re
from typing import List, Dict, Optional
from datetime import datetime

class DataExtractor:
    """PDF/Excel/CSV dosyalarından veri çıkarma"""

    def __init__(self):
        self.supported_formats = ['.pdf', '.xlsx', '.xls', '.csv']

    def extract_from_file(self, file_path: str, file_type: str = None) -> Dict:
        """
        Dosyadan veri çıkar

        Args:
            file_path: Dosya yolu veya UploadedFile objesi
            file_type: Dosya tipi (.pdf, .xlsx, .csv)

        Returns:
            {
                "success": bool,
                "data": List[Dict],  # Çıkarılan emisyon verileri
                "raw_text": str,     # Ham metin (PDF için)
                "tables": List,      # Tablolar
                "error": str         # Hata mesajı (varsa)
            }
        """

        result = {
            "success": False,
            "data": [],
            "raw_text": "",
            "tables": [],
            "error": None
        }

        try:
            # Dosya tipini belirle
            if file_type is None:
                if hasattr(file_path, 'name'):
                    file_type = os.path.splitext(file_path.name)[1].lower()
                else:
                    file_type = os.path.splitext(file_path)[1].lower()

            # Dosya tipine göre işle
            if file_type == '.pdf':
                result = self._extract_from_pdf(file_path)
            elif file_type in ['.xlsx', '.xls']:
                result = self._extract_from_excel(file_path)
            elif file_type == '.csv':
                result = self._extract_from_csv(file_path)
            else:
                result["error"] = f"Desteklenmeyen dosya tipi: {file_type}"

        except Exception as e:
            result["error"] = f"Dosya işleme hatası: {str(e)}"

        return result

    def _extract_from_pdf(self, file_path) -> Dict:
        """PDF'den veri çıkar (OCR + Table extraction)"""

        result = {
            "success": False,
            "data": [],
            "raw_text": "",
            "tables": [],
            "error": None
        }

        try:
            import PyPDF2

            # PDF'den metin çıkar
            if hasattr(file_path, 'read'):
                # Streamlit UploadedFile
                pdf_reader = PyPDF2.PdfReader(file_path)
            else:
                # File path
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)

            # Tüm sayfalardan metin çıkar
            full_text = ""
            for page in pdf_reader.pages:
                full_text += page.extract_text() + "\n"

            result["raw_text"] = full_text

            # Metin analizi ile veri çıkarma
            extracted_data = self._parse_emission_text(full_text)
            result["data"] = extracted_data

            result["success"] = True

        except ImportError:
            result["error"] = "PyPDF2 kurulu değil. pip install PyPDF2"
        except Exception as e:
            result["error"] = f"PDF okuma hatası: {str(e)}"

        return result

    def _extract_from_excel(self, file_path) -> Dict:
        """Excel'den veri çıkar"""

        result = {
            "success": False,
            "data": [],
            "raw_text": "",
            "tables": [],
            "error": None
        }

        try:
            import pandas as pd

            # Excel dosyasını oku
            if hasattr(file_path, 'read'):
                # Streamlit UploadedFile
                df = pd.read_excel(file_path)
            else:
                df = pd.read_excel(file_path)

            # DataFrame'i liste olarak kaydet
            result["tables"].append(df)

            # Excel'den veri çıkarma
            extracted_data = self._parse_excel_dataframe(df)
            result["data"] = extracted_data

            result["success"] = True

        except ImportError:
            result["error"] = "openpyxl kurulu değil. pip install openpyxl"
        except Exception as e:
            result["error"] = f"Excel okuma hatası: {str(e)}"

        return result

    def _extract_from_csv(self, file_path) -> Dict:
        """CSV'den veri çıkar"""

        result = {
            "success": False,
            "data": [],
            "raw_text": "",
            "tables": [],
            "error": None
        }

        try:
            import pandas as pd

            # CSV dosyasını oku
            if hasattr(file_path, 'read'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_csv(file_path)

            result["tables"].append(df)

            # CSV'den veri çıkarma
            extracted_data = self._parse_excel_dataframe(df)
            result["data"] = extracted_data

            result["success"] = True

        except Exception as e:
            result["error"] = f"CSV okuma hatası: {str(e)}"

        return result

    def _parse_emission_text(self, text: str) -> List[Dict]:
        """
        Metinden emisyon verilerini çıkar (NER benzeri)

        Aranacak pattern'ler:
        - "Elektrik: 1,234 kWh"
        - "Scope 1 Emissions: 500 ton CO2e"
        - "Natural Gas Consumption: 200 m³"
        - "Elektrik Tüketimi: 15.000 kWh" (Türkçe format)
        - "GHG Emisyonları: 1.234,56 ton CO2e"
        """

        extracted = []

        # Pattern 1: "Elektrik: 1,234 kWh" formatı (GENİŞLETİLMİŞ)
        # Artık tüketim, emisyon, consumption gibi kelimeleri de yakalar
        pattern1 = r"(elektrik|electricity|doğalgaz|do[ğg]algaz|natural\s*gas|benzin|petrol|diesel|dizel|gaz|fuel|yakıt|yak[ıi]t)[\s:]*(tüketim[i]?|t[üu]ketim[i]?|consumption|emisyon[u]?|emissions?)?[:\s]+([0-9,\.]+)\s*(kwh|mwh|m³|m3|m\^3|litre|l|kg|ton|tonnes)"
        matches1 = re.finditer(pattern1, text.lower(), re.IGNORECASE)

        for match in matches1:
            category = match.group(1).strip()
            value_str = match.group(3).replace(',', '').replace('.', '')  # Türkçe format: 1.234 -> 1234
            unit = match.group(4).strip()

            try:
                value = float(value_str)

                # Kategori mapping
                if 'elektrik' in category or 'electricity' in category:
                    cat_name = "Elektrik"
                    scope = "Scope 2"
                    unit_type = "Energy"
                elif 'doğalgaz' in category or 'natural gas' in category:
                    cat_name = "Doğalgaz"
                    scope = "Scope 1"
                    unit_type = "Energy"
                elif 'benzin' in category or 'petrol' in category or 'diesel' in category or 'dizel' in category:
                    cat_name = "Yakıt"
                    scope = "Scope 1"
                    unit_type = "Volume"
                else:
                    cat_name = category.title()
                    scope = "Unknown"
                    unit_type = "Energy"

                entry = {
                    "category": cat_name,
                    "scope": scope,
                    "amount": value,
                    "unit": unit,
                    "unit_type": unit_type,
                    "source": "pdf_extraction",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "confidence": 0.7  # Orta güven
                }

                extracted.append(entry)

            except ValueError:
                continue

        # Pattern 2: "Scope X: 1,234 ton CO2e" formatı (GENİŞLETİLMİŞ)
        # GHG, emisyon, CO2, carbon gibi kelimeleri de yakalar
        pattern2 = r"(scope|kapsam)[\s]*([123])?[:\s]*(emisyon[u]?|emissions?|ghg)?[:\s]*([0-9,\.]+)\s*(ton|tonnes|kg|mt)\s*(co2|co2e|carbon|karbon)?"
        matches2 = re.finditer(pattern2, text.lower(), re.IGNORECASE)

        for match in matches2:
            scope_num = match.group(2) if match.group(2) else "Unknown"  # Scope number (opsiyonel)
            value_str = match.group(4).replace(',', '').replace('.', '')  # Value
            unit = match.group(5).strip()  # Unit (ton, kg, etc.)

            try:
                value = float(value_str)

                entry = {
                    "category": f"Scope {scope_num} (PDF'den)",
                    "scope": f"Scope {scope_num}",
                    "amount": value,
                    "unit": "ton CO2e" if unit == "ton" else unit,
                    "unit_type": "Weight",
                    "source": "pdf_extraction",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "confidence": 0.8  # Yüksek güven (açık format)
                }

                extracted.append(entry)

            except ValueError:
                continue

        # Pattern 3: Genel emisyon pattern'i (yeni!)
        # "Toplam Emisyon: 1.234 ton CO2e", "GHG Emissions: 5,678 kg CO2"
        pattern3 = r"(toplam|total|ghg|sera\s*gaz[ıi]|greenhouse|emisyon[u]?|emissions?|carbon|karbon|co2)\s*(emisyon[u]?|emissions?|footprint|ayak\s*iz[i]?)?[:\s]+([0-9,\.]+)\s*(ton|tonnes|kg|mt)\s*(co2|co2e|carbon|karbon)?"
        matches3 = re.finditer(pattern3, text.lower(), re.IGNORECASE)

        for match in matches3:
            category = match.group(1).strip()
            value_str = match.group(3).replace(',', '').replace('.', '')
            unit = match.group(4).strip()

            try:
                value = float(value_str)

                entry = {
                    "category": f"{category.title()} Emisyonu",
                    "scope": "Unknown",  # Scope belirsiz
                    "amount": value,
                    "unit": "ton CO2e" if unit in ["ton", "tonnes"] else f"{unit} CO2e",
                    "unit_type": "Weight",
                    "source": "pdf_extraction",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "confidence": 0.7  # Orta güven
                }

                extracted.append(entry)

            except ValueError:
                continue

        return extracted

    def _parse_excel_dataframe(self, df) -> List[Dict]:
        """
        Excel/CSV DataFrame'den emisyon verilerini çıkar

        Beklenen sütunlar (esnek):
        - Category/Kategori
        - Amount/Miktar
        - Unit/Birim
        - Scope (opsiyonel)
        """

        extracted = []

        # Sütun adlarını normalize et (lowercase, strip)
        df.columns = [col.strip().lower() for col in df.columns]

        # Gerekli sütunları bul
        category_col = None
        amount_col = None
        unit_col = None
        scope_col = None

        for col in df.columns:
            if 'category' in col or 'kategori' in col or 'activity' in col or 'aktivite' in col:
                category_col = col
            elif 'amount' in col or 'miktar' in col or 'value' in col or 'değer' in col or 'quantity' in col:
                amount_col = col
            elif 'unit' in col or 'birim' in col:
                unit_col = col
            elif 'scope' in col or 'kapsam' in col:
                scope_col = col

        if not category_col or not amount_col:
            return []  # Gerekli sütunlar bulunamadı

        # Her satırı işle
        for _, row in df.iterrows():
            try:
                category = str(row[category_col]).strip()
                amount = float(row[amount_col])

                # Boş satırları atla
                if category == 'nan' or amount == 0:
                    continue

                unit = str(row[unit_col]).strip() if unit_col and unit_col in row.index else "unknown"
                scope = str(row[scope_col]).strip() if scope_col and scope_col in row.index else "Unknown"

                # Unit type tahmin et
                unit_type = self._guess_unit_type(unit, category)

                entry = {
                    "category": category,
                    "scope": scope if scope != "nan" else "Unknown",
                    "amount": amount,
                    "unit": unit if unit != "nan" else "unknown",
                    "unit_type": unit_type,
                    "source": "excel_import",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "confidence": 0.9  # Yüksek güven (yapılandırılmış veri)
                }

                extracted.append(entry)

            except (ValueError, KeyError):
                continue

        return extracted

    def _guess_unit_type(self, unit: str, category: str = "") -> str:
        """Birimden unit_type tahmin et"""

        unit_lower = unit.lower()
        category_lower = category.lower()

        # Energy
        if any(u in unit_lower for u in ['kwh', 'mwh', 'gwh', 'joule', 'kj', 'mj']):
            return "Energy"

        # Distance
        if any(u in unit_lower for u in ['km', 'mile', 'meter', 'metre']):
            return "Distance"

        # Weight
        if any(u in unit_lower for u in ['kg', 'ton', 'tonne', 'gram', 'g', 'lb']):
            return "Weight"

        # Volume
        if any(u in unit_lower for u in ['m3', 'm³', 'litre', 'liter', 'l', 'gallon']):
            return "Volume"

        # Money
        if any(u in unit_lower for u in ['usd', 'eur', 'gbp', 'tl', 'try', '$', '€', '£']):
            return "Money"

        # Kategori bazlı tahmin
        if any(k in category_lower for k in ['elektrik', 'electricity', 'enerji', 'energy']):
            return "Energy"
        elif any(k in category_lower for k in ['araç', 'vehicle', 'ulaşım', 'transport', 'seyahat', 'travel']):
            return "Distance"
        elif any(k in category_lower for k in ['doğalgaz', 'natural gas', 'gaz', 'gas']):
            return "Volume"

        # Default
        return "Energy"


# Test
if __name__ == "__main__":
    extractor = DataExtractor()

    # Test metni
    test_text = """
    ESG Report 2024

    Energy Consumption:
    - Elektrik: 15,000 kWh
    - Doğalgaz: 500 m³

    GHG Emissions:
    Scope 1: 1,234 ton CO2e
    Scope 2: 2,500 tonnes CO2
    Scope 3: 15,000 ton CO2e

    Vehicle fuel: 200 litre diesel
    """

    result = extractor._parse_emission_text(test_text)

    print("="*60)
    print("EXTRACTED DATA FROM TEXT:")
    print("="*60)
    for item in result:
        print(f"{item['category']}: {item['amount']} {item['unit']} ({item['scope']})")
    print(f"\nTotal: {len(result)} entries extracted")
    print("="*60)
