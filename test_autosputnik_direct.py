#!/usr/bin/env python3
"""
Прямой тест AutoSputnik API для артикула C15300
"""

import requests
import json

def test_autosputnik_api():
    """Тестируем AutoSputnik API напрямую"""
    print("=== Прямой тест AutoSputnik API ===")
    
    # Параметры API
    API_URL = 'https://newapi.auto-sputnik.ru'
    LOGIN = '89219520754'
    PASSWORD = '89219520754'
    
    try:
        # Получаем токен
        print("1. Получение токена...")
        token_url = f'{API_URL}/users/login'
        token_data = {'login': LOGIN, 'password': PASSWORD}
        token_resp = requests.post(token_url, json=token_data, timeout=10)
        token_resp.raise_for_status()
        token = token_resp.json().get('token')
        if not token:
            print("❌ Не удалось получить токен")
            return
        print("✅ Токен получен")
        
        # Делаем запрос к API
        print("\n2. Запрос к API...")
        search_url = f'{API_URL}/products/getproducts'
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        # Тестируем разные варианты запроса
        test_cases = [
            {
                "name": "C15300 + MANN-FILTER + analogi=true",
                "payload": {
                    "articul": "c15300",
                    "brand": "MANN-FILTER",
                    "analogi": True,
                    "tranzit": True
                }
            },
            {
                "name": "C15300 + MANN-FILTER + analogi=false",
                "payload": {
                    "articul": "c15300",
                    "brand": "MANN-FILTER",
                    "analogi": False,
                    "tranzit": True
                }
            },
            {
                "name": "C15300 + MANN-FILTER + tranzit=false",
                "payload": {
                    "articul": "c15300",
                    "brand": "MANN-FILTER",
                    "analogi": True,
                    "tranzit": False
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Тест {i}: {test_case['name']} ---")
            
            response = requests.post(
                search_url,
                json=test_case['payload'],
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('data', [])
                print(f"✅ Статус: {response.status_code}")
                print(f"📊 Товаров: {len(items)}")
                
                # Проверяем пагинацию
                if 'hasNextPage' in data:
                    print(f"📄 Пагинация:")
                    print(f"   - hasNextPage: {data.get('hasNextPage')}")
                    print(f"   - totalCount: {data.get('totalCount')}")
                    print(f"   - pageSize: {data.get('pageSize')}")
                    print(f"   - currentPage: {data.get('currentPage')}")
                
                # Извлекаем уникальные бренды
                brands = set()
                for item in items:
                    brand_name = item.get("brand", {}).get("name", "")
                    if brand_name:
                        brands.add(brand_name)
                
                print(f"🏷️ Уникальных брендов: {len(brands)}")
                print(f"🔍 Бренды: {sorted(brands)}")
                
                # Выводим первые 5 товаров
                print("📋 Первые 5 товаров:")
                for j, item in enumerate(items[:5]):
                    print(f"   {j+1}. {item.get('articul')} | {item.get('brand', {}).get('name')} | {item.get('price_name')}")
                
            else:
                print(f"❌ Ошибка: {response.status_code}")
                print(f"Ответ: {response.text}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_autosputnik_api() 