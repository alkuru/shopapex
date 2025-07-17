#!/usr/bin/env python
"""
Скрипт для загрузки дополнительных реальных товаров из ABCP API
"""
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier, Product, Brand, ProductCategory
from django.db import transaction
import time

def load_more_real_products(target_count=10):
    """Загружает дополнительные реальные товары из ABCP API"""
    
    print(f"🔍 Загрузка дополнительных {target_count} товаров из ABCP API...")
    
    try:
        supplier = Supplier.objects.get(name__icontains='vinttop')
        print(f"✅ Найден поставщик: {supplier.name} (ID: {supplier.id})")
        
    except Supplier.DoesNotExist:
        print("❌ Поставщик VintTop.ru не найден!")
        return False
    
    # Получаем уже существующие артикулы чтобы не дублировать
    existing_articles = set(Product.objects.filter(
        primary_supplier=supplier
    ).values_list('article', flat=True))
    
    print(f"📋 Уже загружено товаров: {len(existing_articles)}")
    print(f"🎯 Цель: загрузить еще {target_count} новых товаров")
    
    # Расширенный список поисковых запросов для большего разнообразия
    search_queries = [
        # Популярные автозапчасти
        "filter",      # Фильтры
        "brake",       # Тормоза  
        "oil",         # Масла
        "spark",       # Свечи зажигания
        "belt",        # Ремни
        "sensor",      # Датчики
        "lamp",        # Лампы
        "battery",     # Аккумуляторы
        
        # Конкретные артикулы популярных брендов
        "BOSCH",       # Бренд Bosch
        "MANN",        # Фильтры Mann
        "MOBIL",       # Масла Mobil
        "NGK",         # Свечи NGK
        "OSRAM",       # Лампы Osram
        "VARTA",       # Аккумуляторы Varta
        "CONTINENTAL", # Continental
        "MICHELIN",    # Шины Michelin
        
        # Популярные артикулы
        "WF0123",      # Фильтр воздушный
        "OF0456",      # Фильтр масляный
        "SP789",       # Свеча зажигания
        "BK123",       # Тормозные колодки
        "BT456",       # Ремень ГРМ
        "LM789",       # Лампа
        "SN123",       # Датчик
        "OL456",       # Масло
        
        # Числовые артикулы
        "12345",       # Общий поиск
        "67890",       # Общий поиск
        "11111",       # Общий поиск
        "22222",       # Общий поиск
        "33333",       # Общий поиск
    ]
    
    all_products = []
    processed_queries = 0
    
    print(f"\n🔍 Поиск товаров по {len(search_queries)} запросам...")
    
    for query in search_queries:
        processed_queries += 1
        print(f"\n🔎 [{processed_queries}/{len(search_queries)}] Поиск: '{query}'")
        
        try:
            success, result = supplier.search_products_by_article(query)
            
            if success and isinstance(result, list) and len(result) > 0:
                print(f"   ✅ Найдено: {len(result)} товаров")
                
                # Обрабатываем результаты
                new_products_from_query = 0
                for item in result:
                    if isinstance(item, dict):
                        # Извлекаем артикул
                        article = item.get('number', item.get('code', f'ART-{len(all_products)}'))
                        
                        # Проверяем, что товар новый
                        if article not in existing_articles and article not in [p.get('number', p.get('code')) for p in all_products]:
                            all_products.append(item)
                            existing_articles.add(article)
                            new_products_from_query += 1
                            
                            name = item.get('description', item.get('name', 'Товар'))[:50]
                            brand = item.get('brand', 'NoName')
                            price = item.get('price', 0)
                            
                            print(f"      + [{len(all_products)}] {article} - {name}... ({brand}, {price} руб.)")
                            
                            # Если набрали достаточно товаров, выходим
                            if len(all_products) >= target_count:
                                print(f"   🎯 Достигнута цель: {target_count} товаров!")
                                break
                
                print(f"   📦 Новых товаров из этого запроса: {new_products_from_query}")
            else:
                print(f"   ⚠️  Ничего не найдено или ошибка: {result[:100] if isinstance(result, str) else 'Пустой результат'}")
                
        except Exception as e:
            print(f"   ❌ Ошибка поиска: {e}")
        
        # Если набрали достаточно товаров, выходим
        if len(all_products) >= target_count:
            break
            
        # Небольшая пауза чтобы не перегружать API
        time.sleep(0.5)
    
    print(f"\n📦 Собрано {len(all_products)} новых товаров для загрузки")
    
    if not all_products:
        print("❌ Не удалось найти новые товары для загрузки")
        return False
    
    # Загружаем товары в базу данных
    print(f"\n💾 Загрузка товаров в базу данных...")
    
    # Получаем или создаем категорию
    test_category, created = ProductCategory.objects.get_or_create(
        name="Тестовые товары ABCP",
        defaults={
            'description': 'Товары загруженные для тестирования интеграции ABCP API',
            'is_active': True,
            'order': 0
        }
    )
    
    loaded_count = 0
    updated_count = 0
    error_count = 0
    
    with transaction.atomic():
        for i, item_data in enumerate(all_products, 1):
            try:
                print(f"\n📝 [{i}/{len(all_products)}] Обработка товара...")
                
                # Извлекаем данные товара
                article = item_data.get('number', item_data.get('code', f'ART-{i}'))
                name = item_data.get('description', item_data.get('name', 'Товар без названия'))
                brand_name = item_data.get('brand', 'NoName')
                price = float(item_data.get('price', 0))
                
                # Обрезаем длинные названия
                if len(name) > 300:
                    name = name[:297] + "..."
                
                print(f"   📋 Артикул: {article}")
                print(f"   🏷️  Название: {name[:50]}...")
                print(f"   🏭 Бренд: {brand_name}")
                print(f"   💰 Цена: {price} руб.")
                
                # Создаем или получаем бренд
                brand, brand_created = Brand.objects.get_or_create(
                    name=brand_name,
                    defaults={'is_active': True}
                )
                
                if brand_created:
                    print(f"   ✅ Создан новый бренд: {brand_name}")
                
                # Создаем или обновляем товар
                product, product_created = Product.objects.update_or_create(
                    article=article,
                    defaults={
                        'name': name,
                        'category': test_category,
                        'brand': brand,
                        'price': price,
                        'stock_quantity': 10,  # Тестовое количество
                        'is_active': True,
                        'primary_supplier': supplier,
                        'description': f'Товар загружен из ABCP API. Полные данные: {item_data}'
                    }
                )
                
                if product_created:
                    loaded_count += 1
                    print(f"   ✅ Создан товар в базе")
                else:
                    updated_count += 1
                    print(f"   🔄 Обновлен существующий товар")
                    
            except Exception as e:
                error_count += 1
                print(f"   ❌ Ошибка загрузки товара: {e}")
                continue
    
    print(f"\n🎯 РЕЗУЛЬТАТ ЗАГРУЗКИ:")
    print(f"   ✅ Создано новых товаров: {loaded_count}")
    print(f"   🔄 Обновлено товаров: {updated_count}")
    print(f"   ❌ Ошибок загрузки: {error_count}")
    print(f"   📊 Успешно обработано: {loaded_count + updated_count}")
    
    return loaded_count + updated_count > 0

def show_all_products():
    """Показывает все загруженные товары"""
    
    print(f"\n📊 ВСЕ ЗАГРУЖЕННЫЕ ТОВАРЫ:")
    print("=" * 80)
    
    products = Product.objects.filter(
        primary_supplier__name__icontains='vinttop'
    ).select_related('brand', 'category').order_by('-id')
    
    if not products:
        print("❌ Нет загруженных товаров")
        return
    
    print(f"📦 Всего товаров в базе: {products.count()}")
    
    for i, product in enumerate(products, 1):
        print(f"\n📝 [{i}] {product.article}")
        print(f"   🏷️  {product.name}")
        print(f"   🏭 Бренд: {product.brand.name}")
        print(f"   💰 Цена: {product.price} руб.")
        print(f"   📦 Остаток: {product.stock_quantity}")
        print(f"   📅 Создан: {product.created_at.strftime('%d.%m.%Y %H:%M')}")

def test_random_search():
    """Тестирует поиск по случайным товарам"""
    
    print(f"\n🔍 ТЕСТИРОВАНИЕ ПОИСКА ПО ЗАГРУЖЕННЫМ ТОВАРАМ:")
    print("=" * 60)
    
    # Получаем несколько случайных товаров для тестирования
    products = Product.objects.filter(
        primary_supplier__name__icontains='vinttop'
    ).order_by('?')[:3]  # Случайные 3 товара
    
    if not products:
        print("❌ Нет товаров для тестирования")
        return
    
    supplier = products.first().primary_supplier
    
    for product in products:
        print(f"\n🔎 Тестируем поиск товара: {product.article}")
        print(f"   📋 Локальное название: {product.name}")
        
        try:
            success, result = supplier.search_products_by_article(product.article)
            
            if success and isinstance(result, list) and len(result) > 0:
                print(f"   ✅ Найдено в API: {len(result)} товаров")
                
                # Показываем первый результат
                first_item = result[0]
                if isinstance(first_item, dict):
                    api_name = first_item.get('description', first_item.get('name', 'Без названия'))
                    api_price = first_item.get('price', 'N/A')
                    api_brand = first_item.get('brand', 'N/A')
                    
                    print(f"   📋 API название: {api_name[:60]}...")
                    print(f"   💰 API цена: {api_price} (локальная: {product.price})")
                    print(f"   🏭 API бренд: {api_brand} (локальный: {product.brand.name})")
            else:
                print(f"   ❌ Товар не найден в API")
                
        except Exception as e:
            print(f"   ❌ Ошибка API поиска: {e}")

if __name__ == "__main__":
    print("🚀 Загрузка дополнительных реальных товаров ABCP API")
    print("=" * 70)
    
    try:
        # Загружаем дополнительные товары
        if load_more_real_products(target_count=10):
            print(f"\n✅ ДОПОЛНИТЕЛЬНЫЕ ТОВАРЫ УСПЕШНО ЗАГРУЖЕНЫ!")
            
            # Показываем все товары
            show_all_products()
            
            # Тестируем поиск
            test_random_search()
            
            print(f"\n🔗 ПОЛЕЗНЫЕ ССЫЛКИ:")
            print(f"   📊 Товары в админке: http://127.0.0.1:8000/admin/catalog/product/")
            print(f"   🌐 Каталог сайта: http://127.0.0.1:8000/catalog/")
            print(f"   🔍 Поиск товаров: http://127.0.0.1:8000/catalog/search/")
            
            print(f"\n🎉 ЗАГРУЗКА ЗАВЕРШЕНА УСПЕШНО!")
            
        else:
            print(f"\n❌ ОШИБКА ЗАГРУЗКИ ДОПОЛНИТЕЛЬНЫХ ТОВАРОВ")
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
