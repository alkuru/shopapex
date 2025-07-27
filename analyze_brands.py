#!/usr/bin/env python3
"""
Анализ брендов AutoSputnik и создание системы сопоставления с AutoKontinent
"""

import json
import os
import sys
import django
from collections import defaultdict

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import AutoKontinentProduct

def load_autosputnik_brands():
    """Загружаем бренды AutoSputnik из JSON файла"""
    print("Загружаем бренды AutoSputnik...")
    
    with open('brands_data/response_1753575298222.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    brands = []
    for item in data.get('data', []):
        brand_name = item.get('name', '').strip()
        if brand_name:
            brands.append(brand_name)
    
    print(f"Загружено {len(brands)} брендов AutoSputnik")
    return brands

def get_autokontinent_brands():
    """Получаем уникальные бренды из базы AutoKontinent"""
    print("Получаем бренды AutoKontinent из базы...")
    
    brands = AutoKontinentProduct.objects.values_list('brand', flat=True).distinct()
    brands = [brand.strip() for brand in brands if brand and brand.strip()]
    
    print(f"Найдено {len(brands)} уникальных брендов AutoKontinent")
    return brands

def find_brand_matches(ak_brands, sp_brands):
    """Ищем возможные совпадения брендов"""
    print("Ищем возможные совпадения брендов...")
    
    matches = []
    potential_matches = []
    
    # Создаем словарь брендов AutoSputnik для быстрого поиска
    sp_brands_dict = {brand.lower(): brand for brand in sp_brands}
    
    for ak_brand in ak_brands:
        ak_lower = ak_brand.lower()
        
        # Точное совпадение
        if ak_lower in sp_brands_dict:
            matches.append({
                'autokontinent': ak_brand,
                'autosputnik': sp_brands_dict[ak_lower],
                'type': 'exact'
            })
            continue
        
        # Частичные совпадения
        found_partial = False
        for sp_brand in sp_brands:
            sp_lower = sp_brand.lower()
            
            # Один бренд содержит другой
            if ak_lower in sp_lower or sp_lower in ak_lower:
                if len(ak_lower) > 3 and len(sp_lower) > 3:  # Исключаем слишком короткие
                    potential_matches.append({
                        'autokontinent': ak_brand,
                        'autosputnik': sp_brand,
                        'type': 'partial'
                    })
                    found_partial = True
        
        # Если не нашли совпадений
        if not found_partial:
            potential_matches.append({
                'autokontinent': ak_brand,
                'autosputnik': 'НЕ НАЙДЕН',
                'type': 'not_found'
            })
    
    return matches, potential_matches

def analyze_brands():
    """Основная функция анализа"""
    print("=== АНАЛИЗ БРЕНДОВ ===")
    
    # Загружаем бренды
    sp_brands = load_autosputnik_brands()
    ak_brands = get_autokontinent_brands()
    
    # Ищем совпадения
    exact_matches, potential_matches = find_brand_matches(ak_brands, sp_brands)
    
    # Выводим результаты
    print(f"\n=== РЕЗУЛЬТАТЫ ===")
    print(f"Точных совпадений: {len(exact_matches)}")
    print(f"Частичных совпадений: {len([m for m in potential_matches if m['type'] == 'partial'])}")
    print(f"Не найдено: {len([m for m in potential_matches if m['type'] == 'not_found'])}")
    
    # Показываем примеры точных совпадений
    print(f"\n=== ТОЧНЫЕ СОВПАДЕНИЯ (первые 10) ===")
    for i, match in enumerate(exact_matches[:10]):
        print(f"{i+1}. {match['autokontinent']} → {match['autosputnik']}")
    
    # Показываем примеры частичных совпадений
    partial_matches = [m for m in potential_matches if m['type'] == 'partial']
    print(f"\n=== ЧАСТИЧНЫЕ СОВПАДЕНИЯ (первые 10) ===")
    for i, match in enumerate(partial_matches[:10]):
        print(f"{i+1}. {match['autokontinent']} → {match['autosputnik']}")
    
    # Показываем примеры не найденных
    not_found = [m for m in potential_matches if m['type'] == 'not_found']
    print(f"\n=== НЕ НАЙДЕНЫ (первые 10) ===")
    for i, match in enumerate(not_found[:10]):
        print(f"{i+1}. {match['autokontinent']}")
    
    # Сохраняем результаты в файл
    results = {
        'exact_matches': exact_matches,
        'potential_matches': potential_matches,
        'summary': {
            'total_autokontinent': len(ak_brands),
            'total_autosputnik': len(sp_brands),
            'exact_matches_count': len(exact_matches),
            'partial_matches_count': len([m for m in potential_matches if m['type'] == 'partial']),
            'not_found_count': len([m for m in potential_matches if m['type'] == 'not_found'])
        }
    }
    
    with open('brands_data/brand_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nРезультаты сохранены в brands_data/brand_analysis_results.json")
    
    return results

if __name__ == "__main__":
    analyze_brands() 