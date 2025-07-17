#!/usr/bin/env python3
"""
Тест API поиска аналогов автозапчастей с исправлениями
"""

import os
import sys
import django
import json
import requests
from unittest.mock import Mock, patch

# Настройка Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex.settings')
django.setup()

def test_get_product_analogs_with_mock_data():
    """Тест метода get_product_analogs с мок-данными различных типов"""
    
    # Импортируем класс Supplier
    from catalog.supplier_models import Supplier
    
    # Создаем тестовый экземпляр поставщика
    supplier = Supplier(
        name='Test Supplier',
        api_type='autoparts',
        api_url='https://api.test.com',
        api_login='test_login',
        api_password='test_password',
        use_online_stocks=True
    )
    
    print("=== Тест поиска аналогов с различными типами данных ===\n")
    
    # Тест 1: Нормальные данные
    print("1. Тест с нормальными данными:")
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"brand": "BOSCH", "number": "0986424815"},
            {"brand": "ATE", "number": "13.0460-2815.2"}
        ]
        mock_get.return_value = mock_response
        
        # Мокаем _search_articles_by_brand
        with patch.object(supplier, '_search_articles_by_brand') as mock_search:
            mock_search.return_value = (True, [
                {
                    "articleCode": "0986424815",
                    "brand": "BOSCH", 
                    "description": "Тормозные колодки",
                    "price": 1500,
                    "availability": 10
                }
            ])
            
            success, result = supplier.get_product_analogs("0986424815")
            print(f"   Результат: success={success}")
            if success:
                print(f"   Найдено аналогов: {result['total_found']}")
            else:
                print(f"   Ошибка: {result}")
    
    # Тест 2: brands_data как строка (была причина ошибки)
    print("\n2. Тест с brands_data как строка:")
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = "Error: Invalid data"  # Строка вместо списка
        mock_get.return_value = mock_response
        
        success, result = supplier.get_product_analogs("invalid_article")
        print(f"   Результат: success={success}")
        print(f"   Сообщение: {result}")
    
    # Тест 3: brands_data со строками в списке
    print("\n3. Тест с brands_data содержащим строки:")
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            "invalid_string_1",  # Строка вместо dict
            {"brand": "BOSCH", "number": "0986424815"},  # Валидный dict
            "invalid_string_2",  # Еще одна строка
            {"brand": "ATE", "number": "13.0460-2815.2"}  # Валидный dict
        ]
        mock_get.return_value = mock_response
        
        with patch.object(supplier, '_search_articles_by_brand') as mock_search:
            mock_search.return_value = (True, [
                {
                    "articleCode": "0986424815",
                    "brand": "BOSCH",
                    "description": "Тормозные колодки",
                    "price": 1500,
                    "availability": 10
                }
            ])
            
            success, result = supplier.get_product_analogs("0986424815")
            print(f"   Результат: success={success}")
            if success:
                print(f"   Найдено аналогов: {result['total_found']}")
                print(f"   Должно быть только 2 (строки пропущены)")
    
    # Тест 4: articles_data со строками
    print("\n4. Тест с articles_data содержащим строки:")
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"brand": "BOSCH", "number": "0986424815"}
        ]
        mock_get.return_value = mock_response
        
        with patch.object(supplier, '_search_articles_by_brand') as mock_search:
            mock_search.return_value = (True, [
                "invalid_product_string",  # Строка вместо dict
                {
                    "articleCode": "0986424815",
                    "brand": "BOSCH",
                    "description": "Тормозные колодки", 
                    "price": 1500,
                    "availability": 10
                },
                "another_invalid_string"  # Еще одна строка
            ])
            
            success, result = supplier.get_product_analogs("0986424815")
            print(f"   Результат: success={success}")
            if success:
                print(f"   Найдено аналогов: {result['total_found']}")
                print(f"   Должен быть только 1 товар (строки пропущены)")
    
    # Тест 5: API ошибка
    print("\n5. Тест с ошибкой API:")
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response
        
        success, result = supplier.get_product_analogs("test_article")
        print(f"   Результат: success={success}")
        print(f"   Сообщение об ошибке: {result}")

def test_real_api_if_configured():
    """Тест с реальным API если настроен"""
    print("\n=== Тест с реальным API (если настроен) ===")
    
    from catalog.supplier_models import Supplier
    
    # Ищем настроенного поставщика
    try:
        supplier = Supplier.objects.filter(
            api_type='autoparts',
            api_url__isnull=False,
            api_login__isnull=False,
            api_password__isnull=False
        ).first()
        
        if supplier:
            print(f"Найден поставщик: {supplier.name}")
            print("Тестируем реальный API...")
            
            # Тестируем популярный артикул
            success, result = supplier.get_product_analogs("0986424815", limit=5)
            print(f"Результат: success={success}")
            
            if success:
                print(f"Найдено аналогов: {result.get('total_found', 0)}")
                analogs = result.get('analogs', [])
                for i, analog in enumerate(analogs[:3]):
                    print(f"  {i+1}. {analog.get('brand')} {analog.get('article')} - {analog.get('name')}")
            else:
                print(f"Ошибка: {result}")
        else:
            print("Не найден настроенный поставщик с API автозапчастей")
            
    except Exception as e:
        print(f"Ошибка доступа к БД: {e}")
        print("Возможно нужно сделать миграции")

if __name__ == "__main__":
    print("Запуск тестов поиска аналогов...\n")
    
    try:
        # Тесты с мок-данными
        test_get_product_analogs_with_mock_data()
        
        # Тест с реальным API
        test_real_api_if_configured()
        
        print("\n" + "="*60)
        print("✅ Все тесты завершены!")
        print("Исправления защищают от ошибки 'str' object has no attribute 'get'")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении тестов: {e}")
        import traceback
        traceback.print_exc()
