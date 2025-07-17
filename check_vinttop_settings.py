#!/usr/bin/env python
"""
Проверка настроек поставщика VintTop в базе данных
"""
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def check_vinttop_settings():
    """Проверяет настройки поставщика VintTop"""
    
    print("🔍 ПРОВЕРКА НАСТРОЕК ПОСТАВЩИКА VINTTOP")
    print("=" * 50)
    
    try:
        # Получаем поставщика VintTop
        supplier = Supplier.objects.get(name__icontains='vinttop')
        
        print(f"✅ Найден поставщик: {supplier.name}")
        print(f"   ID: {supplier.id}")
        print(f"   Активен: {supplier.is_active}")
        print(f"   Создан: {supplier.created_at}")
        print(f"   Обновлен: {supplier.updated_at}")
        
        print(f"\n📡 API настройки:")
        print(f"   Тип API: {supplier.api_type}")
        print(f"   URL API: {supplier.api_url}")
        print(f"   Логин: {supplier.api_login}")
        print(f"   Пароль: '{supplier.api_password}' (длина: {len(supplier.api_password or '')} символов)")
        print(f"   Формат данных: {supplier.data_format}")
        print(f"   Частота синхронизации: {supplier.sync_frequency}")
        
        print(f"\n🏢 Контактная информация:")
        print(f"   Контактное лицо: {supplier.contact_person}")
        print(f"   Email: {supplier.email}")
        print(f"   Телефон: {supplier.phone}")
        print(f"   Сайт: {supplier.website}")
        
        print(f"\n💰 Настройки товаров:")
        print(f"   Наценка: {supplier.markup_percentage}%")
        print(f"   Автоактивация: {supplier.auto_activate_products}")
        
        print(f"\n🔧 Дополнительные настройки:")
        print(f"   Auth settings: {supplier.auth_settings}")
        print(f"   Category mapping: {supplier.category_mapping}")
        
        # Проверяем, есть ли пустые поля
        print(f"\n⚠️  ПРОВЕРКА ОБЯЗАТЕЛЬНЫХ ПОЛЕЙ:")
        
        issues = []
        if not supplier.api_url:
            issues.append("❌ API URL не установлен")
        else:
            print(f"✅ API URL: {supplier.api_url}")
            
        if not supplier.api_login:
            issues.append("❌ API логин не установлен")
        else:
            print(f"✅ API логин: {supplier.api_login}")
            
        if not supplier.api_password:
            issues.append("❌ API пароль не установлен")
        else:
            print(f"✅ API пароль: установлен ('{supplier.api_password}')")
            
        if issues:
            print(f"\n🚨 НАЙДЕНЫ ПРОБЛЕМЫ:")
            for issue in issues:
                print(f"   {issue}")
                
            print(f"\n🔧 ИСПРАВЛЕНИЕ:")
            if not supplier.api_password:
                print(f"   Устанавливаем пароль '0754'...")
                supplier.api_password = "0754"
                
            if not supplier.api_login:
                print(f"   Устанавливаем логин 'autovag@bk.ru'...")
                supplier.api_login = "autovag@bk.ru"
                
            if not supplier.api_url:
                print(f"   Устанавливаем API URL...")
                supplier.api_url = "https://id16251.public.api.abcp.ru"
                
            # Сохраняем изменения
            supplier.save()
            print(f"✅ Настройки исправлены и сохранены!")
            
            # Проверяем еще раз
            supplier.refresh_from_db()
            print(f"\n🔄 ПРОВЕРКА ПОСЛЕ ИСПРАВЛЕНИЯ:")
            print(f"   API URL: {supplier.api_url}")
            print(f"   API логин: {supplier.api_login}")
            print(f"   API пароль: '{supplier.api_password}' (длина: {len(supplier.api_password or '')})")
            
        else:
            print(f"\n✅ Все обязательные поля заполнены правильно!")
        
        return supplier
        
    except Supplier.DoesNotExist:
        print("❌ Поставщик VintTop.ru не найден в базе данных!")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_or_fix_vinttop():
    """Создает или исправляет поставщика VintTop"""
    
    print(f"\n🔧 СОЗДАНИЕ/ИСПРАВЛЕНИЕ ПОСТАВЩИКА VINTTOP")
    print("=" * 50)
    
    try:
        # Попробуем найти существующего
        try:
            supplier = Supplier.objects.get(name__icontains='vinttop')
            print(f"✅ Найден существующий поставщик: {supplier.name}")
            action = "обновлен"
        except Supplier.DoesNotExist:
            print(f"📝 Создаем нового поставщика VintTop...")
            supplier = Supplier()
            action = "создан"
        
        # Устанавливаем все необходимые поля
        supplier.name = "VintTop.ru"
        supplier.description = "Поставщик автозапчастей VintTop.ru через ABCP API"
        supplier.contact_person = "API менеджер"
        supplier.email = "api@vinttop.ru"
        supplier.phone = "+7 (XXX) XXX-XX-XX"
        supplier.website = "https://vinttop.ru"
        
        # API настройки
        supplier.api_type = "autoparts"
        supplier.api_url = "https://id16251.public.api.abcp.ru"
        supplier.api_login = "autovag@bk.ru"
        supplier.api_password = "0754"
        supplier.data_format = "json"
        supplier.sync_frequency = "manual"
        
        # Настройки товаров
        supplier.markup_percentage = 15.00
        supplier.auto_activate_products = False
        supplier.category_mapping = {
            "default_category": 1
        }
        
        # Дополнительные настройки
        supplier.auth_settings = {
            "auth_type": "basic",
            "timeout": 30,
            "verify_ssl": True,
            "api_host": "id16251.public.api.abcp.ru",
            "allowed_from_ip": "46.226.167.12"
        }
        
        supplier.is_active = True
        
        # Сохраняем
        supplier.save()
        
        print(f"✅ Поставщик {action}!")
        print(f"   ID: {supplier.id}")
        print(f"   Название: {supplier.name}")
        print(f"   API URL: {supplier.api_url}")
        print(f"   Логин: {supplier.api_login}")
        print(f"   Пароль: '{supplier.api_password}'")
        
        return supplier
        
    except Exception as e:
        print(f"❌ Ошибка создания/исправления: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Сначала проверяем текущее состояние
    supplier = check_vinttop_settings()
    
    # Если что-то не так, исправляем
    if not supplier or not supplier.api_password:
        print(f"\n" + "="*50)
        supplier = create_or_fix_vinttop()
    
    if supplier:
        print(f"\n🎉 ПОСТАВЩИК ГОТОВ К РАБОТЕ!")
        print(f"   Админка: http://127.0.0.1:8000/admin/catalog/supplier/{supplier.id}/change/")
        print(f"   Можно тестировать API")
    else:
        print(f"\n❌ Не удалось настроить поставщика")
