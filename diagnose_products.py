#!/usr/bin/env python3
"""
Диагностика: выводит 10 товаров с артикулом, названием, категорией, брендом и ценой
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product
    print("📋 ДИАГНОСТИКА ТОВАРОВ (10 штук)")
    print("=" * 60)
    products = Product.objects.all()[:10]
    print(f"{'Артикул':<12} | {'Название':<35} | {'Категория':<18} | {'Бренд':<15} | {'Цена':>8}")
    print("-" * 100)
    for p in products:
        category = p.category.name if p.category else '-'
        brand = p.brand.name if p.brand else '-'
        print(f"{p.article:<12} | {p.name[:35]:<35} | {category:<18} | {brand:<15} | {p.price:8.2f}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
