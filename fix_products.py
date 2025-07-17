#!/usr/bin/env python3
"""
Массовое исправление брендов и цен по справочнику (пример)
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

# Пример справочника: артикул -> (бренд, цена)
FIX_MAP = {
    'CL1097': ('Lunx', 4574),
    'FL1099': ('Mann', 2100),
    'BK1085': ('Brembo', 6500),
    # ...добавьте свои правила...
}

try:
    django.setup()
    from catalog.models import Product, Brand
    print("🔧 МАССОВОЕ ИСПРАВЛЕНИЕ ТОВАРОВ")
    print("=" * 60)
    changed = 0
    for article, (brand_name, price) in FIX_MAP.items():
        products = Product.objects.filter(article=article)
        if not products.exists():
            print(f"❌ Нет товара с артикулом {article}")
            continue
        brand, _ = Brand.objects.get_or_create(name=brand_name)
        for p in products:
            changed_flag = False
            if p.brand != brand:
                print(f"{article}: бренд {p.brand.name if p.brand else '-'} → {brand_name}")
                p.brand = brand
                changed_flag = True
            if abs(p.price - price) > 1:
                print(f"{article}: цена {p.price} → {price}")
                p.price = price
                changed_flag = True
            if changed_flag:
                p.save()
                changed += 1
    print(f"\n🎯 Исправлено товаров: {changed}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
