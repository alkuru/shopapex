#!/usr/bin/env python3
"""
Поиск недостающих брендов для артикула C15300
"""

import requests
import json

def test_missing_brands():
    """Тестируем разные способы получения недостающих брендов"""
    print("=== Поиск недостающих брендов ===")
    
    # Параметры API
    API_URL = 'https://newapi.auto-sputnik.ru'
    LOGIN = '89219520754'
    PASSWORD = '89219520754'
    
    # Недостающие бренды
    missing_brands = [
        'MANDO', 'MFILTER', 'MTF LIGHT', 'NORDFIL', 'PROFI', 'REDSKIN', 
        'S&K', 'STAL', 'STELLOX', 'TESLA TECHNICS', 'TOPCOVER', 'UFI', 'ZENTPARTS'
    ]
    
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
        print("\n2. Тестируем разные варианты запроса...")
        search_url = f'{API_URL}/products/getproducts'
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        # Тест 1: Запрос только по артикулу без бренда
        print("\n--- Тест 1: Только артикул C15300 ---")
        payload1 = {
            "articul": "c15300",
            "analogi": True,
            "tranzit": True
        }
        
        response1 = requests.post(search_url, json=payload1, headers=headers, timeout=15)
        if response1.status_code == 200:
            data1 = response1.json()
            items1 = data1.get('data', [])
            brands1 = set(item.get("brand", {}).get("name", "") for item in items1 if item.get("brand", {}).get("name", ""))
            print(f"✅ Товаров: {len(items1)}")
            print(f"🏷️ Брендов: {len(brands1)}")
            print(f"🔍 Бренды: {sorted(brands1)}")
            
            # Проверяем недостающие бренды
            found_missing = [brand for brand in missing_brands if brand in brands1]
            print(f"✅ Найдено недостающих брендов: {len(found_missing)}")
            if found_missing:
                print(f"🔍 Найденные: {found_missing}")
        else:
            print(f"❌ Ошибка: {response1.status_code}")
        
        # Тест 2: Запрос для каждого недостающего бренда отдельно
        print("\n--- Тест 2: Поиск по каждому недостающему бренду ---")
        found_brands = []
        
        for brand in missing_brands:
            payload2 = {
                "articul": "c15300",
                "brand": brand,
                "analogi": True,
                "tranzit": True
            }
            
            try:
                response2 = requests.post(search_url, json=payload2, headers=headers, timeout=10)
                if response2.status_code == 200:
                    data2 = response2.json()
                    items2 = data2.get('data', [])
                    if items2:
                        found_brands.append(brand)
                        print(f"✅ {brand}: {len(items2)} товаров")
                    else:
                        print(f"❌ {brand}: нет товаров")
                else:
                    print(f"❌ {brand}: ошибка {response2.status_code}")
            except Exception as e:
                print(f"❌ {brand}: ошибка запроса - {e}")
        
        print(f"\n📊 Итого найдено недостающих брендов: {len(found_brands)}")
        if found_brands:
            print(f"🔍 Найденные: {found_brands}")
        
        # Тест 3: Попробуем другие варианты артикула
        print("\n--- Тест 3: Варианты артикула ---")
        article_variants = ["C15300", "c15300", "C-15300", "C_15300", "15300"]
        
        for variant in article_variants:
            payload3 = {
                "articul": variant,
                "brand": "MANN-FILTER",
                "analogi": True,
                "tranzit": True
            }
            
            try:
                response3 = requests.post(search_url, json=payload3, headers=headers, timeout=10)
                if response3.status_code == 200:
                    data3 = response3.json()
                    items3 = data3.get('data', [])
                    brands3 = set(item.get("brand", {}).get("name", "") for item in items3 if item.get("brand", {}).get("name", ""))
                    missing_found = [brand for brand in missing_brands if brand in brands3]
                    if missing_found:
                        print(f"✅ {variant}: найдено недостающих брендов {len(missing_found)} - {missing_found}")
                    else:
                        print(f"❌ {variant}: недостающих брендов не найдено")
                else:
                    print(f"❌ {variant}: ошибка {response3.status_code}")
            except Exception as e:
                print(f"❌ {variant}: ошибка запроса - {e}")
        
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")

if __name__ == "__main__":
    test_missing_brands() 