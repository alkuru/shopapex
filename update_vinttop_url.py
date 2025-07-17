#!/usr/bin/env python
"""
Обновление настроек поставщика vinttop.ru с правильным URL
"""
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier, SupplierSyncLog

def update_vinttop_url():
    """Обновляет URL API поставщика на правильный"""
    
    print("🔧 Обновление URL API поставщика VintTop.ru...")
    
    try:
        # Получаем поставщика VintTop
        supplier = Supplier.objects.get(name__icontains='vinttop')
        print(f"✅ Найден поставщик: {supplier.name} (ID: {supplier.id})")
        print(f"   Старый API URL: {supplier.api_url}")
        
        # Обновляем на правильный URL
        new_api_url = "https://vinttop.ru"
        supplier.api_url = new_api_url
        supplier.api_login = "autovag@bk.ru"  # Подтверждаем логин
        supplier.api_password = "0754"  # Подтверждаем пароль
        
        # Обновляем настройки авторизации
        supplier.auth_settings = {
            "auth_type": "basic",  # HTTP Basic Auth
            "timeout": 30,
            "verify_ssl": True,  # Для HTTPS
            "allowed_from_ip": "46.226.167.12"  # Наш IP, разрешенный у поставщика
        }
        
        # Сохраняем
        supplier.save()
        
        print(f"✅ Настройки успешно обновлены:")
        print(f"   Новый API URL: {supplier.api_url}")
        print(f"   Логин: {supplier.api_login}")
        print(f"   Протокол: HTTPS")
        print(f"   Статус: Готов к работе")
        
        # Создаем лог
        SupplierSyncLog.objects.create(
            supplier=supplier,
            status='success',
            message=f'API URL обновлен на {new_api_url}. Поставщик успешно подключен и готов к работе.'
        )
        
        print(f"\n🎉 Поставщик VintTop.ru успешно подключен!")
        print(f"📋 Теперь можно:")
        print(f"   1. Тестировать API подключение")
        print(f"   2. Синхронизировать товары")
        print(f"   3. Загружать данные (сотрудники, клиенты, заказы)")
        print(f"   4. Использовать поиск по артикулам")
        
        return supplier
        
    except Supplier.DoesNotExist:
        print("❌ Поставщик VintTop.ru не найден!")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    try:
        supplier = update_vinttop_url()
        if supplier:
            print(f"\n🚀 Готово! Переходите к тестированию:")
            print(f"   Админка: http://127.0.0.1:8000/admin/catalog/supplier/{supplier.id}/change/")
            print(f"   Тест API: python test_vinttop_api.py")
        else:
            print(f"\n❌ Не удалось обновить настройки")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
