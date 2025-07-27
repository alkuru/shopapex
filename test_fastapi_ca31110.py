#!/usr/bin/env python3
"""
Тестирование FastAPI для артикула CA31110
"""
import requests
import json

def test_fastapi_ca31110():
    """
    Тестирует FastAPI для артикула CA31110
    """
    print("=== ТЕСТИРОВАНИЕ FASTAPI ДЛЯ CA31110 ===\n")
    
    # Тестируем разные варианты поиска
    test_cases = [
        ('CA31110', 'Sakura'),
        ('CA31110', ''),
        ('CA31110', 'SAKURA'),
    ]
    
    for article, brand in test_cases:
        print(f"🔍 Тест: article='{article}', brand='{brand}'")
        
        try:
            url = "http://fastapi:8001/unified_search"
            params = {
                'article': article,
                'brand': brand
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   Статус: {response.status_code}")
                print(f"   Тип данных: {type(data)}")
                
                # Проверяем структуру данных
                if isinstance(data, dict):
                    print(f"   Ключи: {list(data.keys())}")
                    if 'items' in data:
                        items = data['items']
                        print(f"   items тип: {type(items)}")
                        print(f"   items длина: {len(items) if isinstance(items, list) else 'не список'}")
                    if 'error' in data:
                        print(f"   error: {data['error']}")
                elif isinstance(data, list):
                    print(f"   Всего товаров: {len(data)}")
                    if data:
                        print(f"   Первый элемент: {type(data[0])}")
                        if isinstance(data[0], dict):
                            print(f"   Ключи первого элемента: {list(data[0].keys())}")
                
                # Анализируем источники
                autokontinent_count = 0
                autosputnik_count = 0
                
                items = []
                if isinstance(data, dict) and 'data' in data:
                    items = data['data']
                elif isinstance(data, list):
                    items = data
                
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            source = item.get('source', 'unknown')
                            if source == 'autokontinent_db':
                                autokontinent_count += 1
                            elif source == 'autosputnik':
                                autosputnik_count += 1
                
                print(f"   AutoKontinent товаров: {autokontinent_count}")
                print(f"   AutoSputnik товаров: {autosputnik_count}")
                
                # Показываем первые несколько товаров
                if isinstance(items, list) and items:
                    print(f"   Первые товары:")
                    for i, item in enumerate(items[:3], 1):
                        if isinstance(item, dict):
                            print(f"     {i}. {item.get('article')} {item.get('brand')} - {item.get('source')} - {item.get('warehouse')}")
                        else:
                            print(f"     {i}. {item} (не словарь)")
                
                print()
                
            else:
                print(f"   ❌ Ошибка HTTP: {response.status_code}")
                print(f"   Ответ: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Ошибка запроса: {e}")
        
        print("-" * 50)

def test_autosputnik_only():
    """
    Тестирует только AutoSputnik API
    """
    print("\n=== ТЕСТИРОВАНИЕ ТОЛЬКО AUTOSPUTNIK ===\n")
    
    try:
        url = "http://fastapi:8001/sputnik/search"
        payload = {
            "articul": "CA31110",
            "brand": "Sakura",
            "analogi": True,
            "tranzit": True
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if not data.get('error') and data.get('data'):
                items = data['data']
                print(f"✅ AutoSputnik вернул {len(items)} товаров")
                
                for i, item in enumerate(items[:5], 1):
                    print(f"   {i}. {item.get('articul')} {item.get('brand', {}).get('name')} - {item.get('price_name')}")
            else:
                print(f"❌ AutoSputnik ошибка: {data.get('error')}")
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

if __name__ == '__main__':
    test_fastapi_ca31110()
    test_autosputnik_only() 