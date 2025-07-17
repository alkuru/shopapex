#!/usr/bin/env python
"""
Ультра-детальная отладка метода get_product_analogs для поиска точного места ошибки
"""

import os
import django
import traceback
import hashlib
import requests
import json

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def debug_api_call():
    """Делаем прямой вызов к ABCP API для отладки"""
    try:
        # Находим ABCP поставщика
        supplier = Supplier.objects.filter(api_type='autoparts').first()
        
        if not supplier:
            print("❌ ABCP поставщик не найден")
            return
            
        print(f"✅ Тестируем поставщика: {supplier.name}")
        
        # Создаем md5-хэш пароля
        password_hash = hashlib.md5(supplier.api_password.encode('utf-8')).hexdigest()
        
        # Тестируем вызов brands API с проблемным артикулом
        test_article = "1234567890"
        brands_url = f"{supplier.api_url.rstrip('/')}/search/brands"
        
        params = {
            'userlogin': supplier.api_login,
            'userpsw': password_hash,
            'number': test_article.strip(),
            'useOnlineStocks': 1 if supplier.use_online_stocks else 0
        }
        
        print(f"\n🔍 Делаем запрос к: {brands_url}")
        print(f"Параметры: {params}")
        
        response = requests.get(brands_url, params=params, timeout=15)
        
        print(f"\n📡 Ответ от API:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Raw Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                brands_data = response.json()
                print(f"\n📊 Разбор JSON ответа:")
                print(f"Тип: {type(brands_data)}")
                
                if isinstance(brands_data, dict):
                    print(f"Ключи словаря: {list(brands_data.keys())}")
                    for key, value in brands_data.items():
                        print(f"  {key}: {type(value)} = {str(value)[:100]}...")
                        
                elif isinstance(brands_data, list):
                    print(f"Длина списка: {len(brands_data)}")
                    for i, item in enumerate(brands_data[:3]):  # Показываем первые 3
                        print(f"  [{i}]: {type(item)} = {str(item)[:100]}...")
                        if isinstance(item, dict):
                            print(f"    Ключи: {list(item.keys())}")
                else:
                    print(f"Неожиданный тип: {type(brands_data)}")
                
                # Теперь тестируем проблемный код
                print(f"\n🔧 Тестируем обработку данных:")
                
                # Проверяем тип данных ответа
                if not isinstance(brands_data, (list, dict)):
                    print(f"❌ Неожиданный тип данных в ответе: {type(brands_data)}")
                    return
                
                # Проверяем на ошибки в ответе (если это словарь)
                if isinstance(brands_data, dict) and 'errorCode' in brands_data:
                    error_code = brands_data.get('errorCode')
                    error_message = brands_data.get('errorMessage', 'Неизвестная ошибка')
                    print(f"❌ ABCP API ошибка {error_code}: {error_message}")
                    return
                
                # Приводим к списку словарей
                if isinstance(brands_data, dict):
                    print("🔄 Преобразуем dict к списку...")
                    # Если ответ - словарь, возможно это единичный объект или структура с данными
                    if 'brands' in brands_data:
                        brands_list = brands_data['brands']
                        print(f"  Найден ключ 'brands': {type(brands_list)}")
                    elif 'data' in brands_data:
                        brands_list = brands_data['data']
                        print(f"  Найден ключ 'data': {type(brands_list)}")
                    else:
                        # Если словарь содержит поля бренда, то это единичный объект
                        if 'brand' in brands_data or 'number' in brands_data:
                            brands_list = [brands_data]
                            print(f"  Создали список из одного объекта: {type(brands_list)}")
                        else:
                            brands_list = []
                            print(f"  Создали пустой список")
                else:
                    brands_list = brands_data
                    print(f"🔄 Используем исходный список: {type(brands_list)}")
                
                # Убеждаемся что у нас список
                if not isinstance(brands_list, list):
                    print(f"❌ Ожидался список брендов, получен {type(brands_list)}")
                    return
                
                print(f"✅ Получили список из {len(brands_list)} элементов")
                
                # Фильтруем только объекты типа dict
                print("🔍 Проверяем типы элементов списка:")
                valid_brands = []
                for i, item in enumerate(brands_list):
                    print(f"  [{i}]: {type(item)}")
                    if isinstance(item, dict):
                        valid_brands.append(item)
                        print(f"    ✅ Добавлен к валидным")
                    else:
                        print(f"    ❌ Пропущен (не dict)")
                
                print(f"✅ Валидных элементов: {len(valid_brands)}")
                
                # Теперь проверяем итерацию по валидным брендам
                print("\n🔄 Итерируемся по валидным брендам:")
                for i, brand_info in enumerate(valid_brands[:2]):  # Только первые 2
                    print(f"  Бренд {i}:")
                    print(f"    Тип: {type(brand_info)}")
                    if isinstance(brand_info, dict):
                        print(f"    Ключи: {list(brand_info.keys())}")
                        brand_name = brand_info.get('brand', '')
                        article_code = brand_info.get('number', test_article)
                        print(f"    brand: {brand_name}")
                        print(f"    number: {article_code}")
                    else:
                        print(f"    ❌ НЕ СЛОВАРЬ! Это {type(brand_info)}")
                        
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_api_call()
