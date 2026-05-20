"""
Activity Database - Climatiq Emission Factor Veritabani
273,000+ emission factor'dan populer ve kullanisli olanlari sunar
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from collections import Counter

class ActivityDatabase:
    """Climatiq emission factor veritabani yoneticisi"""

    def __init__(self):
        project_root = Path(__file__).resolve().parent.parent
        self.data_dir = project_root / "data"
        self.scope1_data = []
        self.scope2_data = []
        self.scope3_data = []
        self.all_data = []

        self._load_data()

    def _load_data(self):
        """JSON dosyalarini yukle"""
        try:
            # Scope 1
            scope1_path = self.data_dir / 'scope1_data.json'
            if scope1_path.exists():
                with open(scope1_path, 'r', encoding='utf-8') as f:
                    self.scope1_data = json.load(f)

            # Scope 2
            scope2_path = self.data_dir / 'scope2_data.json'
            if scope2_path.exists():
                with open(scope2_path, 'r', encoding='utf-8') as f:
                    self.scope2_data = json.load(f)

            # Scope 3 (opsiyonel — dosya yoksa boş liste)
            scope3_path = self.data_dir / 'scope3_data.json'
            if scope3_path.exists():
                with open(scope3_path, 'r', encoding='utf-8') as f:
                    self.scope3_data = json.load(f)

            self.all_data = self.scope1_data + self.scope2_data + self.scope3_data

            print(f"[OK] Yuklendi: {len(self.scope1_data)} Scope 1, {len(self.scope2_data)} Scope 2, {len(self.scope3_data)} Scope 3")

        except Exception as e:
            print(f"[HATA] Veri yukleme hatasi: {e}")

    def search_activities(self,
                         query: str = "",
                         scope: Optional[str] = None,
                         category: Optional[str] = None,
                         region: Optional[str] = None,
                         limit: int = 50) -> List[Dict]:
        """
        Activity ara

        Args:
            query: Arama terimi (name, category, sector'da arar)
            scope: Scope filtresi ("1", "2", "3")
            category: Kategori filtresi
            region: Bolge filtresi (ornek: "TR", "US", "GLOBAL")
            limit: Maksimum sonuc sayisi

        Returns:
            Filtrelenmis activity listesi
        """

        # Scope'a gore veri sec
        if scope == "1":
            data = self.scope1_data
        elif scope == "2":
            data = self.scope2_data
        elif scope == "3":
            data = self.scope3_data
        else:
            data = self.all_data

        results = []
        query_lower = query.lower()

        for activity in data:
            # Query filtresi
            if query:
                if not (query_lower in activity.get('name', '').lower() or
                       query_lower in activity.get('category', '').lower() or
                       query_lower in activity.get('sector', '').lower()):
                    continue

            # Kategori filtresi
            if category and activity.get('category') != category:
                continue

            # Bolge filtresi
            if region and activity.get('region') != region:
                continue

            results.append(activity)

            if len(results) >= limit:
                break

        return results

    def get_categories(self, scope: Optional[str] = None) -> List[str]:
        """Tum kategorileri getir"""
        if scope == "1":
            data = self.scope1_data
        elif scope == "2":
            data = self.scope2_data
        elif scope == "3":
            data = self.scope3_data
        else:
            data = self.all_data

        categories = set(activity.get('category', 'Unknown') for activity in data)
        return sorted(list(categories))

    def get_regions(self, scope: Optional[str] = None) -> List[str]:
        """Tum bolgeleri getir"""
        if scope == "1":
            data = self.scope1_data
        elif scope == "2":
            data = self.scope2_data
        elif scope == "3":
            data = self.scope3_data
        else:
            data = self.all_data

        regions = set(activity.get('region', 'GLOBAL') for activity in data)
        return sorted(list(regions))

    def get_popular_activities(self, scope: Optional[str] = None, top_n: int = 20) -> List[Dict]:
        """
        Populer (sik kullanilan) aktiviteleri getir

        Kriter: Elektrik, dogalgaz, arac, ucak gibi genel kullanim
        """

        # Manuel secilmis populer arama terimleri
        popular_queries = [
            "electricity",
            "natural gas",
            "diesel",
            "petrol",
            "gasoline",
            "flight",
            "car",
            "truck",
            "bus",
            "train",
            "heating",
            "fuel",
            "coal",
            "waste",
            "water"
        ]

        results = []
        for query in popular_queries:
            matches = self.search_activities(query=query, scope=scope, limit=5)
            results.extend(matches)

            if len(results) >= top_n:
                break

        # Unique yap (activity_id bazinda)
        seen = set()
        unique_results = []
        for activity in results:
            if activity['activity_id'] not in seen:
                seen.add(activity['activity_id'])
                unique_results.append(activity)

        return unique_results[:top_n]

    def get_activity_by_id(self, activity_id: str) -> Optional[Dict]:
        """Activity ID'ye gore activity getir"""
        for activity in self.all_data:
            if activity['activity_id'] == activity_id:
                return activity
        return None

    def get_stats(self) -> Dict:
        """Veritabani istatistikleri"""
        return {
            "total": len(self.all_data),
            "scope1": len(self.scope1_data),
            "scope2": len(self.scope2_data),
            "scope3": len(self.scope3_data),
            "categories": len(self.get_categories()),
            "regions": len(self.get_regions())
        }


# Test
if __name__ == "__main__":
    print("="*60)
    print("ACTIVITY DATABASE TEST")
    print("="*60)

    db = ActivityDatabase()

    # Istatistikler
    stats = db.get_stats()
    print(f"\n[STATS]")
    print(f"Total: {stats['total']:,}")
    print(f"Scope 1: {stats['scope1']:,}")
    print(f"Scope 2: {stats['scope2']:,}")
    print(f"Scope 3: {stats['scope3']:,}")
    print(f"Categories: {stats['categories']}")
    print(f"Regions: {stats['regions']}")

    # Test: Elektrik ara
    print(f"\n[TEST 1] 'electricity' arama (Scope 2):")
    results = db.search_activities(query="electricity", scope="2", limit=5)
    for i, activity in enumerate(results, 1):
        print(f"{i}. {activity['name'][:60]} ({activity['region']})")

    # Test: Dogalgaz ara
    print(f"\n[TEST 2] 'natural gas' arama (Scope 1):")
    results = db.search_activities(query="natural gas", scope="1", limit=5)
    for i, activity in enumerate(results, 1):
        print(f"{i}. {activity['name'][:60]} ({activity['region']})")

    # Test: Populer aktiviteler
    print(f"\n[TEST 3] Populer aktiviteler:")
    popular = db.get_popular_activities(top_n=10)
    for i, activity in enumerate(popular, 1):
        print(f"{i}. {activity['name'][:60]} (Scope {activity['scopes'][0]})")

    # Test: Kategoriler
    print(f"\n[TEST 4] Ilk 10 kategori:")
    categories = db.get_categories()[:10]
    for cat in categories:
        print(f"  - {cat}")

    print("\n" + "="*60)