#!/usr/bin/env python
import requests
from bs4 import BeautifulSoup

def test_web_search():
    """Тестирует веб-поиск с подсветкой Mann"""
    
    print("🌐 Тестирование веб-поиска с подсветкой Mann...")
    
    # Тест 1: Поиск C15300
    print("\n1️⃣ Тест: Поиск C15300")
    url = "http://localhost/catalog/search/?q=C15300"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем бренды Mann
            mann_brands = soup.find_all('strong', class_='brand-mann')
            print(f"   Найдено брендов с классом 'brand-mann': {len(mann_brands)}")
            
            for i, brand in enumerate(mann_brands[:5]):
                print(f"   {i+1}. {brand.text}")
            
            # Ищем все бренды
            all_brands = soup.find_all('strong')
            print(f"   Всего брендов: {len(all_brands)}")
            
            # Проверяем, есть ли бренд Mann
            mann_found = False
            for brand in all_brands:
                if 'Mann' in brand.text and 'brand-mann' in brand.get('class', []):
                    mann_found = True
                    print(f"   ✅ Найден Mann с подсветкой: {brand.text}")
                    break
            
            if not mann_found:
                print("   ❌ Mann с подсветкой не найден")
                
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Ошибка запроса: {e}")
    
    print("\n📋 Инструкция по проверке:")
    print("1. Откройте: http://localhost/catalog/search/?q=C15300")
    print("2. Выберите бренд 'Mann'")
    print("3. В результатах поиска бренд 'Mann' должен быть подсвечен зеленым")

if __name__ == '__main__':
    test_web_search() 