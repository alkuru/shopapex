#!/usr/bin/env python3
"""
Простой тест - проверяем, что теперь показываются товары из обоих источников
"""

import requests
import json

def test_analog_search():
    print("=== Тест поиска аналогов ===\n")
    
    # Тестируем OC47 Knecht/Mahle
    url = "http://localhost:8001/unified_search"
    params = {"article": "OC47", "brand": "Knecht/Mahle"}
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            debug = data.get('debug', {})
            
            print(f"✅ API ответ получен")
            print(f"📊 Статистика:")
            print(f"   - АвтоКонтинент (основной): {debug.get('autokontinent_count', 0)}")
            print(f"   - АвтоКонтинент (аналоги): {debug.get('autokontinent_analog_count', 0)}")
            print(f"   - АвтоСпутник: {debug.get('autosputnik_count', 0)}")
            print(f"   - Всего: {debug.get('total_count', 0)}")
            
            analog_articles = debug.get('analog_articles_found', [])
            print(f"\n🔍 Найденные аналоги для поиска в АвтоКонтиненте:")
            for analog in analog_articles:
                print(f"   - {analog[0]} {analog[1]}")
            
            # Ищем C33010 в результатах
            items = data.get('data', [])
            c33010_found = False
            for item in items:
                if item.get('article') == 'C33010':
                    c33010_found = True
                    print(f"\n✅ НАЙДЕН C33010!")
                    print(f"   Бренд: {item.get('brand')}")
                    print(f"   Источник: {item.get('source')}")
                    print(f"   Склад: {item.get('warehouse')}")
                    print(f"   Цена: {item.get('price')}")
                    break
            
            if not c33010_found:
                print(f"\n❌ C33010 НЕ найден в результатах")
                
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_analog_search()
