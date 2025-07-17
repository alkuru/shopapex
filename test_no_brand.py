#!/usr/bin/env python
"""
Тест без фильтрации по бренду
"""

import os
import django
import traceback

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def test_without_brand_filter():
    """Тестируем без фильтрации по бренду"""
    try:
        # Находим ABCP поставщика
        supplier = Supplier.objects.filter(api_type='autoparts').first()
        
        if not supplier:
            print("❌ ABCP поставщик не найден")
            return
            
        print(f"✅ Тестируем поставщика: {supplier.name}")
        
        # Тестируем без фильтрации по бренду
        test_cases = [
            {"article": "1234567890", "brand": None, "limit": 5},
            {"article": "BRAKE_PAD_123", "brand": None, "limit": 5},
            {"article": "1234567890", "brand": "testBrandNewD", "limit": 5},
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"\n--- Тест {i+1}: {test_case} ---")
            
            try:
                success, result = supplier.get_product_analogs(
                    article=test_case["article"],
                    brand=test_case["brand"],
                    limit=test_case["limit"]
                )
                
                print(f"Результат: success={success}")
                
                if success:
                    print(f"Найдено аналогов: {result.get('total_found', 0)}")
                    analogs = result.get('analogs', [])
                    for analog in analogs[:3]:  # Показываем только первые 3
                        print(f"  - {analog.get('article')} {analog.get('brand')} - {analog.get('name')[:50]}...")
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
    test_without_brand_filter()
