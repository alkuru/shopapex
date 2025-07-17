#!/usr/bin/env python
"""
Скрипт для тестирования интеграции supplier-моделей и API
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex.settings')
django.setup()

from catalog.models import (
    Supplier, SupplierProduct, SupplierSyncLog,
    APIHealthCheck, APIMonitorLog, SupplierStaff,
    SupplierDeliveryMethod, SupplierOrderStatus,
    SupplierClientGroup, SupplierClient, SupplierOrder,
    SupplierOrderItem, SupplierOrderHistory, SupplierBalanceTransaction
)

def test_supplier_models():
    """Тестирование всех supplier-моделей"""
    print("🔍 Тестирование supplier-моделей...")
    
    models_to_test = [
        ('Supplier', Supplier),
        ('SupplierProduct', SupplierProduct),
        ('SupplierSyncLog', SupplierSyncLog),
        ('APIHealthCheck', APIHealthCheck),
        ('APIMonitorLog', APIMonitorLog),
        ('SupplierStaff', SupplierStaff),
        ('SupplierDeliveryMethod', SupplierDeliveryMethod),
        ('SupplierOrderStatus', SupplierOrderStatus),
        ('SupplierClientGroup', SupplierClientGroup),
        ('SupplierClient', SupplierClient),
        ('SupplierOrder', SupplierOrder),
        ('SupplierOrderItem', SupplierOrderItem),
        ('SupplierOrderHistory', SupplierOrderHistory),
        ('SupplierBalanceTransaction', SupplierBalanceTransaction),
    ]
    
    for model_name, model_class in models_to_test:
        try:
            count = model_class.objects.count()
            print(f"✅ {model_name}: {count} записей")
        except Exception as e:
            print(f"❌ {model_name}: Ошибка - {e}")
    
    print()

def test_supplier_admin():
    """Тестирование админки поставщиков"""
    print("🔍 Тестирование админки...")
    
    try:
        # Импортируем админку
        from catalog.admin import (
            SupplierAdmin, SupplierProductAdmin, SupplierSyncLogAdmin,
            APIHealthCheckAdmin, APIMonitorLogAdmin, SupplierStaffAdmin,
            SupplierDeliveryMethodAdmin, SupplierOrderStatusAdmin,
            SupplierClientGroupAdmin, SupplierClientAdmin, SupplierOrderAdmin,
            SupplierBalanceTransactionAdmin
        )
        print("✅ Все админ-классы успешно импортированы")
    except Exception as e:
        print(f"❌ Ошибка импорта админки: {e}")
    
    print()

def test_supplier_viewsets():
    """Тестирование ViewSet'ов"""
    print("🔍 Тестирование ViewSet'ов...")
    
    try:
        from catalog.views import (
            SupplierViewSet, SupplierProductViewSet, SupplierSyncLogViewSet,
            SupplierStaffViewSet, SupplierDeliveryMethodViewSet,
            SupplierOrderStatusViewSet, SupplierClientGroupViewSet,
            SupplierClientViewSet, SupplierOrderViewSet,
            SupplierBalanceTransactionViewSet
        )
        print("✅ Все ViewSet'ы успешно импортированы")
    except Exception as e:
        print(f"❌ Ошибка импорта ViewSet'ов: {e}")
    
    print()

def test_supplier_serializers():
    """Тестирование сериализаторов"""
    print("🔍 Тестирование сериализаторов...")
    
    try:
        from catalog.serializers import (
            SupplierSerializer, SupplierProductSerializer, SupplierSyncLogSerializer,
            SupplierStaffSerializer, SupplierDeliveryMethodSerializer,
            SupplierOrderStatusSerializer, SupplierClientGroupSerializer,
            SupplierClientSerializer, SupplierOrderSerializer,
            SupplierOrderItemSerializer, SupplierOrderHistorySerializer,
            SupplierBalanceTransactionSerializer
        )
        print("✅ Все сериализаторы успешно импортированы")
    except Exception as e:
        print(f"❌ Ошибка импорта сериализаторов: {e}")
    
    print()

def test_api_product_analogs():
    """Тестирование API поиска аналогов"""
    print("🔍 Тестирование API поиска аналогов...")
    
    try:
        from catalog.views import ProductAnalogsView
        print("✅ ProductAnalogsView успешно импортирован")
        
        # Проверяем наличие активных поставщиков
        active_suppliers = Supplier.objects.filter(
            is_active=True,
            api_type='autoparts'
        )
        print(f"✅ Найдено активных поставщиков API автозапчастей: {active_suppliers.count()}")
        
        for supplier in active_suppliers:
            print(f"   - {supplier.name} (ID: {supplier.id})")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print()

def main():
    """Главная функция тестирования"""
    print("🚀 Начинаем тестирование интеграции supplier-моделей")
    print("=" * 60)
    
    test_supplier_models()
    test_supplier_admin()
    test_supplier_viewsets()
    test_supplier_serializers()
    test_api_product_analogs()
    
    print("🎉 Тестирование завершено!")
    print("=" * 60)

if __name__ == '__main__':
    main()
