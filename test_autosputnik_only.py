#!/usr/bin/env python3
"""
Тест для артикула, который есть только в AutoSputnik
"""

import requests
import json

def test_autosputnik_only():
    """Тестируем артикул, который есть только в AutoSputnik"""
    print("=== Тест артикула только в AutoSputnik ===")
    
    # Попробуем несколько артикулов, которые могут быть только в AutoSputnik
    test_articles = ["PH5883", "FRAM", "MANN", "BOSCH", "MAHLE"]
    
    for article in test_articles:
        print(f"\n--- Тестируем артикул: {article} ---")
        
        try:
            # Тестируем FastAPI unified_search
            fastapi_url = "http://fastapi:8001/unified_search"
            params = {"article": article}
            
            response = requests.get(fastapi_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            print(f"Статус FastAPI: {data.get('status')}")
            
            if data.get('status') == 'ok':
                results = data.get('data', [])
                print(f"Найдено товаров: {len(results)}")
                
                autokontinent_count = sum(1 for item in results if item.get('source') == 'autokontinent_db')
                autosputnik_count = sum(1 for item in results if item.get('source') == 'autosputnik')
                
                print(f"AutoKontinent товаров: {autokontinent_count}")
                print(f"AutoSputnik товаров: {autosputnik_count}")
                
                # Выводим первые несколько товаров
                for i, item in enumerate(results[:5]):
                    print(f"  {i+1}. {item.get('article')} | {item.get('brand')} | {item.get('source')} | {item.get('price')}")
                
                # Если нашли товары AutoSputnik, остановимся
                if autosputnik_count > 0:
                    print(f"✅ Нашли артикул с товарами AutoSputnik: {article}")
                    return article
                    
        except Exception as e:
            print(f"Ошибка теста для {article}: {e}")
    
    print("❌ Не нашли артикул с товарами AutoSputnik")
    return None

def test_specific_article(article):
    """Тестируем конкретный артикул"""
    print(f"\n=== Детальный тест артикула: {article} ===")
    
    try:
        # Тестируем FastAPI unified_search
        fastapi_url = "http://fastapi:8001/unified_search"
        params = {"article": article}
        
        response = requests.get(fastapi_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"Статус FastAPI: {data.get('status')}")
        
        if data.get('status') == 'ok':
            results = data.get('data', [])
            print(f"Найдено товаров: {len(results)}")
            
            autokontinent_count = sum(1 for item in results if item.get('source') == 'autokontinent_db')
            autosputnik_count = sum(1 for item in results if item.get('source') == 'autosputnik')
            
            print(f"AutoKontinent товаров: {autokontinent_count}")
            print(f"AutoSputnik товаров: {autosputnik_count}")
            
            # Выводим все товары
            for i, item in enumerate(results):
                print(f"  {i+1}. {item.get('article')} | {item.get('brand')} | {item.get('source')} | {item.get('price')} | {item.get('warehouse')}")
            
            # Тестируем Django web search
            print(f"\n--- Тест Django web search для {article} ---")
            search_url = "http://web:8000/catalog/search/"
            params = {"q": article}
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            print(f"Статус Django: {response.status_code}")
            
            # Ищем упоминания артикула на странице
            article_mentions = response.text.count(article)
            autokontinent_mentions = response.text.count('ЦС АК') + response.text.count('ЦС АКМСК')
            autosputnik_mentions = response.text.count('AutoSputnik')
            
            print(f"Упоминаний {article} на странице: {article_mentions}")
            print(f"Упоминаний AutoKontinent: {autokontinent_mentions}")
            print(f"Упоминаний AutoSputnik: {autosputnik_mentions}")
            
    except Exception as e:
        print(f"Ошибка детального теста: {e}")

if __name__ == "__main__":
    print("Начинаем поиск артикула с товарами AutoSputnik...")
    
    # Ищем артикул с товарами AutoSputnik
    found_article = test_autosputnik_only()
    
    if found_article:
        # Делаем детальный тест найденного артикула
        test_specific_article(found_article)
    else:
        print("Не удалось найти артикул с товарами AutoSputnik") 