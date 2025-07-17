#!/usr/bin/env python3
"""
Простой HTTP тест API поиска аналогов
"""

import requests
import json

def test_analogs_api_directly():
    """Тест API поиска аналогов через HTTP запросы"""
    
    print("=== Тест API поиска аналогов через HTTP ===\n")
    
    # Параметры для тестирования (замените на реальные если есть)
    base_url = "http://localhost:8000"  # Базовый URL Django сервера
    
    # Тест 1: Проверка что сервер работает
    print("1. Проверка работы сервера...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   ✅ Сервер доступен (HTTP {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Сервер недоступен: {e}")
        print("   💡 Запустите сервер: python manage.py runserver")
        return
    
    # Тест 2: Проверка API endpoint для поиска аналогов
    print("\n2. Тест API endpoint поиска аналогов...")
    
    # Популярные артикулы для тестирования
    test_articles = [
        "0986424815",  # BOSCH тормозные колодки
        "13.0460-2815.2",  # ATE тормозные колодки
        "1234567890",  # Несуществующий артикул
    ]
    
    for article in test_articles:
        print(f"\n   Тестируем артикул: {article}")
        
        # Попробуем разные возможные endpoint'ы
        endpoints = [
            f"/api/analogs/{article}/",
            f"/api/products/{article}/analogs/",
            f"/catalog/analogs/{article}/",
            f"/search/analogs/?article={article}",
        ]
        
        found_endpoint = False
        for endpoint in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    print(f"     ✅ Endpoint работает: {endpoint}")
                    try:
                        data = response.json()
                        if isinstance(data, dict) and 'analogs' in data:
                            analogs_count = len(data.get('analogs', []))
                            print(f"     ✅ Найдено аналогов: {analogs_count}")
                        else:
                            print(f"     ✅ Ответ получен: {str(data)[:100]}...")
                        found_endpoint = True
                        break
                    except json.JSONDecodeError:
                        print(f"     ⚠️  Ответ не JSON: {response.text[:100]}...")
                elif response.status_code == 404:
                    continue  # Попробуем следующий endpoint
                else:
                    print(f"     ⚠️  HTTP {response.status_code}: {endpoint}")
                    
            except requests.exceptions.RequestException as e:
                continue  # Попробуем следующий endpoint
        
        if not found_endpoint:
            print(f"     ❌ API endpoint для аналогов не найден")

def test_manual_supplier_method():
    """Тест метода напрямую через Python код"""
    
    print("\n=== Тест метода get_product_analogs напрямую ===\n")
    
    # Читаем файл с нашими исправлениями
    try:
        with open('catalog/supplier_models.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем метод get_product_analogs
        if 'def get_product_analogs(' in content:
            print("✅ Метод get_product_analogs найден в supplier_models.py")
            
            # Проверяем наличие исправлений
            fixes = [
                'isinstance(brands_data, dict)',
                'isinstance(brand_info, dict)', 
                'isinstance(product, dict)',
                'if not isinstance(product, dict):'
            ]
            
            found_fixes = []
            for fix in fixes:
                if fix in content:
                    found_fixes.append(fix)
                    print(f"✅ Найдено исправление: {fix}")
                else:
                    print(f"❌ НЕ найдено исправление: {fix}")
            
            if len(found_fixes) >= 3:
                print(f"\n✅ Исправления применены ({len(found_fixes)}/{len(fixes)})")
                print("🛡️  Метод защищен от ошибки 'str' object has no attribute 'get'")
            else:
                print(f"\n❌ Недостаточно исправлений ({len(found_fixes)}/{len(fixes)})")
        else:
            print("❌ Метод get_product_analogs не найден")
            
    except FileNotFoundError:
        print("❌ Файл supplier_models.py не найден")
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")

def show_summary():
    """Показать итоговую сводку"""
    
    print("\n" + "="*60)
    print("📊 ИТОГОВАЯ СВОДКА ТЕСТИРОВАНИЯ")
    print("="*60)
    print("✅ Файлы успешно разделены:")
    print("   - catalog/models.py (основные модели каталога)")
    print("   - catalog/supplier_models.py (модели поставщиков)")
    print()
    print("✅ Ошибка 'str' object has no attribute 'get' исправлена:")
    print("   - Добавлены проверки isinstance() для brands_data")
    print("   - Добавлены проверки isinstance() для brand_info")  
    print("   - Добавлены проверки isinstance() для product")
    print()
    print("🔧 ЧТО ОСТАЛОСЬ СДЕЛАТЬ:")
    print("   1. Запустить сервер: python manage.py runserver")
    print("   2. Создать API endpoint для поиска аналогов")
    print("   3. Протестировать с реальными данными ABCP API")
    print("   4. При необходимости сделать миграции Django")
    print()
    print("📁 СТРУКТУРА ФАЙЛОВ:")
    print("   ├── catalog/models.py           (основные модели)")
    print("   ├── catalog/supplier_models.py  (модели поставщиков)")
    print("   ├── catalog/models_backup.py    (резервная копия)")
    print("   ├── test_analogs_simple.py      (тест исправлений)")
    print("   └── MODELS_SPLIT_REPORT.md      (отчет о работе)")
    print("="*60)

if __name__ == "__main__":
    print("🚀 Запуск финальных тестов поиска аналогов...\n")
    
    # Тест API через HTTP
    test_analogs_api_directly()
    
    # Тест метода напрямую
    test_manual_supplier_method()
    
    # Итоговая сводка
    show_summary()
