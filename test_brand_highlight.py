#!/usr/bin/env python3
"""
Тест подсветки брендов MANN-FILTER и KNECHT/MAHLE
"""

import requests
from bs4 import BeautifulSoup

def test_brand_highlighting():
    """Тестируем подсветку брендов на странице поиска"""
    print("=== Тест подсветки брендов ===")
    
    # URL для тестирования
    search_url = "http://localhost/catalog/search/"
    
    # Тестируем разные варианты
    test_cases = [
        {"q": "C15300", "description": "Поиск C15300 без выбранного бренда"},
        {"q": "C15300", "brand": "MANN-FILTER", "description": "Поиск C15300 с выбранным MANN-FILTER"},
        {"q": "C15300", "brand": "KNECHT/MAHLE", "description": "Поиск C15300 с выбранным KNECHT/MAHLE"},
        {"q": "OC47", "description": "Поиск OC47 без выбранного бренда"},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Тест {i}: {test_case['description']} ---")
        
        try:
            # Делаем запрос
            params = {"q": test_case["q"]}
            if "brand" in test_case:
                params["brand"] = test_case["brand"]
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Парсим HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем подсвеченные бренды
            mann_highlighted = soup.find_all(class_="brand-mann")
            knecht_highlighted = soup.find_all(class_="brand-knecht")
            
            print(f"✅ Статус: {response.status_code}")
            print(f"🔍 Подсвеченных MANN-FILTER: {len(mann_highlighted)}")
            print(f"🔍 Подсвеченных KNECHT/MAHLE: {len(knecht_highlighted)}")
            
            # Выводим текст подсвеченных элементов
            if mann_highlighted:
                print("📋 MANN-FILTER подсвечены:")
                for elem in mann_highlighted:
                    print(f"   - {elem.get_text().strip()}")
            
            if knecht_highlighted:
                print("📋 KNECHT/MAHLE подсвечены:")
                for elem in knecht_highlighted:
                    print(f"   - {elem.get_text().strip()}")
            
            # Проверяем, есть ли бренды в таблице
            table_rows = soup.find_all('tr')
            mann_count = 0
            knecht_count = 0
            
            for row in table_rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    brand_cell = cells[1]  # Вторая колонка - бренд
                    brand_text = brand_cell.get_text().strip()
                    if 'MANN-FILTER' in brand_text:
                        mann_count += 1
                    if 'KNECHT' in brand_text or 'MAHLE' in brand_text:
                        knecht_count += 1
            
            print(f"📊 Всего MANN-FILTER в таблице: {mann_count}")
            print(f"📊 Всего KNECHT/MAHLE в таблице: {knecht_count}")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_brand_highlighting() 