"""Target Recommender Test Script"""
import sys
sys.path.insert(0, '.')
from models.target_recommendation.recommender import TargetRecommender

print("=== Target Recommender Test ===\n")

recommender = TargetRecommender(verbose=True)

company = {
    "name": "EcoTech Industries",
    "scope1_emissions": 15000,
    "scope2_emissions": 10000,
    "scope3_emissions": 75000,
    "base_year": 2024
}

total = company["scope1_emissions"] + company["scope2_emissions"] + company["scope3_emissions"]
print(f"Sirket: {company['name']}")
print(f"Toplam Emisyon: {total:,} ton CO2e\n")

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
        print(f"  - {action['action']}: {action['reduction_potential']} azaltim")

investment = recommender.estimate_investment(pathway, company)
print(f"\n=== Yatirim Tahmini ===")
print(f"Toplam Yatirim: {investment['total_investment']}")
print(f"Yillik Tasarruf: {investment['estimated_annual_savings']}")
print(f"Geri Odeme: {investment['payback_period']}")

print("\n" + "="*40)
print("BASARILI")
print("="*40)

