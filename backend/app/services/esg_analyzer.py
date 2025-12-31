"""
ESG Report Analyzer Service - Enhanced Version
PDF raporlarından ESG bilgilerini gelişmiş algoritmalarla çıkarır
"""

import os
import re
import math
from typing import Dict, List, Tuple
from pathlib import Path

# Add backend to path
import sys
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir.parent))


class ESGAnalyzer:
    """Gelişmiş ESG metin analizi servisi"""

    def __init__(self):
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.use_api = False
        
        if self.api_key:
            try:
                from huggingface_hub import InferenceClient
                self.client = InferenceClient(token=self.api_key)
                self.use_api = True
            except ImportError:
                pass

        # Genişletilmiş scope keywords - ASCII ve Unicode uyumlu
        self.scope_keywords = {
            "scope1": {
                "primary": [r"scope\s*1", r"kapsam\s*1", r"dogrudan\s*emisyon", r"do[gğ]rudan"],
                "secondary": [
                    r"natural\s*gas", r"do[gğ]algaz", r"do[gğ]al\s*gaz", r"dogalgaz",
                    r"fuel\s*combustion", r"yak[ıi]t\s*yanma", r"yakit",
                    r"company\s*vehicles?", r"[sş]irket\s*ara[cç]", r"sirket\s*arac", r"filo",
                    r"diesel", r"dizel", r"petrol", r"benzin",
                    r"lpg", r"k[oö]m[uü]r", r"komur", r"coal", r"fuel\s*oil",
                    r"kazan", r"boiler", r"furnace", r"f[ıi]r[ıi]n",
                    r"jenerator", r"generator", r"forklift"
                ],
                "weight": 1.0
            },
            "scope2": {
                "primary": [r"scope\s*2", r"kapsam\s*2", r"dolayli\s*emisyon", r"dolayı"],
                "secondary": [
                    r"purchased\s*electricity", r"sat[ıi]n\s*al[ıi]nan\s*elektrik",
                    r"elektrik\s*t[uü]ketim", r"elektrik\s*tuketim", r"electricity\s*consumption",
                    r"grid", r"[sş]ebeke", r"sebeke", r"kwh", r"mwh",
                    r"steam", r"buhar", r"heating", r"[ıi]s[ıi]tma", r"isitma",
                    r"cooling", r"so[gğ]utma", r"sogutma", r"district\s*heat",
                    r"merkezi\s*[ıi]s[ıi]tma", r"enerji\s*tedarik"
                ],
                "weight": 0.8
            },
            "scope3": {
                "primary": [r"scope\s*3", r"kapsam\s*3", r"de[gğ]er\s*zinciri", r"deger\s*zinciri"],
                "secondary": [
                    r"value\s*chain", r"supply\s*chain", r"tedarik\s*zinciri",
                    r"business\s*travel", r"i[sş]\s*seyahat", r"is\s*seyahat",
                    r"upstream", r"downstream", r"commut",
                    r"waste", r"at[ıi]k", r"atik", r"employee\s*travel",
                    r"logistics", r"lojistik", r"nakliye", r"freight",
                    r"purchased\s*goods", r"sat[ıi]n\s*al[ıi]nan\s*[uü]r[uü]n",
                    r"leased\s*asset", r"kiral[ıi]k", r"franchise",
                    r"investment", r"yat[ıi]r[ıi]m", r"yatirim", r"financed"
                ],
                "weight": 0.6
            }
        }
        
        # Genişletilmiş ESG keywords - ASCII ve Unicode uyumlu
        self.esg_keywords = {
            "Environmental": {
                "high_weight": [
                    "carbon", "karbon", "emission", "emisyon", "co2",
                    "ghg", "sera gaz", "greenhouse", "climate", "iklim",
                    "net zero", "net sifir", "carbon neutral", "karbon notr"
                ],
                "medium_weight": [
                    "energy", "enerji", "renewable", "yenilenebilir",
                    "solar", "gunes", "wind", "ruzgar", "waste", "atik",
                    "water", "su", "pollution", "kirlilik", "recycl",
                    "geri donusum", "biodiversity", "biyocesitlilik",
                    "tuketim", "consumption"
                ],
                "low_weight": [
                    "sustainability", "surdurulebilir", "environment", "cevre",
                    "green", "yesil", "eco", "eko", "organic", "organik"
                ]
            },
            "Social": {
                "high_weight": [
                    "human rights", "insan haklar", "child labor", "cocuk isci",
                    "forced labor", "zorla calistirma", "discrimination", "ayrimcilik",
                    "harassment", "taciz", "safety incident", "is kazasi", "kaza"
                ],
                "medium_weight": [
                    "employee", "calisan", "personel", "diversity", "cesitlilik",
                    "health", "saglik", "safety", "guvenlik", "training", "egitim",
                    "inclusion", "kapsayici", "gender", "cinsiyet", "kadin", "women"
                ],
                "low_weight": [
                    "community", "toplum", "social", "sosyal", "stakeholder",
                    "paydas", "volunteer", "gonullu", "donation", "bagis"
                ]
            },
            "Governance": {
                "high_weight": [
                    "corruption", "yolsuzluk", "bribery", "rusvet",
                    "fraud", "dolandiricilik", "anti-competitive", "rekabet",
                    "money laundering", "kara para", "sanction", "yaptirim"
                ],
                "medium_weight": [
                    "board", "yonetim kurulu", "audit", "denetim",
                    "compliance", "uyum", "ethics", "etik", "transparency", "seffaflik",
                    "independent director", "bagimsiz uye", "risk management", "risk yonetimi"
                ],
                "low_weight": [
                    "governance", "yonetisim", "policy", "politika",
                    "procedure", "prosedur", "reporting", "raporlama", "disclosure", "aciklama"
                ]
            }
        }
        
        # Negatif göstergeler (risk artırıcı) - ASCII uyumlu
        self.risk_indicators = {
            "high_risk": [
                r"increase[ds]?\s+emissions?", r"emisyon\s*art", r"artti", r"artis",
                r"exceed", r"asim", r"violation", r"ihlal",
                r"penalty", r"ceza", r"fine\s+\$", r"para\s+cezas",
                r"lawsuit", r"dava", r"investigation", r"sorusturma",
                r"spill", r"sizinti", r"accident", r"kaza",
                r"fatality", r"olum", r"injury", r"yaralandi", r"yaralanma"
            ],
            "medium_risk": [
                r"challenge", r"zorluk", r"concern", r"endise",
                r"delay", r"gecikme", r"miss\s+target", r"hedef.*kacir", r"kacirdik",
                r"below\s+target", r"hedefin\s+alt"
            ],
            "positive": [
                r"reduc", r"azalt", r"decreas", r"dusur",
                r"improv", r"iyilestir", r"achiev", r"basar",
                r"exceed\s+target", r"hedefi\s+as", r"award", r"odul",
                r"certifi", r"sertifika", r"iso\s*14001", r"iso\s*45001"
            ]
        }
        
        # Benchmark değerleri (sektör ortalamaları - ton CO2e)
        self.benchmarks = {
            "small": 1000,      # Küçük şirket
            "medium": 10000,    # Orta şirket
            "large": 100000,    # Büyük şirket
            "enterprise": 1000000  # Kurumsal
        }

    def analyze_text(self, text: str) -> Dict:
        """
        Gelişmiş ESG metin analizi
        """
        text_lower = text.lower()
        word_count = len(text.split())
        
        # Temel analizler
        scope_detection = self._detect_scopes_enhanced(text_lower)
        emission_values = self._extract_emission_values_enhanced(text)
        esg_classification = self._classify_esg_enhanced(text_lower, word_count)
        sentiment = self._analyze_sentiment(text_lower)
        targets = self._extract_targets(text_lower)
        
        # Risk skoru hesapla (dinamik)
        risk_score = self._calculate_risk_score_enhanced(
            scope_detection, emission_values, esg_classification, 
            sentiment, targets, word_count
        )
        
        # Güven skoru
        confidence = self._calculate_confidence(text_lower, word_count, emission_values)
        
        results = {
            "scope_detection": scope_detection,
            "emission_values": emission_values,
            "esg_classification": esg_classification,
            "risk_score": risk_score,
            "sentiment": sentiment,
            "targets": targets,
            "confidence": confidence,
            "summary": "",
            "recommendations": []
        }
        
        # Öneriler oluştur
        results["recommendations"] = self._generate_recommendations_enhanced(results)
        
        # Özet oluştur
        results["summary"] = self._generate_summary_enhanced(results)
        
        return results

    def _detect_scopes_enhanced(self, text: str) -> Dict:
        """Gelişmiş scope tespiti - skor ve güvenle"""
        results = {}
        
        for scope, config in self.scope_keywords.items():
            primary_matches = 0
            secondary_matches = 0
            
            # Primary keywords (doğrudan bahsetme)
            for pattern in config["primary"]:
                matches = len(re.findall(pattern, text))
                primary_matches += matches
            
            # Secondary keywords (dolaylı bahsetme)
            for pattern in config["secondary"]:
                matches = len(re.findall(pattern, text))
                secondary_matches += matches
            
            # Skor hesapla
            score = (primary_matches * 3 + secondary_matches * 1) * config["weight"]
            detected = primary_matches > 0 or secondary_matches >= 2
            confidence = "high" if primary_matches > 0 else ("medium" if secondary_matches >= 2 else "low")
            
            results[scope] = {
                "detected": detected,
                "score": round(score, 2),
                "primary_matches": primary_matches,
                "secondary_matches": secondary_matches,
                "confidence": confidence
            }
        
        return results

    def _extract_emission_values_enhanced(self, text: str) -> List[Dict]:
        """Gelişmiş emisyon değeri çıkarma"""
        patterns = [
            # Scope bazlı değerler
            (r"scope\s*1[:\s]+?([\d.,]+)\s*(ton|mt|kg)", "Scope 1"),
            (r"scope\s*2[:\s]+?([\d.,]+)\s*(ton|mt|kg)", "Scope 2"),
            (r"scope\s*3[:\s]+?([\d.,]+)\s*(ton|mt|kg)", "Scope 3"),
            (r"kapsam\s*1[:\s]+?([\d.,]+)\s*(ton|mt|kg)", "Scope 1"),
            (r"kapsam\s*2[:\s]+?([\d.,]+)\s*(ton|mt|kg)", "Scope 2"),
            (r"kapsam\s*3[:\s]+?([\d.,]+)\s*(ton|mt|kg)", "Scope 3"),
            # Toplam değerler
            (r"toplam[:\s]+?([\d.,]+)\s*(ton|mt|kg)\s*(co2|karbon)", "Total"),
            (r"total[:\s]+?([\d.,]+)\s*(ton|mt|kg)\s*(co2|carbon)", "Total"),
            # Genel CO2 değerleri
            (r"([\d.,]+)\s*(ton|mt)\s*(co2e?|karbon|carbon)", "General"),
            (r"([\d.,]+)\s*(milyon|million)\s*(ton|mt)\s*(co2|karbon)", "General (Million)"),
            # Yoğunluk değerleri
            (r"([\d.,]+)\s*(kg|ton)\s*co2[e]?\s*/\s*(kwh|mwh|unit)", "Intensity"),
        ]
        
        emissions = []
        text_lower = text.lower()
        
        for pattern, category in patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                try:
                    groups = match.groups()
                    value_str = groups[0].replace(',', '.').replace(' ', '')
                    
                    # Binlik ayracı düzelt
                    if value_str.count('.') > 1:
                        value_str = value_str.replace('.', '', value_str.count('.') - 1)
                    
                    value = float(value_str)
                    
                    # Milyon ise çarp
                    if "milyon" in match.group(0) or "million" in match.group(0):
                        value *= 1000000
                    
                    unit = "ton CO2e"
                    if "kg" in match.group(0):
                        unit = "kg CO2e"
                        value = value / 1000  # kg'ı tona çevir
                    
                    emissions.append({
                        "value": round(value, 2),
                        "unit": unit,
                        "category": category,
                        "context": match.group(0)[:80],
                        "raw_value": groups[0]
                    })
                except:
                    continue
        
        # Duplicate temizle ve sırala
        seen = set()
        unique = []
        for em in sorted(emissions, key=lambda x: x['value'], reverse=True):
            key = (em['value'], em['category'])
            if key not in seen:
                seen.add(key)
                unique.append(em)
        
        return unique[:15]

    def _classify_esg_enhanced(self, text: str, word_count: int) -> Dict:
        """Gelişmiş ESG sınıflandırma - ağırlıklı skorlama"""
        scores = {"Environmental": 0, "Social": 0, "Governance": 0}
        details = {"Environmental": [], "Social": [], "Governance": []}
        
        for category, weights in self.esg_keywords.items():
            for keyword in weights["high_weight"]:
                count = text.count(keyword.lower())
                if count > 0:
                    scores[category] += count * 3
                    details[category].append(f"{keyword}({count}x3)")
            
            for keyword in weights["medium_weight"]:
                count = text.count(keyword.lower())
                if count > 0:
                    scores[category] += count * 2
                    details[category].append(f"{keyword}({count}x2)")
            
            for keyword in weights["low_weight"]:
                count = text.count(keyword.lower())
                if count > 0:
                    scores[category] += count * 1
                    details[category].append(f"{keyword}({count}x1)")
        
        # Normalize ve yüzdeye çevir
        total = sum(scores.values()) or 1
        
        # Kelime yoğunluğuna göre düzelt
        density_factor = min(word_count / 100, 10)  # Max 10x
        
        result = {}
        for cat in scores:
            raw_pct = scores[cat] / total
            # Yoğunluk ve denge faktörü
            adjusted = raw_pct * 100
            result[cat] = {
                "percentage": round(adjusted, 1),
                "raw_score": scores[cat],
                "top_keywords": details[cat][:5]
            }
        
        return result

    def _analyze_sentiment(self, text: str) -> Dict:
        """Risk göstergelerine göre sentiment analizi"""
        high_risk_count = 0
        medium_risk_count = 0
        positive_count = 0
        
        for pattern in self.risk_indicators["high_risk"]:
            high_risk_count += len(re.findall(pattern, text))
        
        for pattern in self.risk_indicators["medium_risk"]:
            medium_risk_count += len(re.findall(pattern, text))
        
        for pattern in self.risk_indicators["positive"]:
            positive_count += len(re.findall(pattern, text))
        
        # Net sentiment skoru (-100 to +100)
        negative_score = high_risk_count * 10 + medium_risk_count * 5
        positive_score = positive_count * 5
        
        net_score = positive_score - negative_score
        net_score = max(-100, min(100, net_score))
        
        if net_score > 20:
            sentiment = "Pozitif"
        elif net_score < -20:
            sentiment = "Negatif"
        else:
            sentiment = "Notr"
        
        return {
            "score": net_score,
            "label": sentiment,
            "positive_indicators": positive_count,
            "negative_indicators": high_risk_count + medium_risk_count,
            "high_risk_count": high_risk_count,
            "medium_risk_count": medium_risk_count
        }

    def _extract_targets(self, text: str) -> Dict:
        """Hedef ve taahhütleri çıkar"""
        targets = {
            "net_zero": None,
            "reduction_targets": [],
            "certifications": []
        }
        
        # Net zero hedefi - proximity-aware patterns (max 30 char arada)
        net_zero_patterns = [
            # Year after keyword (more reliable)
            r"net[\s-]?zero\s+by\s+(\d{4})",
            r"net[\s-]?zero\s+(\d{4})",
            r"net[\s-]?zero.{0,20}(\d{4})",
            r"net[\s-]?sifir\s+(\d{4})",
            r"net[\s-]?sifir.{0,20}(\d{4})",
            r"carbon[\s-]?neutral\s+by\s+(\d{4})",
            r"carbon[\s-]?neutral.{0,20}(\d{4})",
            r"karbon[\s-]?notr.{0,20}(\d{4})",
            # Year before keyword (limited distance)
            r"(\d{4}).{0,20}net[\s-]?zero",
            r"(\d{4}).{0,20}net[\s-]?sifir",
            r"(\d{4}).{0,20}karbon[\s-]?notr",
            r"(\d{4}).{0,20}carbon[\s-]?neutral",
            # Turkish patterns
            r"(\d{4})\s+yilinda.{0,20}hedefliyoruz",
            r"hedefliyoruz.{0,20}(\d{4})",
            r"hedef.{0,15}(\d{4})",
            r"(\d{4}).{0,15}hedef",
        ]
        
        for pattern in net_zero_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    year = int(match) if isinstance(match, str) else int(match)
                    if 2025 <= year <= 2100:  # Gelecek yil araliği
                        targets["net_zero"] = year
                        break
                except:
                    continue
            if targets["net_zero"]:
                break
        
        # Azaltım hedefleri
        reduction_patterns = [
            r"(\d+)\s*%\s*reduc", r"(\d+)\s*%\s*azalt",
            r"reduce\s+by\s+(\d+)\s*%", r"(\d+)\s*%\s*decrease",
            r"yuzde\s*(\d+)", r"%\s*(\d+)\s*azal"
        ]
        
        for pattern in reduction_patterns:
            matches = re.findall(pattern, text)
            for m in matches:
                try:
                    val = int(m)
                    if 0 < val <= 100:
                        targets["reduction_targets"].append(val)
                except:
                    pass
        
        # Sertifikasyonlar
        cert_patterns = [
            (r"iso\s*14001", "ISO 14001"),
            (r"iso\s*45001", "ISO 45001"),
            (r"iso\s*50001", "ISO 50001"),
            (r"leed", "LEED"),
            (r"breeam", "BREEAM"),
            (r"cdp\s*[a-z]", "CDP"),
            (r"sbti", "SBTi")
        ]
        
        for pattern, name in cert_patterns:
            if re.search(pattern, text):
                targets["certifications"].append(name)
        
        return targets

    def _calculate_risk_score_enhanced(self, scope_det: Dict, emissions: List, 
                                        esg_class: Dict, sentiment: Dict, 
                                        targets: Dict, word_count: int) -> Dict:
        """Dinamik ve çok boyutlu risk skorlama"""
        
        # Component skorları
        scope_risk = 0
        emission_risk = 0
        esg_balance_risk = 0
        sentiment_risk = 0
        transparency_risk = 0
        
        # 1. Scope Kapsam Riski (0-25)
        for scope, data in scope_det.items():
            if not data["detected"]:
                if scope == "scope1":
                    scope_risk += 10  # Scope 1 kritik
                elif scope == "scope2":
                    scope_risk += 8
                elif scope == "scope3":
                    scope_risk += 7   # Scope 3 zorlu ama önemli
        
        # 2. Emisyon Veri Riski (0-25)
        if len(emissions) == 0:
            emission_risk = 25
        elif len(emissions) == 1:
            emission_risk = 15
        elif len(emissions) < 3:
            emission_risk = 8
        else:
            # Benchmark karşılaştırma
            total_emission = sum(e["value"] for e in emissions if e["category"] in ["Total", "General"])
            if total_emission > self.benchmarks["large"]:
                emission_risk = 10  # Yüksek emisyon
            elif total_emission > self.benchmarks["medium"]:
                emission_risk = 5
        
        # 3. ESG Denge Riski (0-20)
        env_pct = esg_class.get("Environmental", {}).get("percentage", 0)
        soc_pct = esg_class.get("Social", {}).get("percentage", 0)
        gov_pct = esg_class.get("Governance", {}).get("percentage", 0)
        
        # Çok dengesiz dağılım = risk
        max_pct = max(env_pct, soc_pct, gov_pct)
        min_pct = min(env_pct, soc_pct, gov_pct)
        
        if min_pct < 10:
            esg_balance_risk += 10  # Bir kategori çok zayıf
        if max_pct > 80:
            esg_balance_risk += 5   # Tek kategori dominant
        if soc_pct < 15:
            esg_balance_risk += 5   # Sosyal boyut zayıf
        
        # 4. Sentiment Riski (0-15)
        if sentiment["score"] < -30:
            sentiment_risk = 15
        elif sentiment["score"] < 0:
            sentiment_risk = 10
        elif sentiment["score"] < 20:
            sentiment_risk = 5
        
        if sentiment["high_risk_count"] > 2:
            sentiment_risk += 5
        
        # 5. Şeffaflık Riski (0-15)
        if word_count < 100:
            transparency_risk = 15  # Çok kısa rapor
        elif word_count < 300:
            transparency_risk = 10
        elif word_count < 500:
            transparency_risk = 5
        
        # Net zero hedefi varsa risk azalt
        if targets.get("net_zero"):
            if targets["net_zero"] <= 2030:
                transparency_risk -= 5
            elif targets["net_zero"] <= 2050:
                transparency_risk -= 2
        
        # Sertifikasyon varsa risk azalt
        transparency_risk -= len(targets.get("certifications", [])) * 2
        transparency_risk = max(0, transparency_risk)
        
        # Toplam risk
        total_risk = scope_risk + emission_risk + esg_balance_risk + sentiment_risk + transparency_risk
        total_risk = max(0, min(100, total_risk))
        
        # Risk seviyesi - ASCII
        if total_risk < 20:
            level = "Dusuk"
            color = "green"
        elif total_risk < 40:
            level = "Orta-Dusuk"
            color = "lightgreen"
        elif total_risk < 60:
            level = "Orta"
            color = "yellow"
        elif total_risk < 80:
            level = "Orta-Yuksek"
            color = "orange"
        else:
            level = "Yuksek"
            color = "red"
        
        return {
            "total": round(total_risk),
            "level": level,
            "color": color,
            "components": {
                "scope_coverage": round(scope_risk),
                "emission_data": round(emission_risk),
                "esg_balance": round(esg_balance_risk),
                "sentiment": round(sentiment_risk),
                "transparency": round(transparency_risk)
            }
        }

    def _calculate_confidence(self, text: str, word_count: int, emissions: List) -> Dict:
        """Analiz güven skoru"""
        score = 50  # Base
        
        # Kelime sayısı
        if word_count > 500:
            score += 20
        elif word_count > 200:
            score += 10
        elif word_count < 50:
            score -= 20
        
        # Emisyon verisi
        if len(emissions) > 5:
            score += 20
        elif len(emissions) > 2:
            score += 10
        elif len(emissions) == 0:
            score -= 15
        
        # Yapısal içerik
        if re.search(r"scope\s*[123]", text):
            score += 10
        
        score = max(0, min(100, score))
        
        if score > 70:
            level = "Yuksek"
        elif score > 40:
            level = "Orta"
        else:
            level = "Dusuk"
        
        return {"score": score, "level": level}

    def _generate_recommendations_enhanced(self, results: Dict) -> List[Dict]:
        """Detayli ve onceliklendirilmis oneriler"""
        recommendations = []
        
        scope_det = results["scope_detection"]
        esg_class = results["esg_classification"]
        risk = results["risk_score"]
        sentiment = results["sentiment"]
        targets = results["targets"]
        
        # Scope onerileri
        if not scope_det["scope1"]["detected"]:
            recommendations.append({
                "priority": "high",
                "category": "Kapsam",
                "title": "Scope 1 Raporlamasi Eksik",
                "description": "Dogrudan emisyonlarinizi (dogalgaz, arac filosu, yakit) raporlayin.",
                "impact": "Yuksek"
            })
        
        if not scope_det["scope2"]["detected"]:
            recommendations.append({
                "priority": "high",
                "category": "Kapsam",
                "title": "Scope 2 Raporlamasi Eksik",
                "description": "Satin alinan elektrik ve enerji kaynakli emisyonlari ekleyin.",
                "impact": "Yuksek"
            })
        
        if not scope_det["scope3"]["detected"]:
            recommendations.append({
                "priority": "medium",
                "category": "Kapsam",
                "title": "Scope 3 Raporlamasi Gelistirilebilir",
                "description": "Tedarik zinciri ve is seyahati emisyonlarini dahil edin.",
                "impact": "Orta"
            })
        
        # ESG denge onerileri
        env_pct = esg_class.get("Environmental", {}).get("percentage", 0)
        soc_pct = esg_class.get("Social", {}).get("percentage", 0)
        gov_pct = esg_class.get("Governance", {}).get("percentage", 0)
        
        if soc_pct < 15:
            recommendations.append({
                "priority": "medium",
                "category": "Sosyal",
                "title": "Sosyal Boyut Guclendirilmeli",
                "description": "Calisan sagligi, cesitlilik, toplum katkisi konularina yer verin.",
                "impact": "Orta"
            })
        
        if gov_pct < 15:
            recommendations.append({
                "priority": "medium",
                "category": "Yonetisim",
                "title": "Yonetisim Bilgileri Artirilmali",
                "description": "Etik, seffaflik, denetim ve risk yonetimi konularini ekleyin.",
                "impact": "Orta"
            })
        
        # Hedef onerileri
        if not targets.get("net_zero"):
            recommendations.append({
                "priority": "high",
                "category": "Strateji",
                "title": "Net Zero Hedefi Belirlenmeli",
                "description": "2050 veya oncesi icin net sifir karbon hedefi koyun.",
                "impact": "Yuksek"
            })
        
        if len(targets.get("reduction_targets", [])) == 0:
            recommendations.append({
                "priority": "medium",
                "category": "Hedefler",
                "title": "Sayisal Azaltim Hedefleri Ekleyin",
                "description": "Yillik veya donemsel emisyon azaltim yuzdeleri belirtin.",
                "impact": "Orta"
            })
        
        # Sentiment onerileri
        if sentiment["high_risk_count"] > 0:
            recommendations.append({
                "priority": "high",
                "category": "Risk",
                "title": "Yuksek Risk Gostergeleri Mevcut",
                "description": f"{sentiment['high_risk_count']} adet kritik risk ifadesi tespit edildi. Bunlari ele alin.",
                "impact": "Yuksek"
            })
        
        # Eger oneri yoksa pozitif mesaj
        if not recommendations:
            recommendations.append({
                "priority": "low",
                "category": "Genel",
                "title": "Kapsamli Rapor",
                "description": "Raporunuz tum temel ESG bilesenlerini iceriyor. GRI/TCFD uyumunu kontrol edin.",
                "impact": "Dusuk"
            })
        
        # Oncelike gore sirala
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return recommendations

    def _generate_summary_enhanced(self, results: Dict) -> str:
        """Gelişmiş analiz özeti"""
        risk = results["risk_score"]
        scope = results["scope_detection"]
        emissions = results["emission_values"]
        esg = results["esg_classification"]
        sentiment = results["sentiment"]
        confidence = results["confidence"]
        
        summary = "## 📊 ESG Analiz Özeti\n\n"
        
        # Risk özeti
        risk_emoji = "🟢" if risk["total"] < 30 else ("🟡" if risk["total"] < 60 else "🔴")
        summary += f"### Risk Değerlendirmesi\n"
        summary += f"{risk_emoji} **Risk Skoru:** {risk['total']}/100 ({risk['level']})\n\n"
        
        # Scope özeti
        summary += "### Kapsam Tespiti\n"
        for s, data in scope.items():
            emoji = "✅" if data["detected"] else "❌"
            conf = f"({data['confidence']})" if data["detected"] else ""
            summary += f"- {s.replace('scope', 'Scope ')}: {emoji} {conf}\n"
        summary += "\n"
        
        # Emisyon özeti
        if emissions:
            total = sum(e["value"] for e in emissions if e["category"] in ["Total", "General", "Scope 1", "Scope 2", "Scope 3"])
            summary += f"### Emisyon Verileri\n"
            summary += f"**Toplam Tespit:** {total:,.0f} ton CO2e\n\n"
        
        # ESG dağılımı
        summary += "### ESG Dağılımı\n"
        for cat, data in esg.items():
            bar = "█" * int(data["percentage"] / 10) + "░" * (10 - int(data["percentage"] / 10))
            summary += f"- {cat}: {bar} {data['percentage']}%\n"
        summary += "\n"
        
        # Sentiment
        sent_emoji = "😊" if sentiment["score"] > 20 else ("😐" if sentiment["score"] > -20 else "😟")
        summary += f"### Genel Ton\n"
        summary += f"{sent_emoji} {sentiment['label']} (Skor: {sentiment['score']})\n\n"
        
        # Güven
        summary += f"### Analiz Güveni\n"
        summary += f"📊 {confidence['level']} ({confidence['score']}%)\n"
        
        return summary

    def analyze_pdf_bytes(self, pdf_bytes: bytes) -> Dict:
        """PDF bytes'tan analiz"""
        try:
            import PyPDF2
            import io
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if not text.strip():
                return {
                    "error": "PDF'den metin çıkarılamadı",
                    "scope_detection": {s: {"detected": False, "score": 0, "confidence": "none"} for s in ["scope1", "scope2", "scope3"]},
                    "emission_values": [],
                    "esg_classification": {c: {"percentage": 0, "raw_score": 0, "top_keywords": []} for c in ["Environmental", "Social", "Governance"]},
                    "risk_score": {"total": 100, "level": "Yüksek", "color": "red", "components": {}},
                    "sentiment": {"score": 0, "label": "Bilinmiyor"},
                    "targets": {},
                    "confidence": {"score": 0, "level": "Düşük"},
                    "summary": "PDF analiz edilemedi.",
                    "recommendations": [{"priority": "high", "category": "Teknik", "title": "OCR Gerekli", "description": "Taranmış PDF için OCR kullanın."}]
                }
            
            return self.analyze_text(text)
            
        except Exception as e:
            return {"error": f"PDF okuma hatası: {str(e)}"}
