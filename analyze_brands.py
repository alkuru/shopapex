#!/usr/bin/env python3
"""
Анализ и исправление брендов в базе данных
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
    
    print("🔍 АНАЛИЗ БРЕНДОВ В БАЗЕ ДАННЫХ")
    print("=" * 50)
    
    # Получаем все бренды
    brands = Brand.objects.all()
    print(f"📊 Всего брендов: {brands.count()}")
    print("\n🏷️  СПИСОК БРЕНДОВ:")
    
    for brand in brands:
        product_count = Product.objects.filter(brand=brand).count()
        print(f"   {brand.id:2d}. {brand.name} (товаров: {product_count})")
        
        # Показываем несколько товаров из этого бренда
        if product_count > 0:
            products = Product.objects.filter(brand=brand)[:3]
            for product in products:
                print(f"       - {product.article}: {product.name}")
        print()
    
    print("\n🔍 ПРОВЕРКА НА ДУБЛИКАТЫ И НЕПРАВИЛЬНЫЕ БРЕНДЫ:")
    
    # Проверяем дублирующиеся бренды
    brand_names = {}
    duplicates = []
    for brand in brands:
        name_lower = brand.name.lower()
        if name_lower in brand_names:
            duplicates.append((brand, brand_names[name_lower]))
            print(f"⚠️  Дубликат: '{brand.name}' (ID: {brand.id}) и '{brand_names[name_lower].name}' (ID: {brand_names[name_lower].id})")
        else:
            brand_names[name_lower] = brand
    
    # Известные автомобильные бренды
    known_auto_brands = {
        'ate', 'bosch', 'brembo', 'continental', 'denso', 'febi', 'hella', 
        'lemförder', 'mahle', 'mann', 'ngk', 'sachs', 'skf', 'valeo',
        'gates', 'dayco', 'contitech', 'pierburg', 'zimmermann', 'textar',
        'jurid', 'trw', 'lucas', 'delphi', 'fag', 'ina', 'luk'
    }
    
    print(f"\n✅ Корректные автомобильные бренды:")
    correct_brands = []
    for brand in brands:
        if brand.name.lower() in known_auto_brands:
            correct_brands.append(brand)
            print(f"   ✓ {brand.name}")
    
    print(f"\n❌ Неизвестные/неправильные бренды:")
    incorrect_brands = []
    for brand in brands:
        if brand.name.lower() not in known_auto_brands:
            incorrect_brands.append(brand)
            product_count = Product.objects.filter(brand=brand).count()
            print(f"   ✗ {brand.name} (товаров: {product_count})")
    
    print(f"\n📈 СТАТИСТИКА:")
    print(f"   Всего брендов: {brands.count()}")
    print(f"   Корректных брендов: {len(correct_brands)}")
    print(f"   Неправильных брендов: {len(incorrect_brands)}")
    print(f"   Дубликатов: {len(duplicates)}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
