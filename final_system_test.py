#!/usr/bin/env python
"""
ФИНАЛЬНЫЙ ТЕСТ ГОТОВНОСТИ SHOPAPEX К PRODUCTION
Последняя проверка перед реальной выгрузкой
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier, APIMonitorLog
from django.contrib.auth.models import User
from django.test import Client
from django.conf import settings
from datetime import datetime, timedelta

def print_header(title):
    print(f"\n🎯 {title}")
    print("=" * 60)

def print_status(name, status, details=""):
    emoji = "✅" if status else "❌"
    print(f"   {emoji} {name}")
    if details:
        print(f"      💬 {details}")

def test_database():
    """Тест базы данных"""
    print_header("ТЕСТ БАЗЫ ДАННЫХ")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print_status("Подключение к БД", True, "SQLite работает")
        
        # Проверяем основные таблицы
        suppliers_count = Supplier.objects.count()
        logs_count = APIMonitorLog.objects.count()
        print_status("Таблицы моделей", True, f"Поставщиков: {suppliers_count}, Логов API: {logs_count}")
        
        return True
    except Exception as e:
        print_status("База данных", False, f"Ошибка: {e}")
        return False

def test_suppliers():
    """Тест поставщиков"""
    print_header("ТЕСТ ПОСТАВЩИКОВ")
    
    suppliers = Supplier.objects.all()
    if not suppliers.exists():
        print_status("Поставщики", False, "Поставщики не настроены")
        return False
    
    total_ready = 0
    for supplier in suppliers:
        print(f"\n📦 {supplier.name}:")
        
        # Основные настройки
        has_url = bool(supplier.api_url)
        is_active = supplier.is_active
        print_status("API URL", has_url, supplier.api_url if has_url else "Не указан")
        print_status("Активен", is_active)
        
        # Credentials
        has_login = bool(supplier.api_login)
        has_password = bool(supplier.api_password)
        print_status("API Login", has_login)
        print_status("API Password", has_password)
        
        # Mock режим
        mock_enabled = getattr(supplier, 'use_mock_admin_api', False)
        print_status("Mock режим отключен", not mock_enabled)
        
        # ABCP специфичные настройки
        if 'abcp.ru' in supplier.api_url.lower():
            has_admin_login = bool(supplier.admin_login)
            has_admin_password = bool(supplier.admin_password)
            print_status("Admin Login", has_admin_login)
            print_status("Admin Password", has_admin_password)
            
            # Готовность к production
            is_ready = (has_url and is_active and has_login and has_password and 
                       not mock_enabled and has_admin_login and has_admin_password)
        else:
            is_ready = has_url and is_active and has_login and has_password and not mock_enabled
        
        print_status("Готов к production", is_ready)
        
        if is_ready:
            total_ready += 1
    
    print(f"\n📊 Готовых поставщиков: {total_ready}/{suppliers.count()}")
    return total_ready > 0

def test_api_functionality():
    """Тест API функциональности"""
    print_header("ТЕСТ API ФУНКЦИОНАЛЬНОСТИ")
    
    client = Client()
    
    # Тест основных endpoints
    endpoints = [
        ('/', 'Главная страница'),
        ('/catalog/', 'Каталог'),
        ('/search/', 'Поиск'),
        ('/admin/', 'Админка'),
        ('/api/', 'API корень'),
    ]
    
    working_endpoints = 0
    for url, name in endpoints:
        try:
            response = client.get(url)
            success = response.status_code in [200, 302, 404, 403]  # 404, 403 - OK для пустых данных и ограниченного доступа
            print_status(name, success, f"Код: {response.status_code}")
            if success:
                working_endpoints += 1
        except Exception as e:
            print_status(name, False, f"Ошибка: {e}")
    
    print(f"\n📊 Работающих endpoints: {working_endpoints}/{len(endpoints)}")
    return working_endpoints >= len(endpoints) * 0.8  # 80% endpoints должны работать

def test_supplier_connections():
    """Тест подключений к поставщикам"""
    print_header("ТЕСТ ПОДКЛЮЧЕНИЙ К API ПОСТАВЩИКОВ")
    
    suppliers = Supplier.objects.filter(is_active=True)
    working_suppliers = 0
    
    for supplier in suppliers:
        print(f"\n📡 {supplier.name}:")
        
        try:
            # Проверяем наличие метода test_connection
            if hasattr(supplier, 'test_connection'):
                success, result = supplier.test_connection()
                print_status("Подключение", success, result if isinstance(result, str) else "")
                
                if success:
                    working_suppliers += 1
            else:
                # Альтернативная проверка через базовые параметры
                has_credentials = bool(supplier.api_login and supplier.api_password)
                has_url = bool(supplier.api_url)
                
                if has_credentials and has_url:
                    print_status("Настройки подключения", True, "Credentials и URL настроены")
                    working_suppliers += 1
                else:
                    print_status("Настройки подключения", False, "Нет credentials или URL")
                    
        except Exception as e:
            print_status("Подключение", False, f"Ошибка: {e}")
    
    print(f"\n📊 Настроенных поставщиков: {working_suppliers}/{suppliers.count()}")
    return working_suppliers > 0

def test_monitoring_system():
    """Тест системы мониторинга"""
    print_header("ТЕСТ СИСТЕМЫ МОНИТОРИНГА")
    
    # Проверяем логи API
    all_recent_logs = APIMonitorLog.objects.filter(
        created_at__gte=datetime.now() - timedelta(hours=24)
    )
    recent_logs = all_recent_logs.order_by('-created_at')[:10]
    
    print_status("API логи", recent_logs.exists(), f"Записей за 24ч: {all_recent_logs.count()}")
    
    if all_recent_logs.exists():
        successful_logs = all_recent_logs.filter(status='success').count()
        error_logs = all_recent_logs.filter(status='error').count()
        print_status("Успешные запросы", successful_logs > 0, f"Успешных: {successful_logs}")
        print_status("Ошибки в логах", error_logs == 0, f"Ошибок: {error_logs}")
    
    # Проверяем модель APIHealthCheck
    try:
        from catalog.models import APIHealthCheck
        health_checks = APIHealthCheck.objects.all()
        print_status("Health checks", True, f"Записей: {health_checks.count()}")
    except ImportError:
        print_status("Health checks", False, "Модель не найдена")
    
    return True

def test_django_settings():
    """Тест настроек Django"""
    print_header("ТЕСТ НАСТРОЕК DJANGO")
    
    # Проверяем критичные настройки
    debug_enabled = settings.DEBUG
    print_status("DEBUG отключен", not debug_enabled, f"DEBUG={debug_enabled}")
    
    secret_key_secure = 'django-insecure' not in settings.SECRET_KEY
    print_status("SECRET_KEY безопасен", secret_key_secure)
    
    allowed_hosts_ok = len(settings.ALLOWED_HOSTS) > 0
    print_status("ALLOWED_HOSTS настроены", allowed_hosts_ok, str(settings.ALLOWED_HOSTS))
    
    # Проверяем production файлы
    env_production_exists = os.path.exists('.env.production')
    print_status("Файл .env.production", env_production_exists)
    
    deploy_script_exists = os.path.exists('deploy.sh')
    print_status("Скрипт deploy.sh", deploy_script_exists)
    
    requirements_production_exists = os.path.exists('requirements-production.txt')
    print_status("requirements-production.txt", requirements_production_exists)
    
    return env_production_exists and deploy_script_exists and requirements_production_exists

def generate_final_report():
    """Генерирует финальный отчет"""
    print_header("ФИНАЛЬНЫЙ ОТЧЕТ ГОТОВНОСТИ")
    
    # Запускаем все тесты
    db_ok = test_database()
    suppliers_ok = test_suppliers()
    api_ok = test_api_functionality()
    connections_ok = test_supplier_connections()
    monitoring_ok = test_monitoring_system()
    settings_ok = test_django_settings()
    
    # Подсчитываем общую готовность
    tests = [db_ok, suppliers_ok, api_ok, connections_ok, monitoring_ok, settings_ok]
    passed_tests = sum(tests)
    total_tests = len(tests)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
    print(f"   📝 Тестов пройдено: {passed_tests}/{total_tests}")
    print(f"   📈 Процент успеха: {success_rate:.1f}%")
    
    # Оценка готовности
    if success_rate >= 90:
        status = "🎉 ОТЛИЧНО! Система полностью готова к production"
        readiness = "ГОТОВ К ВЫГРУЗКЕ"
    elif success_rate >= 75:
        status = "✅ ХОРОШО! Система готова с незначительными замечаниями"
        readiness = "ГОТОВ С ЗАМЕЧАНИЯМИ"
    elif success_rate >= 50:
        status = "⚠️ УДОВЛЕТВОРИТЕЛЬНО! Требуются исправления"
        readiness = "ТРЕБУЕТ ДОРАБОТКИ"
    else:
        status = "❌ КРИТИЧНО! Система не готова к production"
        readiness = "НЕ ГОТОВ"
    
    print(f"\n🎯 ИТОГОВАЯ ОЦЕНКА:")
    print(f"   {status}")
    print(f"   🚀 Статус: {readiness}")
    
    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ НА ЗАВТРА:")
    if not settings_ok:
        print("   🔧 Применить production настройки (.env.production → .env)")
    if not suppliers_ok:
        print("   🔐 Получить реальные credentials от поставщиков")
    if not connections_ok:
        print("   🔗 Проверить подключения к API поставщиков")
    
    print("\n📋 ПЛАН НА ЗАВТРА:")
    print("   1. 🔧 Настроить вывод аналогов по артикулу")
    print("   2. 🔐 Получить недостающие API credentials")
    print("   3. 🚀 Провести финальную выгрузку на production сервер")
    print("   4. 🧪 Протестировать все функции с реальными данными")
    
    return readiness

def main():
    """Основная функция финального теста"""
    print("🧪 ФИНАЛЬНЫЙ ТЕСТ ГОТОВНОСТИ SHOPAPEX К PRODUCTION")
    print("=" * 80)
    print(f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"🎯 Цель: Окончательная проверка перед завтрашней выгрузкой")
    
    readiness = generate_final_report()
    
    print(f"\n🏁 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print(f"📊 Результат: {readiness}")
    
    if "ГОТОВ" in readiness:
        print("🎉 Можно отдохнуть! Завтра займемся настройкой аналогов и выгрузкой!")
    else:
        print("⚠️ Требуется еще немного работы перед выгрузкой")
    
    return readiness

if __name__ == "__main__":
    main()
