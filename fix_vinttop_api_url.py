#!/usr/bin/env python
"""
Скрипт для исправления URL API поставщика vinttop.ru
Исправляем с нашего IP на их API сервер
"""
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier, SupplierSyncLog

def fix_vinttop_api_url():
    """Исправляет URL API поставщика vinttop.ru"""
    
    print("🔧 Исправление настроек API для VintTop.ru...")
    
    try:
        # Получаем поставщика VintTop
        supplier = Supplier.objects.get(name__icontains='vinttop')
        print(f"✅ Найден поставщик: {supplier.name} (ID: {supplier.id})")
        print(f"   Старый API URL: {supplier.api_url}")
        
        # Правильный API URL от поставщика
        correct_api_url = "http://178.208.92.49"  # API сервер поставщика
        
        print(f"🔧 Обновляем API URL на: {correct_api_url}")
        print(f"📍 Наш IP 46.226.167.12 разрешен у поставщика")
        
        # Обновляем настройки
        supplier.api_url = correct_api_url
        supplier.api_login = "autovag@bk.ru"  # Подтверждаем логин
        supplier.api_password = "0754"  # Подтверждаем пароль
        
        # Дополнительные настройки для безопасности
        supplier.auth_settings = {
            "auth_type": "basic",  # HTTP Basic Auth
            "timeout": 30,
            "verify_ssl": False,  # Для HTTP
            "allowed_from_ip": "46.226.167.12"  # Наш IP, разрешенный у поставщика
        }
        
        # Сохраняем
        supplier.save()
        
        print(f"✅ Настройки обновлены:")
        print(f"   Новый API URL: {supplier.api_url}")
        print(f"   Логин: {supplier.api_login}")
        print(f"   Наш IP (разрешен): 46.226.167.12")
        print(f"   Их API сервер: 178.208.92.49")
        
        # Создаем лог
        SupplierSyncLog.objects.create(
            supplier=supplier,
            status='info',
            message='API URL исправлен на http://178.208.92.49. Готов к тестированию с разрешенного IP.'
        )
        
        print("\n📋 Настройки подключения:")
        print("✅ Наш IP 46.226.167.12 разрешен у поставщика")
        print("✅ API URL поставщика: http://178.208.92.49")
        print("✅ Авторизация: HTTP Basic Auth")
        print("✅ Логин/пароль настроены")
        
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
        supplier = fix_vinttop_api_url()
        if supplier:
            print(f"\n� Настройки исправлены! Можно тестировать:")
            print(f"   Админка: http://127.0.0.1:8000/admin/catalog/supplier/{supplier.id}/change/")
            print(f"   Тест API: нажмите кнопку 'Тест API' в админке")
        else:
            print(f"\n❌ Не удалось исправить настройки")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        print(f"4. Проведите тест API подключения")
