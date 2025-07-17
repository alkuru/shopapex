#!/usr/bin/env python
"""
Тест только обработки brands_data без вызова _search_articles_by_brand
"""

import os
import django
import traceback
import hashlib
import requests

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def test_brands_processing():
    """Тестируем только обработку brands_data"""
    try:
        # Находим ABCP поставщика
        supplier = Supplier.objects.filter(api_type='autoparts').first()
        
        if not supplier:
            print("❌ ABCP поставщик не найден")
            return
            
        print(f"✅ Тестируем поставщика: {supplier.name}")
        
        # Имитируем получение данных от API
        article = "1234567890"
        brand = None
        limit = 20
        
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
        
        print(f"📡 Делаем запрос к brands API...")
        response = requests.get(brands_url, params=params, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            return
            
        brands_data = response.json()
        print(f"✅ Получили данные брендов: {type(brands_data)}")
        print(f"📊 Исходные данные: {brands_data}")
        
        # Теперь имитируем обработку как в методе get_product_analogs
        try:
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
                print("🔄 Преобразуем словарь в список...")
                brands_list = []
                for key, value in brands_data.items():
                    print(f"  Ключ: {key}, Значение: {type(value)}")
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
                brands_data = [b for b in brands_data if isinstance(b, dict) and b.get('brand', '').lower() == brand.lower()]
                print(f"✅ После фильтрации по бренду: {len(brands_data)} элементов")
            
            # Ограничиваем количество результатов
            if limit and len(brands_data) > limit:
                brands_data = brands_data[:limit]
                print(f"✂️ Ограничили до {limit} элементов")
            
            # Проверяем что все в порядке с циклом
            print(f"\n🔄 Начинаем итерацию по {len(brands_data)} брендам...")
            
            for i, brand_info in enumerate(brands_data):
                print(f"--- Бренд {i+1} ---")
                print(f"Тип: {type(brand_info)}")
                
                # Проверяем что это действительно словарь
                if not isinstance(brand_info, dict):
                    print(f"❌ Не dict, пропускаем")
                    continue
                    
                print(f"Ключи: {list(brand_info.keys())}")
                
                # Извлекаем данные
                brand_name = brand_info.get('brand', '')
                article_code = brand_info.get('number', article)
                print(f"Бренд: {brand_name}")
                print(f"Артикул: {article_code}")
                
                # Вместо вызова _search_articles_by_brand просто возвращаем фиктивные данные
                print(f"🔄 Имитируем успешный вызов _search_articles_by_brand...")
                
                # Создаем фиктивные данные товара
                fake_articles_data = [
                    {
                        'articleCode': article_code,
                        'articleCodeFix': article_code,
                        'brand': brand_name,
                        'description': 'Тестовый товар',
                        'price': 100.0,
                        'availability': 5,
                        'deliveryPeriod': 1,
                        'weight': '0.5',
                        'articleId': 'test123'
                    }
                ]
                
                print(f"✅ Обрабатываем {len(fake_articles_data)} фиктивных продуктов")
                
                # Убеждаемся что articles_data - это список
                products_list = fake_articles_data
                
                # Убеждаемся что это список
                if not isinstance(products_list, list):
                    print(f"❌ Ожидался список продуктов, получен {type(products_list)}")
                    continue
                    
                for j, product in enumerate(products_list):
                    print(f"  Продукт {j+1}: {type(product)}")
                    # Проверяем что продукт - это словарь
                    if not isinstance(product, dict):
                        print(f"    ❌ Не dict, пропускаем")
                        continue
                        
                    # Тест создания аналога
                    print(f"    🔧 Создаем аналог...")
                    
                    # ЭТО МЕСТО ГДЕ МОЖЕТ БЫТЬ ОШИБКА
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
                        print(f"    ✅ Аналог создан: {analog['article']} {analog['brand']}")
                        
                    except Exception as e:
                        print(f"    ❌ ОШИБКА при создании аналога: {e}")
                        print(f"    Тип продукта: {type(product)}")
                        print(f"    Значение продукта: {product}")
                        traceback.print_exc()
                
                # Для тестирования ограничимся первым брендом
                break
                
            print(f"\n✅ Обработка завершена успешно!")
            
        except Exception as e:
            print(f"❌ ОШИБКА в обработке: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_brands_processing()
