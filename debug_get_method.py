#!/usr/bin/env python
"""
Детальная отладка метода get_product_analogs для поиска источника ошибки 'str' object has no attribute 'get'
"""

import os
import django
import traceback

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def test_get_product_analogs_debug():
    """Тестируем get_product_analogs с детальной отладкой"""
    try:
        # Находим ABCP поставщика
        supplier = Supplier.objects.filter(api_type='autoparts').first()
        
        if not supplier:
            print("❌ ABCP поставщик не найден")
            return
            
        print(f"✅ Тестируем поставщика: {supplier.name}")
        print(f"   API URL: {supplier.api_url}")
        print(f"   Login: {supplier.api_login}")
        print(f"   Has password: {'✅' if supplier.api_password else '❌'}")
        
        # Тестируем с артикулом который должен вернуть ошибку
        test_cases = [
            {"article": "INVALID_ARTICLE_123456", "brand": None},
            {"article": "1234567890", "brand": "UNKNOWN_BRAND"},
            {"article": "BRAKE_PAD_123", "brand": "TRW"},
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"\n--- Тест {i+1}: {test_case} ---")
            
            try:
                success, result = supplier.get_product_analogs(
                    article=test_case["article"],
                    brand=test_case["brand"],
                    limit=5
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
    test_get_product_analogs_debug()
