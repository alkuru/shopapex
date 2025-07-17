#!/usr/bin/env python
"""
Переключатель режимов ShopApex: Development ↔ Production
Быстрое переключение между mock и реальными данными
"""

import os
import sys
import django
from pathlib import Path

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def show_current_mode():
    """Показывает текущий режим работы"""
    print("🔍 ТЕКУЩИЙ РЕЖИМ SHOPAPEX:")
    print("=" * 50)
    
    try:
        suppliers = Supplier.objects.all()
        mock_enabled = suppliers.filter(use_mock_admin_api=True).count()
        mock_disabled = suppliers.filter(use_mock_admin_api=False).count()
        
        if mock_enabled > 0:
            print(f"   🤖 DEVELOPMENT РЕЖИМ")
            print(f"   📊 Mock включен у {mock_enabled} поставщиков")
            print(f"   📊 Mock выключен у {mock_disabled} поставщиков")
        else:
            print(f"   🚀 PRODUCTION РЕЖИМ") 
            print(f"   📊 Все {mock_disabled} поставщиков работают с реальными данными")
            
        # Проверяем Django настройки
        from django.conf import settings
        print(f"   🔧 DEBUG: {'🔴 True' if settings.DEBUG else '✅ False'}")
        
        # Проверяем .env файл
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
                if 'DEBUG=True' in content:
                    print(f"   📄 .env: 🔴 Development настройки")
                else:
                    print(f"   📄 .env: ✅ Production настройки")
        else:
            print(f"   📄 .env: ❌ Файл не найден")
            
    except Exception as e:
        print(f"   ❌ Ошибка при проверке режима: {e}")
    
    print()

def switch_to_development():
    """Переключает в development режим (mock данные)"""
    print("🤖 ПЕРЕКЛЮЧЕНИЕ В DEVELOPMENT РЕЖИМ:")
    print("=" * 50)
    
    try:
        suppliers = Supplier.objects.all()
        switched_count = 0
        
        for supplier in suppliers:
            if not supplier.use_mock_admin_api:
                supplier.use_mock_admin_api = True
                supplier.save()
                switched_count += 1
                print(f"   ✅ {supplier.name}: Mock режим включен")
            else:
                print(f"   ✅ {supplier.name}: Mock режим уже был включен")
        
        print(f"\n📊 Результат: Mock режим включен у {switched_count} поставщиков")
        
        # Создаем development .env если нужно
        env_dev_content = """# Development настройки для ShopApex
DEBUG=True
SECRET_KEY=django-insecure-@8)8^!+((9bg7r_-p74d1da5gut(m(5%cn78za0nid(0dx#e-9
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# SQLite для разработки
DATABASE_URL=sqlite:///db.sqlite3

# Development настройки
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
CELERY_TASK_ALWAYS_EAGER=True
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_dev_content)
        
        print("   ✅ Создан .env для development")
        print("   🔄 Перезапустите сервер для применения изменений")
        
    except Exception as e:
        print(f"   ❌ Ошибка при переключении в development: {e}")
    
    print()

def switch_to_production():
    """Переключает в production режим (реальные данные)"""
    print("🚀 ПЕРЕКЛЮЧЕНИЕ В PRODUCTION РЕЖИМ:")
    print("=" * 50)
    
    try:
        suppliers = Supplier.objects.all()
        switched_count = 0
        
        for supplier in suppliers:
            if supplier.use_mock_admin_api:
                supplier.use_mock_admin_api = False
                supplier.save()
                switched_count += 1
                print(f"   ✅ {supplier.name}: Mock режим отключен")
            else:
                print(f"   ✅ {supplier.name}: Mock режим уже был отключен")
        
        print(f"\n📊 Результат: Mock режим отключен у {switched_count} поставщиков")
        
        # Копируем production настройки если они есть
        if os.path.exists('.env.production'):
            import shutil
            shutil.copy('.env.production', '.env')
            print("   ✅ Скопированы production настройки из .env.production")
        else:
            print("   ⚠️  Файл .env.production не найден!")
            print("   📝 Создайте .env.production или запустите prepare_for_production.py")
        
        print("   🔄 Перезапустите сервер для применения изменений")
        print("   ⚠️  Убедитесь что у поставщиков есть реальные credentials!")
        
    except Exception as e:
        print(f"   ❌ Ошибка при переключении в production: {e}")
    
    print()

def validate_production_readiness():
    """Проверяет готовность к production"""
    print("✅ ПРОВЕРКА ГОТОВНОСТИ К PRODUCTION:")
    print("=" * 50)
    
    issues = []
    
    try:
        suppliers = Supplier.objects.all()
        
        # Проверяем mock режимы
        mock_enabled = suppliers.filter(use_mock_admin_api=True)
        if mock_enabled.exists():
            issues.append(f"🤖 Mock режим включен у {mock_enabled.count()} поставщиков")
        else:
            print("   ✅ Все mock режимы отключены")
        
        # Проверяем credentials
        no_credentials = []
        for supplier in suppliers.filter(is_active=True):
            if not supplier.api_login or not supplier.api_password:
                no_credentials.append(supplier.name)
        
        if no_credentials:
            issues.append(f"🔐 Нет credentials у поставщиков: {', '.join(no_credentials)}")
        else:
            print("   ✅ У всех активных поставщиков есть credentials")
        
        # Проверяем Django настройки
        from django.conf import settings
        if settings.DEBUG:
            issues.append("🔧 DEBUG=True (должно быть False)")
        else:
            print("   ✅ DEBUG=False")
        
        # Проверяем .env.production
        if not os.path.exists('.env.production'):
            issues.append("📄 Файл .env.production не найден")
        else:
            print("   ✅ Файл .env.production существует")
        
        # Показываем результат
        if issues:
            print(f"\n🔴 НАЙДЕНО {len(issues)} ПРОБЛЕМ:")
            for issue in issues:
                print(f"   {issue}")
            print("\n📝 Запустите prepare_for_production.py для исправления")
        else:
            print("\n🎉 ПРОЕКТ ГОТОВ К PRODUCTION!")
            
    except Exception as e:
        print(f"   ❌ Ошибка при проверке готовности: {e}")
    
    print()

def show_menu():
    """Показывает главное меню"""
    print("🔄 ПЕРЕКЛЮЧАТЕЛЬ РЕЖИМОВ SHOPAPEX")
    print("=" * 50)
    print("1. 📊 Показать текущий режим")
    print("2. 🤖 Переключить в Development (mock данные)")
    print("3. 🚀 Переключить в Production (реальные данные)")  
    print("4. ✅ Проверить готовность к Production")
    print("5. 📋 Показать статус поставщиков")
    print("0. ❌ Выход")
    print()

def show_suppliers_status():
    """Показывает детальный статус всех поставщиков"""
    print("📋 СТАТУС ПОСТАВЩИКОВ:")
    print("=" * 50)
    
    try:
        suppliers = Supplier.objects.all().order_by('name')
        
        for supplier in suppliers:
            print(f"\n📦 {supplier.name}:")
            print(f"   🔗 API URL: {supplier.api_url}")
            print(f"   ⚡ Активен: {'Да' if supplier.is_active else 'Нет'}")
            print(f"   🤖 Mock режим: {'🔴 Включен' if supplier.use_mock_admin_api else '✅ Выключен'}")
            
            # Проверяем credentials
            credentials_status = []
            if supplier.api_login:
                credentials_status.append("✅ API Login")
            else:
                credentials_status.append("❌ API Login")
                
            if supplier.api_password:
                credentials_status.append("✅ API Password")
            else:
                credentials_status.append("❌ API Password")
            
            # Для ABCP API проверяем admin credentials
            if 'abcp.ru' in supplier.api_url.lower():
                if supplier.admin_login:
                    credentials_status.append("✅ Admin Login")
                else:
                    credentials_status.append("❌ Admin Login")
                    
                if supplier.admin_password:
                    credentials_status.append("✅ Admin Password")
                else:
                    credentials_status.append("❌ Admin Password")
                    
                if supplier.office_id:
                    credentials_status.append("✅ Office ID")
                else:
                    credentials_status.append("⚠️ Office ID")
            
            print(f"   🔐 Credentials: {', '.join(credentials_status)}")
            
            # Готовность к production
            has_all_credentials = supplier.api_login and supplier.api_password
            if 'abcp.ru' in supplier.api_url.lower():
                has_all_credentials = has_all_credentials and supplier.admin_login and supplier.admin_password
            
            is_ready = has_all_credentials and not supplier.use_mock_admin_api and supplier.is_active
            readiness = "✅ Готов" if is_ready else "🔴 Не готов"
            print(f"   🎯 Production: {readiness}")
            
    except Exception as e:
        print(f"   ❌ Ошибка при получении статуса поставщиков: {e}")
    
    print()

def main():
    """Основная функция"""
    while True:
        show_menu()
        
        try:
            choice = input("Выберите действие (0-5): ").strip()
            
            if choice == '1':
                show_current_mode()
            elif choice == '2':
                switch_to_development()
            elif choice == '3':
                switch_to_production()
            elif choice == '4':
                validate_production_readiness()
            elif choice == '5':
                show_suppliers_status()
            elif choice == '0':
                print("👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор. Попробуйте еще раз.\n")
                
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}\n")

if __name__ == "__main__":
    main()
