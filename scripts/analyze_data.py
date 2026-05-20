"""
Climatiq Emission Factors - Veri Analiz Script'i
Bu script, indirilen verileri analiz etmek için örnekler içerir.
"""

import json
import os
from collections import Counter, defaultdict
from pathlib import Path

# Proje kökü: scripts/ -> ESG_project/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def data_path(filename: str) -> Path:
    """data/ klasöründeki dosya yolu."""
    return DATA_DIR / filename


def load_json(filename: str):
    """JSON dosyasını data/ klasöründen yükle."""
    path = data_path(filename)
    if not path.exists():
        raise FileNotFoundError(f"Veri dosyası bulunamadı: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_summary():
    """Özet istatistikleri göster"""
    print("="*60)
    print("CLIMATIQ EMISSION FACTORS - ÖZET İSTATİSTİKLER")
    print("="*60)

    summary = load_json('summary.json')

    print(f"\nToplam Kayıt: {summary['total_records']:,}")
    print(f"\nScope Dağılımı:")
    print(f"  Scope 1: {summary['scope1_count']:,} ({summary['scope1_count']/summary['total_records']*100:.1f}%)")
    print(f"  Scope 2: {summary['scope2_count']:,} ({summary['scope2_count']/summary['total_records']*100:.1f}%)")
    print(f"  Scope 3: {summary['scope3_count']:,} ({summary['scope3_count']/summary['total_records']*100:.1f}%)")
    print(f"  Scope Yok: {summary['no_scope_count']:,} ({summary['no_scope_count']/summary['total_records']*100:.1f}%)")

    print(f"\nScope 3 Alt Kategorileri:")
    scope3_details = {k: v for k, v in summary['unique_scope_values'].items() if k.startswith('3.')}
    for scope, count in sorted(scope3_details.items(), key=lambda x: x[1], reverse=True):
        print(f"  {scope}: {count:,}")

def analyze_sources():
    """Veri kaynaklarını analiz et"""
    print("\n" + "="*60)
    print("VERİ KAYNAKLARI ANALİZİ")
    print("="*60)

    all_data = load_json('all_emission_factors.json')

    # Kaynak dağılımı
    sources = Counter(record['source'] for record in all_data)

    print(f"\nToplam Kaynak Sayısı: {len(sources)}")
    print(f"\nEn Çok Kullanılan 10 Kaynak:")
    for i, (source, count) in enumerate(sources.most_common(10), 1):
        print(f"  {i}. {source}: {count:,} kayıt ({count/len(all_data)*100:.1f}%)")

def analyze_regions():
    """Bölge dağılımını analiz et"""
    print("\n" + "="*60)
    print("BÖLGE DAĞILIMI ANALİZİ")
    print("="*60)

    all_data = load_json('all_emission_factors.json')

    # Bölge dağılımı
    regions = Counter(record['region'] for record in all_data)

    print(f"\nToplam Bölge Sayısı: {len(regions)}")
    print(f"\nEn Çok Veri Olan 10 Bölge:")
    for i, (region, count) in enumerate(regions.most_common(10), 1):
        # İlk kaydın bölge adını al
        region_name = next(r['region_name'] for r in all_data if r['region'] == region)
        print(f"  {i}. {region} ({region_name}): {count:,} kayıt")

def analyze_categories():
    """Kategori dağılımını analiz et"""
    print("\n" + "="*60)
    print("KATEGORİ DAĞILIMI ANALİZİ")
    print("="*60)

    all_data = load_json('all_emission_factors.json')

    # Kategori dağılımı
    categories = Counter(record['category'] for record in all_data)

    print(f"\nToplam Kategori Sayısı: {len(categories)}")
    print(f"\nEn Çok Veri Olan 15 Kategori:")
    for i, (category, count) in enumerate(categories.most_common(15), 1):
        print(f"  {i}. {category}: {count:,} kayıt")

def analyze_years():
    """Yıl dağılımını analiz et"""
    print("\n" + "="*60)
    print("YIL DAĞILIMI ANALİZİ")
    print("="*60)

    all_data = load_json('all_emission_factors.json')

    # Yıl dağılımı
    years = Counter(record['year'] for record in all_data)

    print(f"\nVeri Yılları:")
    for year, count in sorted(years.items(), reverse=True)[:10]:
        print(f"  {year}: {count:,} kayıt")

def search_by_keyword(keyword):
    """Anahtar kelimeye göre arama yap"""
    print("\n" + "="*60)
    print(f"ARAMA SONUÇLARI: '{keyword}'")
    print("="*60)

    all_data = load_json('all_emission_factors.json')

    # Arama
    results = [
        record for record in all_data
        if keyword.lower() in record['name'].lower() or
           keyword.lower() in record['category'].lower() or
           keyword.lower() in record['description'].lower()
    ]

    print(f"\nBulunan Kayıt: {len(results)}")

    if results:
        print(f"\nİlk 5 Sonuç:")
        for i, record in enumerate(results[:5], 1):
            print(f"\n{i}. {record['name']}")
            print(f"   Kategori: {record['category']}")
            print(f"   Scope: {', '.join(record['scopes'])}")
            print(f"   Kaynak: {record['source']}")
            print(f"   Bölge: {record['region']} ({record['region_name']})")
            print(f"   Birim: {record['unit']}")

def analyze_scope3_transport():
    """Scope 3 ulaşım verilerini analiz et (scope3_data.json gerekir)"""
    print("\n" + "="*60)
    print("SCOPE 3 - ULAŞIM VERİLERİ ANALİZİ")
    print("="*60)

    scope3_file = data_path('scope3_data.json')
    if not scope3_file.exists():
        print("\n[ATLANDI] data/scope3_data.json bulunamadı.")
        print("  Scope 3 özet istatistikleri için summary.json kullanılabilir.")
        print("  Tam Scope 3 analizi için ayrı veri dosyası indirilmelidir.")
        return

    scope3_data = load_json('scope3_data.json')

    # Ulaşım ile ilgili kayıtlar
    transport_keywords = ['transport', 'shipping', 'freight', 'vehicle', 'flight', 'aviation']

    transport_data = [
        record for record in scope3_data
        if any(keyword in record['category'].lower() or keyword in record['name'].lower()
               for keyword in transport_keywords)
    ]

    print(f"\nToplam Scope 3 Kayıt: {len(scope3_data):,}")
    if scope3_data:
        print(f"Ulaşım İle İlgili Kayıt: {len(transport_data):,} ({len(transport_data)/len(scope3_data)*100:.1f}%)")

    # Alt scope dağılımı
    transport_scopes = Counter()
    for record in transport_data:
        for scope in record['scopes']:
            transport_scopes[scope] += 1

    print(f"\nUlaşım Verilerinin Scope Dağılımı:")
    for scope, count in sorted(transport_scopes.items()):
        print(f"  {scope}: {count:,} kayıt")

def main():
    """Ana fonksiyon"""
    print("\nCLIMATIQ EMISSION FACTORS - VERI ANALIZI\n")
    print(f"Veri klasörü: {DATA_DIR}\n")

    if not DATA_DIR.exists():
        print(f"[HATA] data/ klasörü bulunamadı: {DATA_DIR}")
        return

    # Tüm analizleri çalıştır
    analyze_summary()

    # Aşağıdakiler all_emission_factors.json gerektirir (opsiyonel)
    optional_file = data_path('all_emission_factors.json')
    if optional_file.exists():
        analyze_sources()
        analyze_regions()
        analyze_categories()
        analyze_years()
        search_by_keyword("electricity")
    else:
        print("\n[BILGI] all_emission_factors.json yok — kaynak/bölge/kategori analizleri atlandı.")

    analyze_scope3_transport()

    print("\n" + "="*60)
    print("ANALİZ TAMAMLANDI!")
    print("="*60)

if __name__ == '__main__':
    main()
