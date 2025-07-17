#!/usr/bin/env python3
"""
Установка наценки 0% для всех товаров и всех поставщиков
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, Supplier
    
    print("🔧 УСТАНОВКА НАЦЕНКИ 0% ДЛЯ ВСЕХ ТОВАРОВ И ПОСТАВЩИКОВ")
    print("=" * 50)
    updated = 0
    for product in Product.objects.all():
        if hasattr(product, 'markup_percentage'):
            product.markup_percentage = 0
            product.save()
            updated += 1
    print(f"✅ Обновлено товаров с наценкой: {updated}")
    # Для всех поставщиков
    updated_sup = 0
    for supplier in Supplier.objects.all():
        if hasattr(supplier, 'markup_percentage'):
            supplier.markup_percentage = 0
            supplier.save()
            updated_sup += 1
    print(f"✅ Обновлено поставщиков: {updated_sup}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
