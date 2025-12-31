"""
Sector Benchmarking Model
=========================

Şirketleri sektör ortalamasıyla karşılaştırıp konumlandırır.

Özellikler:
- NAICS kodları ile sektör eşleştirme
- Percentile ranking
- Peer comparison
- Clustering (K-Means, DBSCAN)

Metrikler:
- emission_intensity: kg CO2e / $ Revenue
- energy_intensity: kWh / m²
- renewable_ratio: Yenilenebilir oranı

Kullanım:
    from models.sector_benchmark import SectorBenchmarker
    
    benchmarker = SectorBenchmarker()
    benchmarker.load_sector_data()
    result = benchmarker.benchmark(company_data)
"""

__all__ = [
    "SectorBenchmarker",
    "NAICSMatcher",
    "PercentileRanker",
    "PeerComparator"
]

