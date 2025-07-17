#!/usr/bin/env python
"""
Скрипт для обновления поставщика VintTop с административными учетными данными
"""
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def update_supplier_credentials():
    """Обновляет учетные данные поставщика VintTop"""
    
    print("🔍 Поиск поставщика VintTop.ru...")
    
    try:
        # Получаем поставщика VintTop
        supplier = Supplier.objects.get(name__icontains='vinttop')
        print(f"✅ Найден поставщик: {supplier.name} (ID: {supplier.id})")
        
        # Отображаем текущие настройки
        print(f"\n📊 Текущие настройки:")
        print(f"   API URL: {supplier.api_url}")
        print(f"   Клиентский логин: {supplier.api_login}")
        print(f"   Админский логин: {supplier.admin_login or 'НЕ НАСТРОЕН'}")
        
        # Обновляем административные учетные данные
        # Для тестирования используем те же учетные данные, что и для клиентского доступа
        if not supplier.admin_login:
            supplier.admin_login = supplier.api_login
            print(f"✅ Установлен админский логин: {supplier.admin_login}")
        
        if not supplier.admin_password:
            supplier.admin_password = supplier.api_password
            print(f"✅ Установлен админский пароль")
        
        # Сохраняем изменения
        supplier.save()
        print(f"✅ Поставщик обновлен!")
        
        return supplier
        
    except Supplier.DoesNotExist:
        print("❌ Поставщик VintTop.ru не найден!")
        return None

def test_admin_api(supplier):
    """Тестирует административные методы API"""
    
    print(f"\n🔧 Тестирование административных методов API...")
    
    # Список административных endpoints для тестирования
    admin_endpoints = [
        ('cp/managers', 'Сотрудники'),
        ('cp/statuses', 'Статусы заказов'),
        ('cp/users', 'Пользователи'),
        ('cp/orders', 'Заказы'),
    ]
    
    results = {}
    
    for endpoint, description in admin_endpoints:
        print(f"\n🔎 Тестирование: {description} ({endpoint})")
        try:
            success, data = supplier._make_admin_request(endpoint)
            
            if success:
                print(f"✅ {description}: API ответил успешно")
                if isinstance(data, dict):
                    print(f"   Ключи в ответе: {list(data.keys())}")
                elif isinstance(data, list):
                    print(f"   Количество элементов: {len(data)}")
                results[endpoint] = True
            else:
                print(f"❌ {description}: {data}")
                results[endpoint] = False
                
        except Exception as e:
            print(f"❌ {description}: Исключение - {e}")
            results[endpoint] = False
    
    return results

if __name__ == "__main__":
    print("🚀 Обновление административных учетных данных ABCP API")
    print("=" * 60)
    
    try:
        # Обновляем поставщика
        supplier = update_supplier_credentials()
        
        if supplier:
            # Тестируем административные методы
            results = test_admin_api(supplier)
            
            print(f"\n🎯 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
            print("=" * 40)
            
            success_count = sum(1 for result in results.values() if result)
            total_count = len(results)
            
            for endpoint, success in results.items():
                status = "✅ Работает" if success else "❌ Ошибка"
                print(f"   {endpoint}: {status}")
            
            print(f"\n📊 Итого: {success_count}/{total_count} методов работают")
            
            if success_count > 0:
                print(f"\n✅ Административный API частично или полностью функционален!")
                print(f"🔧 Теперь можно запустить полную синхронизацию:")
                print(f"   python test_vinttop_api.py")
            else:
                print(f"\n⚠️  Административный API не работает")
                print(f"🔧 Проверьте учетные данные и настройки API")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
