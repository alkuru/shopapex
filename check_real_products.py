#!/usr/bin/env python3
"""
Проверка реальных товаров в базе данных
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, Brand
    
    print("🔍 РЕАЛЬНЫЕ ТОВАРЫ В БАЗЕ ДАННЫХ")
    print("=" * 50)
    
    # Показать первые 10 товаров
    products = Product.objects.filter(is_active=True)[:10]
    
    if not products.exists():
        print("❌ Нет активных товаров в базе данных")
    else:
        print(f"📊 Найдено товаров: {products.count()}")
        print("\nПервые 10 товаров:")
        
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.article} - {product.name[:50]}...")
            print(f"   Бренд: {product.brand.name}")
            print(f"   Цена: {product.price} руб.")
            print()
    
    # Показать популярные бренды
    brands = Brand.objects.filter(is_active=True)[:5]
    print("🏷️  ПОПУЛЯРНЫЕ БРЕНДЫ:")
    for brand in brands:
        count = Product.objects.filter(brand=brand, is_active=True).count()
        print(f"   {brand.name}: {count} товаров")
    
    print("\n🎯 РЕКОМЕНДАЦИЯ:")
    print("Выберите любой артикул из списка выше и протестируйте:")
    print("http://127.0.0.1:8000/catalog/supplier-api-search/?q=АРТИКУЛ")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
