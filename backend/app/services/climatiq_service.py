"""
Climatiq API Calculator for Streamlit
Emisyon hesaplama ve scope kategorilendirme
"""

import os
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class EmissionResult:
    """Emisyon hesaplama sonucu"""
    activity_name: str
    amount: float
    unit: str
    co2e_kg: float
    co2e_ton: float
    scope: str
    category: str
    region: str
    source: str
    year: int

class ClimatiqCalculator:
    """Climatiq API ile emisyon hesaplayıcı"""

    def __init__(self):
        self.api_key = os.getenv('CLIMATIQ_API_KEY')
        self.base_url = 'https://api.climatiq.io/data/v1'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def estimate(self, activity_id: str, params: dict, region: Optional[str] = None) -> Optional[EmissionResult]:
        """
        Emission tahmini yap

        Args:
            activity_id: Climatiq activity ID
            params: Parametreler (örn: {"energy": 1000, "energy_unit": "kWh"})
            region: Bölge kodu (opsiyonel)

        Returns:
            EmissionResult veya None
        """

        url = f'{self.base_url}/estimate'

        payload = {
            "emission_factor": {
                "activity_id": activity_id,
                "data_version": "^29"
            },
            "parameters": params
        }

        if region:
            payload["emission_factor"]["region"] = region

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                ef = data.get('emission_factor', {})

                return EmissionResult(
                    activity_name=ef.get('name', 'Unknown'),
                    amount=list(params.values())[0],
                    unit=list(params.values())[1],
                    co2e_kg=data.get('co2e', 0),
                    co2e_ton=data.get('co2e', 0) / 1000,
                    scope=self._determine_scope(ef.get('scopes', [])),
                    category=ef.get('category', 'Other'),
                    region=ef.get('region', 'GLOBAL'),
                    source=ef.get('source', 'N/A'),
                    year=ef.get('year', 0)
                )
            else:
                print(f"API Error: {response.status_code} - {response.text[:200]}")
                return None

        except Exception as e:
            print(f"Exception: {str(e)}")
            return None

    def _determine_scope(self, scopes: List) -> str:
        """Scope belirle"""
        if not scopes:
            return "Unknown"

        scope_str = str(scopes[0])

        if scope_str.startswith('1'):
            return "Scope 1"
        elif scope_str.startswith('2'):
            return "Scope 2"
        elif scope_str.startswith('3'):
            return f"Scope 3.{scope_str.split('.')[-1] if '.' in scope_str else ''}"
        else:
            return "Other"

    # ==================== HAZIR HESAPLAMALAR ====================

    def calculate_electricity(self, kwh: float, region: str = "TR") -> Optional[EmissionResult]:
        """Elektrik tüketimi hesapla"""
        return self.estimate(
            activity_id="electricity-supply_grid-source_supplier_mix",
            params={"energy": kwh, "energy_unit": "kWh"},
            region=region
        )

    def calculate_natural_gas(self, m3: float) -> Optional[EmissionResult]:
        """Doğalgaz tüketimi hesapla"""
        return self.estimate(
            activity_id="fuel_type_natural_gas",
            params={"volume": m3, "volume_unit": "m3"}
        )

    def calculate_petrol_vehicle(self, km: float, region: str = "GB") -> Optional[EmissionResult]:
        """Benzinli araç hesapla"""
        return self.estimate(
            activity_id="passenger_vehicle-vehicle_type_car-fuel_source_petrol-engine_size_medium-vehicle_age_na-vehicle_weight_na",
            params={"distance": km, "distance_unit": "km"},
            region=region
        )

    def calculate_diesel_vehicle(self, km: float, region: str = "GB") -> Optional[EmissionResult]:
        """Dizel araç hesapla"""
        return self.estimate(
            activity_id="passenger_vehicle-vehicle_type_car-fuel_source_diesel-engine_size_medium-vehicle_age_na-vehicle_weight_na",
            params={"distance": km, "distance_unit": "km"},
            region=region
        )

    def calculate_flight_economy(self, km: float) -> Optional[EmissionResult]:
        """Uçak (ekonomi) hesapla"""
        return self.estimate(
            activity_id="passenger_flight-route_type_domestic-aircraft_type_na-distance_na-class_economy-rf_included",
            params={"distance": km, "distance_unit": "km"}
        )

    def calculate_flight_business(self, km: float) -> Optional[EmissionResult]:
        """Uçak (business) hesapla"""
        return self.estimate(
            activity_id="passenger_flight-route_type_domestic-aircraft_type_na-distance_na-class_business-rf_included",
            params={"distance": km, "distance_unit": "km"}
        )

    def calculate_batch(self, emission_data: List[Dict]) -> List[EmissionResult]:
        """
        Toplu hesaplama yap

        Args:
            emission_data: Veri listesi (esg_app.py'den gelen)

        Returns:
            EmissionResult listesi
        """

        results = []

        for entry in emission_data:
            category = entry.get('category')

            # VERITABANINDAN GELEN (activity_id var)
            if 'activity_id' in entry and entry.get('amount', 0) > 0:
                activity_id = entry['activity_id']
                amount = entry['amount']
                unit = entry.get('unit', 'unknown')
                region = entry.get('region', 'GLOBAL')

                # unit_type'a gore parametre olustur (veritabanından gelen)
                unit_type = entry.get('unit_type', 'Energy')
                params = {}

                if unit_type == 'Energy':
                    params = {"energy": amount, "energy_unit": "kWh"}
                elif unit_type == 'Distance':
                    params = {"distance": amount, "distance_unit": "km"}
                elif unit_type == 'Weight':
                    params = {"weight": amount, "weight_unit": "kg"}
                elif unit_type == 'Volume':
                    params = {"volume": amount, "volume_unit": "m3"}
                elif unit_type == 'Money':
                    params = {"money": amount, "money_unit": "usd"}
                else:
                    # Fallback: unit string parsing
                    if 'kwh' in unit.lower():
                        params = {"energy": amount, "energy_unit": "kWh"}
                    elif 'km' in unit.lower():
                        params = {"distance": amount, "distance_unit": "km"}
                    elif 'kg' in unit.lower():
                        params = {"weight": amount, "weight_unit": "kg"}
                    else:
                        params = {"energy": amount, "energy_unit": "kWh"}  # Default to energy

                result = self.estimate(
                    activity_id=activity_id,
                    params=params,
                    region=region if region != 'GLOBAL' else None
                )

                if result:
                    results.append(result)

            # ENERJİ
            elif category == "Enerji":
                electricity_kwh = entry.get('electricity_kwh', 0)
                natural_gas_m3 = entry.get('natural_gas_m3', 0)
                region = entry.get('region', 'TR')

                if electricity_kwh > 0:
                    result = self.calculate_electricity(electricity_kwh, region)
                    if result:
                        results.append(result)

                if natural_gas_m3 > 0:
                    result = self.calculate_natural_gas(natural_gas_m3)
                    if result:
                        results.append(result)

            # ULAŞIM
            elif category == "Ulaşım":
                vehicle_km = entry.get('vehicle_km', 0)
                fuel_type = entry.get('fuel_type', 'Benzin')
                flight_km = entry.get('flight_km', 0)
                flight_class = entry.get('flight_class', 'Ekonomi')

                if vehicle_km > 0:
                    if fuel_type == "Benzin":
                        result = self.calculate_petrol_vehicle(vehicle_km)
                    elif fuel_type == "Dizel":
                        result = self.calculate_diesel_vehicle(vehicle_km)
                    else:
                        result = None  # Elektrikli araç için ayrı API

                    if result:
                        results.append(result)

                if flight_km > 0:
                    if flight_class == "Ekonomi":
                        result = self.calculate_flight_economy(flight_km)
                    else:
                        result = self.calculate_flight_business(flight_km)

                    if result:
                        results.append(result)

        return results

    def summarize_by_scope(self, results: List[EmissionResult]) -> Dict[str, float]:
        """Scope'lara göre özet"""
        summary = {
            "Scope 1": 0,
            "Scope 2": 0,
            "Scope 3": 0,
            "Other": 0
        }

        for result in results:
            scope = result.scope.split('.')[0] if '.' in result.scope else result.scope
            if scope in summary:
                summary[scope] += result.co2e_ton
            else:
                summary["Other"] += result.co2e_ton

        return summary

# Test
if __name__ == "__main__":
    calc = ClimatiqCalculator()

    print("="*60)
    print("CLIMATIQ CALCULATOR TEST")
    print("="*60)

    # Test 1: Elektrik
    print("\n[TEST 1] Elektrik - 10,000 kWh (TR)")
    result = calc.calculate_electricity(10000, "TR")
    if result:
        print(f"[OK] {result.co2e_ton:.2f} ton CO2e ({result.scope})")

    # Test 2: Araç
    print("\n[TEST 2] Benzinli Araç - 1,000 km")
    result = calc.calculate_petrol_vehicle(1000)
    if result:
        print(f"[OK] {result.co2e_ton:.2f} ton CO2e ({result.scope})")

    # Test 3: Uçak
    print("\n[TEST 3] Uçak (Ekonomi) - 500 km")
    result = calc.calculate_flight_economy(500)
    if result:
        print(f"[OK] {result.co2e_ton:.2f} ton CO2e ({result.scope})")

    print("\n" + "="*60)
