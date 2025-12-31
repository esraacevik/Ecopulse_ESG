"""
Target Recommendation Model
============================

Net zero hedefi ve azaltım planı önerisi.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Tuple
from pathlib import Path
from datetime import datetime
import json


class TargetRecommender:
    """
    Net zero hedefi ve azaltım yol haritası önerici
    
    SBTi (Science Based Targets initiative) uyumlu hedefler önerir.
    """
    
    # SBTi uyumlu yıllık azaltım oranları
    SBTI_RATES = {
        "1.5C": 0.042,  # Yıllık %4.2 azaltım
        "well_below_2C": 0.025,  # Yıllık %2.5 azaltım
        "2C": 0.015  # Yıllık %1.5 azaltım
    }
    
    # Azaltım aksiyonları ve potansiyelleri
    REDUCTION_ACTIONS = {
        "scope1": {
            "fleet_electrification": {
                "name": "Filo Elektrifikasyonu",
                "potential_reduction": 0.70,  # %70 azaltım
                "cost_level": "high",
                "timeline_years": 5,
                "description": "Arac filosunun elektrikli araclara gecisi"
            },
            "fuel_switching": {
                "name": "Yakit Degisimi",
                "potential_reduction": 0.40,
                "cost_level": "medium",
                "timeline_years": 2,
                "description": "Dogalgazdan biyogaz/hidrojene gecis"
            },
            "efficiency_improvements": {
                "name": "Verimlilik Iyilestirme",
                "potential_reduction": 0.25,
                "cost_level": "low",
                "timeline_years": 1,
                "description": "Ekipman ve surec optimizasyonu"
            }
        },
        "scope2": {
            "renewable_ppa": {
                "name": "Yenilenebilir Enerji PPA",
                "potential_reduction": 1.0,  # %100 azaltım
                "cost_level": "low",
                "timeline_years": 1,
                "description": "Yesil enerji satin alma sozlesmesi"
            },
            "onsite_solar": {
                "name": "Tesis Ustu Gunes Paneli",
                "potential_reduction": 0.40,
                "cost_level": "medium",
                "timeline_years": 2,
                "description": "Kendi yenilenebilir enerji uretimi"
            },
            "energy_efficiency": {
                "name": "Enerji Verimliligi",
                "potential_reduction": 0.30,
                "cost_level": "medium",
                "timeline_years": 3,
                "description": "LED, HVAC optimizasyonu, yalitim"
            }
        },
        "scope3": {
            "supplier_engagement": {
                "name": "Tedarikci Katilimi",
                "potential_reduction": 0.25,
                "cost_level": "low",
                "timeline_years": 5,
                "description": "Tedarikcilerin karbon azaltimi icin angaje edilmesi"
            },
            "travel_reduction": {
                "name": "Is Seyahati Azaltimi",
                "potential_reduction": 0.60,
                "cost_level": "low",
                "timeline_years": 1,
                "description": "Uzaktan calisma ve video konferans"
            },
            "logistics_optimization": {
                "name": "Lojistik Optimizasyonu",
                "potential_reduction": 0.20,
                "cost_level": "medium",
                "timeline_years": 3,
                "description": "Tedarik zinciri optimizasyonu"
            },
            "product_lifecycle": {
                "name": "Urun Yasam Dongusu",
                "potential_reduction": 0.15,
                "cost_level": "high",
                "timeline_years": 5,
                "description": "Surdurulebilir urun tasarimi"
            }
        }
    }
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
    
    def _log(self, message: str):
        if self.verbose:
            print(f"[Recommender] {message}")
    
    def analyze_current_state(
        self,
        company_data: Dict
    ) -> Dict:
        """
        Mevcut durumu analiz et
        
        Args:
            company_data: {
                "name": "Company",
                "scope1_emissions": 10000,  # ton CO2e
                "scope2_emissions": 8000,
                "scope3_emissions": 50000,
                "base_year": 2023
            }
        """
        scope1 = company_data.get("scope1_emissions", 0)
        scope2 = company_data.get("scope2_emissions", 0)
        scope3 = company_data.get("scope3_emissions", 0)
        total = scope1 + scope2 + scope3
        
        return {
            "total_emissions": total,
            "scope_breakdown": {
                "scope1": scope1,
                "scope2": scope2,
                "scope3": scope3
            },
            "scope_percentages": {
                "scope1": round(scope1 / total * 100, 1) if total > 0 else 0,
                "scope2": round(scope2 / total * 100, 1) if total > 0 else 0,
                "scope3": round(scope3 / total * 100, 1) if total > 0 else 0
            },
            "base_year": company_data.get("base_year", datetime.now().year)
        }
    
    def generate_pathway(
        self,
        company_data: Dict,
        target_year: int = 2030,
        ambition: str = "1.5C",
        include_scope3: bool = True
    ) -> Dict:
        """
        Net zero yol haritasi olustur
        
        Args:
            company_data: Sirket verileri
            target_year: Hedef yil
            ambition: "1.5C", "well_below_2C", "2C"
            include_scope3: Scope 3 dahil mi
        
        Returns:
            Yol haritasi
        """
        current_state = self.analyze_current_state(company_data)
        base_year = current_state["base_year"]
        total_emissions = current_state["total_emissions"]
        
        # SBTi uyumlu yillik azaltim
        annual_rate = self.SBTI_RATES.get(ambition, 0.042)
        years_to_target = target_year - base_year
        
        # Hedef emisyon hesapla
        target_reduction = 1 - (1 - annual_rate) ** years_to_target
        target_emissions = total_emissions * (1 - target_reduction)
        
        # Yillik hedefler
        yearly_targets = {}
        for year in range(base_year, target_year + 1):
            years_passed = year - base_year
            reduction = 1 - (1 - annual_rate) ** years_passed
            yearly_targets[year] = {
                "target_emissions": round(total_emissions * (1 - reduction)),
                "cumulative_reduction": round(reduction * 100, 1)
            }
        
        # Scope bazli azaltim onerileri
        scope_strategies = self._generate_scope_strategies(
            current_state,
            target_reduction,
            years_to_target,
            include_scope3
        )
        
        return {
            "company": company_data.get("name", "Unknown"),
            "current_emissions": total_emissions,
            "target_year": target_year,
            "target_emissions": round(target_emissions),
            "total_reduction": round(target_reduction * 100, 1),
            "ambition": ambition,
            "sbti_aligned": True,
            "yearly_targets": yearly_targets,
            "scope_strategies": scope_strategies,
            "milestones": self._generate_milestones(base_year, target_year, yearly_targets)
        }
    
    def _generate_scope_strategies(
        self,
        current_state: Dict,
        target_reduction: float,
        years: int,
        include_scope3: bool
    ) -> Dict:
        """Scope bazli strateji olustur"""
        strategies = {}
        scopes = current_state["scope_breakdown"]
        
        for scope_key in ["scope1", "scope2", "scope3"]:
            if scope_key == "scope3" and not include_scope3:
                continue
            
            scope_emissions = scopes[scope_key]
            if scope_emissions == 0:
                continue
            
            scope_num = scope_key[-1]
            actions = self.REDUCTION_ACTIONS.get(scope_key, {})
            
            recommended_actions = []
            cumulative_reduction = 0
            
            for action_id, action in actions.items():
                if cumulative_reduction >= target_reduction:
                    break
                
                if action["timeline_years"] <= years:
                    reduction_amount = scope_emissions * action["potential_reduction"]
                    
                    recommended_actions.append({
                        "action": action["name"],
                        "description": action["description"],
                        "reduction_potential": f"{action['potential_reduction']*100:.0f}%",
                        "reduction_tons": round(reduction_amount),
                        "cost_level": action["cost_level"],
                        "timeline": f"{action['timeline_years']} yil"
                    })
                    
                    cumulative_reduction += action["potential_reduction"]
            
            if recommended_actions:
                strategies[f"Scope {scope_num}"] = {
                    "current_emissions": scope_emissions,
                    "recommended_actions": recommended_actions
                }
        
        return strategies
    
    def _generate_milestones(
        self,
        base_year: int,
        target_year: int,
        yearly_targets: Dict
    ) -> List[Dict]:
        """Onemli kilometre taslari olustur"""
        milestones = []
        
        # Ara hedefler
        years = list(range(base_year, target_year + 1))
        
        # Her 2 yilda bir milestone
        for i, year in enumerate(years):
            if i % 2 == 0 or year == target_year:
                target = yearly_targets.get(year, {})
                milestones.append({
                    "year": year,
                    "target": target.get("target_emissions", 0),
                    "reduction": f"{target.get('cumulative_reduction', 0)}%"
                })
        
        return milestones
    
    def estimate_investment(
        self,
        pathway: Dict,
        company_data: Dict
    ) -> Dict:
        """
        Gerekli yatirim tahmini
        
        Args:
            pathway: generate_pathway ciktisi
            company_data: Sirket verileri
        """
        total_emissions = pathway["current_emissions"]
        
        # Basit maliyet tahmini (ton basina)
        cost_per_ton = {
            "low": 20,    # $20/ton
            "medium": 50,  # $50/ton
            "high": 100   # $100/ton
        }
        
        total_investment = 0
        investment_breakdown = []
        
        for scope, strategy in pathway.get("scope_strategies", {}).items():
            for action in strategy.get("recommended_actions", []):
                reduction_tons = action["reduction_tons"]
                cost_level = action["cost_level"]
                cost = reduction_tons * cost_per_ton.get(cost_level, 50)
                
                investment_breakdown.append({
                    "action": action["action"],
                    "scope": scope,
                    "estimated_cost": f"${cost:,.0f}",
                    "cost_level": cost_level
                })
                
                total_investment += cost
        
        # ROI tahmini (karbon fiyati bazli)
        carbon_price = 50  # $/ton CO2e
        annual_savings = total_emissions * pathway["total_reduction"] / 100 * carbon_price
        payback_years = total_investment / annual_savings if annual_savings > 0 else 0
        
        return {
            "total_investment": f"${total_investment:,.0f}",
            "investment_breakdown": investment_breakdown,
            "estimated_annual_savings": f"${annual_savings:,.0f}",
            "payback_period": f"{payback_years:.1f} yil" if payback_years > 0 else "N/A"
        }
    
    def generate_report(
        self,
        company_data: Dict,
        target_year: int = 2030
    ) -> Dict:
        """
        Kapsamli hedef raporu olustur
        """
        pathway = self.generate_pathway(company_data, target_year)
        investment = self.estimate_investment(pathway, company_data)
        
        return {
            "summary": {
                "company": company_data.get("name", "Unknown"),
                "current_emissions": pathway["current_emissions"],
                "target_year": target_year,
                "target_emissions": pathway["target_emissions"],
                "total_reduction": f"{pathway['total_reduction']}%",
                "sbti_aligned": pathway["sbti_aligned"]
            },
            "pathway": pathway,
            "investment": investment,
            "generated_at": datetime.now().isoformat()
        }


# Test
if __name__ == "__main__":
    print("=== Target Recommender Test ===\n")
    
    recommender = TargetRecommender(verbose=True)
    
    # Test sirketi
    company = {
        "name": "EcoTech Industries",
        "scope1_emissions": 15000,
        "scope2_emissions": 10000,
        "scope3_emissions": 75000,
        "base_year": 2024
    }
    
    print(f"Sirket: {company['name']}")
    print(f"Toplam Emisyon: {sum([company['scope1_emissions'], company['scope2_emissions'], company['scope3_emissions']]):,} ton CO2e\n")
    
    # Pathway olustur
    pathway = recommender.generate_pathway(company, target_year=2030, ambition="1.5C")
    
    print("=== Net Zero Pathway ===")
    print(f"Hedef Yil: {pathway['target_year']}")
    print(f"Hedef Emisyon: {pathway['target_emissions']:,} ton CO2e")
    print(f"Toplam Azaltim: {pathway['total_reduction']}%")
    print(f"SBTi Uyumlu: {pathway['sbti_aligned']}")
    
    print("\n=== Milestones ===")
    for ms in pathway["milestones"]:
        print(f"  {ms['year']}: {ms['target']:,} ton ({ms['reduction']} azaltim)")
    
    print("\n=== Scope Stratejileri ===")
    for scope, strategy in pathway["scope_strategies"].items():
        print(f"\n{scope} ({strategy['current_emissions']:,} ton):")
        for action in strategy["recommended_actions"][:2]:
            print(f"  - {action['action']}: {action['reduction_potential']} azaltim ({action['timeline']})")
    
    # Yatirim tahmini
    investment = recommender.estimate_investment(pathway, company)
    print(f"\n=== Yatirim Tahmini ===")
    print(f"Toplam Yatirim: {investment['total_investment']}")
    print(f"Yillik Tasarruf: {investment['estimated_annual_savings']}")
    print(f"Geri Odeme: {investment['payback_period']}")
    
    print("\n" + "="*40)
    print("BASARILI")
    print("="*40)

