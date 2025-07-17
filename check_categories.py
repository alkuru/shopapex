#!/usr/bin/env python3
"""
Проверка и анализ категорий в базе данных
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, ProductCategory, Brand
    
    print("📋 АНАЛИЗ КАТЕГОРИЙ В БАЗЕ ДАННЫХ")
    print("=" * 50)
    
    # Получаем все категории
    categories = ProductCategory.objects.all()
    print(f"📊 Всего категорий: {categories.count()}")
    print("\n🏷️  СПИСОК КАТЕГОРИЙ:")
    
    for category in categories:
        product_count = Product.objects.filter(category=category).count()
        print(f"   {category.id:2d}. {category.name} (товаров: {product_count})")
        if hasattr(category, 'description') and category.description:
            print(f"       Описание: {category.description[:100]}...")
        
        # Показываем несколько товаров из этой категории
        if product_count > 0:
            products = Product.objects.filter(category=category)[:3]
            for product in products:
                print(f"       - {product.article}: {product.name}")
        print()
    
    # Проверяем товары без категории
    products_without_category = Product.objects.filter(category__isnull=True)
    if products_without_category.exists():
        print(f"⚠️  Товары без категории: {products_without_category.count()}")
        for product in products_without_category[:5]:
            print(f"   - {product.article}: {product.name}")
    
    # Проверяем дублирующиеся категории
    print("\n🔍 ПРОВЕРКА НА ДУБЛИКАТЫ:")
    category_names = {}
    for category in categories:
        name_lower = category.name.lower()
        if name_lower in category_names:
            print(f"⚠️  Дубликат найден: '{category.name}' (ID: {category.id}) и '{category_names[name_lower].name}' (ID: {category_names[name_lower].id})")
        else:
            category_names[name_lower] = category
    
    if not any(name_lower in category_names for name_lower in category_names if category_names.get(name_lower)):
        print("✅ Дубликатов не найдено")
    
    print("\n📈 СТАТИСТИКА:")
    print(f"   Всего товаров: {Product.objects.count()}")
    print(f"   Всего категорий: {categories.count()}")
    print(f"   Всего брендов: {Brand.objects.count()}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
