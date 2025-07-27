#!/usr/bin/env python3
"""
Прямой тест AutoSputnik API
"""

import requests
import json

def test_sputnik_direct():
    print("=== ПРЯМОЙ ТЕСТ AUTOSPUTNIK API ===")
    
    # Тестируем артикул CA31110
    article = "CA31110"
    
    print(f"Тестируем артикул: {article}")
    
    try:
        # 1. Получаем токен
        print("\n1. Получение токена...")
        token_url = "https://newapi.auto-sputnik.ru/users/login"
        token_data = {"login": "89219520754", "password": "89219520754"}
        
        token_resp = requests.post(token_url, json=token_data, timeout=10)
        token_resp.raise_for_status()
        
        token = token_resp.json().get('token')
        if not token:
            print("❌ Не удалось получить токен")
            return
        
        print("✅ Токен получен")
        
        # 2. Получаем список брендов для артикула
        print("\n2. Получение списка брендов...")
        brands_url = f"https://newapi.auto-sputnik.ru/products/getbrands?articul={article}"
        headers = {"Authorization": f"Bearer {token}"}
        
        brands_resp = requests.get(brands_url, headers=headers, timeout=10)
        brands_resp.raise_for_status()
        
        brands_data = brands_resp.json()
        print(f"Ответ API: {json.dumps(brands_data, indent=2, ensure_ascii=False)}")
        
        if brands_data.get("error"):
            print(f"❌ Ошибка API: {brands_data.get('error')}")
            return
        
        brands = brands_data.get("data", [])
        print(f"Найдено брендов: {len(brands)}")
        
        for brand in brands:
            print(f"  - {brand.get('name')}")
        
        # 3. Тестируем поиск для каждого бренда
        print("\n3. Поиск товаров по брендам...")
        search_url = "https://newapi.auto-sputnik.ru/products/getproducts"
        
        all_results = []
        
        for brand in brands[:3]:  # Тестируем первые 3 бренда
            brand_name = brand.get("name", "")
            print(f"\n   Тестируем бренд: {brand_name}")
            
            payload = {
                "articul": article,
                "brand": brand_name,
                "analogi": True,
                "tranzit": True
            }
            
            try:
                response = requests.post(search_url, json=payload, headers=headers, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                print(f"   Статус: {response.status_code}")
                print(f"   Ответ: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
                
                if not data.get("error") and data.get("data"):
                    results = data.get("data", [])
                    print(f"   Найдено товаров: {len(results)}")
                    all_results.extend(results)
                else:
                    print(f"   Ошибка или нет данных: {data.get('error')}")
                    
            except Exception as e:
                print(f"   Ошибка запроса: {e}")
        
        print(f"\n=== ИТОГО ===")
        print(f"Всего найдено товаров в AutoSputnik: {len(all_results)}")
        
        if all_results:
            print("✅ Товары найдены в AutoSputnik!")
            for i, item in enumerate(all_results[:5]):
                print(f"  {i+1}. {item.get('articul')} | {item.get('brand', {}).get('name')} | {item.get('price')}")
        else:
            print("❌ Товары не найдены в AutoSputnik")
            
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")

if __name__ == "__main__":
    test_sputnik_direct() 