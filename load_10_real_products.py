#!/usr/bin/env python3
"""
Загрузка 10 реальных товаров бренда Mann в базу данных
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, Brand, ProductCategory
    
    print("📦 ЗАГРУЗКА 10 ТОВАРОВ MANN")
    print("=" * 40)
    
    # Получаем или создаём бренд Mann
    brand, _ = Brand.objects.get_or_create(name='Mann')
    # Получаем или создаём категорию Фильтры
    category, _ = ProductCategory.objects.get_or_create(name='Фильтры')
    
    products_data = [
        {"article": "C 35 154", "name": "Воздушный фильтр Mann C 35 154", "purchase_price": 1200},
        {"article": "W 914/2", "name": "Масляный фильтр Mann W 914/2", "purchase_price": 650},
        {"article": "HU 719/7 x", "name": "Масляный фильтр Mann HU 719/7 x", "purchase_price": 900},
        {"article": "CUK 2545", "name": "Салонный фильтр Mann CUK 2545", "purchase_price": 1100},
        {"article": "C 25 024", "name": "Воздушный фильтр Mann C 25 024", "purchase_price": 1050},
        {"article": "WK 820/17", "name": "Топливный фильтр Mann WK 820/17", "purchase_price": 1700},
        {"article": "C 27 125", "name": "Воздушный фильтр Mann C 27 125", "purchase_price": 1300},
        {"article": "W 75/3", "name": "Масляный фильтр Mann W 75/3", "purchase_price": 600},
        {"article": "C 30 195", "name": "Воздушный фильтр Mann C 30 195", "purchase_price": 1250},
        {"article": "CU 2939", "name": "Салонный фильтр Mann CU 2939", "purchase_price": 950},
    ]
    
    for p in products_data:
        product, created = Product.objects.get_or_create(
            article=p["article"],
            defaults={
                "name": p["name"],
                "category": category,
                "brand": brand,
                "purchase_price": p["purchase_price"],
                "price": p["purchase_price"],
                "description": f"{p['name']} (бренд Mann)"
            }
        )
        if not created:
            product.name = p["name"]
            product.category = category
            product.brand = brand
            product.purchase_price = p["purchase_price"]
            product.price = p["purchase_price"]
            product.description = f"{p['name']} (бренд Mann)"
            product.save()
            print(f"♻️  Обновлён: {product.article} — {product.name} (закупочная {product.purchase_price})")
        else:
            print(f"✅ Добавлен: {product.article} — {product.name} (закупочная {product.purchase_price})")
    print("\n🎉 ЗАГРУЗКА ЗАВЕРШЕНА!")
    print(f"Всего товаров Mann: {Product.objects.filter(brand=brand).count()}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
