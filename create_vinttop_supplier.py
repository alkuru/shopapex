#!/usr/bin/env python
"""
Скрипт для создания поставщика vinttop.ru с настройками API
"""
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier, SupplierSyncLog

def create_vinttop_supplier():
    """Создает поставщика vinttop.ru с настройками API"""
    
    # Проверяем, существует ли уже такой поставщик
    existing_supplier = Supplier.objects.filter(name__icontains='vinttop').first()
    if existing_supplier:
        print(f"Поставщик {existing_supplier.name} уже существует (ID: {existing_supplier.id})")
        print("Обновляем настройки...")
        supplier = existing_supplier
    else:
        print("Создаем нового поставщика vinttop.ru...")
        supplier = Supplier()
    
    # Основная информация
    supplier.name = "VintTop.ru"
    supplier.description = "Поставщик автозапчастей VintTop.ru - профессиональные запчасти для легковых и грузовых автомобилей"
    supplier.contact_person = "Менеджер API"
    supplier.email = "api@vinttop.ru"
    supplier.phone = "+7 (xxx) xxx-xx-xx"
    supplier.website = "https://vinttop.ru/"
    
    # API настройки для автозапчастей
    supplier.api_type = "autoparts"
    supplier.api_url = "http://46.226.167.12"  # IP адрес их API
    supplier.api_login = "autovag@bk.ru"  # Логин для API
    supplier.api_password = "0754"  # Пароль для API
    supplier.data_format = "json"
    supplier.sync_frequency = "manual"
    
    # Настройки товаров
    supplier.markup_percentage = 15.00  # 15% наценка
    supplier.auto_activate_products = False  # Ручная активация товаров
    supplier.category_mapping = {
        "default_category": 1,  # ID категории по умолчанию
        "brake_systems": 2,
        "engine_parts": 3,
        "suspension": 4
    }
    
    supplier.is_active = True
    
    # Сохраняем
    supplier.save()
    
    print(f"✅ Поставщик {supplier.name} успешно {'обновлен' if existing_supplier else 'создан'}")
    print(f"   ID: {supplier.id}")
    print(f"   API URL: {supplier.api_url}")
    print(f"   Тип API: {supplier.get_api_type_display()}")
    print(f"   Статус: {'Активен' if supplier.is_active else 'Неактивен'}")
    
    # Создаем начальный лог
    SupplierSyncLog.objects.create(
        supplier=supplier,
        status='info',
        message='Поставщик vinttop.ru настроен с логином autovag@bk.ru. Готов к тестированию API.'
    )
    
    print("\n📋 Следующие шаги:")
    print("1. Откройте админку Django")
    print(f"2. Перейдите в Каталог > Поставщики > {supplier.name}")
    print("3. Нажмите 'Тест API' для проверки подключения")
    print("4. Запустите 'Полная синхронизация' для загрузки данных")
    print("5. Используйте 'Интеграция API' для работы с сущностями")
    
    return supplier

if __name__ == "__main__":
    try:
        supplier = create_vinttop_supplier()
        print(f"\n🚀 Поставщик готов! Перейдите в админку: http://127.0.0.1:8000/admin/catalog/supplier/{supplier.id}/change/")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
