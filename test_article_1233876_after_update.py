#!/usr/bin/env python3
"""
Тест артикула 12-33876-01 после обновления брендов
"""

import requests
import json

def test_article_1233876():
    """Тестируем артикул 12-33876-01"""
    
    # Параметры поиска
    article = "12-33876-01"
    brand = "REINZ"  # Теперь используем обновленный бренд
    
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
            print("Найденные товары:")
            for i, item in enumerate(data['data'][:5], 1):  # Показываем первые 5
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
            # Ищем количество товаров в HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем товары в таблице (tr элементы)
            product_rows = soup.find_all('tr')
            print(f"Всего строк в таблице: {len(product_rows)}")
            
            # Ищем строки с товарами (исключаем заголовки и кнопки)
            product_items = []
            for row in product_rows:
                # Проверяем, что это строка с товаром (есть ячейки с артикулом)
                cells = row.find_all('td')
                if len(cells) >= 8:  # Должно быть 8 колонок
                    first_cell = cells[0].get_text(strip=True)
                    if first_cell and first_cell != '-':  # Не пустая и не дефис
                        product_items.append(row)
            
            print(f"Найдено товаров в HTML: {len(product_items)}")
            
            # Показываем первые товары
            for i, item in enumerate(product_items[:3], 1):
                cells = item.find_all('td')
                if len(cells) >= 8:
                    article_cell = cells[0].get_text(strip=True)
                    brand_cell = cells[1].get_text(strip=True)
                    name_cell = cells[2].get_text(strip=True)
                    print(f"  {i}. {article_cell} | {brand_cell} | {name_cell}")
            
            # Ищем кнопку "More offers"
            more_offers = soup.find('button', string=lambda x: x and 'предложений' in x)
            if more_offers:
                print(f"Кнопка 'More offers': {more_offers.text}")
            else:
                print("Кнопка 'More offers' не найдена")
                
            # Ищем группы товаров
            groups_info = soup.find_all('div', string=lambda x: x and 'аналоги артикула' in x)
            print(f"Найдено групп товаров: {len(groups_info)}")
            
        else:
            print(f"Ошибка HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"Ошибка Django: {e}")
    
    # 3. Проверяем базу данных
    print("\n3. Проверка базы данных:")
    try:
        import os
        import django
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
        django.setup()
        
        from catalog.models import AutoKontinentProduct
        
        # Ищем товары с этим артикулом
        products = AutoKontinentProduct.objects.filter(article=article)
        print(f"Товаров в базе с артикулом {article}: {products.count()}")
        
        for product in products:
            print(f"  - {product.brand} {product.article} (бренд: {product.brand})")
            
    except Exception as e:
        print(f"Ошибка проверки БД: {e}")

if __name__ == "__main__":
    test_article_1233876() 