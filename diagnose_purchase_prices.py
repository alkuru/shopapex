#!/usr/bin/env python3
"""
Показывает закупочные и розничные цены для всех товаров Mann
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, Brand
    print("📋 ТОВАРЫ MANN: закупочная и розничная цена")
    print("=" * 60)
    brand = Brand.objects.get(name='Mann')
    products = Product.objects.filter(brand=brand)
    print(f"{'Артикул':<12} | {'Закупочная':>10} | {'Розничная':>10}")
    print("-" * 40)
    for p in products:
        print(f"{p.article:<12} | {p.purchase_price if p.purchase_price is not None else '-':>10} | {p.price:>10}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
