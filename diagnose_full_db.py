#!/usr/bin/env python3
"""
Полная диагностика: путь к базе, настройки, количество товаров, все поля товаров
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    import settings
except ImportError:
    settings = None

try:
    django.setup()
    from catalog.models import Product
    from django.conf import settings as dj_settings
    print("📋 ПОЛНАЯ ДИАГНОСТИКА БАЗЫ ДАННЫХ")
    print("=" * 60)
    db_path = dj_settings.DATABASES['default']['NAME']
    print(f"Путь к базе данных: {db_path}")
    print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    print(f"DEBUG: {getattr(dj_settings, 'DEBUG', '-')}")
    print(f"Всего товаров: {Product.objects.count()}")
    print("\nТовары:")
    print(f"{'Артикул':<12} | {'Название':<30} | {'Закупочная':>10} | {'Розничная':>10}")
    print("-" * 70)
    for p in Product.objects.all():
        print(f"{p.article:<12} | {p.name[:30]:<30} | {p.purchase_price if hasattr(p, 'purchase_price') and p.purchase_price is not None else '-':>10} | {p.price:>10}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
