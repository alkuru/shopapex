#!/usr/bin/env python
"""
Скрипт для загрузки и тестирования реальных товаров из ABCP API
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

def load_real_products():
    """Загружает реальные товары из ABCP API"""
    
    print("🔍 Поиск поставщика VintTop.ru...")
    
    try:
        supplier = Supplier.objects.get(name__icontains='vinttop')
        print(f"✅ Найден поставщик: {supplier.name} (ID: {supplier.id})")
        
    except Supplier.DoesNotExist:
        print("❌ Поставщик VintTop.ru не найден!")
        return False
    
    print(f"\n🔧 Тестирование поиска товаров по популярным артикулам...")
    
    # Список популярных артикулов для тестирования
    test_articles = [
        "0986424815",  # Bosch тормозные колодки
        "1987949678",  # Bosch фильтр
        "BP1234",      # Общий артикул
        "GF456",       # Тест
        "MANN",        # По бренду
        "oil",         # По ключевому слову
        "brake",       # Тормоза
        "filter",      # Фильтры
        "spark",       # Свечи
        "light"        # Фары
    ]
    
    all_products = []
    
    for article in test_articles:
        print(f"\n🔎 Поиск по запросу: '{article}'")
        try:
            success, result = supplier.search_products_by_article(article)
            
            if success and isinstance(result, list) and len(result) > 0:
                print(f"   ✅ Найдено: {len(result)} товаров")
                
                # Берем первые 2 товара из каждого поиска
                for item in result[:2]:
                    if isinstance(item, dict) and item not in all_products:
                        all_products.append(item)
                        print(f"      + Добавлен: {item.get('name', 'Без названия')[:50]}...")
                        
                        # Ограничиваем общее количество
                        if len(all_products) >= 10:
                            break
            else:
                print(f"   ⚠️  Ничего не найдено")
                
        except Exception as e:
            print(f"   ❌ Ошибка поиска: {e}")
        
        # Если набрали достаточно товаров, выходим
        if len(all_products) >= 10:
            break
    
    print(f"\n📦 Собрано {len(all_products)} уникальных товаров для загрузки")
    
    if not all_products:
        print("❌ Не удалось найти товары для загрузки")
        return False
    
    print(f"\n💾 Загрузка товаров в базу данных...")
    
    # Создаем тестовую категорию если её нет
    test_category, created = ProductCategory.objects.get_or_create(
        name="Тестовые товары ABCP",
        defaults={
            'description': 'Товары загруженные для тестирования интеграции ABCP API',
            'is_active': True,
            'order': 0
        }
    )
    
    if created:
        print(f"   ✅ Создана категория: {test_category.name}")
    
    loaded_count = 0
    updated_count = 0
    
    with transaction.atomic():
        for item_data in all_products:
            try:
                # Извлекаем данные товара
                article = item_data.get('number', item_data.get('code', f'ART-{loaded_count}'))
                name = item_data.get('name', item_data.get('title', 'Товар без названия'))
                brand_name = item_data.get('brand', 'NoName')
                price = float(item_data.get('price', 0))
                
                # Создаем или получаем бренд
                brand, created = Brand.objects.get_or_create(
                    name=brand_name,
                    defaults={'is_active': True}
                )
                
                # Создаем или обновляем товар
                product, created = Product.objects.update_or_create(
                    article=article,
                    defaults={
                        'name': name[:300],  # Ограничиваем длину
                        'category': test_category,
                        'brand': brand,
                        'price': price,
                        'stock_quantity': 10,  # Тестовое количество
                        'is_active': True,
                        'primary_supplier': supplier,
                        'description': f'Товар загружен из ABCP API для тестирования. Данные: {item_data}'
                    }
                )
                
                if created:
                    loaded_count += 1
                    print(f"   ✅ Создан товар: {article} - {name[:50]}...")
                else:
                    updated_count += 1
                    print(f"   🔄 Обновлен товар: {article} - {name[:50]}...")
                    
            except Exception as e:
                print(f"   ❌ Ошибка загрузки товара: {e}")
                continue
    
    print(f"\n🎯 РЕЗУЛЬТАТ ЗАГРУЗКИ:")
    print(f"   ✅ Создано товаров: {loaded_count}")
    print(f"   🔄 Обновлено товаров: {updated_count}")
    print(f"   📊 Всего обработано: {loaded_count + updated_count}")
    
    return loaded_count + updated_count > 0

def test_product_search():
    """Тестирует поиск загруженных товаров"""
    
    print(f"\n🔍 ТЕСТИРОВАНИЕ ПОИСКА ЗАГРУЖЕННЫХ ТОВАРОВ")
    print("=" * 60)
    
    # Получаем загруженные товары
    products = Product.objects.filter(
        primary_supplier__name__icontains='vinttop'
    ).select_related('brand', 'category')[:10]
    
    if not products:
        print("❌ Нет загруженных товаров для тестирования")
        return False
    
    print(f"📦 Найдено {products.count()} товаров в базе")
    
    for product in products:
        print(f"\n📝 Товар: {product.name}")
        print(f"   🏷️  Артикул: {product.article}")
        print(f"   🏭 Бренд: {product.brand.name}")
        print(f"   💰 Цена: {product.price} руб.")
        print(f"   📦 Остаток: {product.stock_quantity}")
        print(f"   ✅ Активен: {'Да' if product.is_active else 'Нет'}")
    
    print(f"\n🔍 ТЕСТИРОВАНИЕ ПОИСКА ЧЕРЕЗ API")
    print("-" * 40)
    
    supplier = products.first().primary_supplier
    
    # Тестируем поиск по артикулам загруженных товаров
    for product in products[:3]:  # Берем первые 3 для теста
        print(f"\n🔎 Поиск в API по артикулу: {product.article}")
        try:
            success, result = supplier.search_products_by_article(product.article)
            
            if success and isinstance(result, list):
                found_count = len(result)
                print(f"   ✅ Найдено в API: {found_count} товаров")
                
                if found_count > 0:
                    # Показываем первый найденный товар
                    first_item = result[0]
                    if isinstance(first_item, dict):
                        api_name = first_item.get('name', 'Без названия')
                        api_price = first_item.get('price', 'N/A')
                        api_brand = first_item.get('brand', 'N/A')
                        
                        print(f"   📋 API товар: {api_name}")
                        print(f"   💰 API цена: {api_price}")
                        print(f"   🏭 API бренд: {api_brand}")
                        
                        # Сравниваем с локальными данными
                        print(f"   🔄 Локальный товар: {product.name}")
                        print(f"   💰 Локальная цена: {product.price}")
                        print(f"   🏭 Локальный бренд: {product.brand.name}")
                        
                        if str(api_price) != str(product.price):
                            print(f"   ⚠️  ВНИМАНИЕ: Цены отличаются!")
            else:
                print(f"   ❌ Товар не найден в API: {result}")
                
        except Exception as e:
            print(f"   ❌ Ошибка поиска: {e}")
    
    return True

def show_admin_urls():
    """Показывает полезные URL для работы с товарами"""
    
    print(f"\n🔗 ПОЛЕЗНЫЕ ССЫЛКИ ДЛЯ РАБОТЫ С ТОВАРАМИ:")
    print("=" * 60)
    print(f"📊 Товары в админке:")
    print(f"   http://127.0.0.1:8000/admin/catalog/product/")
    print(f"📋 Категории товаров:")
    print(f"   http://127.0.0.1:8000/admin/catalog/productcategory/")
    print(f"🏭 Бренды:")
    print(f"   http://127.0.0.1:8000/admin/catalog/brand/")
    print(f"🔧 Поставщик VintTop:")
    print(f"   http://127.0.0.1:8000/admin/catalog/supplier/4/change/")
    print(f"🌐 Каталог на сайте:")
    print(f"   http://127.0.0.1:8000/catalog/")
    print(f"🔍 Поиск на сайте:")
    print(f"   http://127.0.0.1:8000/catalog/search/")

if __name__ == "__main__":
    print("🚀 Загрузка и тестирование реальных товаров ABCP API")
    print("=" * 60)
    
    try:
        # Загружаем товары
        if load_real_products():
            print(f"\n✅ ТОВАРЫ УСПЕШНО ЗАГРУЖЕНЫ!")
            
            # Тестируем поиск
            if test_product_search():
                print(f"\n✅ ПОИСК ПРОТЕСТИРОВАН УСПЕШНО!")
            
            # Показываем полезные ссылки
            show_admin_urls()
            
            print(f"\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
            print(f"📝 Теперь можно работать с реальными товарами")
            
        else:
            print(f"\n❌ ОШИБКА ЗАГРУЗКИ ТОВАРОВ")
            print(f"🔧 Проверьте подключение к API")
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
