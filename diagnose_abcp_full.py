#!/usr/bin/env python
"""
Диагностический скрипт для ABCP API интеграции
Проверяет какие методы работают и что нужно для полной интеграции
"""
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def diagnose_abcp_integration():
    """Диагностирует состояние ABCP API интеграции"""
    
    print("🔍 Диагностика интеграции ABCP API")
    print("=" * 60)
    
    try:
        # Получаем поставщика VintTop
        supplier = Supplier.objects.get(name__icontains='vinttop')
        print(f"✅ Найден поставщик: {supplier.name} (ID: {supplier.id})")
        
        print(f"\n📊 ТЕКУЩИЕ НАСТРОЙКИ:")
        print(f"   API URL: {supplier.api_url}")
        print(f"   Тип API: {supplier.get_api_type_display()}")
        print(f"   Клиентский логин: {supplier.api_login}")
        print(f"   Клиентский пароль: {'✅ Есть' if supplier.api_password else '❌ Не задан'}")
        print(f"   Админский логин: {supplier.admin_login or '❌ Не задан'}")
        print(f"   Админский пароль: {'✅ Есть' if supplier.admin_password else '❌ Не задан'}")
        
        print(f"\n🔧 ТЕСТИРОВАНИЕ КЛИЕНТСКОГО API:")
        print("-" * 40)
        
        # Тестируем клиентские методы
        client_methods = [
            ('search/articles', 'Поиск товаров', {'number': 'TEST123'}),
            ('search/brands', 'Поиск брендов', {'number': 'TEST123'}),
            ('user/info', 'Информация о пользователе', {}),
        ]
        
        client_results = {}
        
        for endpoint, description, params in client_methods:
            print(f"🔎 {description} ({endpoint})")
            try:
                success, data = supplier._make_abcp_request(endpoint, params)
                
                if success:
                    print(f"   ✅ Успешно: {type(data).__name__}")
                    client_results[endpoint] = True
                else:
                    print(f"   ❌ Ошибка: {data}")
                    client_results[endpoint] = False
                    
            except Exception as e:
                print(f"   ❌ Исключение: {e}")
                client_results[endpoint] = False
        
        print(f"\n🔧 ТЕСТИРОВАНИЕ АДМИНИСТРАТИВНОГО API:")
        print("-" * 40)
        
        # Тестируем административные методы
        admin_methods = [
            ('cp/managers', 'Список сотрудников'),
            ('cp/statuses', 'Статусы заказов'),
            ('cp/users', 'Список пользователей'),
            ('cp/orders', 'Список заказов'),
        ]
        
        admin_results = {}
        
        for endpoint, description in admin_methods:
            print(f"🔎 {description} ({endpoint})")
            try:
                success, data = supplier._make_admin_request(endpoint)
                
                if success:
                    print(f"   ✅ Успешно: {type(data).__name__}")
                    admin_results[endpoint] = True
                else:
                    print(f"   ❌ Ошибка: {data}")
                    admin_results[endpoint] = False
                    
            except Exception as e:
                print(f"   ❌ Исключение: {e}")
                admin_results[endpoint] = False
        
        # Подводим итоги
        print(f"\n🎯 ИТОГОВАЯ ДИАГНОСТИКА:")
        print("=" * 60)
        
        client_success = sum(1 for result in client_results.values() if result)
        admin_success = sum(1 for result in admin_results.values() if result)
        
        print(f"📊 Клиентский API: {client_success}/{len(client_results)} методов работают")
        print(f"📊 Административный API: {admin_success}/{len(admin_results)} методов работают")
        
        if client_success > 0:
            print(f"\n✅ КЛИЕНТСКИЙ API ФУНКЦИОНАЛЕН")
            print(f"   ✅ Поиск товаров работает")
            print(f"   ✅ Можно получать информацию о товарах")
            print(f"   ✅ Базовая интеграция активна")
        else:
            print(f"\n❌ КЛИЕНТСКИЙ API НЕ РАБОТАЕТ")
            print(f"   ❌ Проверьте клиентские логин/пароль")
        
        if admin_success > 0:
            print(f"\n✅ АДМИНИСТРАТИВНЫЙ API ФУНКЦИОНАЛЕН")
            print(f"   ✅ Можно синхронизировать заказы")
            print(f"   ✅ Можно управлять клиентами")
            print(f"   ✅ Полная интеграция активна")
        else:
            print(f"\n⚠️  АДМИНИСТРАТИВНЫЙ API НЕ РАБОТАЕТ")
            print(f"   ⚠️  Нужны отдельные учетные данные API-администратора")
            print(f"   ⚠️  Синхронизация заказов/клиентов недоступна")
        
        print(f"\n📝 ЧТО НУЖНО ДЛЯ ПОЛНОЙ ИНТЕГРАЦИИ:")
        print("-" * 40)
        
        if client_success == 0:
            print(f"1. ❌ Получить рабочие клиентские логин/пароль от VintTop")
        else:
            print(f"1. ✅ Клиентские учетные данные работают")
        
        if admin_success == 0:
            print(f"2. ❌ Получить логин/пароль API-администратора от VintTop")
            print(f"   📞 Обратиться в техподдержку VintTop за админскими правами")
            print(f"   📧 Указать, что нужен доступ к API.ABCP.Admin методам")
        else:
            print(f"2. ✅ Административные учетные данные работают")
        
        print(f"\n🔧 КАК ИСПРАВИТЬ:")
        print("-" * 40)
        print(f"1. Зайдите в админку Django:")
        print(f"   http://127.0.0.1:8000/admin/catalog/supplier/{supplier.id}/change/")
        print(f"2. В разделе 'API настройки' заполните:")
        print(f"   - Логин API (клиентский): для поиска товаров")
        print(f"   - Пароль API (клиентский): для поиска товаров")
        print(f"   - Логин API-администратора: для управления заказами")
        print(f"   - Пароль API-администратора: для управления заказами")
        print(f"3. Сохраните изменения")
        print(f"4. Запустите тест снова: python test_vinttop_api.py")
        
        return supplier
        
    except Supplier.DoesNotExist:
        print("❌ Поставщик VintTop.ru не найден!")
        print("🔧 Создайте поставщика через админку или запустите:")
        print("   python create_vinttop_supplier.py")
        return None

if __name__ == "__main__":
    try:
        diagnose_abcp_integration()
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
