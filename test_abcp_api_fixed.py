#!/usr/bin/env python
"""
Тест исправленного ABCP API интеграции для поиска аналогов
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from catalog.models import Supplier

def test_abcp_api_compliance():
    """Тестирование соответствия ABCP API документации"""
    print("🔍 ТЕСТ СООТВЕТСТВИЯ ABCP API")
    print("=" * 50)
    
    # Получаем поставщика
    try:
        supplier = Supplier.objects.filter(is_active=True, api_type='autoparts').first()
        if not supplier:
            print("❌ Нет настроенных поставщиков API автозапчастей")
            return False
        
        print(f"✅ Найден поставщик: {supplier.name}")
        print(f"   URL: {supplier.api_url}")
        
    except Exception as e:
        print(f"❌ Ошибка получения поставщика: {e}")
        return False
    
    # Тест 1: Поиск брендов по артикулу
    print("\n🔍 ТЕСТ 1: Поиск брендов по артикулу")
    test_article = "01089"  # Тестовый артикул из документации
    
    try:
        success, result = supplier.get_abcp_brands(number=test_article)
        if success:
            print(f"✅ get_abcp_brands работает: найдено {len(result) if isinstance(result, list) else 'неизвестно'} брендов")
            if isinstance(result, list) and result:
                print(f"   Первый бренд: {result[0].get('brand', 'Неизвестно')}")
            elif isinstance(result, dict):
                print(f"   Результат: {list(result.keys())[:3]}")
        else:
            print(f"⚠️ get_abcp_brands ошибка: {result}")
    except Exception as e:
        print(f"❌ Ошибка get_abcp_brands: {e}")
    
    # Тест 2: Поиск товаров по артикулу и бренду
    print("\n🔍 ТЕСТ 2: Поиск товаров по артикулу и бренду")
    test_brand = "Febi"  # Тестовый бренд из документации
    
    try:
        success, result = supplier.search_products_by_article(test_article, test_brand)
        if success:
            print(f"✅ search_products_by_article работает")
            if isinstance(result, list):
                print(f"   Найдено товаров: {len(result)}")
                if result:
                    product = result[0]
                    print(f"   Первый товар: {product.get('brand', '')} {product.get('articleCode', '')} - {product.get('description', '')[:50]}...")
                    print(f"   Цена: {product.get('price', 0)} | Наличие: {product.get('availability', 0)}")
            else:
                print(f"   Результат не является списком: {type(result)}")
        else:
            print(f"⚠️ search_products_by_article ошибка: {result}")
    except Exception as e:
        print(f"❌ Ошибка search_products_by_article: {e}")
    
    # Тест 3: ИСПРАВЛЕННЫЙ поиск аналогов
    print("\n🔍 ТЕСТ 3: ИСПРАВЛЕННЫЙ поиск аналогов")
    
    try:
        success, result = supplier.get_product_analogs(test_article, limit=5)
        if success:
            print(f"✅ get_product_analogs работает корректно!")
            if isinstance(result, list):
                print(f"   Найдено аналогов: {len(result)}")
                for i, analog in enumerate(result[:3]):
                    print(f"   Аналог {i+1}: {analog.get('brand', '')} {analog.get('article', '')} - {analog.get('name', '')[:40]}...")
                    print(f"              Цена: {analog.get('price', 0)} | Наличие: {analog.get('availability', 0)}")
            else:
                print(f"   Неожиданный тип результата: {type(result)}")
        else:
            print(f"⚠️ get_product_analogs ошибка: {result}")
    except Exception as e:
        print(f"❌ Ошибка get_product_analogs: {e}")
    
    # Тест 4: Проверка параметров согласно документации
    print("\n🔍 ТЕСТ 4: Проверка параметров API")
    
    # Проверяем наличие критических полей в модели
    critical_fields = ['api_url', 'api_login', 'api_password', 'use_online_stocks', 'office_id']
    missing_fields = []
    
    for field in critical_fields:
        if hasattr(supplier, field):
            value = getattr(supplier, field)
            print(f"   ✅ {field}: {'настроено' if value else 'пусто'}")
        else:
            missing_fields.append(field)
            print(f"   ❌ {field}: ОТСУТСТВУЕТ")
    
    if missing_fields:
        print(f"⚠️ Отсутствуют поля: {', '.join(missing_fields)}")
    else:
        print("✅ Все критические поля присутствуют")
    
    print("\n" + "=" * 50)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    
    return True

if __name__ == '__main__':
    test_abcp_api_compliance()
