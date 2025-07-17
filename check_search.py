#!/usr/bin/env python3
"""
Проверка поиска товаров
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product
    
    print("🔍 ПРОВЕРКА ПОИСКА ТОВАРОВ")
    print("=" * 40)
    
    # Проверим, есть ли товар K20PBR-S10
    article = "K20PBR-S10"
    
    # Точный поиск
    exact_product = Product.objects.filter(article=article).first()
    if exact_product:
        print(f"✅ Товар найден точным поиском: {exact_product.article}")
        print(f"   Название: {exact_product.name}")
        print(f"   Активен: {exact_product.is_active}")
        print(f"   ID: {exact_product.id}")
    else:
        print(f"❌ Товар {article} не найден точным поиском")
    
    # Поиск с icontains
    similar_products = Product.objects.filter(article__icontains="K20PBR").all()
    print(f"\n📊 Похожие товары (содержат K20PBR): {similar_products.count()}")
    for product in similar_products:
        print(f"   - {product.article}: {product.name} (активен: {product.is_active})")
    
    # Поиск в названии
    name_search = Product.objects.filter(name__icontains="K20PBR").all()
    print(f"\n📊 Поиск в названии (K20PBR): {name_search.count()}")
    for product in name_search:
        print(f"   - {product.article}: {product.name}")
    
    # Проверим все товары с Unknown брендом
    unknown_products = Product.objects.filter(brand__name="Unknown").all()
    print(f"\n📊 Товары с брендом Unknown: {unknown_products.count()}")
    for product in unknown_products[:5]:
        print(f"   - {product.article}: {product.name} (активен: {product.is_active})")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
