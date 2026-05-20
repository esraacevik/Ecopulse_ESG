import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('CLIMATIQ_API_KEY')
BASE_URL = 'https://api.climatiq.io'

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

def search_emission_factors(query=None, category=None, scope=None, region=None):
    """Search for available emission factors"""
    url = f'{BASE_URL}/data/v1/search'

    params = {
        'data_version': '^29',
        'results_per_page': 10
    }

    if query:
        params['query'] = query
    if category:
        params['category'] = category
    if scope:
        # Scope can be "1", "2", "3.1", etc.
        params['scope'] = scope
    if region:
        params['region'] = region.upper()  # Ensure uppercase

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
        else:
            print(f"[HATA] Search API: {response.status_code}")
            print(response.text)
            return []
    except Exception as e:
        print(f"[HATA] {str(e)}")
        return []

def estimate_emission(activity_id, value, unit):
    """Calculate emission using Estimate API"""
    url = f'{BASE_URL}/data/v1/estimate'

    payload = {
        "emission_factor": {
            "activity_id": activity_id,
            "data_version": "^29"
        },
        "parameters": {
            unit: value
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"[HATA] Estimate API: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"[HATA] {str(e)}")
        return None

def display_emission_factors(factors):
    """Display emission factors in a readable format"""
    if not factors:
        print("Sonuc bulunamadi.")
        return

    print(f"\nToplam {len(factors)} sonuc bulundu:")
    print("="*100)

    for idx, factor in enumerate(factors, 1):
        print(f"\n[{idx}] {factor.get('name', 'N/A')}")
        print(f"    Activity ID: {factor.get('activity_id', 'N/A')}")
        print(f"    Category: {factor.get('category', 'N/A')}")
        print(f"    Sector: {factor.get('sector', 'N/A')}")
        print(f"    Scope: {', '.join(map(str, factor.get('scopes', [])))}")
        print(f"    Region: {factor.get('region_name', 'N/A')} ({factor.get('region', 'N/A')})")
        print(f"    Unit: {factor.get('unit', 'N/A')}")
        print(f"    Source: {factor.get('source', 'N/A')} ({factor.get('year', 'N/A')})")
    print("="*100)

def interactive_calculator():
    """Interactive emission calculator"""
    print("="*100)
    print("CLIMATIQ EMISSION CALCULATOR")
    print("="*100)
    print("\nBu arac ile emisyon hesaplamalari yapabilirsiniz.")
    print("Once bir aktivite arayacak, sonra hesaplama yapacaksiniz.\n")

    while True:
        print("\n" + "="*100)
        print("ADIM 1: EMISSION FACTOR ARAMA")
        print("="*100)

        # Search parameters
        print("\nArama kriterleri (bos birakmak icin Enter basin):")
        query = input("  Anahtar kelime (orn: diesel, electricity, flight): ").strip()
        category = input("  Kategori (orn: Fuels, Energy, Transport): ").strip()
        scope = input("  Scope (1, 2, 3.1, vb.): ").strip()
        region = input("  Bolge kodu (orn: TR, US, GLOBAL): ").strip()

        # Search
        print("\nAranyor...")
        factors = search_emission_factors(
            query=query or None,
            category=category or None,
            scope=scope or None,
            region=region or None
        )

        if not factors:
            retry = input("\nSonuc bulunamadi. Tekrar denemek ister misiniz? (e/h): ")
            if retry.lower() != 'e':
                break
            continue

        # Display results
        display_emission_factors(factors)

        # Select factor
        print("\n" + "="*100)
        print("ADIM 2: EMISSION FACTOR SECIMI")
        print("="*100)

        try:
            selection = int(input(f"\nHangi emission factor'u kullanmak istersiniz? (1-{len(factors)}): "))
            if selection < 1 or selection > len(factors):
                print("[HATA] Gecersiz secim!")
                continue

            selected_factor = factors[selection - 1]
        except ValueError:
            print("[HATA] Gecersiz giris!")
            continue

        # Show selected factor details
        print("\n" + "-"*100)
        print("SECILEN EMISSION FACTOR:")
        print("-"*100)
        print(f"Name: {selected_factor.get('name')}")
        print(f"Activity ID: {selected_factor.get('activity_id')}")
        print(f"Unit: {selected_factor.get('unit')}")
        print(f"Scope: {', '.join(map(str, selected_factor.get('scopes', [])))}")
        print("-"*100)

        # Get calculation parameters
        print("\n" + "="*100)
        print("ADIM 3: HESAPLAMA PARAMETRELERI")
        print("="*100)

        unit_type = selected_factor.get('unit_type', '').lower()
        unit = selected_factor.get('unit', '')

        # Determine parameter name based on unit type
        if 'weight' in unit_type or 'kg' in unit or 'ton' in unit:
            param_name = 'weight'
            param_unit = 'kg'
        elif 'volume' in unit_type or 'liter' in unit or 'l' in unit or 'm3' in unit:
            param_name = 'volume'
            param_unit = 'l'
        elif 'energy' in unit_type or 'kwh' in unit or 'mwh' in unit or 'kj' in unit:
            param_name = 'energy'
            param_unit = 'kWh'
        elif 'distance' in unit_type or 'km' in unit or 'mile' in unit:
            param_name = 'distance'
            param_unit = 'km'
        elif 'money' in unit_type or 'usd' in unit or 'eur' in unit:
            param_name = 'money'
            param_unit = 'usd'
        else:
            # Generic
            param_name = 'weight'
            param_unit = unit.split('/')[0] if '/' in unit else 'kg'

        print(f"\nBirim tipi: {selected_factor.get('unit_type', 'N/A')}")
        print(f"Birim: {unit}")
        print(f"Parametre: {param_name} ({param_unit})")

        try:
            value = float(input(f"\nMiktar girin ({param_unit}): "))
        except ValueError:
            print("[HATA] Gecersiz miktar!")
            continue

        # Calculate emission
        print("\n" + "="*100)
        print("ADIM 4: EMISYON HESAPLAMA")
        print("="*100)
        print("\nHesaplaniyor...")

        result = estimate_emission(
            activity_id=selected_factor.get('activity_id'),
            value=value,
            unit=param_name
        )

        if result:
            print("\n" + "="*100)
            print("HESAPLAMA SONUCU")
            print("="*100)

            co2e = result.get('co2e', 0)
            co2e_unit = result.get('co2e_unit', 'kg')

            print(f"\nAktivite: {selected_factor.get('name')}")
            print(f"Miktar: {value} {param_unit}")
            print(f"\n>>> TOPLAM EMISYON: {co2e:,.2f} {co2e_unit} CO2e <<<")

            # Show factor if available
            ef = result.get('emission_factor', {})
            if ef.get('factor'):
                print(f"\nKullanilan Emission Factor: {ef.get('factor')} {ef.get('factor_unit', 'kg CO2e/unit')}")
                print(f"Hesaplama Metodu: {ef.get('factor_calculation_method', 'N/A')}")

            # Constituent gases
            gases = result.get('constituent_gases', {})
            if gases.get('co2e_total'):
                print(f"\nGaz Dagilimi:")
                print(f"  CO2: {gases.get('co2', 0):,.2f} kg")
                print(f"  CH4: {gases.get('ch4', 0):,.6f} kg")
                print(f"  N2O: {gases.get('n2o', 0):,.6f} kg")

            print("="*100)

            # Save result
            save = input("\nSonucu kaydetmek ister misiniz? (e/h): ")
            if save.lower() == 'e':
                filename = f"emission_result_{selected_factor.get('activity_id', 'unknown')}_{int(value)}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        'input': {
                            'activity_id': selected_factor.get('activity_id'),
                            'activity_name': selected_factor.get('name'),
                            'value': value,
                            'unit': param_unit
                        },
                        'result': result
                    }, f, indent=2, ensure_ascii=False)
                print(f"[OK] Sonuc kaydedildi: {filename}")
        else:
            print("\n[HATA] Hesaplama yapilamadi!")

        # Continue?
        print("\n" + "="*100)
        again = input("\nBaska bir hesaplama yapmak ister misiniz? (e/h): ")
        if again.lower() != 'e':
            break

    print("\n[TAMAMLANDI] Hesaplama araci kapatildi.")
    print("="*100)

if __name__ == '__main__':
    interactive_calculator()
