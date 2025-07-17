#!/usr/bin/env python3
"""
Комплексная диагностика проблем в базе данных
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
    
    print("🔍 КОМПЛЕКСНАЯ ДИАГНОСТИКА БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    # 1. ПРОБЛЕМЫ С АРТИКУЛАМИ
    print("\n📋 1. АНАЛИЗ АРТИКУЛОВ:")
    print("-" * 30)
    
    all_products = Product.objects.all()
    print(f"Всего товаров: {all_products.count()}")
    
    # Проверка формата артикулов
    invalid_articles = []
    for product in all_products[:20]:  # Показываем первые 20
        article = product.article
        print(f"  {article:15} | {product.brand.name if product.brand else 'НЕТ БРЕНДА':15} | {product.name[:50]}")
        
        # Проверяем подозрительные артикулы
        if len(article) < 3 or len(article) > 20:
            invalid_articles.append(f"{article} (длина: {len(article)})")
    
    if invalid_articles:
        print(f"\n⚠️  Подозрительные артикулы: {len(invalid_articles)}")
        for art in invalid_articles[:10]:
            print(f"    - {art}")
    
    # 2. ПРОБЛЕМЫ С БРЕНДАМИ
    print("\n🏷️  2. АНАЛИЗ БРЕНДОВ:")
    print("-" * 30)
    
    brands = Brand.objects.all()
    print(f"Всего брендов: {brands.count()}")
    
    brand_product_count = {}
    for brand in brands:
        count = Product.objects.filter(brand=brand).count()
        brand_product_count[brand.name] = count
        print(f"  {brand.name:20} | товаров: {count:3d}")
    
    # Проверка товаров без бренда
    no_brand_products = Product.objects.filter(brand__isnull=True)
    if no_brand_products.exists():
        print(f"\n⚠️  Товары без бренда: {no_brand_products.count()}")
        for product in no_brand_products[:5]:
            print(f"    - {product.article}: {product.name}")
    
    # 3. ПРОБЛЕМЫ СВЯЗЕЙ АРТИКУЛ-БРЕНД
    print("\n🔗 3. АНАЛИЗ СВЯЗЕЙ АРТИКУЛ-БРЕНД:")
    print("-" * 40)
    
    mismatched_products = []
    for product in all_products:
        article = product.article
        brand_name = product.brand.name if product.brand else "НЕТ"
        
        # Проверяем логику соответствия
        # Например, артикул FL1099 должен быть от бренда фильтров
        if article.startswith('FL') and brand_name not in ['Mann', 'Mahle', 'Bosch', 'Hella']:
            mismatched_products.append(f"{article} -> {brand_name} (масляный фильтр)")
        elif article.startswith('AF') and brand_name not in ['Mann', 'Mahle', 'Bosch', 'Hella']:
            mismatched_products.append(f"{article} -> {brand_name} (воздушный фильтр)")
        elif article.startswith('BK') and brand_name not in ['Brembo', 'ATE', 'TRW', 'Bosch']:
            mismatched_products.append(f"{article} -> {brand_name} (тормозной диск)")
        elif article.startswith('CL') and brand_name not in ['Sachs', 'Valeo', 'LuK']:
            mismatched_products.append(f"{article} -> {brand_name} (сцепление)")
    
    if mismatched_products:
        print(f"⚠️  Подозрительные связи артикул-бренд: {len(mismatched_products)}")
        for mismatch in mismatched_products[:10]:
            print(f"    - {mismatch}")
    
    # 4. АНАЛИЗ НАЗВАНИЙ ТОВАРОВ
    print("\n📝 4. АНАЛИЗ НАЗВАНИЙ ТОВАРОВ:")
    print("-" * 35)
    
    strange_names = []
    for product in all_products:
        name = product.name
        article = product.article
        brand = product.brand.name if product.brand else "НЕТ"
        
        # Проверяем странные названия
        if article in name and brand in name:
            # Нормально - артикул и бренд в названии
            continue
        elif len(name) < 10:
            strange_names.append(f"{article} -> '{name}' (слишком короткое)")
        elif name.count(' ') < 2:
            strange_names.append(f"{article} -> '{name}' (мало слов)")
    
    if strange_names:
        print(f"⚠️  Подозрительные названия: {len(strange_names)}")
        for name in strange_names[:10]:
            print(f"    - {name}")
    
    # 5. ДУБЛИКАТЫ
    print("\n🔄 5. ПОИСК ДУБЛИКАТОВ:")
    print("-" * 25)
    
    # Дубликаты артикулов
    from django.db.models import Count
    duplicate_articles = Product.objects.values('article').annotate(count=Count('article')).filter(count__gt=1)
    if duplicate_articles:
        print(f"⚠️  Дублирующиеся артикулы: {len(duplicate_articles)}")
        for dup in duplicate_articles:
            print(f"    - {dup['article']} ({dup['count']} раз)")
    
    # Дубликаты брендов (по имени)
    duplicate_brands = Brand.objects.values('name').annotate(count=Count('name')).filter(count__gt=1)
    if duplicate_brands:
        print(f"⚠️  Дублирующиеся бренды: {len(duplicate_brands)}")
        for dup in duplicate_brands:
            print(f"    - {dup['name']} ({dup['count']} раз)")
    
    # 6. ОБЩИЕ РЕКОМЕНДАЦИИ
    print("\n💡 РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ:")
    print("-" * 35)
    
    if invalid_articles:
        print("  1. Исправить неправильные артикулы")
    if no_brand_products.exists():
        print("  2. Назначить бренды товарам без брендов")
    if mismatched_products:
        print("  3. Исправить несоответствия артикул-бренд")
    if duplicate_articles:
        print("  4. Удалить дублирующиеся артикулы")
    if duplicate_brands:
        print("  5. Объединить дублирующиеся бренды")
    
    print("\n🎯 ДИАГНОСТИКА ЗАВЕРШЕНА!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
