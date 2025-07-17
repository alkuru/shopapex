#!/usr/bin/env python
"""
Скрипт для тестирования интеграции с API vinttop.ru
"""
import os
import sys
import django
import requests

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def test_vinttop_integration():
    """Тестирует интеграцию с vinttop.ru"""
    
    print("🔍 Поиск поставщика VintTop.ru...")
    
    try:
        # Получаем поставщика VintTop
        supplier = Supplier.objects.get(name__icontains='vinttop')
        print(f"✅ Найден поставщик: {supplier.name} (ID: {supplier.id})")
        print(f"   API URL: {supplier.api_url}")
        print(f"   Логин: {supplier.api_login}")
        print(f"   Тип API: {supplier.get_api_type_display()}")
        
    except Supplier.DoesNotExist:
        print("❌ Поставщик VintTop.ru не найден!")
        return False
    
    print("\n" + "="*60)
    print("🔧 ТЕСТ 1: Проверка подключения к API")
    print("="*60)
    
    try:
        # Тест подключения к API
        success, message = supplier.test_api_connection()
        
        if success:
            print("✅ Подключение к API успешно!")
            print(f"   Сообщение: {message}")
        else:
            print("❌ Ошибка подключения к API!")
            print(f"   Ошибка: {message}")
            return False
            
    except Exception as e:
        print(f"❌ Исключение при тестировании API: {e}")
        return False
    
    print("\n" + "="*60)
    print("🔍 ТЕСТ 2: Поиск товаров по артикулу")
    print("="*60)
    
    # Список тестовых артикулов для проверки
    test_articles = [
        "0986424815",  # Bosch
        "1234567890",  # Тестовый
        "BP1234",      # Общий формат
    ]
    
    for article in test_articles:
        print(f"\n🔎 Поиск артикула: {article}")
        try:
            success, result = supplier.search_products_by_article(article)
            
            if success:
                if isinstance(result, list) and len(result) > 0:
                    print(f"✅ Найдено товаров: {len(result)}")
                    
                    # Показываем первые товары
                    count = 0
                    for item in result[:3]:
                        count += 1
                        if isinstance(item, dict):
                            name = item.get('name', item.get('title', 'Без названия'))
                            code = item.get('code', item.get('number', article))
                            price = item.get('price', 'N/A')
                            brand = item.get('brand', 'N/A')
                            print(f"   {count}. {name}")
                            print(f"      Артикул: {code}")
                            print(f"      Цена: {price}")
                            print(f"      Бренд: {brand}")
                        else:
                            print(f"   {count}. {item}")
                            
                    if len(result) > 3:
                        print(f"   ... и еще {len(result) - 3} товаров")
                else:
                    print(f"✅ Результат: {result}")
            else:
                print(f"❌ Ошибка поиска: {result}")
                
        except Exception as e:
            print(f"❌ Исключение при поиске: {e}")
    
    print("\n" + "="*60)
    print("👥 ТЕСТ 3: Синхронизация сотрудников")
    print("="*60)
    
    try:
        success, message = supplier.sync_staff()
        
        if success:
            print(f"✅ Синхронизация сотрудников успешна!")
            print(f"   Результат: {message}")
        else:
            print(f"❌ Ошибка синхронизации сотрудников: {message}")
            
    except Exception as e:
        print(f"❌ Исключение при синхронизации сотрудников: {e}")
    
    print("\n" + "="*60)
    print("🚚 ТЕСТ 4: Синхронизация способов доставки")
    print("="*60)
    
    try:
        success, message = supplier.sync_delivery_methods()
        
        if success:
            print(f"✅ Синхронизация способов доставки успешна!")
            print(f"   Результат: {message}")
        else:
            print(f"❌ Ошибка синхронизации доставки: {message}")
            
    except Exception as e:
        print(f"❌ Исключение при синхронизации доставки: {e}")
    
    print("\n" + "="*60)
    print("📊 ТЕСТ 5: Синхронизация статусов заказов")
    print("="*60)
    
    try:
        success, message = supplier.sync_order_statuses()
        
        if success:
            print(f"✅ Синхронизация статусов заказов успешна!")
            print(f"   Результат: {message}")
        else:
            print(f"❌ Ошибка синхронизации статусов: {message}")
            
    except Exception as e:
        print(f"❌ Исключение при синхронизации статусов: {e}")
    
    print("\n" + "="*60)
    print("👤 ТЕСТ 6: Синхронизация клиентов")
    print("="*60)
    
    try:
        success, message = supplier.sync_clients()
        
        if success:
            print(f"✅ Синхронизация клиентов успешна!")
            print(f"   Результат: {message}")
        else:
            print(f"❌ Ошибка синхронизации клиентов: {message}")
            
    except Exception as e:
        print(f"❌ Исключение при синхронизации клиентов: {e}")
    
    print("\n" + "="*60)
    print("📦 ТЕСТ 7: Синхронизация заказов")
    print("="*60)
    
    try:
        success, message = supplier.sync_orders()
        
        if success:
            print(f"✅ Синхронизация заказов успешна!")
            print(f"   Результат: {message}")
        else:
            print(f"❌ Ошибка синхронизации заказов: {message}")
            
    except Exception as e:
        print(f"❌ Исключение при синхронизации заказов: {e}")
    
    print("\n" + "="*60)
    print("🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ")
    print("="*60)
    
    # Проверяем количество загруженных данных
    from catalog.models import (
        SupplierStaff, SupplierDeliveryMethod, SupplierOrderStatus,
        SupplierClientGroup, SupplierClient, SupplierOrder
    )
    
    staff_count = SupplierStaff.objects.filter(supplier=supplier).count()
    delivery_count = SupplierDeliveryMethod.objects.filter(supplier=supplier).count()
    status_count = SupplierOrderStatus.objects.filter(supplier=supplier).count()
    group_count = SupplierClientGroup.objects.filter(supplier=supplier).count()
    client_count = SupplierClient.objects.filter(supplier=supplier).count()
    order_count = SupplierOrder.objects.filter(supplier=supplier).count()
    
    print(f"📊 Статистика данных в базе:")
    print(f"   👥 Сотрудники: {staff_count}")
    print(f"   🚚 Способы доставки: {delivery_count}")
    print(f"   📊 Статусы заказов: {status_count}")
    print(f"   🏷️  Группы клиентов: {group_count}")
    print(f"   👤 Клиенты: {client_count}")
    print(f"   📦 Заказы: {order_count}")
    
    total_records = staff_count + delivery_count + status_count + group_count + client_count + order_count
    
    if total_records > 0:
        print(f"\n✅ Интеграция работает! Загружено {total_records} записей")
        print("🎉 Тестирование успешно завершено!")
        return True
    else:
        print(f"\n⚠️  Данные не загружены, возможны проблемы с API")
        print("🔧 Проверьте логи и настройки подключения")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестирования интеграции VintTop.ru")
    print("=" * 60)
    
    try:
        success = test_vinttop_integration()
        
        if success:
            print(f"\n🎯 Тестирование завершено успешно!")
            print(f"📝 Перейдите в админку для дальнейшей работы:")
            print(f"   http://127.0.0.1:8000/admin/catalog/supplier/4/change/")
        else:
            print(f"\n❌ Тестирование выявило проблемы")
            print(f"🔧 Проверьте настройки API и подключение")
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
