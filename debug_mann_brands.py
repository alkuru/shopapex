#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import AutoKontinentProduct

def debug_mann_brands():
    """Отлаживает бренды Mann"""
    
    print("🔍 Отладка брендов Mann...")
    
    # Поиск точного совпадения "Mann"
    exact_mann = AutoKontinentProduct.objects.filter(brand__iexact='mann')
    print(f"\n1️⃣ Точное совпадение 'Mann': {exact_mann.count()}")
    for product in exact_mann[:3]:
        print(f"   ✅ {product.brand} {product.article} - {product.name[:50]}...")
    
    # Поиск содержащих "mann"
    contains_mann = AutoKontinentProduct.objects.filter(brand__icontains='mann')
    print(f"\n2️⃣ Содержащих 'mann': {contains_mann.count()}")
    
    # Уникальные бренды содержащие "mann"
    unique_brands = contains_mann.values_list('brand', flat=True).distinct()
    print(f"\n3️⃣ Уникальные бренды с 'mann':")
    for brand in unique_brands[:10]:
        print(f"   📝 '{brand}'")
    
    # Тест тега brand_highlight
    from catalog.templatetags.brand_extras import brand_highlight
    print(f"\n4️⃣ Тест тега brand_highlight:")
    test_brands = ['Mann', 'MANN', 'mann', 'Automann', 'DENCKERMANN']
    for brand in test_brands:
        result = brand_highlight(brand)
        print(f"   '{brand}' -> '{result}'")

if __name__ == '__main__':
    debug_mann_brands() 