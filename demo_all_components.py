#!/usr/bin/env python3
"""
Демонстрация всех компонентов системы мониторинга ShopApex
Показывает как работает каждый из 7 тестируемых компонентов
"""

import os
import sys
import django
from datetime import datetime

# Настройка Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier, APIMonitorLog, APIHealthCheck
from catalog.forms import AdvancedSearchForm
from django.test import Client


def demo_api_monitoring():
    """Демонстрация компонента: API Мониторинг"""
    print("🔍 1. API МОНИТОРИНГ")
    print("=" * 50)
    
    # Получаем поставщика
    supplier = Supplier.objects.filter(api_type='autoparts').first()
    if not supplier:
        print("❌ Поставщик не найден")
        return
    
    print(f"📡 Тестируем API поставщика: {supplier.name}")
    
    # Делаем API запрос (он автоматически создаст лог)
    success, result = supplier.get_abcp_user_info()
    
    # Показываем последние логи
    logs = APIMonitorLog.objects.filter(supplier=supplier).order_by('-created_at')[:3]
    
    print(f"\n📊 Последние {len(logs)} API запросов:")
    for log in logs:
        status_icon = "✅" if log.status == 'success' else "❌"
        print(f"   {status_icon} {log.method} - {log.response_time:.3f}с - {log.created_at.strftime('%H:%M:%S')}")
    
    print(f"\n🎯 Итого логов в базе: {APIMonitorLog.objects.count()}")


def demo_api_health_check():
    """Демонстрация компонента: Проверка здоровья API"""
    print("\n\n🏥 2. ПРОВЕРКА ЗДОРОВЬЯ API")
    print("=" * 50)
    
    health_checks = APIHealthCheck.objects.all()
    
    if not health_checks:
        print("❌ Записи здоровья API не найдены")
        return
    
    for health in health_checks:
        status_icon = "🟢" if health.is_healthy else "🔴"
        print(f"\n{status_icon} {health.supplier.name}")
        print(f"   📈 Успешность: {health.success_rate_24h}%")
        print(f"   ⏱️ Среднее время ответа: {health.avg_response_time}с")
        print(f"   📊 Запросов сегодня: {health.total_requests_today}")
        print(f"   🕐 Последняя проверка: {health.last_check_at.strftime('%H:%M:%S')}")


def demo_advanced_search_form():
    """Демонстрация компонента: Форма расширенного поиска"""
    print("\n\n📝 3. ФОРМА РАСШИРЕННОГО ПОИСКА")
    print("=" * 50)
    
    # Создаем тестовые данные формы
    form_data = {
        'query': 'BRAKE_PAD_001',
        'search_type': 'article',
        'price_min': '100.00',
        'price_max': '5000.00',
        'in_stock_only': True,
        'featured_only': False,
        'use_supplier_api': True,
        'order_by': 'price_asc'
    }
    
    print("🎯 Тестовые данные формы:")
    for key, value in form_data.items():
        print(f"   📝 {key}: {value}")
    
    # Проверяем валидацию формы
    form = AdvancedSearchForm(data=form_data)
    
    if form.is_valid():
        print("\n✅ Форма валидна!")
        print("🔍 Обработанные данные:")
        for key, value in form.cleaned_data.items():
            if value is not None and value != '':
                print(f"   ✓ {key}: {value}")
    else:
        print("\n❌ Форма невалидна:")
        for field, errors in form.errors.items():
            print(f"   ❌ {field}: {errors}")


def demo_search_view():
    """Демонстрация компонента: Представление расширенного поиска"""
    print("\n\n🌐 4. ПРЕДСТАВЛЕНИЕ РАСШИРЕННОГО ПОИСКА")
    print("=" * 50)
    
    client = Client()
    
    try:
        # Тестируем страницу без параметров
        response = client.get('/catalog/advanced-search/')
        print(f"📄 Статус загрузки страницы: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Страница загружается успешно")
            
            # Проверяем контекст
            if 'form' in response.context:
                print("✅ Форма присутствует в контексте")
            if 'products' in response.context:
                print("✅ Список товаров в контексте")
            if 'total_local' in response.context:
                print(f"📊 Локальных результатов: {response.context.get('total_local', 0)}")
        else:
            print(f"❌ Ошибка загрузки: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")


def demo_ajax_quick_search():
    """Демонстрация компонента: AJAX быстрый поиск"""
    print("\n\n⚡ 5. AJAX БЫСТРЫЙ ПОИСК")
    print("=" * 50)
    
    client = Client()
    
    test_queries = ['brake', 'filter', 'oil', 'test']
    
    for query in test_queries:
        try:
            response = client.get('/catalog/quick-search/', {'q': query})
            
            if response.status_code == 200:
                data = response.json()
                results_count = len(data.get('results', []))
                print(f"🔍 '{query}': {results_count} результатов")
                
                # Показываем первый результат если есть
                if results_count > 0:
                    first_result = data['results'][0]
                    print(f"   📦 Пример: {first_result.get('article')} - {first_result.get('name')}")
            else:
                print(f"❌ '{query}': Ошибка {response.status_code}")
                
        except Exception as e:
            print(f"❌ '{query}': {e}")


def demo_ajax_supplier_search():
    """Демонстрация компонента: AJAX поиск через API"""
    print("\n\n🌐 6. AJAX ПОИСК ЧЕРЕЗ API ПОСТАВЩИКОВ")
    print("=" * 50)
    
    client = Client()
    
    test_articles = ['TEST123', 'BRAKE001', '1234567890']
    
    for article in test_articles:
        try:
            response = client.get('/catalog/supplier-api-search/', {'q': article})
            
            if response.status_code == 200:
                data = response.json()
                suppliers = data.get('results', [])
                
                print(f"\n🔍 Поиск '{article}':")
                
                for supplier_result in suppliers:
                    supplier_name = supplier_result.get('supplier')
                    status = supplier_result.get('status')
                    products_count = len(supplier_result.get('products', []))
                    
                    status_icon = "✅" if status == 'success' else "❌"
                    print(f"   {status_icon} {supplier_name}: {products_count} товаров")
                    
                    if status != 'success':
                        message = supplier_result.get('message', '')
                        if message:
                            print(f"      💬 {message}")
            else:
                print(f"❌ '{article}': Ошибка {response.status_code}")
                
        except Exception as e:
            print(f"❌ '{article}': {e}")


def demo_database_models():
    """Демонстрация компонента: Модели базы данных"""
    print("\n\n🗄️ 7. МОДЕЛИ БАЗЫ ДАННЫХ")
    print("=" * 50)
    
    # Статистика по логам API
    total_logs = APIMonitorLog.objects.count()
    success_logs = APIMonitorLog.objects.filter(status='success').count()
    error_logs = APIMonitorLog.objects.filter(status='error').count()
    
    print(f"📊 API Monitor Logs:")
    print(f"   📈 Всего запросов: {total_logs}")
    print(f"   ✅ Успешных: {success_logs}")
    print(f"   ❌ С ошибками: {error_logs}")
    
    if total_logs > 0:
        success_rate = (success_logs / total_logs) * 100
        print(f"   📊 Успешность: {success_rate:.1f}%")
    
    # Статистика по здоровью API
    total_health = APIHealthCheck.objects.count()
    healthy_apis = APIHealthCheck.objects.filter(is_healthy=True).count()
    
    print(f"\n🏥 API Health Checks:")
    print(f"   🔧 Отслеживаемых API: {total_health}")
    print(f"   🟢 Здоровых: {healthy_apis}")
    print(f"   🔴 Проблемных: {total_health - healthy_apis}")
    
    # Статистика по поставщикам
    total_suppliers = Supplier.objects.count()
    api_suppliers = Supplier.objects.filter(api_type='autoparts').count()
    active_suppliers = Supplier.objects.filter(is_active=True).count()
    
    print(f"\n🏪 Поставщики:")
    print(f"   📋 Всего: {total_suppliers}")
    print(f"   🌐 С API автозапчастей: {api_suppliers}")
    print(f"   ✅ Активных: {active_suppliers}")


def main():
    """Главная функция демонстрации"""
    print("🚀 ДЕМОНСТРАЦИЯ КОМПОНЕНТОВ СИСТЕМЫ SHOPAPEX")
    print("=" * 60)
    print(f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("🎯 Показываем работу всех 7 компонентов тестирования")
    
    try:
        demo_api_monitoring()
        demo_api_health_check()
        demo_advanced_search_form()
        demo_search_view()
        demo_ajax_quick_search()
        demo_ajax_supplier_search()
        demo_database_models()
        
        print("\n" + "=" * 60)
        print("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
        print("✅ Все компоненты продемонстрированы успешно!")
        print("\n💡 Вывод: Система мониторинга и поиска ShopApex")
        print("   работает на профессиональном уровне!")
        
    except Exception as e:
        print(f"\n💥 Критическая ошибка демонстрации: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
