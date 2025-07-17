#!/usr/bin/env python
"""
Прямой тест метода get_product_analogs
"""
import os
import sys
import django
import traceback

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def test_get_product_analogs_direct():
    """Прямой тест метода get_product_analogs"""
    
    print("🔍 Прямой тест get_product_analogs...")
    print("=" * 50)
    
    try:
        supplier = Supplier.objects.filter(is_active=True, api_type='autoparts').first()
        
        if not supplier:
            print("❌ Нет поставщиков")
            return
        
        print(f"📦 Поставщик: {supplier.name}")
        
        # Тестируем метод напрямую
        print(f"\n🔍 Вызываем get_product_analogs('test123')...")
        
        try:
            success, result = supplier.get_product_analogs('test123')
            print(f"✅ Метод выполнился без исключений")
            print(f"   Успех: {success}")
            print(f"   Результат: {result}")
            
            if success:
                print(f"   ✅ Успешный результат!")
                if isinstance(result, dict):
                    analogs = result.get('analogs', [])
                    print(f"   Количество аналогов: {len(analogs)}")
                else:
                    print(f"   ⚠️ Результат не является словарем: {type(result)}")
            else:
                print(f"   ⚠️ Неуспешный результат: {result}")
                
        except Exception as e:
            print(f"❌ ОШИБКА в get_product_analogs: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_get_product_analogs_direct()
