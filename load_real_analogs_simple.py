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
    
    # Получаем первые несколько товаров для теста
    products = Product.objects.all()[:10]  # Берем первые 10 товаров для теста
    print(f"📊 Будем искать аналоги для {products.count()} товаров")
    
    # Создаем экземпляр поставщика для вызова методов
    supplier = Supplier()
    
    total_analogs_found = 0
    
    for i, product in enumerate(products, 1):
        print(f"\n[{i}/{products.count()}] Ищем аналоги для: {product.article} - {product.name}")
        
        try:
            # Получаем аналоги через API
            analogs = supplier.get_product_analogs(product.article, product.brand.name if product.brand else None)
            
            if not analogs:
                print(f"   ❌ Аналоги не найдены")
                continue
            
            print(f"   ✅ Найдено {len(analogs)} аналогов")
            
            # Обрабатываем каждый аналог
            analog_count = 0
            for analog_data in analogs[:5]:  # Берем только первые 5 аналогов
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
                            'price': float(analog_price) if analog_price else product.price,
                            'description': f"Аналог для {product.article}"
                        }
                    )
                    
                    if created:
                        print(f"   ➕ Создан товар-аналог: {analog_product.article}")
                    
                    # Создаем связь аналога (проверяем, что это не тот же товар)
                    if analog_product.article != product.article:
                        analog_relation, created = ProductAnalog.objects.get_or_create(
                            product=product,
                            analog_product=analog_product
                        )
                        
                        if created:
                            print(f"   🔗 Создана связь: {product.article} -> {analog_product.article}")
                            total_analogs_found += 1
                            analog_count += 1
                    
                except Exception as e:
                    print(f"   ❌ Ошибка при обработке аналога: {e}")
                    continue
            
            print(f"   📈 Добавлено аналогов для {product.article}: {analog_count}")
            
        except Exception as e:
            print(f"   ❌ Ошибка при поиске аналогов: {e}")
            continue
        
        # Пауза между запросами
        time.sleep(random.uniform(1.0, 2.0))
    
    print(f"\n🎉 ЗАГРУЗКА ЗАВЕРШЕНА!")
    print(f"✅ Всего найдено и создано аналогов: {total_analogs_found}")
    
    # Статистика
    total_products = Product.objects.count()
    products_with_analogs = Product.objects.filter(analogs__isnull=False).distinct().count()
    
    print(f"📊 Всего товаров в базе: {total_products}")
    print(f"📊 Товаров с аналогами: {products_with_analogs}")
    print(f"📊 Всего связей аналогов: {ProductAnalog.objects.count()}")
    
    # Покажем примеры
    print(f"\n📋 ПРИМЕРЫ ТОВАРОВ С АНАЛОГАМИ:")
    for product in Product.objects.filter(analogs__isnull=False).distinct()[:5]:
        analog_count = product.analogs.count()
        print(f"   {product.article} - {product.name} ({analog_count} аналогов)")
        for analog in product.analogs.all()[:3]:
            print(f"     → {analog.analog_product.article} - {analog.analog_product.name}")
    
except Exception as e:
    print(f"❌ Критическая ошибка: {e}")
    import traceback
    traceback.print_exc()
