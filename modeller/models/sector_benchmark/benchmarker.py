"""
Sector Benchmarking Model
==========================

Şirketleri sektör ortalamasıyla karşılaştırma ve konumlandırma.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Tuple
from pathlib import Path
import json

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config import DATASETS, get_dataset_path


class SectorBenchmarker:
    """
    Sektör bazlı karşılaştırma ve benchmark sistemi
    
    NAICS kodları kullanarak şirketleri sektör ortalamasıyla karşılaştırır.
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        
        # Veri setleri
        self.sector_factors = None  # NAICS emission factors
        self.corporate_data = None  # Corporate environmental data
        self.ember_data = None      # Country electricity data
        
        # Benchmark verisi
        self.sector_benchmarks = {}
        self.country_benchmarks = {}
        
        self.is_loaded = False
    
    def _log(self, message: str):
        if self.verbose:
            print(f"[Benchmarker] {message}")
    
    def load_data(self) -> "SectorBenchmarker":
        """
        Gerekli veri setlerini yükle
        """
        self._log("Veri setleri yükleniyor...")
        
        # 1. Supply Chain GHG Emission Factors
        try:
            factor_path = get_dataset_path("supply_chain_ghg", "co2e")
            self.sector_factors = pd.read_csv(factor_path)
            self._log(f"  -> Sector factors: {len(self.sector_factors)} satır")
        except Exception as e:
            self._log(f"  -> Sector factors yüklenemedi: {e}")
            self._create_sample_sector_factors()
        
        # 2. Corporate Environmental Impact (opsiyonel)
        try:
            corp_path = get_dataset_path("corporate_environmental", "sample")
            self.corporate_data = pd.read_csv(corp_path)
            self._log(f"  -> Corporate data: {len(self.corporate_data)} satır")
        except Exception as e:
            self._log(f"  -> Corporate data yüklenemedi: {e}")
        
        # 3. Ember data (opsiyonel)
        try:
            ember_path = get_dataset_path("ember", "yearly")
            self.ember_data = pd.read_csv(ember_path)
            self._log(f"  -> Ember data: {len(self.ember_data)} satır")
        except Exception as e:
            self._log(f"  -> Ember data yüklenemedi: {e}")
        
        # Benchmark hesapla
        self._calculate_benchmarks()
        
        self.is_loaded = True
        return self
    
    def _create_sample_sector_factors(self):
        """Örnek sektör faktörleri oluştur (test için)"""
        self._log("  -> Örnek sektör faktörleri oluşturuluyor...")
        
        self.sector_factors = pd.DataFrame([
            {"naics_code": "111", "sector": "Agriculture", "emission_factor": 0.45, "unit": "kg CO2e/USD"},
            {"naics_code": "211", "sector": "Oil and Gas", "emission_factor": 1.85, "unit": "kg CO2e/USD"},
            {"naics_code": "221", "sector": "Utilities", "emission_factor": 1.20, "unit": "kg CO2e/USD"},
            {"naics_code": "236", "sector": "Construction", "emission_factor": 0.55, "unit": "kg CO2e/USD"},
            {"naics_code": "311", "sector": "Food Manufacturing", "emission_factor": 0.65, "unit": "kg CO2e/USD"},
            {"naics_code": "325", "sector": "Chemical Manufacturing", "emission_factor": 1.45, "unit": "kg CO2e/USD"},
            {"naics_code": "331", "sector": "Metal Manufacturing", "emission_factor": 1.75, "unit": "kg CO2e/USD"},
            {"naics_code": "336", "sector": "Transportation Equipment", "emission_factor": 0.85, "unit": "kg CO2e/USD"},
            {"naics_code": "423", "sector": "Wholesale Trade", "emission_factor": 0.25, "unit": "kg CO2e/USD"},
            {"naics_code": "441", "sector": "Retail Trade", "emission_factor": 0.20, "unit": "kg CO2e/USD"},
            {"naics_code": "481", "sector": "Air Transportation", "emission_factor": 2.50, "unit": "kg CO2e/USD"},
            {"naics_code": "484", "sector": "Truck Transportation", "emission_factor": 1.10, "unit": "kg CO2e/USD"},
            {"naics_code": "511", "sector": "Information Technology", "emission_factor": 0.15, "unit": "kg CO2e/USD"},
            {"naics_code": "522", "sector": "Financial Services", "emission_factor": 0.10, "unit": "kg CO2e/USD"},
            {"naics_code": "541", "sector": "Professional Services", "emission_factor": 0.12, "unit": "kg CO2e/USD"},
            {"naics_code": "611", "sector": "Education", "emission_factor": 0.18, "unit": "kg CO2e/USD"},
            {"naics_code": "621", "sector": "Healthcare", "emission_factor": 0.22, "unit": "kg CO2e/USD"},
            {"naics_code": "721", "sector": "Hospitality", "emission_factor": 0.35, "unit": "kg CO2e/USD"},
        ])
    
    def _calculate_benchmarks(self):
        """Sektör benchmark değerlerini hesapla"""
        if self.sector_factors is None:
            return
        
        # Kolon isimlerini standartlaştır
        df = self.sector_factors.copy()
        
        # Olası kolon isimleri
        naics_cols = ["2017 NAICS Code", "naics_code", "NAICS_Code", "NAICS"]
        sector_cols = ["2017 NAICS Title", "sector", "Sector", "Industry"]
        factor_cols = ["Supply Chain Emission Factors with Margins", 
                      "emission_factor", "Emission_Factor", "Factor"]
        
        naics_col = next((c for c in naics_cols if c in df.columns), None)
        sector_col = next((c for c in sector_cols if c in df.columns), None)
        factor_col = next((c for c in factor_cols if c in df.columns), None)
        
        if naics_col and sector_col and factor_col:
            for _, row in df.iterrows():
                naics = str(row[naics_col])[:3]  # İlk 3 hane
                sector = row[sector_col]
                factor = row[factor_col]
                
                if pd.notna(factor):
                    try:
                        self.sector_benchmarks[naics] = {
                            "sector": sector,
                            "emission_factor": float(factor),
                            "unit": "kg CO2e/USD"
                        }
                    except:
                        pass
        
        self._log(f"Benchmark hesaplandı: {len(self.sector_benchmarks)} sektör")
    
    def get_sector_by_naics(self, naics_code: str) -> Optional[Dict]:
        """
        NAICS koduna göre sektör bilgisi al
        
        Args:
            naics_code: NAICS kodu (2-6 hane)
        
        Returns:
            Sektör bilgisi
        """
        # Tam eşleşme
        if naics_code in self.sector_benchmarks:
            return self.sector_benchmarks[naics_code]
        
        # Prefix eşleşme (6 -> 3 hane)
        for length in [5, 4, 3, 2]:
            prefix = naics_code[:length]
            if prefix in self.sector_benchmarks:
                return self.sector_benchmarks[prefix]
        
        return None
    
    def benchmark_company(
        self,
        company_data: Dict
    ) -> Dict:
        """
        Şirketi sektör ortalamasıyla karşılaştır
        
        Args:
            company_data: {
                "name": "Company Name",
                "naics_code": "336111",  # veya "sector": "Automotive"
                "total_emissions": 50000,  # ton CO2e
                "revenue": 1000000000,  # USD
                "employees": 5000
            }
        
        Returns:
            Benchmark sonuçları
        """
        if not self.is_loaded:
            self.load_data()
        
        result = {
            "company": company_data.get("name", "Unknown"),
            "success": False
        }
        
        # Sektör bilgisi al
        sector_info = None
        if "naics_code" in company_data:
            sector_info = self.get_sector_by_naics(str(company_data["naics_code"]))
        
        if sector_info is None:
            # Manuel sektör eşleştirme
            sector_name = company_data.get("sector", "Unknown")
            for naics, info in self.sector_benchmarks.items():
                if sector_name.lower() in info["sector"].lower():
                    sector_info = info
                    break
        
        if sector_info is None:
            result["error"] = "Sektör bulunamadı"
            return result
        
        result["sector"] = sector_info["sector"]
        result["sector_emission_factor"] = sector_info["emission_factor"]
        
        # Emisyon yoğunluğu hesapla
        total_emissions = company_data.get("total_emissions", 0)
        revenue = company_data.get("revenue", 0)
        employees = company_data.get("employees", 0)
        
        if revenue > 0:
            # kg CO2e per USD revenue
            company_intensity = (total_emissions * 1000) / revenue  # ton -> kg
            sector_intensity = sector_info["emission_factor"]
            
            # Karşılaştırma
            ratio = company_intensity / sector_intensity if sector_intensity > 0 else 0
            
            # Percentile hesapla (basit yaklaşım)
            if ratio < 0.5:
                percentile = 90  # Top 10%
                rating = "A"
            elif ratio < 0.75:
                percentile = 75
                rating = "B"
            elif ratio < 1.0:
                percentile = 50
                rating = "C"
            elif ratio < 1.5:
                percentile = 25
                rating = "D"
            else:
                percentile = 10
                rating = "F"
            
            result["metrics"] = {
                "company_intensity": round(company_intensity, 4),
                "sector_intensity": round(sector_intensity, 4),
                "ratio": round(ratio, 2),
                "percentile": percentile,
                "rating": rating
            }
            
            result["interpretation"] = self._generate_interpretation(rating, ratio)
            result["success"] = True
        
        if employees > 0:
            result["metrics"]["emissions_per_employee"] = round(total_emissions / employees, 2)
        
        return result
    
    def _generate_interpretation(self, rating: str, ratio: float) -> str:
        """Sonuç yorumu oluştur"""
        interpretations = {
            "A": f"Şirket sektör ortalamasının %{int((1-ratio)*100)} altında. Mükemmel performans!",
            "B": f"Şirket sektör ortalamasının altında. İyi performans.",
            "C": f"Şirket sektör ortalamasına yakın. Ortalama performans.",
            "D": f"Şirket sektör ortalamasının %{int((ratio-1)*100)} üstünde. İyileştirme gerekli.",
            "F": f"Şirket sektör ortalamasının %{int((ratio-1)*100)} üstünde. Acil aksiyon gerekli."
        }
        return interpretations.get(rating, "")
    
    def compare_companies(
        self,
        companies: List[Dict]
    ) -> pd.DataFrame:
        """
        Birden fazla şirketi karşılaştır
        
        Args:
            companies: Şirket listesi
        
        Returns:
            Karşılaştırma DataFrame
        """
        results = []
        for company in companies:
            benchmark = self.benchmark_company(company)
            if benchmark.get("success"):
                results.append({
                    "company": benchmark["company"],
                    "sector": benchmark["sector"],
                    "intensity": benchmark["metrics"]["company_intensity"],
                    "sector_avg": benchmark["metrics"]["sector_intensity"],
                    "ratio": benchmark["metrics"]["ratio"],
                    "percentile": benchmark["metrics"]["percentile"],
                    "rating": benchmark["metrics"]["rating"]
                })
        
        return pd.DataFrame(results).sort_values("percentile", ascending=False)
    
    def get_sector_list(self) -> List[Dict]:
        """Mevcut sektör listesi"""
        return [
            {"naics": naics, "sector": info["sector"], "factor": info["emission_factor"]}
            for naics, info in self.sector_benchmarks.items()
        ]
    
    def get_recommendations(
        self,
        benchmark_result: Dict
    ) -> List[str]:
        """
        Benchmark sonucuna göre öneriler
        """
        if not benchmark_result.get("success"):
            return []
        
        rating = benchmark_result["metrics"]["rating"]
        ratio = benchmark_result["metrics"]["ratio"]
        
        recommendations = []
        
        if rating in ["D", "F"]:
            recommendations.append("🔴 Scope 1 emisyonlarını azaltmak için yakıt verimliliğini artırın")
            recommendations.append("🔴 Yenilenebilir enerji kaynaklarına geçiş yapın (Scope 2)")
            recommendations.append("🔴 Tedarik zinciri emisyonlarını değerlendirin (Scope 3)")
        
        elif rating == "C":
            recommendations.append("🟡 Enerji verimliliği projelerine yatırım yapın")
            recommendations.append("🟡 Karbon ayak izi takip sistemi kurun")
            recommendations.append("🟡 Çalışan farkındalık programları başlatın")
        
        elif rating in ["A", "B"]:
            recommendations.append("🟢 Mevcut iyi uygulamaları sürdürün")
            recommendations.append("🟢 Net zero hedefi belirlemeyi düşünün")
            recommendations.append("🟢 Tedarikçilerinizi de dönüşüme dahil edin")
        
        return recommendations


# Test
if __name__ == "__main__":
    print("=== Sector Benchmarker Test ===\n")
    
    # Benchmarker oluştur
    benchmarker = SectorBenchmarker(verbose=True)
    benchmarker.load_data()
    
    # Test şirketleri
    companies = [
        {
            "name": "EcoTech Manufacturing",
            "naics_code": "336",
            "sector": "Transportation Equipment",
            "total_emissions": 25000,  # ton CO2e
            "revenue": 500000000,  # $500M
            "employees": 2000
        },
        {
            "name": "GreenBank Finance",
            "naics_code": "522",
            "sector": "Financial Services",
            "total_emissions": 1000,
            "revenue": 200000000,
            "employees": 500
        },
        {
            "name": "HighCarbon Steel",
            "naics_code": "331",
            "sector": "Metal Manufacturing",
            "total_emissions": 150000,
            "revenue": 800000000,
            "employees": 3000
        }
    ]
    
    # Benchmark
    print("\n=== Benchmark Sonuçları ===\n")
    for company in companies:
        result = benchmarker.benchmark_company(company)
        if result["success"]:
            print(f"{result['company']}:")
            print(f"  Sektör: {result['sector']}")
            print(f"  Rating: {result['metrics']['rating']}")
            print(f"  Percentile: {result['metrics']['percentile']}")
            print(f"  Yorum: {result['interpretation']}")
            print()
    
    # Karşılaştırma tablosu
    print("\n=== Karşılaştırma Tablosu ===")
    comparison = benchmarker.compare_companies(companies)
    print(comparison.to_string())
    
    print("\n=== Test Başarılı ===")

