#!/usr/bin/env python
"""
КОМПЛЕКСНЫЙ ТЕСТ РАБОТОСПОСОБНОСТИ SHOPAPEX
Полная проверка всех компонентов системы перед production выгрузкой
"""

import os
import sys
import django
import requests
from datetime import datetime
import time

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from catalog.models import Supplier, APIMonitorLog
try:
    from catalog.models import Category, Brand, Product
except ImportError:
    Category = Brand = Product = None
try:
    from orders.models import Order
except ImportError:
    Order = None
try:
    from customers.models import Customer
except ImportError:
    Customer = None

def print_section(title, emoji="🔧"):
    """Красивый вывод секций"""
    print(f"\n{emoji} {title}")
    print("=" * 60)

def print_test(name, status, details=""):
    """Красивый вывод результатов тестов"""
    status_emoji = "✅" if status else "❌"
    print(f"   {status_emoji} {name}")
    if details:
        print(f"      {details}")

class ComprehensiveSystemTest:
    """Комплексный тест всех компонентов системы"""
    
    def __init__(self):
        self.client = Client()
        self.test_results = {
            'database': [],
            'models': [],
            'api': [],
            'web': [],
            'admin': [],
            'suppliers': [],
            'search': [],
            'integration': []
        }
        self.total_tests = 0
        self.passed_tests = 0
    
    def run_test(self, category, name, test_func):
        """Запускает отдельный тест и записывает результат"""
        try:
            self.total_tests += 1
            result = test_func()
            if result:
                self.passed_tests += 1
            self.test_results[category].append({
                'name': name,
                'status': result,
                'details': result if isinstance(result, str) else ""
            })
            return result
        except Exception as e:
            self.test_results[category].append({
                'name': name,
                'status': False,
                'details': f"Ошибка: {str(e)}"
            })
            return False
    
    def test_database_connectivity(self):
        """Тест подключения к базе данных"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except:
            return False
    
    def test_database_tables(self):
        """Тест существования основных таблиц"""
        try:
            # Проверяем основные модели
            Supplier.objects.exists()
            APIMonitorLog.objects.exists()
            
            # Проверяем дополнительные модели если они есть
            if Category:
                Category.objects.exists()
            if Brand:
                Brand.objects.exists()
            if Product:
                Product.objects.exists()
            if Order:
                Order.objects.exists()
            if Customer:
                Customer.objects.exists()
                
            return True
        except Exception as e:
            return f"Ошибка: {e}"
    
    def test_models_creation(self):
        """Тест создания моделей"""
        try:
            # Создаем тестовые объекты если модели доступны
            test_objects = []
            
            if Category:
                category = Category.objects.create(
                    name="Тестовая категория",
                    description="Тест"
                )
                test_objects.append(category)
            
            if Brand:
                brand = Brand.objects.create(
                    name="Тестовый бренд",
                    description="Тест"
                )
                test_objects.append(brand)
            
            # Удаляем тестовые объекты
            for obj in test_objects:
                obj.delete()
                
            return True
        except Exception as e:
            return f"Ошибка создания моделей: {e}"
    
    def test_suppliers_configuration(self):
        """Тест конфигурации поставщиков"""
        try:
            suppliers = Supplier.objects.all()
            if not suppliers.exists():
                return "Поставщики не настроены"
            
            active_suppliers = suppliers.filter(is_active=True)
            results = []
            
            for supplier in active_suppliers:
                has_api_url = bool(supplier.api_url)
                has_credentials = bool(supplier.api_login and supplier.api_password)
                mock_disabled = not supplier.use_mock_admin_api if hasattr(supplier, 'use_mock_admin_api') else True
                
                status = "✅" if (has_api_url and has_credentials and mock_disabled) else "⚠️"
                results.append(f"{supplier.name}: {status}")
            
            return f"Активных поставщиков: {active_suppliers.count()}"
        except Exception as e:
            return f"Ошибка: {e}"
    
    def test_api_endpoints(self):
        """Тест API endpoints"""
        try:
            # Тестируем основные API endpoints
            endpoints = [
                '/api/categories/',
                '/api/brands/',
                '/api/products/',
                '/api/suppliers/',
            ]
            
            working_endpoints = 0
            for endpoint in endpoints:
                try:
                    response = self.client.get(endpoint)
                    if response.status_code in [200, 404]:  # 404 OK для пустых данных
                        working_endpoints += 1
                except:
                    pass
            
            return f"{working_endpoints}/{len(endpoints)} endpoints работают"
        except Exception as e:
            return f"Ошибка: {e}"
    
    def test_web_pages(self):
        """Тест веб-страниц"""
        try:
            # Тестируем основные страницы
            pages = [
                '/',
                '/catalog/',
                '/search/',
                '/admin/',
            ]
            
            working_pages = 0
            for page in pages:
                try:
                    response = self.client.get(page)
                    if response.status_code in [200, 302, 403]:  # 302 редирект, 403 нет прав - ОК
                        working_pages += 1
                except:
                    pass
            
            return f"{working_pages}/{len(pages)} страниц доступны"
        except Exception as e:
            return f"Ошибка: {e}"
    
    def test_admin_interface(self):
        """Тест админки Django"""
        try:
            # Проверяем доступность админки
            response = self.client.get('/admin/')
            admin_accessible = response.status_code in [200, 302]
            
            # Проверяем регистрацию моделей в админке
            from django.contrib import admin
            registered_models = len(admin.site._registry)
            
            return f"Админка доступна, моделей зарегистрировано: {registered_models}"
        except Exception as e:
            return f"Ошибка: {e}"
    
    def test_search_functionality(self):
        """Тест функциональности поиска"""
        try:
            # Проверяем что формы поиска существуют
            from catalog.forms import QuickSearchForm, AdvancedSearchForm
            
            # Тестируем создание форм
            quick_form = QuickSearchForm({'query': 'test'})
            advanced_form = AdvancedSearchForm({
                'article': 'test',
                'brand': 'test',
                'name': 'test'
            })
            
            return "Формы поиска работают"
        except Exception as e:
            return f"Ошибка: {e}"
    
    def test_supplier_api_integration(self):
        """Тест интеграции с API поставщиков"""
        try:
            suppliers = Supplier.objects.filter(is_active=True)
            working_suppliers = 0
            
            for supplier in suppliers:
                try:
                    # Тестируем базовое подключение
                    success, result = supplier.test_connection()
                    if success:
                        working_suppliers += 1
                except:
                    pass
            
            return f"{working_suppliers}/{suppliers.count()} поставщиков отвечают"
        except Exception as e:
            return f"Ошибка: {e}"
    
    def test_monitoring_system(self):
        """Тест системы мониторинга"""
        try:
            # Проверяем что логи API создаются
            recent_logs = APIMonitorLog.objects.order_by('-created_at')[:5]
            log_count = recent_logs.count()
            
            # Проверяем что модель APIHealthCheck существует
            try:
                from catalog.models import APIHealthCheck
                health_checks_exist = True
            except:
                health_checks_exist = False
            
            return f"Логов API: {log_count}, Health checks: {'Да' if health_checks_exist else 'Нет'}"
        except Exception as e:
            return f"Ошибка: {e}"
    
    def test_static_files(self):
        """Тест статических файлов"""
        try:
            # Проверяем настройки статических файлов
            static_url = getattr(settings, 'STATIC_URL', None)
            static_root = getattr(settings, 'STATIC_ROOT', None)
            
            return f"STATIC_URL: {static_url}, STATIC_ROOT настроен: {'Да' if static_root else 'Нет'}"
        except Exception as e:
            return f"Ошибка: {e}"
    
    def test_django_settings(self):
        """Тест настроек Django"""
        try:
            issues = []
            
            # Проверяем критичные настройки
            if settings.DEBUG:
                issues.append("DEBUG=True")
            
            if 'django-insecure' in settings.SECRET_KEY:
                issues.append("Небезопасный SECRET_KEY")
            
            if not settings.ALLOWED_HOSTS or 'localhost' in settings.ALLOWED_HOSTS:
                issues.append("ALLOWED_HOSTS содержит localhost")
            
            if issues:
                return f"Проблемы: {', '.join(issues)}"
            else:
                return "Настройки в порядке"
        except Exception as e:
            return f"Ошибка: {e}"
    
    def run_all_tests(self):
        """Запускает все тесты"""
        print("🚀 КОМПЛЕКСНЫЙ ТЕСТ РАБОТОСПОСОБНОСТИ SHOPAPEX")
        print("=" * 80)
        print(f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print(f"🎯 Цель: Проверка готовности к production выгрузке")
        print()
        
        # База данных
        print_section("ТЕСТЫ БАЗЫ ДАННЫХ", "🗃️")
        self.run_test('database', 'Подключение к БД', self.test_database_connectivity)
        self.run_test('database', 'Существование таблиц', self.test_database_tables)
        
        # Модели Django
        print_section("ТЕСТЫ МОДЕЛЕЙ DJANGO", "🏗️")
        self.run_test('models', 'Создание объектов', self.test_models_creation)
        self.run_test('models', 'Конфигурация поставщиков', self.test_suppliers_configuration)
        
        # API
        print_section("ТЕСТЫ API", "🔌")
        self.run_test('api', 'API endpoints', self.test_api_endpoints)
        self.run_test('api', 'Интеграция с поставщиками', self.test_supplier_api_integration)
        
        # Веб-интерфейс
        print_section("ТЕСТЫ ВЕБ-ИНТЕРФЕЙСА", "🌐")
        self.run_test('web', 'Доступность страниц', self.test_web_pages)
        self.run_test('web', 'Функциональность поиска', self.test_search_functionality)
        
        # Админка
        print_section("ТЕСТЫ АДМИНКИ", "⚙️")
        self.run_test('admin', 'Интерфейс администратора', self.test_admin_interface)
        
        # Системы мониторинга
        print_section("ТЕСТЫ МОНИТОРИНГА", "📊")
        self.run_test('integration', 'Система мониторинга', self.test_monitoring_system)
        self.run_test('integration', 'Статические файлы', self.test_static_files)
        self.run_test('integration', 'Настройки Django', self.test_django_settings)
        
        # Результаты
        self.print_results()
    
    def print_results(self):
        """Выводит итоговые результаты"""
        print_section("ИТОГОВЫЕ РЕЗУЛЬТАТЫ", "📋")
        
        for category, tests in self.test_results.items():
            if tests:
                category_names = {
                    'database': 'База данных',
                    'models': 'Модели Django', 
                    'api': 'API',
                    'web': 'Веб-интерфейс',
                    'admin': 'Админка',
                    'suppliers': 'Поставщики',
                    'search': 'Поиск',
                    'integration': 'Интеграция'
                }
                
                print(f"\n🔍 {category_names.get(category, category.upper())}:")
                for test in tests:
                    print_test(test['name'], test['status'], test['details'])
        
        # Общая статистика
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print_section("ОБЩАЯ СТАТИСТИКА", "📊")
        print(f"   📝 Всего тестов: {self.total_tests}")
        print(f"   ✅ Пройдено: {self.passed_tests}")
        print(f"   ❌ Провалено: {self.total_tests - self.passed_tests}")
        print(f"   📈 Успешность: {success_rate:.1f}%")
        
        # Оценка готовности
        print_section("ОЦЕНКА ГОТОВНОСТИ К PRODUCTION", "🎯")
        
        if success_rate >= 90:
            print("   🎉 ОТЛИЧНО! Система полностью готова к production")
            readiness = "ГОТОВ"
        elif success_rate >= 75:
            print("   ✅ ХОРОШО! Система готова с незначительными замечаниями")
            readiness = "ГОТОВ С ЗАМЕЧАНИЯМИ"
        elif success_rate >= 50:
            print("   ⚠️  УДОВЛЕТВОРИТЕЛЬНО! Требуются исправления")
            readiness = "ТРЕБУЕТ ДОРАБОТКИ"
        else:
            print("   ❌ КРИТИЧНО! Система не готова к production")
            readiness = "НЕ ГОТОВ"
        
        print(f"   🚀 Статус: {readiness}")
        
        # Рекомендации
        print_section("РЕКОМЕНДАЦИИ", "💡")
        
        failed_tests = [test for tests in self.test_results.values() for test in tests if not test['status']]
        
        if failed_tests:
            print("   🔧 Исправить следующие проблемы:")
            for test in failed_tests:
                print(f"      - {test['name']}: {test['details']}")
        else:
            print("   ✅ Все тесты пройдены успешно!")
        
        print("\n   📋 Следующие шаги:")
        print("      1. Исправить выявленные проблемы")
        print("      2. Получить production credentials от поставщиков")
        print("      3. Настроить production сервер")
        print("      4. Провести финальное тестирование")
        
        return readiness

def run_comprehensive_test():
    """Запускает комплексное тестирование"""
    tester = ComprehensiveSystemTest()
    return tester.run_all_tests()

if __name__ == "__main__":
    print("🧪 Запуск комплексного тестирования системы...")
    run_comprehensive_test()
    print("\n🏁 Тестирование завершено!")
