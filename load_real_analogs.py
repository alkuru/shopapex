#!/usr/bin/env python3
"""
Загрузка реальных аналогов для товаров из базы через ABCP API
"""

import os
import sys
import django
import time
import random

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, ProductAnalog, Brand, ProductCategory
    from catalog.supplier_models import Supplier
    
    print("🔍 ЗАГРУЗКА РЕАЛЬНЫХ АНАЛОГОВ")
    print("=" * 40)
    
    # Получаем поставщика ABCP
    try:
        supplier = Supplier.objects.get(name='ABCP')
        print(f"✅ Поставщик найден: {supplier.name}")
    except Supplier.DoesNotExist:
        print("❌ Поставщик ABCP не найден")
        # Создадим поставщика ABCP если его нет
        supplier = Supplier.objects.create(
            name='ABCP',
            api_url='https://api.abcp.ru/',
            is_active=True
        )
        print(f"✅ Создан поставщик: {supplier.name}")
    
    # Получаем все товары из базы
    products = Product.objects.all()[:20]  # Берем первые 20 товаров для теста
    print(f"📊 Будем искать аналоги для {products.count()} товаров")
    
    total_analogs_found = 0
    
    for i, product in enumerate(products, 1):
        print(f"\n[{i}/{products.count()}] Ищем аналоги для: {product.article} - {product.name}")
        
        try:
            # Получаем аналоги через API
            analogs = supplier.get_product_analogs(product.article)
            
            if not analogs:
                print(f"   ❌ Аналоги не найдены")
                continue
            
            print(f"   ✅ Найдено {len(analogs)} аналогов")
            
            # Обрабатываем каждый аналог
            for analog_data in analogs:
                try:
                    # Извлекаем данные аналога
                    if isinstance(analog_data, dict):
                        analog_article = analog_data.get('article', '')
                        analog_name = analog_data.get('name', '')
                        analog_brand = analog_data.get('brand', '')
                        analog_price = analog_data.get('price', 0)
                    else:
                        print(f"   ⚠️  Некорректный формат данных аналога: {analog_data}")
                        continue
                    
                    if not analog_article:
                        continue
                    
                    # Находим или создаем бренд
                    if analog_brand:
                        brand, _ = Brand.objects.get_or_create(
                            name=analog_brand,
                            defaults={'description': f'Бренд {analog_brand}'}
                        )
                    else:
                        brand = product.brand
                    
                    # Создаем товар-аналог если его нет
                    analog_product, created = Product.objects.get_or_create(
                        article=analog_article,
                        defaults={
                            'name': analog_name or f'Аналог {analog_article}',
                            'category': product.category,
                            'brand': brand,
                            'price': analog_price or product.price,
                            'description': f"Аналог для {product.article}"
                        }
                    )
                    
                    if created:
                        print(f"   ➕ Создан товар-аналог: {analog_product.article}")
                    
                    # Создаем связь аналога
                    analog_relation, created = ProductAnalog.objects.get_or_create(
                        product=product,
                        analog_product=analog_product
                    )
                    
                    if created:
                        print(f"   🔗 Создана связь: {product.article} -> {analog_product.article}")
                        total_analogs_found += 1
                    
                except Exception as e:
                    print(f"   ❌ Ошибка при обработке аналога: {e}")
                    continue
            
        except Exception as e:
            print(f"   ❌ Ошибка при поиске аналогов: {e}")
            continue
        
        # Пауза между запросами
        time.sleep(random.uniform(0.5, 1.0))
    
    print(f"\n🎉 ЗАГРУЗКА ЗАВЕРШЕНА!")
    print(f"✅ Всего найдено и создано аналогов: {total_analogs_found}")
    
    # Статистика
    total_products = Product.objects.count()
    products_with_analogs = Product.objects.filter(analogs__isnull=False).distinct().count()
    
    print(f"📊 Всего товаров в базе: {total_products}")
    print(f"📊 Товаров с аналогами: {products_with_analogs}")
    print(f"📊 Всего связей аналогов: {ProductAnalog.objects.count()}")
    
except Exception as e:
    print(f"❌ Критическая ошибка: {e}")
    import traceback
    traceback.print_exc()
