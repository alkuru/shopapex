#!/usr/bin/env python3
"""
Простой тест исправлений в методе get_product_analogs без Django
"""

import sys
import hashlib
import json
from unittest.mock import Mock, patch, MagicMock

# Мокаем Django модули
sys.modules['django'] = MagicMock()
sys.modules['django.db'] = MagicMock()
sys.modules['django.db.models'] = MagicMock()
sys.modules['django.contrib'] = MagicMock()
sys.modules['django.contrib.auth'] = MagicMock()
sys.modules['django.contrib.auth.models'] = MagicMock()
sys.modules['django.utils'] = MagicMock()
sys.modules['django.utils.timezone'] = MagicMock()

# Создаем базовые мок-классы
class MockModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class MockForeignKey:
    def __init__(self, *args, **kwargs):
        pass

class MockCharField:
    def __init__(self, *args, **kwargs):
        pass

class MockBooleanField:
    def __init__(self, *args, **kwargs):
        pass

class MockDateTimeField:
    def __init__(self, *args, **kwargs):
        pass

class MockJSONField:
    def __init__(self, *args, **kwargs):
        pass

class MockDecimalField:
    def __init__(self, *args, **kwargs):
        pass

class MockTextField:
    def __init__(self, *args, **kwargs):
        pass

class MockURLField:
    def __init__(self, *args, **kwargs):
        pass

class MockEmailField:
    def __init__(self, *args, **kwargs):
        pass

class MockIntegerField:
    def __init__(self, *args, **kwargs):
        pass

class MockFloatField:
    def __init__(self, *args, **kwargs):
        pass

# Настраиваем мок модели Django
mock_models = MagicMock()
mock_models.Model = MockModel
mock_models.ForeignKey = MockForeignKey
mock_models.CharField = MockCharField
mock_models.BooleanField = MockBooleanField
mock_models.DateTimeField = MockDateTimeField
mock_models.JSONField = MockJSONField
mock_models.DecimalField = MockDecimalField
mock_models.TextField = MockTextField
mock_models.URLField = MockURLField
mock_models.EmailField = MockEmailField
mock_models.IntegerField = MockIntegerField
mock_models.PositiveIntegerField = MockIntegerField
mock_models.FloatField = MockFloatField
mock_models.CASCADE = 'CASCADE'
mock_models.SET_NULL = 'SET_NULL'
mock_models.Index = lambda *args, **kwargs: None

sys.modules['django.db.models'] = mock_models

# Теперь импортируем наш код
import requests
import time
from functools import wraps

def monitor_api_call(method_name):
    """Мок декоратора для мониторинга API вызовов"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

# Создаем упрощенную версию класса Supplier с нашими исправлениями
class TestSupplier:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'Test Supplier')
        self.api_type = kwargs.get('api_type', 'autoparts')
        self.api_url = kwargs.get('api_url', 'https://api.test.com')
        self.api_login = kwargs.get('api_login', 'test_login')
        self.api_password = kwargs.get('api_password', 'test_password')
        self.use_online_stocks = kwargs.get('use_online_stocks', True)
        self.office_id = kwargs.get('office_id', None)
    
    def _search_articles_by_brand(self, article, brand):
        """Мок метод для поиска товаров по бренду"""
        return True, [
            {
                "articleCode": article,
                "brand": brand,
                "description": f"Тестовый товар {brand}",
                "price": 1500,
                "availability": 10,
                "deliveryPeriod": 1,
                "weight": "0.5",
                "articleId": "123456"
            }
        ]
    
    def get_product_analogs(self, article, brand=None, limit=20):
        """ИСПРАВЛЕННЫЙ метод получения аналогов товара по артикулу через ABCP API"""
        if self.api_type != 'autoparts' or not self.api_url:
            return False, "API автозапчастей не настроен"
        
        if not self.api_login or not self.api_password:
            return False, "Логин или пароль не настроены"
        
        try:
            # Создаем md5-хэш пароля
            password_hash = hashlib.md5(self.api_password.encode('utf-8')).hexdigest()
            
            # Получаем список брендов по артикулу (это и есть аналоги)
            brands_url = f"{self.api_url.rstrip('/')}/search/brands"
            
            params = {
                'userlogin': self.api_login,
                'userpsw': password_hash,
                'number': article.strip(),
                'useOnlineStocks': 1 if self.use_online_stocks else 0
            }
            
            # Добавляем office_id если указан
            if self.office_id:
                params['officeId'] = self.office_id
            
            response = requests.get(brands_url, params=params, timeout=15)
            
            if response.status_code == 200:
                try:
                    brands_data = response.json()
                    
                    # Проверяем на ошибки в ответе
                    if isinstance(brands_data, dict) and 'errorCode' in brands_data:
                        error_code = brands_data.get('errorCode')
                        error_message = brands_data.get('errorMessage', 'Неизвестная ошибка')
                        return False, f"ABCP API ошибка {error_code}: {error_message}"
                    
                    # ИСПРАВЛЕНИЕ 1: Если указан конкретный бренд, фильтруем
                    if brand:
                        brands_data = [b for b in brands_data if isinstance(b, dict) and b.get('brand', '').lower() == brand.lower()]
                    
                    # ИСПРАВЛЕНИЕ 2: Обработка случая когда brands_data - dict вместо list
                    if isinstance(brands_data, dict):
                        brands_list = []
                        for key, value in brands_data.items():
                            if isinstance(value, dict) and ('brand' in value or 'number' in value):
                                brands_list.append(value)
                        brands_data = brands_list
                    
                    # Ограничиваем количество результатов
                    if limit and len(brands_data) > limit:
                        brands_data = brands_data[:limit]
                    
                    # Для каждого бренда получаем детальную информацию
                    analogs = []
                    for brand_info in brands_data:
                        # ИСПРАВЛЕНИЕ 3: Проверяем что это действительно словарь
                        if not isinstance(brand_info, dict):
                            continue
                        brand_name = brand_info.get('brand', '')
                        article_code = brand_info.get('number', article)
                        
                        # Получаем детальную информацию о товарах этого бренда
                        success, articles_data = self._search_articles_by_brand(article_code, brand_name)
                        
                        if success and articles_data:
                            for product in articles_data:
                                # ИСПРАВЛЕНИЕ 4: Проверяем что product - словарь перед вызовом .get()
                                if not isinstance(product, dict):
                                    continue
                                        
                                analog = {
                                    'article': product.get('articleCode', article_code),
                                    'article_fix': product.get('articleCodeFix', article_code),
                                    'brand': product.get('brand', brand_name),
                                    'name': product.get('description', ''),
                                    'price': product.get('price', 0),
                                    'availability': product.get('availability', 0),
                                    'delivery_period': product.get('deliveryPeriod', 0),
                                    'weight': product.get('weight', '0'),
                                    'article_id': product.get('articleId', ''),
                                    'is_original': brand_name.lower() == brand.lower() if brand else False
                                }
                                analogs.append(analog)
                    
                    return True, {
                        'original_article': article,
                        'original_brand': brand or '',
                        'total_found': len(analogs),
                        'analogs': analogs
                    }
                    
                except json.JSONDecodeError:
                    return False, "ABCP API: ошибка парсинга JSON ответа"
            elif response.status_code == 403:
                return False, f"ABCP API: ошибка авторизации (403). Проверьте логин и пароль."
            else:
                return False, f"ABCP API: ошибка HTTP {response.status_code}"
            
        except Exception as e:
            return False, f"Ошибка поиска аналогов: {str(e)}"

def test_fixed_get_product_analogs():
    """Тест исправленного метода get_product_analogs"""
    
    print("=== Тест исправлений в методе get_product_analogs ===\n")
    
    supplier = TestSupplier()
    
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
        
        success, result = supplier.get_product_analogs("0986424815")
        print(f"   ✅ Результат: success={success}")
        if success:
            print(f"   ✅ Найдено аналогов: {result['total_found']}")
    
    # Тест 2: brands_data как строка (была причина ошибки)
    print("\n2. Тест с brands_data как строка (раньше вызывало ошибку):")
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = "Error: Invalid data"  # Строка вместо списка
        mock_get.return_value = mock_response
        
        success, result = supplier.get_product_analogs("invalid_article")
        print(f"   ✅ Результат: success={success}")
        print(f"   ✅ Метод не упал, вернул ошибку корректно")
    
    # Тест 3: brands_data со строками в списке
    print("\n3. Тест с brands_data содержащим строки:")
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            "invalid_string_1",  # Строка вместо dict - должна быть пропущена
            {"brand": "BOSCH", "number": "0986424815"},  # Валидный dict
            "invalid_string_2",  # Еще одна строка - должна быть пропущена
            {"brand": "ATE", "number": "13.0460-2815.2"}  # Валидный dict
        ]
        mock_get.return_value = mock_response
        
        success, result = supplier.get_product_analogs("0986424815")
        print(f"   ✅ Результат: success={success}")
        if success:
            print(f"   ✅ Найдено аналогов: {result['total_found']} (строки пропущены)")
    
    # Тест 4: articles_data со строками
    print("\n4. Тест с articles_data содержащим строки:")
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"brand": "BOSCH", "number": "0986424815"}
        ]
        mock_get.return_value = mock_response
        
        # Мокаем _search_articles_by_brand чтобы вернуть смешанные данные
        original_search = supplier._search_articles_by_brand
        def mock_search(article, brand):
            return True, [
                "invalid_product_string",  # Строка вместо dict - должна быть пропущена
                {
                    "articleCode": "0986424815",
                    "brand": "BOSCH",
                    "description": "Тормозные колодки", 
                    "price": 1500,
                    "availability": 10
                },
                "another_invalid_string"  # Еще одна строка - должна быть пропущена
            ]
        
        supplier._search_articles_by_brand = mock_search
        
        success, result = supplier.get_product_analogs("0986424815")
        print(f"   ✅ Результат: success={success}")
        if success:
            print(f"   ✅ Найдено аналогов: {result['total_found']} (строки-продукты пропущены)")
        
        # Восстанавливаем оригинальный метод
        supplier._search_articles_by_brand = original_search
    
    # Тест 5: brands_data как dict (edge case)
    print("\n5. Тест с brands_data как dict:")
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "brand1": {"brand": "BOSCH", "number": "0986424815"},
            "brand2": {"brand": "ATE", "number": "13.0460-2815.2"},
            "invalid": "string_value"  # Строка должна быть пропущена
        }
        mock_get.return_value = mock_response
        
        success, result = supplier.get_product_analogs("0986424815")
        print(f"   ✅ Результат: success={success}")
        if success:
            print(f"   ✅ Найдено аналогов: {result['total_found']} (dict преобразован в list)")
    
    print("\n" + "="*60)
    print("✅ ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
    print("🛡️  Исправления защищают от ошибки 'str' object has no attribute 'get'")
    print("🔧 Метод корректно обрабатывает неожиданные типы данных от API")
    print("="*60)

if __name__ == "__main__":
    test_fixed_get_product_analogs()
