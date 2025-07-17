#!/usr/bin/env python3
"""
Диагностика дублей: выводит все артикулы, у которых есть товары с разными брендами и ценами
"""
import os
import sys
import django
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product
    print("📋 ДИАГНОСТИКА ДУБЛЕЙ ПО АРТИКУЛАМ")
    print("=" * 80)
    products = Product.objects.all()
    by_article = defaultdict(list)
    for p in products:
        by_article[p.article].append(p)
    count = 0
    for article, items in by_article.items():
        if len(items) > 1:
            brands = set(i.brand.name if i.brand else '-' for i in items)
            prices = set(i.price for i in items)
            if len(brands) > 1 or len(prices) > 1:
                count += 1
                print(f"Артикул: {article}")
                for i in items:
                    brand = i.brand.name if i.brand else '-'
                    print(f"   {i.name[:30]:<30} | {brand:<12} | {i.price:8.2f}")
                print("-")
    print(f"\nВсего артикулов с дублями по бренду/цене: {count}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
