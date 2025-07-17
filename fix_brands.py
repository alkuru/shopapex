#!/usr/bin/env python3
"""
Исправление брендов в базе данных
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
    
    print("🔧 ИСПРАВЛЕНИЕ БРЕНДОВ В БАЗЕ ДАННЫХ")
    print("=" * 50)
    
    # 1. Исправляем дубликат SKF/Skf
    try:
        skf_uppercase = Brand.objects.get(name='SKF')
        skf_lowercase = Brand.objects.get(name='Skf')
        
        # Переносим товары с "Skf" на "SKF"
        products_to_fix = Product.objects.filter(brand=skf_lowercase)
        for product in products_to_fix:
            product.brand = skf_uppercase
            product.save()
            print(f"✅ Товар {product.article}: Skf → SKF")
        
        # Удаляем дублирующийся бренд
        skf_lowercase.delete()
        print(f"✅ Удален дублирующийся бренд 'Skf'")
        
    except Brand.DoesNotExist:
        print("ℹ️  Дубликат SKF/Skf не найден")
    
    # 2. Исправляем "Mann Filter" на "Mann"
    try:
        mann_filter = Brand.objects.get(name='Mann Filter')
        mann, created = Brand.objects.get_or_create(name='Mann')
        
        # Переносим товары с "Mann Filter" на "Mann"
        products_to_fix = Product.objects.filter(brand=mann_filter)
        for product in products_to_fix:
            product.brand = mann
            product.save()
            print(f"✅ Товар {product.article}: Mann Filter → Mann")
        
        # Удаляем неправильный бренд
        mann_filter.delete()
        print(f"✅ Удален неправильный бренд 'Mann Filter'")
        
    except Brand.DoesNotExist:
        print("ℹ️  Бренд 'Mann Filter' не найден")
    
    # 3. Удаляем пустые бренды (у которых нет товаров)
    empty_brands = []
    for brand in Brand.objects.all():
        if Product.objects.filter(brand=brand).count() == 0:
            empty_brands.append(brand.name)
            brand.delete()
            print(f"✅ Удален пустой бренд: {brand.name}")
    
    if not empty_brands:
        print("ℹ️  Пустых брендов не найдено")
    
    # 4. Проверяем товары без брендов
    products_without_brand = Product.objects.filter(brand__isnull=True)
    if products_without_brand.exists():
        print(f"\n⚠️  Товары без бренда: {products_without_brand.count()}")
        
        # Создаем общий бренд для товаров без бренда
        unknown_brand, created = Brand.objects.get_or_create(name='Неизвестный бренд')
        for product in products_without_brand:
            product.brand = unknown_brand
            product.save()
            print(f"✅ Товар {product.article}: добавлен бренд 'Неизвестный бренд'")
    
    print(f"\n🎯 ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!")
    
    # Показываем финальную статистику
    print("\n📈 ФИНАЛЬНАЯ СТАТИСТИКА БРЕНДОВ:")
    brands = Brand.objects.all().order_by('name')
    for brand in brands:
        count = Product.objects.filter(brand=brand).count()
        if count > 0:  # Показываем только бренды с товарами
            print(f"   {brand.name}: {count} товаров")
    
    print(f"\nВсего активных брендов: {brands.filter(product__isnull=False).distinct().count()}")
    print(f"Всего товаров: {Product.objects.count()}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
