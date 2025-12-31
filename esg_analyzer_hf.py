"""
ESG Report Analyzer with Hugging Face Models
PDF raporlarından ESG bilgilerini otomatik çıkarır
"""

import os
import re
from typing import Dict, List, Tuple
from dotenv import load_dotenv

load_dotenv()

class ESGAnalyzer:
    """Hugging Face ESG modelleri ile rapor analizi"""

    def __init__(self):
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')

        if not self.api_key:
            print("[WARNING] HUGGINGFACE_API_KEY bulunamadi. Basit analiz modu kullanilacak.")
            self.use_api = False
        else:
            try:
                from huggingface_hub import InferenceClient
                self.client = InferenceClient(token=self.api_key)
                self.use_api = True
                print("[OK] Hugging Face API baglantisi kuruldu")
            except ImportError:
                print("[WARNING] huggingface_hub kurulu degil. pip install huggingface_hub")
                self.use_api = False

        # ESG için özel modeller
        self.models = {
            "esg_classification": "yiyanghkust/finbert-esg",  # ESG sınıflandırma
            "sentiment": "ProsusAI/finbert",  # Finansal sentiment
            "ner": "dslim/bert-base-NER"  # Named Entity Recognition
        }

        # Scope keywords (regex için)
        self.scope_keywords = {
            "scope1": [
                r"scope\s*1", r"direct\s*emissions?", r"doğrudan\s*emisyon",
                r"natural\s*gas", r"doğalgaz", r"fuel\s*combustion",
                r"company\s*vehicles?", r"şirket\s*araç"
            ],
            "scope2": [
                r"scope\s*2", r"indirect\s*emissions?", r"dolaylı\s*emisyon",
                r"purchased\s*electricity", r"satın\s*alınan\s*elektrik",
                r"steam", r"buhar", r"heating", r"ısıtma"
            ],
            "scope3": [
                r"scope\s*3", r"value\s*chain", r"değer\s*zinciri",
                r"supply\s*chain", r"tedarik\s*zinciri", r"business\s*travel",
                r"iş\s*seyahat", r"upstream", r"downstream"
            ]
        }

    def analyze_text(self, text: str) -> Dict:
        """
        ESG metnini analiz et

        Args:
            text: Analiz edilecek metin (PDF'den çıkarılmış)

        Returns:
            Analiz sonuçları dict
        """

        results = {
            "scope_detection": self._detect_scopes(text),
            "emission_values": self._extract_emission_values(text),
            "esg_classification": self._classify_esg(text),
            "risk_score": 0,
            "summary": ""
        }

        # Risk skoru hesapla
        results["risk_score"] = self._calculate_risk_score(results)

        # Özet oluştur
        results["summary"] = self._generate_summary(results)

        return results

    def _detect_scopes(self, text: str) -> Dict[str, bool]:
        """Metinde hangi scope'lar geçiyor tespit et"""

        text_lower = text.lower()

        detected = {
            "scope1": False,
            "scope2": False,
            "scope3": False
        }

        for scope, patterns in self.scope_keywords.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    detected[scope] = True
                    break

        return detected

    def _extract_emission_values(self, text: str) -> List[Dict]:
        """Metindeki emisyon değerlerini çıkar"""

        # Regex patterns for emission values
        patterns = [
            # "1,234 ton CO2e", "1234.5 tonnes CO2"
            r"([\d,\.]+)\s*(ton|tonne|kg|mt)s?\s*(co2|co2e|carbon|karbon)",
            # "CO2: 1,234 tons"
            r"(co2|co2e|carbon|karbon)[:\s]+([\d,\.]+)\s*(ton|tonne|kg)",
            # "Scope 1: 1,234 ton CO2e"
            r"scope\s*[123][:\s]+([\d,\.]+)\s*(ton|tonne|kg)",
        ]

        emissions = []

        for pattern in patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                try:
                    # Sayıyı çıkar
                    value_str = match.group(1) if match.group(1).replace(',', '').replace('.', '').isdigit() else match.group(2)
                    value = float(value_str.replace(',', ''))

                    emissions.append({
                        "value": value,
                        "unit": match.group(2) if len(match.groups()) > 1 else "ton",
                        "context": match.group(0)
                    })
                except:
                    continue

        return emissions[:10]  # İlk 10 bulgu

    def _classify_esg(self, text: str) -> Dict:
        """ESG kategorilerine göre sınıflandır (HF modeli ile)"""

        if not self.use_api:
            # Basit keyword-based classification
            return self._simple_esg_classification(text)

        try:
            # Hugging Face FinBERT-ESG modeli
            # Bu model metni E/S/G kategorilerine ayırır

            # Metni kısalt (model limiti)
            text_sample = text[:512]

            response = self.client.text_classification(
                text_sample,
                model=self.models["esg_classification"]
            )

            # Response: [{"label": "Environmental", "score": 0.95}, ...]
            categories = {
                "Environmental": 0,
                "Social": 0,
                "Governance": 0
            }

            for item in response:
                label = item.get("label", "")
                score = item.get("score", 0)

                if "environ" in label.lower() or label == "E":
                    categories["Environmental"] = max(categories["Environmental"], score)
                elif "social" in label.lower() or label == "S":
                    categories["Social"] = max(categories["Social"], score)
                elif "govern" in label.lower() or label == "G":
                    categories["Governance"] = max(categories["Governance"], score)

            return categories

        except Exception as e:
            print(f"⚠️ ESG classification hatası: {e}")
            return self._simple_esg_classification(text)

    def _simple_esg_classification(self, text: str) -> Dict:
        """Basit keyword-based ESG sınıflandırma"""

        text_lower = text.lower()

        keywords = {
            "Environmental": [
                "carbon", "emission", "climate", "energy", "waste",
                "karbon", "emisyon", "iklim", "enerji", "atık",
                "renewable", "sustainability", "pollution"
            ],
            "Social": [
                "employee", "diversity", "health", "safety", "community",
                "çalışan", "çeşitlilik", "sağlık", "güvenlik", "toplum",
                "human rights", "labor", "inclusion"
            ],
            "Governance": [
                "board", "ethics", "compliance", "audit", "transparency",
                "yönetim kurulu", "etik", "uyum", "denetim", "şeffaflık",
                "risk management", "governance structure"
            ]
        }

        scores = {category: 0 for category in keywords.keys()}

        for category, words in keywords.items():
            for word in words:
                scores[category] += text_lower.count(word)

        # Normalize (0-1 arası)
        total = sum(scores.values()) or 1
        return {cat: round(score / total, 2) for cat, score in scores.items()}

    def _calculate_risk_score(self, results: Dict) -> float:
        """ESG risk skoru hesapla (0-100)"""

        risk = 0

        # Scope tespiti
        scopes = results["scope_detection"]
        if not scopes["scope1"]:
            risk += 20
        if not scopes["scope2"]:
            risk += 15
        if not scopes["scope3"]:
            risk += 30  # Scope 3 en önemli

        # Emisyon değerleri
        if len(results["emission_values"]) == 0:
            risk += 25  # Hiç veri yok

        # ESG kategorileri
        esg = results["esg_classification"]
        if esg.get("Environmental", 0) < 0.3:
            risk += 10  # Çevresel bilgi az

        return min(risk, 100)

    def _generate_summary(self, results: Dict) -> str:
        """Analiz özeti oluştur"""

        scopes = results["scope_detection"]
        emissions = results["emission_values"]
        risk = results["risk_score"]

        summary = "### Analiz Ozeti\n\n"

        # Scope tespiti
        summary += "**Tespit Edilen Scope'lar:**\n"
        summary += f"- Scope 1: {'[OK] Var' if scopes['scope1'] else '[X] Yok'}\n"
        summary += f"- Scope 2: {'[OK] Var' if scopes['scope2'] else '[X] Yok'}\n"
        summary += f"- Scope 3: {'[OK] Var' if scopes['scope3'] else '[X] Yok'}\n\n"

        # Emisyon değerleri
        if emissions:
            summary += f"**Bulunan Emisyon Degerleri:** {len(emissions)} adet\n"
            for em in emissions[:3]:
                summary += f"- {em['value']} {em['unit']} ({em['context'][:50]}...)\n"
            summary += "\n"

        # Risk skoru
        if risk < 30:
            risk_level = "[LOW] Dusuk Risk"
        elif risk < 60:
            risk_level = "[MED] Orta Risk"
        else:
            risk_level = "[HIGH] Yuksek Risk"

        summary += f"**Risk Skoru:** {risk}/100 - {risk_level}\n"

        return summary

    def analyze_pdf(self, pdf_path: str) -> Dict:
        """PDF dosyasını analiz et"""

        try:
            import PyPDF2

            # PDF'den metin çıkar
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()

            # Analiz et
            return self.analyze_text(text)

        except ImportError:
            return {"error": "PyPDF2 kurulu değil. pip install PyPDF2"}
        except Exception as e:
            return {"error": f"PDF okuma hatası: {str(e)}"}


# Test
if __name__ == "__main__":
    print("="*60)
    print("ESG ANALYZER TEST")
    print("="*60)

    analyzer = ESGAnalyzer()

    # Test metni
    test_text = """
    ESG Report 2024

    Our company's greenhouse gas emissions for 2024:

    Scope 1 Emissions: 1,234 ton CO2e
    - Direct emissions from company vehicles
    - Natural gas consumption: 500 m³

    Scope 2 Emissions: 2,500 tonnes CO2
    - Purchased electricity: 10,000 kWh

    Scope 3 Emissions: 15,000 ton CO2e
    - Business travel
    - Supply chain emissions

    We are committed to reaching Net Zero by 2050.
    """

    print("\n[TEST] Analyzing sample ESG text...")
    results = analyzer.analyze_text(test_text)

    print("\n[RESULTS]")
    print(f"Scopes: {results['scope_detection']}")
    print(f"Emissions found: {len(results['emission_values'])}")
    print(f"ESG Classification: {results['esg_classification']}")
    print(f"Risk Score: {results['risk_score']}/100")
    print(f"\n{results['summary']}")

    print("\n" + "="*60)
