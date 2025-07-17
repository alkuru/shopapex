#!/usr/bin/env python
"""
Тест метода _search_articles_by_brand
"""

import os
import django
import traceback

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def test_search_articles_by_brand():
    """Тестируем _search_articles_by_brand"""
    try:
        # Находим ABCP поставщика
        supplier = Supplier.objects.filter(api_type='autoparts').first()
        
        if not supplier:
            print("❌ ABCP поставщик не найден")
            return
            
        print(f"✅ Тестируем поставщика: {supplier.name}")
        
        # Тестируем метод _search_articles_by_brand
        test_cases = [
            {"article": "1234567890", "brand": "testBrandNewD"},
            {"article": "INVALID_ARTICLE", "brand": "INVALID_BRAND"},
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"\n--- Тест {i+1}: {test_case} ---")
            
            try:
                success, result = supplier._search_articles_by_brand(
                    article=test_case["article"],
                    brand=test_case["brand"]
                )
                
                print(f"Результат: success={success}")
                
                if success:
                    print(f"Тип результата: {type(result)}")
                    print(f"Результат: {str(result)[:200]}...")
                    
                    # Проверяем структуру результата
                    if isinstance(result, dict):
                        print(f"Ключи словаря: {list(result.keys())}")
                        for key, value in result.items():
                            print(f"  {key}: {type(value)} = {str(value)[:50]}...")
                    elif isinstance(result, list):
                        print(f"Список из {len(result)} элементов")
                        for j, item in enumerate(result[:2]):
                            print(f"  [{j}]: {type(item)} = {str(item)[:50]}...")
                else:
                    print(f"Ошибка: {result}")
                    
            except Exception as e:
                print(f"❌ ОШИБКА в тесте {i+1}: {e}")
                print(f"Тип ошибки: {type(e).__name__}")
                traceback.print_exc()
                
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_search_articles_by_brand()
