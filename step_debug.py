#!/usr/bin/env python
"""
Пошаговая отладка метода get_product_analogs
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

def step_by_step_debug():
    """Пошагово отлаживаем get_product_analogs"""
    try:
        # Находим ABCP поставщика
        supplier = Supplier.objects.filter(api_type='autoparts').first()
        
        if not supplier:
            print("❌ ABCP поставщик не найден")
            return
            
        print(f"✅ Тестируем поставщика: {supplier.name}")
        
        # Имитируем начало метода get_product_analogs
        article = "1234567890"
        brand = "UNKNOWN_BRAND"
        limit = 20
        
        print(f"\n🎯 Тестируем с артикулом: {article}, бренд: {brand}")
        
        # Создаем md5-хэш пароля
        password_hash = hashlib.md5(supplier.api_password.encode('utf-8')).hexdigest()
        
        # Получаем список брендов по артикулу
        brands_url = f"{supplier.api_url.rstrip('/')}/search/brands"
        
        params = {
            'userlogin': supplier.api_login,
            'userpsw': password_hash,
            'number': article.strip(),
            'useOnlineStocks': 1 if supplier.use_online_stocks else 0
        }
        
        print(f"\n📡 Делаем первый запрос к brands API...")
        response = requests.get(brands_url, params=params, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            return
            
        brands_data = response.json()
        print(f"✅ Получили данные брендов: {type(brands_data)}")
        
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
        
        print(f"📊 Исходные данные: {brands_data}")
        
        # Приводим к списку словарей
        if isinstance(brands_data, dict):
            print("🔄 Преобразуем словарь в список...")
            brands_list = []
            for key, value in brands_data.items():
                print(f"  Ключ: {key}, Значение: {type(value)} = {value}")
                if isinstance(value, dict) and ('brand' in value or 'number' in value):
                    brands_list.append(value)
                    print(f"    ✅ Добавлен к списку")
                else:
                    print(f"    ❌ Пропущен")
            brands_data = brands_list
            print(f"✅ Получили список из {len(brands_data)} элементов")
        
        # Убеждаемся что у нас список
        if not isinstance(brands_data, list):
            print(f"❌ Ожидался список брендов, получен {type(brands_data)}")
            return
        
        # Фильтруем только объекты типа dict
        original_count = len(brands_data)
        brands_data = [item for item in brands_data if isinstance(item, dict)]
        print(f"🔍 Отфильтровали dict объекты: {original_count} -> {len(brands_data)}")
        
        # Если указан конкретный бренд, фильтруем
        if brand:
            print(f"🔎 Фильтруем по бренду: {brand}")
            filtered_brands = []
            for b in brands_data:
                if isinstance(b, dict):
                    brand_name = b.get('brand', '')
                    print(f"  Проверяем: {brand_name} vs {brand}")
                    if brand_name.lower() == brand.lower():
                        filtered_brands.append(b)
                        print(f"    ✅ Совпадение!")
                    else:
                        print(f"    ❌ Не совпадает")
                else:
                    print(f"  ❌ Не dict: {type(b)}")
            brands_data = filtered_brands
            print(f"✅ После фильтрации по бренду: {len(brands_data)} элементов")
        
        # Ограничиваем количество результатов
        if limit and len(brands_data) > limit:
            brands_data = brands_data[:limit]
            print(f"✂️ Ограничили до {limit} элементов")
        
        # Теперь итерируемся по брендам
        print(f"\n🔄 Начинаем итерацию по {len(brands_data)} брендам...")
        analogs = []
        
        for i, brand_info in enumerate(brands_data):
            print(f"\n--- Бренд {i+1} ---")
            print(f"Тип: {type(brand_info)}")
            
            # Проверяем что это действительно словарь
            if not isinstance(brand_info, dict):
                print(f"❌ Не dict, пропускаем")
                continue
                
            brand_name = brand_info.get('brand', '')
            article_code = brand_info.get('number', article)
            print(f"Бренд: {brand_name}")
            print(f"Артикул: {article_code}")
            
            # Получаем детальную информацию о товарах этого бренда
            print(f"📡 Делаем запрос к articles API...")
            
            try:
                success, articles_data = supplier._search_articles_by_brand(article_code, brand_name)
                print(f"Результат: success={success}")
                
                if success:
                    print(f"Тип данных статей: {type(articles_data)}")
                    print(f"Данные статей: {str(articles_data)[:200]}...")
                    
                    # Убеждаемся что articles_data - это список или словарь
                    if isinstance(articles_data, dict):
                        if 'articles' in articles_data:
                            products_list = articles_data['articles']
                            print(f"Найден ключ 'articles': {type(products_list)}")
                        elif 'data' in articles_data:
                            products_list = articles_data['data']
                            print(f"Найден ключ 'data': {type(products_list)}")
                        else:
                            products_list = [articles_data]  # Единичный объект
                            print(f"Создан список из единичного объекта")
                    else:
                        products_list = articles_data
                        print(f"Используем исходные данные как список")
                    
                    # Убеждаемся что это список
                    if not isinstance(products_list, list):
                        print(f"❌ Ожидался список продуктов, получен {type(products_list)}")
                        continue
                        
                    print(f"✅ Обрабатываем {len(products_list)} продуктов")
                    
                    for j, product in enumerate(products_list):
                        print(f"  Продукт {j+1}: {type(product)}")
                        # Проверяем что продукт - это словарь
                        if not isinstance(product, dict):
                            print(f"    ❌ Не dict, пропускаем")
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
                        print(f"    ✅ Добавлен аналог: {analog['article']} {analog['brand']}")
                        
                        if len(analogs) >= 3:  # Ограничиваем для тестирования
                            print(f"  🛑 Достигли лимита для тестирования")
                            break
                            
                else:
                    print(f"❌ Ошибка поиска статей: {articles_data}")
                    
            except Exception as e:
                print(f"❌ ОШИБКА в запросе к articles API: {e}")
                traceback.print_exc()
                break
            
            if len(analogs) >= 3:  # Ограничиваем для тестирования
                break
        
        print(f"\n✅ Итого найдено аналогов: {len(analogs)}")
        for analog in analogs:
            print(f"  - {analog['article']} {analog['brand']} - {analog['name'][:30]}...")
        
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    step_by_step_debug()
