#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_warehouse_display():
    """Тестирует отображение складов в поиске"""
    
    # Тестовые запросы
    test_cases = [
        {"article": "C15300", "brand": "MANN-FILTER"},
        {"article": "W7195", "brand": "MANN-FILTER"},
        {"article": "OC47", "brand": "Knecht/Mahle"},
    ]
    
    for test_case in test_cases:
        print(f"\n=== Тест: {test_case['article']} {test_case['brand']} ===")
        
        try:
            # Запрос к API
            url = "http://localhost:8001/unified_search"
            params = test_case
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('data', [])
                
                print(f"Найдено товаров: {len(items)}")
                
                # Группируем по источнику
                autokontinent_items = [item for item in items if item.get('source') == 'autokontinent_db']
                autosputnik_items = [item for item in items if item.get('source') != 'autokontinent_db']
                
                print(f"\nАвтоКонтинент товары ({len(autokontinent_items)}):")
                for item in autokontinent_items[:3]:  # Показываем первые 3
                    print(f"  - {item.get('article')} | {item.get('brand')} | "
                          f"Склад: {item.get('warehouse')} | Наличие: {item.get('availability')}")
                
                print(f"\nАвтоСпутник товары ({len(autosputnik_items)}):")
                for item in autosputnik_items[:3]:  # Показываем первые 3
                    print(f"  - {item.get('article')} | {item.get('brand')} | "
                          f"Склад: {item.get('warehouse')} | Наличие: {item.get('availability')}")
                
            else:
                print(f"Ошибка API: {response.status_code}")
                
        except Exception as e:
            print(f"Ошибка запроса: {e}")

if __name__ == "__main__":
    test_warehouse_display() 