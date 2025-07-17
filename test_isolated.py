#!/usr/bin/env python
"""
Полностью изолированный тест без вызовов к API
"""

import os
import django
import traceback
import json

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

# Монкей-патчинг для изоляции от API
def mock_search_articles_by_brand(self, article, brand):
    """Мок метод _search_articles_by_brand"""
    print(f"🎭 MOCK: _search_articles_by_brand('{article}', '{brand}')")
    
    # Имитируем различные сценарии ответов
    if article == "ERROR_ARTICLE":
        # Имитируем ошибку - возвращаем строку вместо кортежа
        return "Ошибка API"  # ЭТО МОЖЕТ БЫТЬ ИСТОЧНИКОМ ПРОБЛЕМЫ!
    elif article == "EMPTY_ARTICLE":
        return False, "Нет результатов"
    elif article == "SUCCESS_ARTICLE":
        return True, [
            {
                'articleCode': article,
                'articleCodeFix': article,
                'brand': brand,
                'description': 'Тестовый товар',
                'price': 100.0,
                'availability': 5,
                'deliveryPeriod': 1,
                'weight': '0.5',
                'articleId': 'test123'
            }
        ]
    else:
        # Имитируем ответ с неправильной структурой
        return True, "неправильная структура"  # И ЭТО ТОЖЕ!

def test_isolated():
    """Изолированный тест"""
    try:
        # Находим ABCP поставщика
        supplier = Supplier.objects.filter(api_type='autoparts').first()
        
        if not supplier:
            print("❌ ABCP поставщик не найден")
            return
        
        # Заменяем метод на мок
        original_method = supplier._search_articles_by_brand
        supplier._search_articles_by_brand = lambda article, brand: mock_search_articles_by_brand(supplier, article, brand)
        
        print(f"✅ Тестируем поставщика: {supplier.name}")
        
        # Имитируем brands_data из реального API
        fake_brands_data = {
            "testBrand1": {
                "availability": 1,
                "brand": "TestBrand",
                "description": "",
                "number": "SUCCESS_ARTICLE",
                "numberFix": "SUCCESS_ARTICLE"
            },
            "testBrand2": {
                "availability": 1,
                "brand": "ErrorBrand",
                "description": "",
                "number": "ERROR_ARTICLE",
                "numberFix": "ERROR_ARTICLE"
            }
        }
        
        print(f"📊 Имитируем brands_data: {fake_brands_data}")
        
        # Теперь имитируем обработку как в get_product_analogs
        try:
            article = "TEST123"
            brand = None
            limit = 20
            
            brands_data = fake_brands_data
            
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
            
            # Для каждого бренда получаем детальную информацию
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
                print(f"📡 Вызываем _search_articles_by_brand...")
                
                try:
                    result = supplier._search_articles_by_brand(article_code, brand_name)
                    print(f"Результат: {result}")
                    print(f"Тип результата: {type(result)}")
                    
                    # ЗДЕСЬ МОЖЕТ БЫТЬ ПРОБЛЕМА!
                    if isinstance(result, tuple) and len(result) == 2:
                        success, articles_data = result
                        print(f"success: {success}, articles_data: {type(articles_data)}")
                    else:
                        print(f"❌ Неожиданный формат результата: {result}")
                        # Если результат не кортеж, а строка, то в следующем коде будет ошибка
                        success = False
                        articles_data = result  # ЭТО МОЖЕТ БЫТЬ СТРОКА!
                    
                    if success and articles_data:
                        print(f"📦 Обрабатываем articles_data: {type(articles_data)}")
                        
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
                        elif isinstance(articles_data, list):
                            products_list = articles_data
                            print(f"Используем исходные данные как список")
                        else:
                            # ВОТ ОНА ПРОБЛЕМА! Если articles_data - строка, то мы попадаем сюда
                            print(f"❌ articles_data не список и не словарь: {type(articles_data)}")
                            print(f"Значение: {articles_data}")
                            
                            # А потом где-то в коде может быть попытка вызвать .get() на этой строке
                            continue
                        
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
                                
                            # Создаем аналог - ЗДесь тоже может быть ошибка если product - строка
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
                                traceback.print_exc()
                                
                    else:
                        print(f"❌ Ошибка или нет данных: success={success}, articles_data={articles_data}")
                        
                except Exception as e:
                    print(f"❌ ОШИБКА в обработке бренда: {e}")
                    traceback.print_exc()
            
            print(f"\n✅ Найдено аналогов: {len(analogs)}")
            
            # Восстанавливаем оригинальный метод
            supplier._search_articles_by_brand = original_method
            
        except Exception as e:
            print(f"❌ ОШИБКА в обработке: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_isolated()
