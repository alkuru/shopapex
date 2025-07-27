#!/usr/bin/env python3
"""
Тест для артикула 12-33876-01
"""

import requests
import json

def test_article_1233876():
    print("=== ТЕСТ АРТИКУЛА 12-33876-01 ===")
    
    article = "12-33876-01"
    
    print(f"Тестируем артикул: {article}")
    
    # 1. Проверяем FastAPI unified_search
    print("\n1. FastAPI unified_search:")
    try:
        response = requests.get("http://fastapi:8001/unified_search", params={"article": article}, timeout=10)
        data = response.json()
        
        if data.get('status') == 'ok':
            results = data.get('data', [])
            print(f"   Найдено товаров: {len(results)}")
            
            ak_count = sum(1 for item in results if item.get('source') == 'autokontinent_db')
            sp_count = sum(1 for item in results if item.get('source') == 'autosputnik')
            
            print(f"   AutoKontinent: {ak_count}")
            print(f"   AutoSputnik: {sp_count}")
            
            # Показываем все товары
            for i, item in enumerate(results):
                print(f"   {i+1}. {item['article']} | {item['brand']} | {item['source']} | {item['price']} | {item.get('warehouse', 'N/A')}")
        else:
            print(f"   Ошибка: {data.get('message')}")
            
    except Exception as e:
        print(f"   Ошибка FastAPI: {e}")
    
    # 2. Проверяем Django web search
    print("\n2. Django web search:")
    try:
        response = requests.get("http://web:8000/catalog/search/", params={"q": article}, timeout=10)
        print(f"   Статус: {response.status_code}")
        
        # Считаем упоминания
        ak_mentions = response.text.count('ЦС АК') + response.text.count('ЦС АКМСК')
        sp_mentions = response.text.count('AutoSputnik')
        article_mentions = response.text.count(article)
        
        print(f"   Упоминаний {article}: {article_mentions}")
        print(f"   Упоминаний AutoKontinent: {ak_mentions}")
        print(f"   Упоминаний AutoSputnik: {sp_mentions}")
        
    except Exception as e:
        print(f"   Ошибка Django: {e}")
    
    # 3. Прямой тест AutoSputnik API
    print("\n3. Прямой тест AutoSputnik API:")
    try:
        # Получаем токен
        token_url = "https://newapi.auto-sputnik.ru/users/login"
        token_data = {"login": "89219520754", "password": "89219520754"}
        
        token_resp = requests.post(token_url, json=token_data, timeout=10)
        token_resp.raise_for_status()
        
        token = token_resp.json().get('token')
        if not token:
            print("   ❌ Не удалось получить токен")
            return
        
        # Получаем список брендов
        brands_url = f"https://newapi.auto-sputnik.ru/products/getbrands?articul={article}"
        headers = {"Authorization": f"Bearer {token}"}
        
        brands_resp = requests.get(brands_url, headers=headers, timeout=10)
        brands_resp.raise_for_status()
        
        brands_data = brands_resp.json()
        print(f"   Ответ API брендов: {json.dumps(brands_data, indent=2, ensure_ascii=False)}")
        
        if brands_data.get("error"):
            print(f"   ❌ Ошибка API: {brands_data.get('error')}")
            return
        
        brands = brands_data.get("data", [])
        print(f"   Найдено брендов: {len(brands)}")
        
        # Тестируем поиск для каждого бренда
        search_url = "https://newapi.auto-sputnik.ru/products/getproducts"
        all_results = []
        
        for brand in brands:
            brand_name = brand.get("name", "")
            print(f"   Тестируем бренд: {brand_name}")
            
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
                if not data.get("error") and data.get("data"):
                    results = data.get("data", [])
                    print(f"     Найдено товаров: {len(results)}")
                    all_results.extend(results)
                else:
                    print(f"     Ошибка или нет данных: {data.get('error')}")
                    
            except Exception as e:
                print(f"     Ошибка запроса: {e}")
        
        print(f"   Всего найдено товаров в AutoSputnik: {len(all_results)}")
        
        if all_results:
            print("   ✅ Товары найдены в AutoSputnik!")
            for i, item in enumerate(all_results[:5]):
                print(f"     {i+1}. {item.get('articul')} | {item.get('brand', {}).get('name')} | {item.get('price')} | {item.get('price_name')}")
        else:
            print("   ❌ Товары не найдены в AutoSputnik")
            
    except Exception as e:
        print(f"   ❌ Общая ошибка AutoSputnik API: {e}")
    
    print("\n=== РЕЗУЛЬТАТ ===")
    if sp_count > 0:
        print("✅ УСПЕХ: Товары AutoSputnik показываются!")
    else:
        print("❌ ПРОБЛЕМА: Товары AutoSputnik не показываются")

if __name__ == "__main__":
    test_article_1233876() 