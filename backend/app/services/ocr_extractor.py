"""
OCR Data Extractor Service
PDF/Image dosyalarından OCR ile veri çıkarma
"""

import os
import re
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

# Add backend to path
import sys
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir.parent))


class OCRExtractor:
    """PDF/Image dosyalarından OCR ile emisyon verisi çıkarma"""

    def __init__(self):
        self.supported_formats = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
        self.tesseract_available = self._check_tesseract()

    def _check_tesseract(self) -> bool:
        """Tesseract OCR kurulu mu kontrol et"""
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            return True
        except:
            return False

    def extract_from_image_bytes(self, image_bytes: bytes, filename: str = "") -> Dict:
        """
        Image bytes'tan OCR ile metin çıkar
        
        Args:
            image_bytes: Görüntü verisi
            filename: Dosya adı (format tespiti için)
        
        Returns:
            Çıkarılan veriler
        """
        result = {
            "success": False,
            "raw_text": "",
            "extracted_data": [],
            "confidence": 0,
            "error": None
        }

        if not self.tesseract_available:
            result["error"] = "Tesseract OCR kurulu değil. pip install pytesseract ve Tesseract kurulumu gerekli."
            return result

        try:
            import pytesseract
            from PIL import Image
            import io

            # Image'ı aç
            image = Image.open(io.BytesIO(image_bytes))
            
            # OCR uygula
            text = pytesseract.image_to_string(image, lang='tur+eng')
            
            result["raw_text"] = text
            result["success"] = True
            
            # Metinden veri çıkar
            result["extracted_data"] = self._parse_emission_text(text)
            
            # Güven skoru (basit hesaplama)
            result["confidence"] = min(0.9, len(text) / 1000)

        except ImportError as e:
            result["error"] = f"Gerekli kütüphane kurulu değil: {str(e)}"
        except Exception as e:
            result["error"] = f"OCR hatası: {str(e)}"

        return result

    def extract_from_pdf_bytes(self, pdf_bytes: bytes) -> Dict:
        """
        PDF bytes'tan OCR ile metin çıkar
        
        Args:
            pdf_bytes: PDF verisi
        
        Returns:
            Çıkarılan veriler
        """
        result = {
            "success": False,
            "raw_text": "",
            "extracted_data": [],
            "pages_processed": 0,
            "confidence": 0,
            "error": None
        }

        # Önce normal PDF okumayı dene
        try:
            import PyPDF2
            import io
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            result["pages_processed"] = len(pdf_reader.pages)
            
            if text.strip():
                result["raw_text"] = text
                result["success"] = True
                result["extracted_data"] = self._parse_emission_text(text)
                result["confidence"] = 0.9  # Normal PDF okuma yüksek güvenilir
                return result
                
        except Exception as e:
            pass  # OCR'a devam et

        # OCR ile dene (taranmış PDF'ler için)
        if not self.tesseract_available:
            result["error"] = "PDF metin içermiyor ve Tesseract OCR kurulu değil."
            return result

        try:
            import pdf2image
            import pytesseract
            from PIL import Image
            import io
            
            # PDF'i görüntülere dönüştür
            images = pdf2image.convert_from_bytes(pdf_bytes)
            
            all_text = ""
            for i, image in enumerate(images):
                page_text = pytesseract.image_to_string(image, lang='tur+eng')
                all_text += f"\n--- Sayfa {i+1} ---\n{page_text}"
            
            result["raw_text"] = all_text
            result["pages_processed"] = len(images)
            result["success"] = True
            result["extracted_data"] = self._parse_emission_text(all_text)
            result["confidence"] = 0.7  # OCR daha düşük güvenilirlik

        except ImportError as e:
            result["error"] = f"pdf2image veya pytesseract kurulu değil: {str(e)}"
        except Exception as e:
            result["error"] = f"OCR PDF hatası: {str(e)}"

        return result

    def _parse_emission_text(self, text: str) -> List[Dict]:
        """
        Metinden emisyon verilerini çıkar
        """
        extracted = []

        # Pattern 1: Enerji tüketimi
        pattern1 = r"(elektrik|electricity|doğalgaz|natural\s*gas|benzin|petrol|diesel|dizel)[\s:]*(tüketim[i]?|consumption)?[:\s]+([0-9,\.]+)\s*(kwh|mwh|m³|m3|litre|l|kg|ton)"
        matches1 = re.finditer(pattern1, text.lower(), re.IGNORECASE)

        for match in matches1:
            try:
                category = match.group(1).strip()
                value_str = match.group(3).replace(',', '')
                unit = match.group(4).strip()
                
                # Türkçe format düzeltme (1.234 -> 1234, 1.234,56 -> 1234.56)
                if '.' in value_str and ',' not in value_str:
                    # 1.234 formatı (bin ayracı olarak nokta)
                    value_str = value_str.replace('.', '')
                elif ',' in value_str:
                    # 1.234,56 formatı
                    value_str = value_str.replace('.', '').replace(',', '.')
                
                value = float(value_str)

                # Kategori mapping
                if 'elektrik' in category or 'electricity' in category:
                    cat_name = "Elektrik"
                    scope = "Scope 2"
                elif 'doğalgaz' in category or 'natural gas' in category:
                    cat_name = "Doğalgaz"
                    scope = "Scope 1"
                elif any(x in category for x in ['benzin', 'petrol', 'diesel', 'dizel']):
                    cat_name = "Yakıt"
                    scope = "Scope 1"
                else:
                    cat_name = category.title()
                    scope = "Unknown"

                extracted.append({
                    "category": cat_name,
                    "scope": scope,
                    "amount": value,
                    "unit": unit,
                    "source": "ocr_extraction",
                    "confidence": 0.7
                })

            except ValueError:
                continue

        # Pattern 2: Scope emisyonları
        pattern2 = r"(scope|kapsam)[\s]*([123])[:\s]*(emisyon)?[:\s]*([0-9,\.]+)\s*(ton|kg)"
        matches2 = re.finditer(pattern2, text.lower(), re.IGNORECASE)

        for match in matches2:
            try:
                scope_num = match.group(2)
                value_str = match.group(4).replace(',', '')
                
                if '.' in value_str and value_str.count('.') > 1:
                    value_str = value_str.replace('.', '')
                elif '.' in value_str:
                    # Normal ondalık
                    pass
                    
                value = float(value_str)
                unit = match.group(5).strip()

                extracted.append({
                    "category": f"Scope {scope_num} Emisyonu",
                    "scope": f"Scope {scope_num}",
                    "amount": value,
                    "unit": f"{unit} CO2e",
                    "source": "ocr_extraction",
                    "confidence": 0.8
                })

            except ValueError:
                continue

        # Pattern 3: CO2 emisyonu
        pattern3 = r"(toplam|total|ghg|co2|karbon)[\s]*(emisyon[u]?|emission)?[:\s]+([0-9,\.]+)\s*(ton|kg)"
        matches3 = re.finditer(pattern3, text.lower(), re.IGNORECASE)

        for match in matches3:
            try:
                category = match.group(1).strip()
                value_str = match.group(3).replace(',', '')
                
                if '.' in value_str and value_str.count('.') > 1:
                    value_str = value_str.replace('.', '')
                    
                value = float(value_str)
                unit = match.group(4).strip()

                extracted.append({
                    "category": f"{category.title()} Emisyonu",
                    "scope": "Unknown",
                    "amount": value,
                    "unit": f"{unit} CO2e",
                    "source": "ocr_extraction",
                    "confidence": 0.7
                })

            except ValueError:
                continue

        # Duplicate temizleme
        seen = set()
        unique = []
        for item in extracted:
            key = (item['category'], item['amount'], item['unit'])
            if key not in seen:
                seen.add(key)
                unique.append(item)

        return unique

    def extract_invoice_data(self, text: str) -> Dict:
        """
        Fatura metninden yapılandırılmış veri çıkar
        """
        result = {
            "electricity_kwh": 0,
            "natural_gas_m3": 0,
            "water_litre": 0,
            "period": "",
            "provider": "",
            "amount_tl": 0,
            "raw_values": []
        }

        text_lower = text.lower()

        # Helper function to parse Turkish number format
        def parse_turkish_number(val_str):
            # Remove spaces
            val_str = val_str.strip()
            # Check if it's Turkish format (1.234,56) or (1.234)
            if ',' in val_str:
                # 1.234,56 format -> 1234.56
                val_str = val_str.replace('.', '').replace(',', '.')
            elif val_str.count('.') > 1:
                # 1.234.567 format -> 1234567
                val_str = val_str.replace('.', '')
            elif '.' in val_str:
                # Could be 1.234 (thousand) or 1.5 (decimal)
                parts = val_str.split('.')
                if len(parts[1]) == 3:
                    # Likely thousand separator (1.234)
                    val_str = val_str.replace('.', '')
                # else it's decimal, keep as is
            return float(val_str)

        # Elektrik tüketimi - look for specific "TÜKETİM" patterns first
        # Also handle UTF-8 encoding issues (TÜKETİMİ can become TÃœKETÄ°MÄ°)
        # Handle newlines between label and value
        elec_patterns = [
            # Turkish correct encoding
            r"elektrik\s+tüketimi[:\s]+([0-9,\.]+)\s*kwh",
            r"tüketimi[:\s]+([0-9,\.]+)\s*kwh",
            # UTF-8 garbled (common in PDF extraction) with newline handling
            r"elektr.{1,5}k\s+t.{1,5}ket.{1,5}m.{0,3}[:\s\n]+([0-9,\.]+)\s*kwh",
            r"t.{1,5}ket.{1,5}m.{0,3}[:\s\n]+([0-9,\.]+)\s*kwh",
            # Generic patterns with newline handling
            r"elektrik[:\s\n]+([0-9,\.]+)\s*kwh",
            r"consumption[:\s\n]+([0-9,\.]+)\s*kwh",
        ]
        for pattern in elec_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    result["electricity_kwh"] = parse_turkish_number(match.group(1))
                    result["raw_values"].append({"type": "electricity", "value": result["electricity_kwh"], "unit": "kWh"})
                    break
                except:
                    pass

        # Doğalgaz tüketimi - look for specific patterns
        # Handle UTF-8 encoding issues and various m³ representations
        gas_patterns = [
            # Turkish correct encoding
            r"doğalgaz\s+tüketimi[:\s]+([0-9,\.]+)\s*m[³3²]",
            r"tüketimi[:\s]+([0-9,\.]+)\s*m[³3²]",
            # UTF-8 garbled
            r"do.{1,5}algaz\s+t.{1,5}ket.{1,5}m.{0,3}[:\s]+([0-9,\.]+)\s*m.{0,3}",
            r"do.{1,5}algaz[:\s]+([0-9,\.]+)\s*m.{0,3}",
            # Generic patterns (m³ can appear as mÂ³, m3, etc.)
            r"gaz[:\s]+([0-9,\.]+)\s*m[³3²]",
            r"consumption[:\s]+([0-9,\.]+)\s*m[³3²]",
        ]
        for pattern in gas_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                try:
                    result["natural_gas_m3"] = parse_turkish_number(match.group(1))
                    result["raw_values"].append({"type": "natural_gas", "value": result["natural_gas_m3"], "unit": "m³"})
                    break
                except:
                    pass

        # Su tüketimi - look for specific patterns
        water_patterns = [
            r"su\s+tüketimi[:\s]+([0-9,\.]+)\s*m[³3]",
            r"su\s+tüketimi[:\s]+([0-9,\.]+)\s*litre",
            r"tüketimi[:\s]+([0-9,\.]+)\s*m[³3]\s*\(([0-9,\.]+)\s*litre",
            r"([0-9,\.]+)\s*litre\s*toplam",
            r"([0-9,\.]+)\s*litre",
        ]
        for pattern in water_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    val = parse_turkish_number(match.group(1))
                    # If it's m³, convert to litre (1 m³ = 1000 L)
                    if 'm³' in pattern or 'm3' in pattern:
                        result["water_litre"] = val * 1000
                    else:
                        result["water_litre"] = val
                    result["raw_values"].append({"type": "water", "value": result["water_litre"], "unit": "litre"})
                    break
                except:
                    pass

        # Dönem tespiti
        period_patterns = [
            r"dönem[i]?[:\s]+(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)\s*(\d{4})",
            r"(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)\s*(\d{4})",
            r"(\d{2})[\/\-](\d{4})",
            r"(january|february|march|april|may|june|july|august|september|october|november|december)\s*(\d{4})"
        ]
        for pattern in period_patterns:
            match = re.search(pattern, text_lower)
            if match:
                result["period"] = match.group(0)
                break

        # Tutar (TL) - look for GENEL TOPLAM first
        amount_patterns = [
            r"genel\s+toplam[:\s]+([0-9,\.]+)\s*(tl|₺)?",
            r"toplam[:\s]+([0-9,\.]+)\s*(tl|₺)",
            r"tutar[:\s]+([0-9,\.]+)\s*(tl|₺)",
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                try:
                    result["amount_tl"] = parse_turkish_number(match.group(1))
                    break
                except:
                    pass

        return result

