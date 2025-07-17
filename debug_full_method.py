#!/usr/bin/env python
"""
Создаем полную копию get_product_analogs для пошаговой отладки
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

def debug_get_product_analogs(supplier, article, brand=None, limit=20):
    """Отладочная версия get_product_analogs"""
    print(f"🎯 DEBUG: get_product_analogs('{article}', '{brand}', {limit})")
    
    if supplier.api_type != 'autoparts' or not supplier.api_url:
        return False, "API автозапчастей не настроен"
    
    if not supplier.api_login or not supplier.api_password:
        return False, "Логин или пароль не настроены"
    
    try:
        # Создаем md5-хэш пароля
        password_hash = hashlib.md5(supplier.api_password.encode('utf-8')).hexdigest()
        print(f"✅ Пароль хэширован")
        
        # Получаем список брендов по артикулу (это и есть аналоги)
        brands_url = f"{supplier.api_url.rstrip('/')}/search/brands"
        
        params = {
            'userlogin': supplier.api_login,
            'userpsw': password_hash,
            'number': article.strip(),
            'useOnlineStocks': 1 if supplier.use_online_stocks else 0
        }
        
        # Добавляем office_id если указан
        if supplier.office_id:
            params['officeId'] = supplier.office_id
        
        print(f"📡 Делаем запрос к {brands_url} с параметрами: {params}")
        response = requests.get(brands_url, params=params, timeout=15)
        print(f"📡 Получен ответ: {response.status_code}")
        
        if response.status_code == 200:
            try:
                brands_data = response.json()
                print(f"📊 JSON данные получены: {type(brands_data)}")
                print(f"📊 Содержимое: {brands_data}")
                
                # Проверяем тип данных ответа
                if not isinstance(brands_data, (list, dict)):
                    error_msg = f"ABCP API: неожиданный тип данных в ответе: {type(brands_data)}"
                    print(f"❌ {error_msg}")
                    return False, error_msg
                
                # Проверяем на ошибки в ответе (если это словарь)
                if isinstance(brands_data, dict) and 'errorCode' in brands_data:
                    error_code = brands_data.get('errorCode')
                    error_message = brands_data.get('errorMessage', 'Неизвестная ошибка')
                    error_msg = f"ABCP API ошибка {error_code}: {error_message}"
                    print(f"❌ {error_msg}")
                    return False, error_msg
                
                print(f"✅ Проверки пройдены")
                
                # Приводим к списку словарей
                if isinstance(brands_data, dict):
                    print(f"🔄 Преобразуем dict в список...")
                    brands_list = []
                    for key, value in brands_data.items():
                        print(f"  Обрабатываем ключ: {key} -> {type(value)}")
                        if isinstance(value, dict) and ('brand' in value or 'number' in value):
                            brands_list.append(value)
                            print(f"    ✅ Добавлен")
                        else:
                            print(f"    ❌ Пропущен")
                    brands_data = brands_list
                    print(f"✅ Получили список из {len(brands_data)} элементов")
                
                # Убеждаемся что у нас список
                if not isinstance(brands_data, list):
                    error_msg = f"ABCP API: ожидался список брендов, получен {type(brands_data)}"
                    print(f"❌ {error_msg}")
                    return False, error_msg
                
                # Фильтруем только объекты типа dict
                original_count = len(brands_data)
                brands_data = [item for item in brands_data if isinstance(item, dict)]
                print(f"🔍 Отфильтровали dict объекты: {original_count} -> {len(brands_data)}")
                
                # Если указан конкретный бренд, фильтруем
                if brand:
                    print(f"🔎 Фильтруем по бренду: {brand}")
                    filtered_data = []
                    for b in brands_data:
                        if isinstance(b, dict):
                            brand_name = b.get('brand', '')
                            print(f"  Проверяем бренд: {brand_name}")
                            if brand_name.lower() == brand.lower():
                                filtered_data.append(b)
                                print(f"    ✅ Совпадение")
                            else:
                                print(f"    ❌ Не совпадает")
                        else:
                            print(f"  ❌ Не dict: {type(b)}")
                    brands_data = filtered_data
                    print(f"✅ После фильтрации: {len(brands_data)} элементов")
                
                # Ограничиваем количество результатов
                if limit and len(brands_data) > limit:
                    brands_data = brands_data[:limit]
                    print(f"✂️ Ограничили до {limit} элементов")
                
                # Для каждого бренда получаем детальную информацию
                analogs = []
                print(f"🔄 Начинаем обработку {len(brands_data)} брендов...")
                
                for i, brand_info in enumerate(brands_data):
                    print(f"\n--- Бренд {i+1} ---")
                    print(f"Тип brand_info: {type(brand_info)}")
                    print(f"Значение brand_info: {brand_info}")
                    
                    # ЗДЕСЬ МОЖЕТ БЫТЬ ПРОБЛЕМА!
                    # Проверяем что это действительно словарь
                    if not isinstance(brand_info, dict):
                        print(f"❌ brand_info не dict, пропускаем")
                        continue
                    
                    print(f"✅ brand_info is dict")
                    
                    try:
                        brand_name = brand_info.get('brand', '')
                        print(f"✅ brand_name extracted: {brand_name}")
                    except Exception as e:
                        print(f"❌ Ошибка при извлечении brand_name: {e}")
                        print(f"brand_info тип: {type(brand_info)}")
                        print(f"brand_info значение: {brand_info}")
                        continue
                    
                    try:
                        article_code = brand_info.get('number', article)
                        print(f"✅ article_code extracted: {article_code}")
                    except Exception as e:
                        print(f"❌ Ошибка при извлечении article_code: {e}")
                        continue
                    
                    print(f"🎯 Бренд: {brand_name}, Артикул: {article_code}")
                    
                    # Получаем детальную информацию о товарах этого бренда
                    print(f"📡 Вызываем _search_articles_by_brand...")
                    try:
                        success, articles_data = supplier._search_articles_by_brand(article_code, brand_name)
                        print(f"✅ _search_articles_by_brand вернул: success={success}, type={type(articles_data)}")
                        
                        if success and articles_data:
                            print(f"📦 Обрабатываем articles_data...")
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
                                    
                                print(f"    ✅ Продукт является dict")
                                
                                # ЗДЕСЬ ТОЖЕ МОЖЕТ БЫТЬ ПРОБЛЕМА!
                                try:
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
                                    print(f"    ✅ Аналог создан: {analog['article']} {analog['brand']}")
                                    
                                except Exception as e:
                                    print(f"    ❌ ОШИБКА при создании аналога: {e}")
                                    print(f"    Тип продукта: {type(product)}")
                                    print(f"    Значение продукта: {product}")
                                    raise  # Пробрасываем исключение дальше
                        else:
                            print(f"❌ Нет данных от _search_articles_by_brand: {articles_data}")
                            
                    except Exception as e:
                        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА в обработке бренда: {e}")
                        print(f"Тип ошибки: {type(e).__name__}")
                        raise  # Пробрасываем исключение дальше
                
                print(f"\n✅ Обработка завершена. Найдено аналогов: {len(analogs)}")
                
                return True, {
                    'original_article': article,
                    'original_brand': brand or '',
                    'total_found': len(analogs),
                    'analogs': analogs
                }
                
            except json.JSONDecodeError:
                error_msg = "ABCP API: ошибка парсинга JSON ответа"
                print(f"❌ {error_msg}")
                return False, error_msg
        elif response.status_code == 403:
            error_msg = f"ABCP API: ошибка авторизации (403). Проверьте логин и пароль."
            print(f"❌ {error_msg}")
            return False, error_msg
        else:
            error_msg = f"ABCP API: ошибка HTTP {response.status_code}"
            print(f"❌ {error_msg}")
            return False, error_msg
        
    except Exception as e:
        error_msg = f"Ошибка поиска аналогов: {str(e)}"
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {error_msg}")
        print(f"Тип ошибки: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False, error_msg

def test_debug_version():
    """Тестируем отладочную версию"""
    try:
        # Находим ABCP поставщика
        supplier = Supplier.objects.filter(api_type='autoparts').first()
        
        if not supplier:
            print("❌ ABCP поставщик не найден")
            return
            
        print(f"✅ Тестируем поставщика: {supplier.name}")
        
        # Тестируем проблемный случай
        success, result = debug_get_product_analogs(
            supplier,
            article="1234567890",
            brand=None,
            limit=5
        )
        
        print(f"\n🎯 ФИНАЛЬНЫЙ РЕЗУЛЬТАТ:")
        print(f"Success: {success}")
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_debug_version()
