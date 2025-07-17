#!/usr/bin/env python3
"""
Загрузка 100 товаров в базу данных
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
    from catalog.models import Product, Brand, ProductCategory
    
    print("📦 ЗАГРУЗКА 100 ТОВАРОВ В БАЗУ ДАННЫХ")
    print("=" * 50)
    
    # Создаем категории
    categories_data = [
        'Тормозная система',
        'Двигатель',
        'Трансмиссия',
        'Подвеска',
        'Электрика',
        'Кузов',
        'Фильтры',
        'Масла и жидкости'
    ]
    
    categories = []
    for cat_name in categories_data:
        category, created = ProductCategory.objects.get_or_create(
            name=cat_name,
            defaults={'is_active': True}
        )
        categories.append(category)
        if created:
            print(f"✅ Создана категория: {cat_name}")
    
    # Создаем бренды
    brands_data = [
        'Bosch', 'Mann Filter', 'Mahle', 'Febi', 'Lemförder',
        'TRW', 'Sachs', 'Brembo', 'ATE', 'Continental',
        'NGK', 'Denso', 'Hella', 'Valeo', 'SKF'
    ]
    
    brands = []
    for brand_name in brands_data:
        brand, created = Brand.objects.get_or_create(
            name=brand_name,
            defaults={'is_active': True}
        )
        brands.append(brand)
        if created:
            print(f"✅ Создан бренд: {brand_name}")
    
    # Создаем 100 товаров
    products_data = [
        {'prefix': 'BRP', 'type': 'Тормозные колодки'},
        {'prefix': 'FL', 'type': 'Масляный фильтр'},
        {'prefix': 'AF', 'type': 'Воздушный фильтр'},
        {'prefix': 'SP', 'type': 'Свеча зажигания'},
        {'prefix': 'SH', 'type': 'Амортизатор'},
        {'prefix': 'CV', 'type': 'ШРУС'},
        {'prefix': 'BK', 'type': 'Тормозной диск'},
        {'prefix': 'WP', 'type': 'Водяной насос'},
        {'prefix': 'TB', 'type': 'Ремень ГРМ'},
        {'prefix': 'CL', 'type': 'Сцепление'}
    ]
    
    created_count = 0
    
    for i in range(100):
        product_template = random.choice(products_data)
        article = f"{product_template['prefix']}{1000 + i}"
        
        # Проверяем, что товар не существует
        if Product.objects.filter(article=article).exists():
            continue
            
        brand = random.choice(brands)
        category = random.choice(categories)
        price = random.randint(500, 15000)
        
        product = Product.objects.create(
            article=article,
            name=f"{product_template['type']} {brand.name} {article}",
            brand=brand,
            category=category,
            price=price,
            description=f"Качественный {product_template['type'].lower()} от {brand.name}",
            stock_quantity=random.randint(0, 50),
            is_active=True,
            is_featured=random.choice([True, False])
        )
        
        created_count += 1
        if created_count % 10 == 0:
            print(f"📊 Создано товаров: {created_count}")
    
    print(f"\n🎉 ЗАГРУЗКА ЗАВЕРШЕНА!")
    print(f"✅ Создано товаров: {created_count}")
    print(f"✅ Всего товаров в базе: {Product.objects.count()}")
    print(f"✅ Всего категорий: {ProductCategory.objects.count()}")
    print(f"✅ Всего брендов: {Brand.objects.count()}")
    
    # Покажем несколько примеров
    print(f"\n📋 ПРИМЕРЫ СОЗДАННЫХ ТОВАРОВ:")
    sample_products = Product.objects.filter(article__startswith='BRP').order_by('-id')[:5]
    for product in sample_products:
        print(f"   {product.article} - {product.name} ({product.price} руб.)")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
