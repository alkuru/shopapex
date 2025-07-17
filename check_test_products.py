#!/usr/bin/env python3
"""
Проверка количества тестовых товаров в базе данных
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, ProductAnalog, Brand, ProductCategory
    
    print("🔍 ПРОВЕРКА ТЕСТОВЫХ ТОВАРОВ")
    print("=" * 40)
    
    # Подсчет всех товаров
    total_products = Product.objects.count()
    print(f"📊 Всего товаров в базе: {total_products}")
    
    # Паттерны для тестовых товаров
    test_patterns = [
        'TEST',
        'ANALOG',
        'C30005',
        'BRP1078',
        'FAKE',
        'DEMO',
        'SAMPLE'
    ]
    
    test_products = []
    for pattern in test_patterns:
        products = Product.objects.filter(article__icontains=pattern)
        test_products.extend(products)
        if products.exists():
            print(f"🔍 Товары с паттерном '{pattern}': {products.count()}")
            for product in products[:5]:  # Показываем первые 5
                print(f"   - {product.article}: {product.name}")
            if products.count() > 5:
                print(f"   ... и еще {products.count() - 5} товаров")
    
    # Уникальные тестовые товары
    unique_test_ids = set(p.id for p in test_products)
    unique_test_count = len(unique_test_ids)
    
    print(f"\n📊 Уникальных тестовых товаров: {unique_test_count}")
    
    # Проверим аналоги
    test_analogs = ProductAnalog.objects.filter(
        product__article__in=[p.article for p in test_products]
    ).count()
    
    analog_of_test = ProductAnalog.objects.filter(
        analog_product__article__in=[p.article for p in test_products]
    ).count()
    
    print(f"📊 Связей аналогов от тестовых товаров: {test_analogs}")
    print(f"📊 Связей аналогов к тестовым товарам: {analog_of_test}")
    
    # Товары с очень короткими артикулами (возможно тестовые)
    short_articles = Product.objects.filter(article__regex=r'^.{1,3}$')
    if short_articles.exists():
        print(f"\n🔍 Товары с короткими артикулами (1-3 символа): {short_articles.count()}")
        for product in short_articles:
            print(f"   - {product.article}: {product.name}")
    
    # Товары без брендов (возможно тестовые)
    no_brand_products = Product.objects.filter(brand__isnull=True)
    if no_brand_products.exists():
        print(f"\n🔍 Товары без брендов: {no_brand_products.count()}")
        for product in no_brand_products[:10]:
            print(f"   - {product.article}: {product.name}")
    
    print("\n✅ ПРОВЕРКА ЗАВЕРШЕНА")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
