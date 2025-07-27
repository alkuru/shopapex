#!/usr/bin/env python3
"""
Тест изменений для артикула C15300
Проверяем, что теперь показываются и AutoKontinent и AutoSputnik товары
"""

import requests
from bs4 import BeautifulSoup
import json

def test_c15300_search():
    """Тестируем поиск артикула C15300"""
    print("=== Тест артикула C15300 ===")
    
    # URL поиска (внутри Docker контейнера)
    search_url = "http://web:8000/catalog/search/"
    params = {"q": "C15300"}
    
    try:
        print(f"Делаем запрос: {search_url}?q=C15300")
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        
        print(f"Статус ответа: {response.status_code}")
        
        # Парсим HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем все строки товаров
        product_rows = soup.select('.product-row, .product-item, tr[data-article]')
        print(f"Найдено строк товаров: {len(product_rows)}")
        
        # Ищем кнопку "Еще предложения"
        more_offers_buttons = soup.find_all(string=lambda text: text and 'Еще предложения' in text)
        print(f"Найдено кнопок 'Еще предложения': {len(more_offers_buttons)}")
        
        # Выводим текст страницы для анализа
        print("\n=== Первые 2000 символов HTML ===")
        print(response.text[:2000])
        
        # Ищем все упоминания C15300
        c15300_mentions = response.text.count('C15300')
        print(f"\nУпоминаний C15300 на странице: {c15300_mentions}")
        
        # Ищем упоминания AutoKontinent и AutoSputnik
        autokontinent_mentions = response.text.count('ЦС АК') + response.text.count('ЦС АКМСК')
        autosputnik_mentions = response.text.count('AutoSputnik')
        
        print(f"Упоминаний AutoKontinent (ЦС АК/ЦС АКМСК): {autokontinent_mentions}")
        print(f"Упоминаний AutoSputnik: {autosputnik_mentions}")
        
        return True
        
    except Exception as e:
        print(f"Ошибка при тестировании: {e}")
        return False

def test_fastapi_unified_search():
    """Тестируем FastAPI unified_search напрямую"""
    print("\n=== Тест FastAPI unified_search ===")
    
    try:
        # Тестируем unified_search (внутри Docker контейнера)
        fastapi_url = "http://fastapi:8001/unified_search"
        params = {"article": "C15300"}
        
        print(f"Запрос к FastAPI: {fastapi_url}")
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
            for i, item in enumerate(results[:10]):
                print(f"  {i+1}. {item.get('article')} | {item.get('brand')} | {item.get('source')} | {item.get('price')}")
        
        return True
        
    except Exception as e:
        print(f"Ошибка FastAPI теста: {e}")
        return False

if __name__ == "__main__":
    print("Начинаем тестирование изменений...")
    
    # Тест 1: Django web search
    web_success = test_c15300_search()
    
    # Тест 2: FastAPI unified_search
    fastapi_success = test_fastapi_unified_search()
    
    print(f"\n=== Результаты тестирования ===")
    print(f"Web search: {'УСПЕХ' if web_success else 'ОШИБКА'}")
    print(f"FastAPI search: {'УСПЕХ' if fastapi_success else 'ОШИБКА'}")
    
    if web_success and fastapi_success:
        print("Все тесты прошли успешно!")
    else:
        print("Есть проблемы, нужно проверить логи!") 