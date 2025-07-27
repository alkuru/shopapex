#!/usr/bin/env python3
"""
Проверка бренда Victor Reinz
"""

import json

def check_victor_reinz():
    with open('brands_data/brand_analysis_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    matches = data['potential_matches']
    
    print("=== ПОИСК VICTOR REINZ ===")
    
    # Ищем Victor Reinz
    victor_matches = []
    for m in matches:
        ak_brand = m['autokontinent'].lower()
        if 'victor' in ak_brand or 'reinz' in ak_brand:
            victor_matches.append(m)
    
    print(f"Найдено {len(victor_matches)} совпадений:")
    for m in victor_matches:
        print(f"  {m['autokontinent']} → {m['autosputnik']}")
    
    # Ищем Reinz в AutoSputnik
    print("\n=== ПОИСК REINZ В AUTOSPUTNIK ===")
    with open('brands_data/response_1753575298222.json', 'r', encoding='utf-8') as f:
        sp_data = json.load(f)
    
    reinz_brands = []
    for item in sp_data.get('data', []):
        brand_name = item.get('name', '').lower()
        if 'reinz' in brand_name:
            reinz_brands.append(item['name'])
    
    print(f"Найдено {len(reinz_brands)} брендов с 'Reinz':")
    for brand in reinz_brands:
        print(f"  {brand}")

if __name__ == "__main__":
    check_victor_reinz() 