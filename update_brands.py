#!/usr/bin/env python3
"""
Автоматическое обновление брендов в базе данных AutoKontinent
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

def load_brand_mapping():
    """Загружаем сопоставление брендов"""
    print("Загружаем сопоставление брендов...")
    
    with open('brands_data/brand_analysis_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Создаем словарь сопоставления
    brand_mapping = {}
    
    # Точные совпадения
    for match in data['exact_matches']:
        brand_mapping[match['autokontinent']] = match['autosputnik']
    
    # Частичные совпадения (ручная проверка)
    partial_matches = [m for m in data['potential_matches'] if m['type'] == 'partial']
    
    # Добавляем известные сопоставления
    manual_mappings = {
        'Victor Reinz': 'REINZ',
        'MANN-FILTER': 'Mann',
        'Behr-Hella': 'BEHR',  # или 'HELLA'
        'Autopartner': 'Autopa',  # или другой вариант
    }
    
    brand_mapping.update(manual_mappings)
    
    print(f"Загружено {len(brand_mapping)} сопоставлений брендов")
    return brand_mapping

def update_brands_in_database(brand_mapping):
    """Обновляем бренды в базе данных"""
    print("Обновляем бренды в базе данных...")
    
    updated_count = 0
    total_count = 0
    
    # Получаем все товары
    products = AutoKontinentProduct.objects.all()
    
    for product in products:
        total_count += 1
        old_brand = product.brand
        
        # Проверяем, есть ли сопоставление
        if old_brand in brand_mapping:
            new_brand = brand_mapping[old_brand]
            if old_brand != new_brand:
                product.brand = new_brand
                product.save()
                updated_count += 1
                print(f"Обновлен: {old_brand} → {new_brand}")
    
    print(f"\n=== РЕЗУЛЬТАТЫ ОБНОВЛЕНИЯ ===")
    print(f"Всего товаров: {total_count}")
    print(f"Обновлено брендов: {updated_count}")
    
    return updated_count

def show_brand_statistics():
    """Показываем статистику брендов после обновления"""
    print("\n=== СТАТИСТИКА БРЕНДОВ ПОСЛЕ ОБНОВЛЕНИЯ ===")
    
    # Получаем топ-20 брендов
    from django.db.models import Count
    top_brands = AutoKontinentProduct.objects.values('brand').annotate(
        count=Count('id')
    ).order_by('-count')[:20]
    
    print("Топ-20 брендов по количеству товаров:")
    for i, brand in enumerate(top_brands, 1):
        print(f"{i:2d}. {brand['brand']} - {brand['count']} товаров")

def main():
    """Основная функция"""
    print("=== ОБНОВЛЕНИЕ БРЕНДОВ AUTOKONTINENT ===")
    
    # Загружаем сопоставление
    brand_mapping = load_brand_mapping()
    
    # Показываем сопоставления
    print("\n=== СОПОСТАВЛЕНИЯ БРЕНДОВ ===")
    for old_brand, new_brand in brand_mapping.items():
        print(f"{old_brand} → {new_brand}")
    
    # Спрашиваем подтверждение
    response = input("\nПродолжить обновление? (y/n): ")
    if response.lower() != 'y':
        print("Обновление отменено")
        return
    
    # Обновляем базу данных
    updated_count = update_brands_in_database(brand_mapping)
    
    # Показываем статистику
    show_brand_statistics()
    
    print(f"\n✅ Обновление завершено! Обновлено {updated_count} товаров.")

if __name__ == "__main__":
    main() 