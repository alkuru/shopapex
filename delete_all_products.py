#!/usr/bin/env python3
"""
Удаление всех товаров из базы данных
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product
    count = Product.objects.count()
    Product.objects.all().delete()
    print(f"✅ Удалено товаров: {count}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
