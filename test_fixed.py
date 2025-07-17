#!/usr/bin/env python
"""
Отдельный процесс для тестирования исправлений
"""

import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def test_fixed():
    """Тестируем исправленный метод"""
    try:
        # Находим ABCP поставщика
        supplier = Supplier.objects.filter(api_type='autoparts').first()
        
        if not supplier:
            print("❌ ABCP поставщик не найден")
            return
            
        print(f"✅ Тестируем поставщика: {supplier.name}")
        
        # Тестируем исправленный метод
        print(f"🎯 Вызываем get_product_analogs...")
        success, result = supplier.get_product_analogs('1234567890', None, 5)
        
        print(f"Результат: success={success}")
        if success:
            print(f"Найдено аналогов: {result.get('total_found', 0)}")
            analogs = result.get('analogs', [])
            for analog in analogs[:3]:
                print(f"  - {analog.get('article')} {analog.get('brand')} - {analog.get('name')[:50]}...")
        else:
            print(f"Ошибка: {result}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed()
