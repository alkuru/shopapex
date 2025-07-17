#!/usr/bin/env python3
"""
Тест новых улучшений интеграции с ABCP API
Проверяет: мониторинг API, расширенный поиск, новые модели
"""

import os
import sys
import django
import time
from decimal import Decimal

# Добавляем путь к проекту
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from catalog.models import (
    Supplier, Product, ProductCategory, Brand, 
    APIMonitorLog, APIHealthCheck
)
from catalog.forms import AdvancedSearchForm


def test_api_monitoring():
    """Тестирует систему мониторинга API"""
    print("🔍 Тестирование системы мониторинга API...")
    
    # Получаем поставщика
    supplier = Supplier.objects.filter(api_type='autoparts').first()
    if not supplier:
        print("❌ Поставщик с API автозапчастей не найден")
        return False
    
    print(f"   Тестируем поставщика: {supplier.name}")
    
    # Проверяем количество логов до
    logs_before = APIMonitorLog.objects.count()
    
    # Делаем тестовый API запрос (он должен создать лог)
    success, result = supplier.get_abcp_user_info()
    
    # Проверяем создание лога
    logs_after = APIMonitorLog.objects.count()
    
    if logs_after > logs_before:
        print("   ✅ Лог API запроса создан успешно")
        
        # Проверяем последний лог
        last_log = APIMonitorLog.objects.latest('created_at')
        print(f"   📊 Метод: {last_log.method}")
        print(f"   📊 Статус: {last_log.status}")
        print(f"   📊 Время ответа: {last_log.response_time:.3f}с")
        
        return True
    else:
        print("   ❌ Лог API запроса не создан")
        return False


def test_api_health_check():
    """Тестирует модель проверки здоровья API"""
    print("\n🏥 Тестирование проверки здоровья API...")
    
    supplier = Supplier.objects.filter(api_type='autoparts').first()
    if not supplier:
        print("❌ Поставщик с API автозапчастей не найден")
        return False
    
    # Создаем или получаем health check
    health_check, created = APIHealthCheck.objects.get_or_create(
        supplier=supplier,
        defaults={
            'is_healthy': True,
            'success_rate_24h': 95.5,
            'avg_response_time': 1.2,
            'total_requests_today': 150
        }
    )
    
    print(f"   Статус: {'🟢 Создан' if created else '🔄 Обновлен'}")
    print(f"   Здоровье: {'🟢 Работает' if health_check.is_healthy else '🔴 Не работает'}")
    print(f"   Успешность: {health_check.success_rate_24h}%")
    print(f"   Среднее время ответа: {health_check.avg_response_time}с")
    print(f"   Запросов сегодня: {health_check.total_requests_today}")
    
    return True


def test_advanced_search_form():
    """Тестирует расширенную форму поиска"""
    print("\n🔍 Тестирование расширенной формы поиска...")
    
    # Создаем тестовые данные для формы
    form_data = {
        'query': 'TEST123',
        'search_type': 'article',
        'price_min': '100.00',
        'price_max': '500.00',
        'in_stock_only': True,
        'use_supplier_api': True
    }
    
    form = AdvancedSearchForm(data=form_data)
    
    if form.is_valid():
        print("   ✅ Форма валидна")
        print(f"   📝 Запрос: {form.cleaned_data['query']}")
        print(f"   📝 Тип поиска: {form.cleaned_data['search_type']}")
        print(f"   💰 Цена от: {form.cleaned_data['price_min']}")
        print(f"   💰 Цена до: {form.cleaned_data['price_max']}")
        print(f"   📦 Только в наличии: {form.cleaned_data['in_stock_only']}")
        print(f"   🌐 Использовать API: {form.cleaned_data['use_supplier_api']}")
        return True
    else:
        print("   ❌ Форма невалидна")
        print(f"   ❌ Ошибки: {form.errors}")
        return False


def test_advanced_search_view():
    """Тестирует представление расширенного поиска"""
    print("\n🌐 Тестирование представления расширенного поиска...")
    
    client = Client()
    
    # Тестируем GET запрос без параметров
    try:
        response = client.get('/catalog/advanced-search/')
        
        if response.status_code == 200:
            print("   ✅ Страница загружается успешно")
            print(f"   📄 Статус код: {response.status_code}")
            
            # Проверяем наличие формы в контексте
            if 'form' in response.context and response.context['form'] is not None:
                print("   ✅ Форма присутствует в контексте")
            else:
                print("   ❌ Форма отсутствует в контексте")
                return False
                
            return True
        else:
            print(f"   ❌ Ошибка загрузки страницы: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Ошибка тестирования представления: {e}")
        return False


def test_quick_search_ajax():
    """Тестирует AJAX быстрый поиск"""
    print("\n⚡ Тестирование AJAX быстрого поиска...")
    
    client = Client()
    
    try:
        # Тестируем AJAX запрос
        response = client.get('/catalog/quick-search/', {'q': 'test'})
        
        if response.status_code == 200:
            print("   ✅ AJAX запрос выполнен успешно")
            
            # Проверяем JSON ответ
            try:
                data = response.json()
                if 'results' in data:
                    print("   ✅ JSON ответ корректный")
                    print(f"   📊 Найдено результатов: {len(data['results'])}")
                    return True
                else:
                    print("   ❌ Некорректная структура JSON ответа")
                    return False
            except:
                print("   ❌ Ответ не является JSON")
                return False
        else:
            print(f"   ❌ Ошибка AJAX запроса: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Ошибка тестирования AJAX: {e}")
        return False


def test_supplier_api_search_ajax():
    """Тестирует AJAX поиск через API поставщиков"""
    print("\n🌐 Тестирование AJAX поиска через API поставщиков...")
    
    client = Client()
    
    try:
        # Тестируем AJAX запрос к API поставщиков
        response = client.get('/catalog/supplier-api-search/', {'q': 'TEST123'})
        
        if response.status_code == 200:
            print("   ✅ AJAX запрос к API поставщиков выполнен успешно")
            
            # Проверяем JSON ответ
            try:
                data = response.json()
                if 'results' in data:
                    print("   ✅ JSON ответ корректный")
                    print(f"   📊 Количество поставщиков: {len(data['results'])}")
                    
                    # Показываем результаты по поставщикам
                    for result in data['results']:
                        status_icon = "✅" if result['status'] == 'success' else "❌"
                        print(f"   {status_icon} {result['supplier']}: {len(result['products'])} товаров")
                    
                    return True
                else:
                    print("   ❌ Некорректная структура JSON ответа")
                    return False
            except:
                print("   ❌ Ответ не является JSON")
                return False
        else:
            print(f"   ❌ Ошибка AJAX запроса: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Ошибка тестирования API поиска: {e}")
        return False


def test_database_models():
    """Тестирует новые модели базы данных"""
    print("\n🗄️ Тестирование новых моделей базы данных...")
    
    try:
        # Проверяем модель APIMonitorLog
        log_count = APIMonitorLog.objects.count()
        print(f"   📊 Логов в базе: {log_count}")
        
        # Проверяем модель APIHealthCheck
        health_count = APIHealthCheck.objects.count()
        print(f"   🏥 Записей здоровья в базе: {health_count}")
        
        # Проверяем поставщиков с новыми полями
        suppliers_with_admin = Supplier.objects.filter(admin_login__isnull=False).exclude(admin_login='')
        print(f"   👤 Поставщиков с admin доступом: {suppliers_with_admin.count()}")
        
        # Проверяем новые поля поставщиков
        suppliers = Supplier.objects.filter(api_type='autoparts')
        for supplier in suppliers[:3]:
            print(f"   🏢 {supplier.name}:")
            print(f"      - Офис: {supplier.office_id or 'не указан'}")
            print(f"      - Онлайн склады: {'Да' if supplier.use_online_stocks else 'Нет'}")
            print(f"      - Mock режим: {'Да' if supplier.use_mock_admin_api else 'Нет'}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка тестирования моделей: {e}")
        return False


def main():
    """Главная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ НОВЫХ УЛУЧШЕНИЙ ПРОЕКТА")
    print("=" * 60)
    
    results = []
    
    # Запуск тестов
    tests = [
        ("API Мониторинг", test_api_monitoring),
        ("Проверка здоровья API", test_api_health_check),
        ("Форма расширенного поиска", test_advanced_search_form),
        ("Представление расширенного поиска", test_advanced_search_view),
        ("AJAX быстрый поиск", test_quick_search_ajax),
        ("AJAX поиск через API", test_supplier_api_search_ajax),
        ("Модели базы данных", test_database_models),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 Критическая ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\n📈 РЕЗУЛЬТАТ: {passed}/{total} тестов пройдено")
    print(f"📊 Успешность: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("🚀 Новые улучшения работают корректно!")
    else:
        print(f"\n⚠️ Некоторые тесты провалены. Требуется доработка.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
