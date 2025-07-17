#!/usr/bin/env python
"""
Полный аудит всех mock-заглушек и настроек для подготовки к production
ShopApex - Интернет-магазин автозапчастей
"""

import os
import sys
import re
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from django.conf import settings
from catalog.models import Supplier, APIMonitorLog

def audit_django_settings():
    """Аудит критических настроек Django"""
    print("🔧 АУДИТ НАСТРОЕК DJANGO:")
    print("=" * 50)
    
    # DEBUG режим
    debug_status = "🔴 ВКЛЮЧЕН (ОПАСНО!)" if settings.DEBUG else "✅ ВЫКЛЮЧЕН"
    print(f"   DEBUG: {debug_status}")
    
    # SECRET_KEY
    secret_key = getattr(settings, 'SECRET_KEY', '')
    is_default_key = 'django-insecure' in secret_key
    secret_status = "🔴 ИСПОЛЬЗУЕТСЯ ДЕФОЛТНЫЙ КЛЮЧ!" if is_default_key else "✅ НАСТРОЕН"
    print(f"   SECRET_KEY: {secret_status}")
    
    # ALLOWED_HOSTS
    allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
    has_localhost = any(host in ['localhost', '127.0.0.1', 'testserver'] for host in allowed_hosts)
    hosts_status = "🟡 СОДЕРЖИТ ТЕСТОВЫЕ ХОСТЫ" if has_localhost else "✅ НАСТРОЕНЫ"
    print(f"   ALLOWED_HOSTS: {hosts_status} {allowed_hosts}")
    
    # База данных
    db_engine = settings.DATABASES['default']['ENGINE']
    is_sqlite = 'sqlite3' in db_engine
    db_status = "🟡 SQLite (рекомендуется PostgreSQL)" if is_sqlite else "✅ Production DB"
    print(f"   DATABASE: {db_status}")
    
    print()

def audit_supplier_mock_settings():
    """Аудит mock настроек поставщиков"""
    print("🤖 АУДИТ MOCK НАСТРОЕК ПОСТАВЩИКОВ:")
    print("=" * 50)
    
    try:
        suppliers = Supplier.objects.all()
        
        if not suppliers.exists():
            print("   ⚠️  ПОСТАВЩИКИ НЕ НАЙДЕНЫ")
            return
        
        mock_enabled = []
        mock_disabled = []
        
        for supplier in suppliers:
            print(f"\n📦 {supplier.name}:")
            print(f"   🔗 API URL: {supplier.api_url}")
            print(f"   🔐 API Login: {'✅ Есть' if supplier.api_login else '❌ Нет'}")
            print(f"   🔑 API Password: {'✅ Есть' if supplier.api_password else '❌ Нет'}")
            print(f"   👤 Admin Login: {'✅ Есть' if supplier.admin_login else '❌ Нет'}")
            print(f"   🔒 Admin Password: {'✅ Есть' if supplier.admin_password else '❌ Нет'}")
            
            if hasattr(supplier, 'use_mock_admin_api'):
                mock_status = "🔴 ВКЛЮЧЕН" if supplier.use_mock_admin_api else "✅ ВЫКЛЮЧЕН"
                print(f"   🤖 Mock режим: {mock_status}")
                
                if supplier.use_mock_admin_api:
                    mock_enabled.append(supplier.name)
                else:
                    mock_disabled.append(supplier.name)
            
            print(f"   📍 Office ID: {supplier.office_id or 'Не указан'}")
            print(f"   📦 Online Stocks: {'Да' if supplier.use_online_stocks else 'Нет'}")
            print(f"   🚚 Default Address: {supplier.default_shipment_address or 'Не указан'}")
            print(f"   ⚡ Активен: {'Да' if supplier.is_active else 'Нет'}")
        
        print(f"\n📊 СВОДКА MOCK РЕЖИМОВ:")
        print(f"   🔴 Mock включен: {len(mock_enabled)} поставщиков")
        for name in mock_enabled:
            print(f"      - {name}")
        
        print(f"   ✅ Mock выключен: {len(mock_disabled)} поставщиков")
        for name in mock_disabled:
            print(f"      - {name}")
            
    except Exception as e:
        print(f"   ❌ Ошибка при проверке поставщиков: {e}")
    
    print()

def audit_code_mock_methods():
    """Аудит mock методов в коде"""
    print("🔍 АУДИТ MOCK МЕТОДОВ В КОДЕ:")
    print("=" * 50)
    
    # Файлы для проверки
    files_to_check = [
        'catalog/models.py',
        'catalog/admin.py', 
        'catalog/views.py',
        'catalog/web_views.py'
    ]
    
    mock_patterns = [
        r'use_mock_admin_api',
        r'_get_mock_admin_data',
        r'mock_data\s*=',
        r'Mock\s+API',
        r'mock.*режим',
        r'test.*data',
        r'fake.*data'
    ]
    
    for file_path in files_to_check:
        full_path = os.path.join(os.getcwd(), file_path)
        if os.path.exists(full_path):
            print(f"\n📁 {file_path}:")
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            found_mocks = []
            for i, line in enumerate(content.split('\n'), 1):
                for pattern in mock_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        found_mocks.append(f"   Строка {i}: {line.strip()}")
            
            if found_mocks:
                print(f"   🤖 Найдено {len(found_mocks)} mock ссылок:")
                for mock in found_mocks[:5]:  # Показываем первые 5
                    print(mock)
                if len(found_mocks) > 5:
                    print(f"   ... и еще {len(found_mocks) - 5} ссылок")
            else:
                print("   ✅ Mock ссылки не найдены")
    
    print()

def audit_test_files():
    """Аудит тестовых файлов и скриптов"""
    print("🧪 АУДИТ ТЕСТОВЫХ ФАЙЛОВ:")
    print("=" * 50)
    
    test_patterns = [
        'test_*.py',
        'demo_*.py',
        '*_test.py',
        'audit_*.py',
        'create_debug*.py'
    ]
    
    test_files = []
    for pattern in test_patterns:
        import glob
        test_files.extend(glob.glob(pattern))
    
    if test_files:
        print(f"   📝 Найдено {len(test_files)} тестовых файлов:")
        for file in test_files:
            size = os.path.getsize(file) / 1024  # KB
            print(f"      - {file} ({size:.1f} KB)")
    else:
        print("   ✅ Тестовые файлы не найдены")
    
    print()

def audit_environment_files():
    """Аудит файлов окружения"""
    print("🌍 АУДИТ ФАЙЛОВ ОКРУЖЕНИЯ:")
    print("=" * 50)
    
    env_files = ['.env', '.env.example', '.env.local', '.env.production']
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"   📄 {env_file}: ✅ Найден")
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем настройки
            if 'DEBUG=True' in content:
                print(f"      🔴 DEBUG=True найден!")
            if 'django-insecure' in content:
                print(f"      🔴 Небезопасный SECRET_KEY!")
        else:
            print(f"   📄 {env_file}: ❌ Не найден")
    
    print()

def check_api_logs():
    """Проверка логов API для тестовых данных"""
    print("📊 АУДИТ ЛОГОВ API:")
    print("=" * 50)
    
    try:
        recent_logs = APIMonitorLog.objects.order_by('-created_at')[:10]
        
        if recent_logs:
            print(f"   📝 Последние {len(recent_logs)} записей логов:")
            for log in recent_logs:
                status = "✅" if log.status == 'success' else "❌"
                print(f"      {status} {log.supplier.name} - {log.method} ({log.created_at.strftime('%H:%M:%S')})")
        else:
            print("   📝 Логи API не найдены")
            
    except Exception as e:
        print(f"   ❌ Ошибка при проверке логов: {e}")
    
    print()

def generate_production_checklist():
    """Генерирует чеклист для production развертывания"""
    print("✅ ЧЕКЛИСТ ДЛЯ PRODUCTION:")
    print("=" * 50)
    
    checklist_items = [
        "🔧 НАСТРОЙКИ DJANGO:",
        "   [ ] Установить DEBUG=False в .env",
        "   [ ] Сгенерировать безопасный SECRET_KEY",
        "   [ ] Настроить ALLOWED_HOSTS с реальными доменами",
        "   [ ] Настроить PostgreSQL базу данных",
        "   [ ] Настроить STATIC_ROOT и MEDIA_ROOT",
        "   [ ] Включить HTTPS (SECURE_SSL_REDIRECT=True)",
        "",
        "🤖 MOCK НАСТРОЙКИ:",
        "   [ ] Отключить use_mock_admin_api у всех поставщиков",
        "   [ ] Внести реальные admin_login/admin_password",
        "   [ ] Проверить корректность api_url",
        "   [ ] Настроить office_id для ABCP",
        "   [ ] Проверить use_online_stocks",
        "   [ ] Настроить default_shipment_address",
        "",
        "🗃️ БАЗА ДАННЫХ:",
        "   [ ] Создать production миграции",
        "   [ ] Настроить backup стратегию",
        "   [ ] Создать индексы для производительности",
        "",
        "🔐 БЕЗОПАСНОСТЬ:",
        "   [ ] Настроить CORS правильно",
        "   [ ] Включить CSRF защиту",
        "   [ ] Настроить rate limiting",
        "   [ ] Проверить права доступа к админке",
        "",
        "🚀 РАЗВЕРТЫВАНИЕ:",
        "   [ ] Удалить тестовые файлы (test_*.py, demo_*.py)",
        "   [ ] Настроить логирование",
        "   [ ] Настроить мониторинг",
        "   [ ] Протестировать все API endpoints",
        "   [ ] Создать documentation для API"
    ]
    
    for item in checklist_items:
        print(item)
    
    print()

def main():
    """Основная функция аудита"""
    print("🔍 ПОЛНЫЙ АУДИТ MOCK ЗАГЛУШЕК - SHOPAPEX")
    print("=" * 60)
    print("Проверка готовности к production развертыванию\n")
    
    # Выполняем все проверки
    audit_django_settings()
    audit_supplier_mock_settings()
    audit_code_mock_methods()
    audit_test_files()
    audit_environment_files()
    check_api_logs()
    generate_production_checklist()
    
    print("🎯 АУДИТ ЗАВЕРШЕН!")
    print("=" * 60)
    print("📋 Используйте чеклист выше для подготовки к production")
    print("📧 Свяжитесь с поставщиками для получения реальных credentials")
    print("🚀 После выполнения всех пунктов проект будет готов к выгрузке")

if __name__ == "__main__":
    main()
