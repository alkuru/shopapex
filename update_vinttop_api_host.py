#!/usr/bin/env python
"""
Обновление API URL поставщика vinttop.ru с правильным хостом
"""
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier, SupplierSyncLog

def update_vinttop_api_host():
    """Обновляет API URL поставщика vinttop.ru с правильным хостом"""
    
    print("🔧 Обновление API хоста для VintTop.ru...")
    
    try:
        # Получаем поставщика VintTop
        supplier = Supplier.objects.get(name__icontains='vinttop')
        print(f"✅ Найден поставщик: {supplier.name} (ID: {supplier.id})")
        print(f"   Старый API URL: {supplier.api_url}")
        
        # Обновляем с правильным хостом от поставщика
        new_api_url = "https://id16251.public.api.abcp.ru"
        
        print(f"🔧 Обновляем API URL на: {new_api_url}")
        print(f"📍 Хост предоставлен поставщиком vinttop.ru")
        
        # Обновляем настройки
        supplier.api_url = new_api_url
        supplier.api_login = "autovag@bk.ru"  # Подтверждаем логин
        supplier.api_password = "0754"  # Подтверждаем пароль
        
        # Обновляем настройки авторизации для HTTPS
        supplier.auth_settings = {
            "auth_type": "basic",  # HTTP Basic Auth
            "timeout": 30,
            "verify_ssl": True,  # Для HTTPS
            "api_host": "id16251.public.api.abcp.ru",  # Хост API
            "allowed_from_ip": "46.226.167.12"  # Наш IP, разрешенный у поставщика
        }
        
        # Сохраняем
        supplier.save()
        
        print(f"✅ Настройки обновлены:")
        print(f"   Новый API URL: {supplier.api_url}")
        print(f"   API хост: id16251.public.api.abcp.ru")
        print(f"   Протокол: HTTPS")
        print(f"   Логин: {supplier.api_login}")
        print(f"   Наш IP (разрешен): 46.226.167.12")
        
        # Создаем лог
        SupplierSyncLog.objects.create(
            supplier=supplier,
            status='info',
            message=f'API URL обновлен на {new_api_url}. Хост предоставлен поставщиком. Готов к тестированию.'
        )
        
        print("\n📋 Настройки подключения:")
        print("✅ Наш IP 46.226.167.12 разрешен у поставщика")
        print("✅ API хост: id16251.public.api.abcp.ru")
        print("✅ Протокол: HTTPS")
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
        supplier = update_vinttop_api_host()
        if supplier:
            print(f"\n🚀 API хост обновлен! Можно тестировать:")
            print(f"   Админка: http://127.0.0.1:8000/admin/catalog/supplier/{supplier.id}/change/")
            print(f"   Тест API: нажмите кнопку 'Тест API' в админке")
            print(f"   Или запустите: python test_vinttop_api.py")
        else:
            print(f"\n❌ Не удалось обновить настройки")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
