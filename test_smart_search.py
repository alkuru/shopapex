#!/usr/bin/env python3
"""
Тест умного поиска артикулов
"""

import requests
import json

def test_smart_search():
    """Тестируем умный поиск артикулов"""
    
    # Тестовые артикулы (одинаковые, но с разными разделителями)
    test_cases = [
        ("813386900", "REINZ"),
        ("81-33869-00", "REINZ"),
        ("81.33869.00", "REINZ"),
        ("81 33869 00", "REINZ"),
    ]
    
    print("=== ТЕСТ УМНОГО ПОИСКА АРТИКУЛОВ ===")
    
    for article, brand in test_cases:
        print(f"\n--- Тест: {article} ({brand}) ---")
        
        # 1. Тест FastAPI unified_search
        try:
            fastapi_url = "http://fastapi:8001/unified_search"
            params = {"article": article, "brand": brand}
            
            response = requests.get(fastapi_url, params=params, timeout=10)
            data = response.json()
            
            print(f"Статус: {response.status_code}")
            print(f"Результатов: {len(data.get('data', []))}")
            
            if data.get('data'):
                # Ищем товары с искомым брендом
                reinz_items = [item for item in data['data'] if item.get('brand', '').upper() == brand.upper()]
                print(f"Товаров {brand}: {len(reinz_items)}")
                
                if reinz_items:
                    print(f"Первый товар {brand}: {reinz_items[0].get('article')} - {reinz_items[0].get('source')}")
                else:
                    print(f"Товары {brand} не найдены")
            else:
                print("Товары не найдены")
                
        except Exception as e:
            print(f"Ошибка FastAPI: {e}")
        
        # 2. Тест Django web search
        try:
            web_url = "http://web:8000/catalog/search/"
            params = {"article": article, "brand": brand}
            
            response = requests.get(web_url, params=params, timeout=10)
            
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
                
                print(f"Товаров в HTML: {len(product_items)}")
                
                # Показываем первые товары
                if product_items:
                    cells = product_items[0].find_all('td')
                    if len(cells) >= 8:
                        article_cell = cells[0].get_text(strip=True)
                        brand_cell = cells[1].get_text(strip=True)
                        print(f"Первый товар в HTML: {article_cell} | {brand_cell}")
                
        except Exception as e:
            print(f"Ошибка Django: {e}")

if __name__ == "__main__":
    test_smart_search() 