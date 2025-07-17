#!/usr/bin/env python
"""
Прямой вызов к search/articles API для понимания структуры ответа
"""

import os
import django
import hashlib
import requests
import json

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def test_articles_api_direct():
    """Прямой вызов к search/articles API"""
    try:
        # Находим ABCP поставщика
        supplier = Supplier.objects.filter(api_type='autoparts').first()
        
        if not supplier:
            print("❌ ABCP поставщик не найден")
            return
            
        print(f"✅ Тестируем поставщика: {supplier.name}")
        
        # Создаем md5-хэш пароля
        password_hash = hashlib.md5(supplier.api_password.encode('utf-8')).hexdigest()
        
        # Формируем URL для поиска по артикулу
        search_url = f"{supplier.api_url.rstrip('/')}/search/articles"
        
        # Тестируем с известными данными
        test_cases = [
            {"article": "1234567890", "brand": "testBrandNewD"},
            {"article": "INVALID_ARTICLE", "brand": "INVALID_BRAND"},
            {"article": "1234567890", "brand": ""},  # Пустой бренд
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"\n--- Тест {i+1}: {test_case} ---")
            
            params = {
                'userlogin': supplier.api_login,
                'userpsw': password_hash,
                'number': test_case['article'].strip(),
                'brand': test_case['brand'].strip()
            }
            
            # Добавляем дополнительные параметры
            if supplier.office_id:
                params['officeId'] = supplier.office_id
            
            if supplier.use_online_stocks:
                params['useOnlineStocks'] = 1
            
            # Добавляем адрес доставки если не самовывоз
            if supplier.default_shipment_address != '0':
                params['shipmentAddress'] = supplier.default_shipment_address
            
            print(f"📡 Делаем запрос к: {search_url}")
            print(f"Параметры: {params}")
            
            response = requests.get(search_url, params=params, timeout=15)
            
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {response.headers}")
            print(f"Raw Response: {response.text[:300]}...")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"📊 JSON данные:")
                    print(f"Тип: {type(data)}")
                    
                    if isinstance(data, dict):
                        print(f"Ключи словаря: {list(data.keys())}")
                        
                        # Проверяем на ошибки
                        if 'errorCode' in data:
                            error_code = data.get('errorCode')
                            error_message = data.get('errorMessage', 'Неизвестная ошибка')
                            print(f"❌ ABCP API ошибка {error_code}: {error_message}")
                        else:
                            for key, value in data.items():
                                print(f"  {key}: {type(value)} = {str(value)[:100]}...")
                                
                    elif isinstance(data, list):
                        print(f"Список из {len(data)} элементов")
                        for j, item in enumerate(data[:2]):
                            print(f"  [{j}]: {type(item)} = {str(item)[:100]}...")
                    else:
                        print(f"Неожиданный тип: {type(data)}")
                        print(f"Значение: {data}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
            else:
                print(f"❌ HTTP ошибка: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")

if __name__ == "__main__":
    test_articles_api_direct()
