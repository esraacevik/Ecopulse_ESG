"""
Target Recommendation Model
===========================

Net zero hedefi için azaltım planı ve yol haritası önerir.

Özellikler:
- Trend analizi
- Senaryo modelleme
- Pathway optimization
- SBTi alignment check

Hedef Türleri:
- net_zero: Net sıfır hedefi (2030/2040/2050)
- science_based: Bilim tabanlı hedefler
- sector_aligned: Sektör uyumlu hedefler

Azaltım Aksiyonları:
- Scope 1: Fleet electrification, fuel switching
- Scope 2: Renewable energy, efficiency
- Scope 3: Supplier engagement, travel reduction

Kullanım:
    from models.target_recommendation import TargetRecommender
    
    recommender = TargetRecommender()
    pathway = recommender.generate_pathway(
        current_emissions=50000,
        target_year=2030
    )
"""

__all__ = [
    "TargetRecommender",
    "TrendAnalyzer",
    "ScenarioModeler",
    "PathwayOptimizer"
]

