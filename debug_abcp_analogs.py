#!/usr/bin/env python
"""
Отладка ABCP API запросов
"""
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def debug_supplier_api():
    """Отладочная проверка API поставщика"""
    
    print("🔍 Отладка ABCP API...")
    print("=" * 50)
    
    try:
        # Получаем первого активного поставщика
        supplier = Supplier.objects.filter(is_active=True, api_type='autoparts').first()
        
        if not supplier:
            print("❌ Нет активных поставщиков с типом 'autoparts'")
            return
        
        print(f"📦 Тестируем поставщика: {supplier.name}")
        print(f"🔗 API URL: {supplier.api_url}")
        print(f"👤 Login: {supplier.api_login}")
        print(f"🏢 Office ID: {supplier.office_id}")
        print(f"📍 Shipment Address: {supplier.default_shipment_address}")
        print()
        
        # Тестируем поиск аналогов
        print("🔍 Тестируем поиск аналогов для артикула 'test123'...")
        success, result = supplier.get_product_analogs('test123')
        
        print(f"✅ Успех: {success}")
        print(f"📊 Результат: {result}")
        print()
        
        # Тестируем базовое подключение к API
        print("🔍 Тестируем базовое подключение к API...")
        success, message = supplier.test_api_connection()
        
        print(f"✅ Успех: {success}")
        print(f"💬 Сообщение: {message}")
        print()
        
        # Тестируем поиск брендов
        print("🔍 Тестируем поиск брендов для артикула 'test123'...")
        try:
            success, brands = supplier.get_abcp_brands('test123')
            print(f"✅ Успех: {success}")
            print(f"📊 Бренды: {brands}")
        except Exception as e:
            print(f"❌ Ошибка поиска брендов: {e}")
        
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_supplier_api()
