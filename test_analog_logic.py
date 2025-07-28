#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_analog_logic():
    """Тестирует новую логику поиска аналогов в базе АвтоКонтинента"""

    print("=== Тест новой логики поиска аналогов ===\n")

    # Тестируем поиск OC47 Knecht/Mahle
    test_cases = [
        {"article": "OC47", "brand": "Knecht/Mahle"},
        {"article": "C15300", "brand": "MANN-FILTER"},
    ]

    for test_case in test_cases:
        print(f"\n--- Тест: {test_case['article']} {test_case['brand']} ---")

        try:
            # Запрос к API
            url = "http://localhost:8001/unified_search"
            params = test_case

            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                debug_info = data.get('debug', {})
                
                print(f"✅ API ответ получен")
                print(f"📊 Статистика:")
                print(f"   - АвтоКонтинент (основной): {debug_info.get('autokontinent_count', 0)}")
                print(f"   - АвтоКонтинент (аналоги): {debug_info.get('autokontinent_analog_count', 0)}")
                print(f"   - АвтоСпутник: {debug_info.get('autosputnik_count', 0)}")
                print(f"   - Всего: {debug_info.get('total_count', 0)}")
                
                analog_articles = debug_info.get('analog_articles_found', [])
                if analog_articles:
                    print(f"🔍 Найденные аналоги для поиска в АвтоКонтиненте:")
                    for analog in analog_articles:
                        print(f"   - {analog[0]} {analog[1]}")
                else:
                    print(f"❌ Аналоги не найдены")

                # Проверяем результаты по источникам
                items = data.get('data', [])
                sources = {}
                for item in items:
                    source = item.get('source', 'unknown')
                    if source not in sources:
                        sources[source] = []
                    sources[source].append(f"{item.get('article')} {item.get('brand')}")

                print(f"\n📋 Результаты по источникам:")
                for source, items_list in sources.items():
                    print(f"   {source}: {len(items_list)} товаров")
                    for item in items_list[:3]:  # Показываем первые 3
                        print(f"     - {item}")
                    if len(items_list) > 3:
                        print(f"     ... и еще {len(items_list) - 3}")

            else:
                print(f"❌ Ошибка API: {response.status_code}")

        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")

if __name__ == "__main__":
    test_analog_logic() 