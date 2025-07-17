#!/usr/bin/env python
"""
Тест возвращаемых значений _search_articles_by_brand
"""

import os
import django
import traceback

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def test_return_values():
    """Тестируем возвращаемые значения"""
    try:
        # Находим ABCP поставщика
        supplier = Supplier.objects.filter(api_type='autoparts').first()
        
        if not supplier:
            print("❌ ABCP поставщик не найден")
            return
            
        print(f"✅ Тестируем поставщика: {supplier.name}")
        
        # Тестируем различные случаи
        test_cases = [
            {"article": "1234567890", "brand": "testBrandNewD"},
            {"article": "INVALID_ARTICLE", "brand": "INVALID_BRAND"},
            {"article": "1234567890", "brand": ""},
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"\n--- Тест {i+1}: {test_case} ---")
            
            try:
                result = supplier._search_articles_by_brand(
                    test_case['article'],
                    test_case['brand']
                )
                
                print(f"Результат: {result}")
                print(f"Тип результата: {type(result)}")
                
                # Проверяем формат результата
                if isinstance(result, tuple):
                    if len(result) == 2:
                        success, data = result
                        print(f"  success: {success} (тип: {type(success)})")
                        print(f"  data: {data} (тип: {type(data)})")
                        
                        if success:
                            print(f"  Данные успешны: {str(data)[:100]}...")
                        else:
                            print(f"  Ошибка: {data}")
                    else:
                        print(f"  ❌ Неправильная длина кортежа: {len(result)}")
                else:
                    print(f"  ❌ Результат не кортеж: {type(result)}")
                    
            except Exception as e:
                print(f"❌ ОШИБКА: {e}")
                traceback.print_exc()
                
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_return_values()
