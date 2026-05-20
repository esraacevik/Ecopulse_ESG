"""
External Environmental Data Sources Integration
Data.gov, Datarade.ai, RDC Aviation entegrasyonu
"""

import requests
import pandas as pd
from typing import Dict, List, Optional
import json

class DataGovIntegration:
    """
    Data.gov EPA Emisyon Faktörleri
    Ücretsiz, açık veri API
    """

    def __init__(self):
        self.base_url = "https://catalog.data.gov/api/3/action"
        self.epa_package = "supply-chain-greenhouse-gas-emission-factors"

    def search_datasets(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Data.gov'da dataset ara

        Args:
            query: Arama sorgusu (örn: "emissions", "carbon", "ghg")
            limit: Sonuç sayısı

        Returns:
            List of datasets
        """

        endpoint = f"{self.base_url}/package_search"

        params = {
            "q": query,
            "rows": limit,
            "fq": "organization:epa-gov"  # EPA datasets
        }

        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data["success"]:
                results = data["result"]["results"]
                datasets = []

                for item in results:
                    datasets.append({
                        "title": item.get("title", ""),
                        "name": item.get("name", ""),
                        "notes": item.get("notes", "")[:200],
                        "organization": item.get("organization", {}).get("title", ""),
                        "resources": len(item.get("resources", [])),
                        "url": f"https://catalog.data.gov/dataset/{item.get('name', '')}"
                    })

                return datasets
            else:
                return []

        except Exception as e:
            print(f"[HATA] Data.gov arama hatası: {str(e)}")
            return []

    def get_epa_emission_factors(self) -> Optional[pd.DataFrame]:
        """
        EPA Supply Chain GHG Emission Factors dataset'ini indir

        Returns:
            DataFrame with emission factors veya None
        """

        # EPA GHG dataset URL (örnek - gerçek URL'i bulmanız gerekiyor)
        # Bu örnek bir placeholder URL
        epa_url = "https://www.epa.gov/sites/default/files/2020-12/ghg_emission_factors_hub.csv"

        try:
            print("[ISLEM] EPA emisyon faktorleri indiriliyor...")

            # CSV'yi pandas ile oku
            df = pd.read_csv(epa_url)

            print(f"[BASARILI] {len(df)} adet emisyon faktoru yuklendi")
            print(f"[SUTUNLAR] {', '.join(df.columns.tolist()[:5])}")

            return df

        except Exception as e:
            print(f"[HATA] EPA veri indirme hatasi: {str(e)}")
            print("\n[ALTERNATIF] Manuel indirme:")
            print("1. https://catalog.data.gov/dataset/supply-chain-greenhouse-gas-emission-factors")
            print("2. CSV dosyasini indir")
            print("3. Projeye ekle: emission_factors.csv")

            return None

    def get_emission_factor(self, activity: str, unit: str = "kg") -> Optional[float]:
        """
        Belirli bir aktivite için emisyon faktörü al

        Args:
            activity: Aktivite türü (örn: "Electricity", "Natural Gas")
            unit: Birim (kg, ton)

        Returns:
            Emission factor (kg CO2e per unit) veya None
        """

        # Statik emisyon faktörleri (EPA'dan alınmış örnekler)
        EMISSION_FACTORS = {
            "electricity_kwh": 0.45,  # kg CO2e per kWh (grid average)
            "natural_gas_m3": 2.0,    # kg CO2e per m³
            "diesel_litre": 2.68,     # kg CO2e per litre
            "petrol_litre": 2.31,     # kg CO2e per litre
            "lpg_litre": 1.51,        # kg CO2e per litre
            "coal_kg": 2.42,          # kg CO2e per kg
        }

        # Activity normalization
        activity_normalized = activity.lower().replace(" ", "_")

        # Faktörü bul
        for key, value in EMISSION_FACTORS.items():
            if activity_normalized in key:
                return value

        return None


class RDCAviationIntegration:
    """
    RDC Aviation CO2 API
    Ücretli - API key gerekli
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.rdcaviation.com"  # Placeholder URL

    def calculate_flight_emissions(self, origin: str, destination: str,
                                   passengers: int = 1) -> Optional[Dict]:
        """
        Uçuş CO2 emisyonlarını hesapla

        Args:
            origin: Kalkış havaalanı (IATA code)
            destination: Varış havaalanı (IATA code)
            passengers: Yolcu sayısı

        Returns:
            {
                "distance_km": float,
                "co2_kg": float,
                "co2_per_passenger": float
            }
        """

        if not self.api_key:
            print("[UYARI] RDC Aviation API key gerekli!")
            print("Ucretsiz deneme: https://rdcaviation.com/")
            return None

        # API call (örnek - gerçek endpoint'i dokümentasyondan alın)
        endpoint = f"{self.base_url}/v1/emissions/flight"

        params = {
            "origin": origin,
            "destination": destination,
            "passengers": passengers,
            "api_key": self.api_key
        }

        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            return {
                "distance_km": data.get("distance_km", 0),
                "co2_kg": data.get("total_co2_kg", 0),
                "co2_per_passenger": data.get("co2_per_passenger_kg", 0)
            }

        except Exception as e:
            print(f"[HATA] RDC Aviation API hatasi: {str(e)}")
            return None


class DataradeIntegration:
    """
    Datarade.ai ESG Data Providers
    Ücretli - marketplace
    """

    def __init__(self):
        self.providers = {
            "GIST": "Sustainability data for 18,000+ companies",
            "Financial Modeling Prep": "ESG ratings and environmental metrics",
            "Sustainable Platform": "Environmental impact data for 30,000+ companies"
        }

    def list_providers(self) -> List[Dict]:
        """Available providers listesini döndür"""

        return [
            {"name": name, "description": desc}
            for name, desc in self.providers.items()
        ]

    def get_provider_info(self, provider_name: str) -> str:
        """Provider bilgisi"""

        return self.providers.get(provider_name, "Provider not found")


# =============================================================================
# KULLANIM ÖRNEĞİ
# =============================================================================

def demo_data_sources():
    """Veri kaynaklarını test et"""

    print("=" * 70)
    print("EXTERNAL DATA SOURCES DEMO")
    print("=" * 70)

    # 1. Data.gov (UCRETSIZ)
    print("\n[1] DATA.GOV - EPA EMISSIONS DATA")
    print("-" * 70)

    datagov = DataGovIntegration()

    # Dataset ara
    print("\n[ARAMA] 'emissions' anahtar kelimesiyle arama:")
    datasets = datagov.search_datasets("emissions", limit=5)

    if datasets:
        for idx, ds in enumerate(datasets, 1):
            print(f"\n{idx}. {ds['title']}")
            print(f"   Organizasyon: {ds['organization']}")
            print(f"   URL: {ds['url']}")
    else:
        print("Dataset bulunamadi")

    # Emisyon faktörü al
    print("\n[EMISYON FAKTORU] Elektrik icin:")
    factor = datagov.get_emission_factor("electricity")
    if factor:
        print(f"  {factor} kg CO2e per kWh")

    # 2. RDC Aviation (UCRETLI)
    print("\n\n[2] RDC AVIATION - FLIGHT CO2 API")
    print("-" * 70)

    rdc = RDCAviationIntegration()  # API key yok
    print("[BILGI] API key gerekli (ucretli servis)")
    print("Ornek kullanim:")
    print("  rdc = RDCAviationIntegration(api_key='YOUR_KEY')")
    print("  rdc.calculate_flight_emissions('IST', 'LHR', passengers=100)")

    # 3. Datarade.ai (UCRETLI)
    print("\n\n[3] DATARADE.AI - ESG DATA MARKETPLACE")
    print("-" * 70)

    datarade = DataradeIntegration()
    providers = datarade.list_providers()

    print("\n[MEVCUT PROVIDERS]")
    for idx, provider in enumerate(providers, 1):
        print(f"{idx}. {provider['name']}")
        print(f"   {provider['description']}")

    print("\n" + "=" * 70)
    print("DEMO TAMAMLANDI!")
    print("\nONERI: Data.gov ile baslayın (UCRETSIZ)")
    print("=" * 70)


if __name__ == "__main__":
    demo_data_sources()
