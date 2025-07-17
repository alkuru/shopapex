#!/usr/bin/env python3
"""
Анализ брендов в базе данных
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, Brand, ProductCategory
    
    print("🏷️  АНАЛИЗ БРЕНДОВ В БАЗЕ ДАННЫХ")
    print("=" * 50)
    
    # Получаем все бренды
    brands = Brand.objects.all()
    print(f"📊 Всего брендов: {brands.count()}")
    print("\n🔍 СПИСОК БРЕНДОВ:")
    
    for brand in brands:
        product_count = Product.objects.filter(brand=brand).count()
        print(f"   {brand.id:2d}. {brand.name} (товаров: {product_count})")
        
        # Показываем несколько товаров этого бренда
        if product_count > 0:
            products = Product.objects.filter(brand=brand)[:5]
            for product in products:
                print(f"       - {product.article}: {product.name}")
        print()
    
    # Проверяем товары без бренда
    products_without_brand = Product.objects.filter(brand__isnull=True)
    if products_without_brand.exists():
        print(f"⚠️  Товары без бренда: {products_without_brand.count()}")
        for product in products_without_brand[:5]:
            print(f"   - {product.article}: {product.name}")
    
    # Анализируем правильность определения брендов
    print("\n🔧 АНАЛИЗ ПРАВИЛЬНОСТИ БРЕНДОВ:")
    
    # Реальные бренды автозапчастей
    real_brands = {
        'bosch': 'Bosch',
        'mann': 'Mann Filter', 
        'mahle': 'Mahle',
        'febi': 'Febi',
        'sachs': 'Sachs',
        'ate': 'ATE',
        'brembo': 'Brembo',
        'denso': 'Denso',
        'valeo': 'Valeo',
        'hella': 'Hella',
        'lemforder': 'Lemförder',
        'lemförder': 'Lemförder',
        'ngk': 'NGK',
        'continental': 'Continental',
        'gates': 'Gates',
        'pierburg': 'Pierburg',
        'zimmermann': 'Zimmermann'
    }
    
    wrong_brands = []
    correct_brands = []
    
    for brand in brands:
        brand_name_lower = brand.name.lower()
        if brand_name_lower in real_brands:
            correct_brands.append(brand)
            print(f"✅ {brand.name} - правильный бренд")
        else:
            wrong_brands.append(brand)
            print(f"❌ {brand.name} - неправильный/неизвестный бренд")
    
    print(f"\n📊 СТАТИСТИКА:")
    print(f"   Правильные бренды: {len(correct_brands)}")
    print(f"   Неправильные бренды: {len(wrong_brands)}")
    print(f"   Всего товаров: {Product.objects.count()}")
    
    # Проверим несколько товаров с реальными брендами
    print(f"\n🔍 ПРИМЕРЫ ТОВАРОВ С РЕАЛЬНЫМИ БРЕНДАМИ:")
    for brand in correct_brands[:5]:
        products = Product.objects.filter(brand=brand)[:2]
        for product in products:
            print(f"   {product.article} ({brand.name}): {product.name}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
