"""
Hybrid Emission Calculator
Climatiq API (ücretli) + Data.gov EPA (ücretsiz) birlikte kullanım
"""

import os
from typing import Dict, Optional
from external_data_sources import DataGovIntegration

class HybridEmissionCalculator:
    """
    Akıllı emisyon hesaplayıcı:
    1. Önce Climatiq API dene (detaylı, ücretli)
    2. Başarısız ise Data.gov EPA faktörleri kullan (ücretsiz)
    3. Her ikisi de yoksa manuel faktörler
    """

    def __init__(self):
        # Load environment
        from dotenv import load_dotenv
        load_dotenv()

        # Climatiq API
        self.climatiq_available = False
        self.climatiq_api_key = os.getenv('CLIMATIQ_API_KEY')

        if self.climatiq_api_key:
            try:
                from climatiq_calculator import ClimatiqCalculator
                self.climatiq = ClimatiqCalculator()  # Kendi .env'den okur
                self.climatiq_available = True
                print("[INFO] Climatiq API aktif")
            except Exception as e:
                print(f"[UYARI] Climatiq yuklenemedi: {str(e)}")
                self.climatiq = None
        else:
            self.climatiq = None

        # Data.gov EPA
        self.datagov = DataGovIntegration()

        # Fallback manual factors
        self.MANUAL_FACTORS = {
            "electricity_kwh": 0.45,
            "natural_gas_m3": 2.0,
            "diesel_litre": 2.68,
            "petrol_litre": 2.31,
            "lpg_litre": 1.51,
            "coal_kg": 2.42,
        }

    def calculate_emission(self, category: str, amount: float, unit: str,
                          region: str = "GLOBAL", use_climatiq: bool = True) -> Dict:
        """
        Hibrit emisyon hesaplama

        Args:
            category: Aktivite kategorisi (electricity, natural_gas, etc.)
            amount: Miktar
            unit: Birim (kWh, m³, litre)
            region: Bölge (TR, US, GB, etc.)
            use_climatiq: Climatiq kullanılsın mı?

        Returns:
            {
                "co2_kg": float,
                "source": str,  # "climatiq", "epa", "manual"
                "confidence": str,  # "high", "medium", "low"
                "factor": float,
                "scope": str
            }
        """

        result = {
            "co2_kg": 0,
            "source": None,
            "confidence": "low",
            "factor": 0,
            "scope": "Unknown"
        }

        # STRATEJI 1: Climatiq API (en detaylı)
        if use_climatiq and self.climatiq_available:
            try:
                # Climatiq ile hesapla
                climatiq_result = self._calculate_with_climatiq(
                    category, amount, unit, region
                )

                if climatiq_result:
                    result.update({
                        "co2_kg": climatiq_result["co2_kg"],
                        "source": "climatiq",
                        "confidence": "high",
                        "factor": climatiq_result["factor"],
                        "scope": climatiq_result.get("scope", "Unknown")
                    })
                    return result

            except Exception as e:
                print(f"[UYARI] Climatiq hatası: {str(e)}")
                # Devam et, EPA'yı dene

        # STRATEJI 2: Data.gov EPA (ücretsiz)
        factor = self.datagov.get_emission_factor(category)

        if factor:
            co2_kg = amount * factor

            # Scope belirleme
            scope = self._determine_scope(category)

            result.update({
                "co2_kg": co2_kg,
                "source": "epa",
                "confidence": "medium",
                "factor": factor,
                "scope": scope
            })
            return result

        # STRATEJI 3: Manuel faktörler (fallback)
        key = f"{category.lower()}_{unit.lower()}"

        if key in self.MANUAL_FACTORS:
            factor = self.MANUAL_FACTORS[key]
            co2_kg = amount * factor

            scope = self._determine_scope(category)

            result.update({
                "co2_kg": co2_kg,
                "source": "manual",
                "confidence": "low",
                "factor": factor,
                "scope": scope
            })
            return result

        # Hiçbiri çalışmadı
        return result

    def _calculate_with_climatiq(self, category, amount, unit, region) -> Optional[Dict]:
        """Climatiq API ile hesaplama"""

        if not self.climatiq_available:
            return None

        # Kategori → Climatiq activity_id mapping
        ACTIVITY_MAPPING = {
            "electricity": "electricity-supply_grid-source_supplier_mix",
            "natural_gas": "fuel_type_natural_gas-combustion-stationary",
            "diesel": "fuel_type_diesel-combustion-mobile",
            "petrol": "fuel_type_petrol-combustion-mobile",
            "lpg": "fuel_type_lpg-combustion-mobile",
        }

        category_lower = category.lower().replace(" ", "_")
        activity_id = None

        # Activity ID bul
        for key, value in ACTIVITY_MAPPING.items():
            if key in category_lower:
                activity_id = value
                break

        if not activity_id:
            return None

        # Climatiq parameters
        params = {
            "emission_factor": {
                "activity_id": activity_id,
                "region": region if region != "GLOBAL" else "US",
                "year": "2024"
            }
        }

        # Unit mapping
        unit_map = {
            "kwh": "kWh",
            "m3": "m3",
            "m³": "m3",
            "litre": "l",
            "l": "l",
            "kg": "kg"
        }

        climatiq_unit = unit_map.get(unit.lower(), unit)

        try:
            # Climatiq API call - mevcut methodları kullan
            result = None

            if "electricity" in category_lower:
                result = self.climatiq.calculate_electricity(amount, region)
            elif "natural_gas" in category_lower or "doğalgaz" in category_lower:
                result = self.climatiq.calculate_natural_gas(amount)
            elif "diesel" in category_lower or "dizel" in category_lower:
                # Dizel için km değil litre kullanıyoruz, genel hesaplama gerek
                # Şimdilik EPA'ya düş
                return None
            elif "petrol" in category_lower or "benzin" in category_lower:
                # Benzin için de aynı durum
                return None

            if result and hasattr(result, 'co2e'):
                return {
                    "co2_kg": result.co2e,
                    "factor": result.co2e / amount if amount > 0 else 0,
                    "scope": self._determine_scope(category)
                }

        except Exception as e:
            print(f"[DEBUG] Climatiq error: {str(e)}")
            return None

        return None

    def _determine_scope(self, category: str) -> str:
        """Kategori bazlı Scope belirleme"""

        category_lower = category.lower()

        if any(x in category_lower for x in ["electricity", "elektrik"]):
            return "Scope 2"
        elif any(x in category_lower for x in ["gas", "gaz", "fuel", "yakıt", "coal", "petrol", "diesel"]):
            return "Scope 1"
        elif any(x in category_lower for x in ["flight", "uçuş", "travel", "seyahat"]):
            return "Scope 3"
        else:
            return "Unknown"

    def get_source_info(self) -> Dict:
        """Hangi kaynaklar aktif?"""

        return {
            "climatiq": {
                "available": self.climatiq_available,
                "api_key": bool(self.climatiq_api_key),
                "coverage": "277,011+ factors",
                "cost": "Paid"
            },
            "epa": {
                "available": True,
                "api_key": False,
                "coverage": "Standard factors",
                "cost": "Free"
            },
            "manual": {
                "available": True,
                "api_key": False,
                "coverage": f"{len(self.MANUAL_FACTORS)} factors",
                "cost": "Free"
            }
        }


# =============================================================================
# KULLANIM ÖRNEĞİ
# =============================================================================

def demo_hybrid_calculator():
    """Hibrit hesaplayıcı demo"""

    print("=" * 70)
    print("HYBRID EMISSION CALCULATOR DEMO")
    print("=" * 70)

    calc = HybridEmissionCalculator()

    # Hangi kaynaklar aktif?
    sources = calc.get_source_info()
    print("\n[MEVCUT KAYNAKLAR]")
    for name, info in sources.items():
        status = "[OK] Aktif" if info["available"] else "[X] Pasif"
        print(f"{name.upper():12} {status:15} | {info['coverage']:20} | {info['cost']}")

    print("\n" + "=" * 70)

    # Test 1: Elektrik
    print("\n[TEST 1] Elektrik Tüketimi")
    result = calc.calculate_emission("electricity", 18450, "kWh", region="TR")

    print(f"Miktar: 18,450 kWh")
    print(f"CO2: {result['co2_kg']:,.2f} kg ({result['co2_kg']/1000:.2f} ton)")
    print(f"Kaynak: {result['source'].upper()}")
    print(f"Güven: {result['confidence']}")
    print(f"Faktör: {result['factor']} kg CO2e/kWh")
    print(f"Scope: {result['scope']}")

    # Test 2: Doğalgaz
    print("\n[TEST 2] Doğalgaz Tüketimi")
    result = calc.calculate_emission("natural_gas", 650, "m3", region="TR")

    print(f"Miktar: 650 m³")
    print(f"CO2: {result['co2_kg']:,.2f} kg ({result['co2_kg']/1000:.2f} ton)")
    print(f"Kaynak: {result['source'].upper()}")
    print(f"Güven: {result['confidence']}")
    print(f"Faktör: {result['factor']} kg CO2e/m³")
    print(f"Scope: {result['scope']}")

    # Test 3: Dizel
    print("\n[TEST 3] Dizel Tüketimi")
    result = calc.calculate_emission("diesel", 200, "litre", region="TR")

    print(f"Miktar: 200 litre")
    print(f"CO2: {result['co2_kg']:,.2f} kg ({result['co2_kg']/1000:.2f} ton)")
    print(f"Kaynak: {result['source'].upper()}")
    print(f"Güven: {result['confidence']}")
    print(f"Faktör: {result['factor']} kg CO2e/litre")
    print(f"Scope: {result['scope']}")

    print("\n" + "=" * 70)
    print("DEMO TAMAMLANDI!")
    print("\nHIBRIT SISTEM:")
    print("1. Climatiq API (detaylı, ücretli)")
    print("2. Data.gov EPA (standart, ücretsiz)")
    print("3. Manuel faktörler (fallback)")
    print("=" * 70)


if __name__ == "__main__":
    demo_hybrid_calculator()
