"""Sector Benchmarker Test Script"""
import sys
sys.path.insert(0, '.')
from models.sector_benchmark.benchmarker import SectorBenchmarker

print("=== Sector Benchmarker Test ===\n")

benchmarker = SectorBenchmarker(verbose=True)
benchmarker.load_data()

companies = [
    {"name": "EcoTech Mfg", "naics_code": "336", "total_emissions": 25000, "revenue": 500000000, "employees": 2000},
    {"name": "GreenBank", "naics_code": "522", "total_emissions": 1000, "revenue": 200000000, "employees": 500},
    {"name": "HighCarbon Steel", "naics_code": "331", "total_emissions": 150000, "revenue": 800000000, "employees": 3000}
]

print("\n=== Individual Benchmarks ===\n")
for company in companies:
    result = benchmarker.benchmark_company(company)
    if result["success"]:
        m = result["metrics"]
        print(f"{result['company']}: Rating={m['rating']}, Percentile={m['percentile']}%, Ratio={m['ratio']}")
    else:
        print(f"{company['name']}: {result.get('error', 'Error')}")

print("\n=== Comparison Table ===\n")
comparison = benchmarker.compare_companies(companies)
print(comparison[["company", "sector", "rating", "percentile"]].to_string())

print("\n=== Recommendations (HighCarbon Steel) ===")
result = benchmarker.benchmark_company(companies[2])
recs = benchmarker.get_recommendations(result)
for rec in recs:
    print(f"  {rec}")

print("\n" + "="*40)
print("BASARILI")
print("="*40)

