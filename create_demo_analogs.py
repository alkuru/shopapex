#!/usr/bin/env python3
"""
Создание тестовых аналогов для демонстрации системы
"""

import os
import sys
import django
import random

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, ProductAnalog, Brand, ProductCategory
    
    print("🔧 СОЗДАНИЕ ТЕСТОВЫХ АНАЛОГОВ")
    print("=" * 40)
    
    # Получаем случайные товары для создания аналогов
    products = Product.objects.all()[:20]  # Берем первые 20 товаров
    
    total_analogs_created = 0
    
    for i, product in enumerate(products, 1):
        print(f"\n[{i}/{products.count()}] Создаем аналоги для: {product.article} - {product.name}")
        
        # Создаем 2-3 аналога для каждого товара
        num_analogs = random.randint(1, 3)
        
        for j in range(num_analogs):
            # Генерируем артикул аналога
            analog_article = f"{product.article}-A{j+1}"
            
            # Выбираем случайный бренд из существующих
            brands = Brand.objects.all()
            if brands:
                analog_brand = random.choice(brands)
            else:
                analog_brand = product.brand
            
            # Создаем товар-аналог
            analog_product, created = Product.objects.get_or_create(
                article=analog_article,
                defaults={
                    'name': f'Аналог {product.name}',
                    'category': product.category,
                    'brand': analog_brand,
                    'price': product.price + random.uniform(-500, 500),
                    'description': f"Аналог для {product.article}"
                }
            )
            
            if created:
                print(f"   ➕ Создан товар-аналог: {analog_product.article} ({analog_brand.name})")
            
            # Создаем связь аналога
            analog_relation, created = ProductAnalog.objects.get_or_create(
                product=product,
                analog_product=analog_product
            )
            
            if created:
                print(f"   🔗 Создана связь: {product.article} -> {analog_product.article}")
                total_analogs_created += 1
    
    print(f"\n🎉 СОЗДАНИЕ ЗАВЕРШЕНО!")
    print(f"✅ Всего создано аналогов: {total_analogs_created}")
    
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
        for analog in product.analogs.all():
            print(f"     → {analog.analog_product.article} - {analog.analog_product.name} ({analog.analog_product.brand.name})")
    
except Exception as e:
    print(f"❌ Критическая ошибка: {e}")
    import traceback
    traceback.print_exc()
