#!/usr/bin/env python3
"""
Тест артикула 813386900
"""

import requests
import json

def test_article_813386900():
    """Тестируем артикул 813386900"""
    
    # Параметры поиска
    article = "813386900"
    brand = "REINZ"
    
    print(f"=== ТЕСТ АРТИКУЛА {article} ===")
    print(f"Бренд: {brand}")
    
    # 1. Тест FastAPI unified_search
    print("\n1. Тест FastAPI unified_search:")
    try:
        fastapi_url = "http://fastapi:8001/unified_search"
        params = {"article": article, "brand": brand}
        
        response = requests.get(fastapi_url, params=params, timeout=10)
        data = response.json()
        
        print(f"Статус: {response.status_code}")
        print(f"Результатов: {len(data.get('data', []))}")
        
        if data.get('data'):
            print("Найденные товары (первые 10):")
            for i, item in enumerate(data['data'][:10], 1):
                print(f"  {i}. {item.get('brand')} {item.get('article')} - {item.get('source')}")
                print(f"     Цена: {item.get('price')}, Наличие: {item.get('availability')}")
                print(f"     Склад: {item.get('warehouse')}, Срок: {item.get('delivery_time')}")
        else:
            print("Товары не найдены")
            
        print(f"Debug: {data.get('debug', {})}")
        
    except Exception as e:
        print(f"Ошибка FastAPI: {e}")
    
    # 2. Тест Django web search
    print("\n2. Тест Django web search:")
    try:
        web_url = "http://web:8000/catalog/search/"
        params = {"article": article, "brand": brand}
        
        response = requests.get(web_url, params=params, timeout=10)
        
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем товары в таблице
            product_rows = soup.find_all('tr')
            product_items = []
            for row in product_rows:
                cells = row.find_all('td')
                if len(cells) >= 8:
                    first_cell = cells[0].get_text(strip=True)
                    if first_cell and first_cell != '-':
                        product_items.append(row)
            
            print(f"Найдено товаров в HTML: {len(product_items)}")
            
            # Показываем первые товары
            print("Первые товары в результатах:")
            for i, item in enumerate(product_items[:5], 1):
                cells = item.find_all('td')
                if len(cells) >= 8:
                    article_cell = cells[0].get_text(strip=True)
                    brand_cell = cells[1].get_text(strip=True)
                    name_cell = cells[2].get_text(strip=True)
                    print(f"  {i}. {article_cell} | {brand_cell} | {name_cell}")
            
    except Exception as e:
        print(f"Ошибка Django: {e}")

if __name__ == "__main__":
    test_article_813386900() 