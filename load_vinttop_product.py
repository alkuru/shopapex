#!/usr/bin/env python3
"""
Загрузка товара K20PBR-S10 с VintTop
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.supplier_models import Supplier
    
    print("🔍 ЗАГРУЗКА ТОВАРА K20PBR-S10 С VINTTOP")
    print("=" * 50)
    
    # Найдем поставщика VintTop
    supplier = Supplier.objects.filter(name__icontains='VintTop').first()
    
    if not supplier:
        print("❌ Поставщик VintTop не найден")
        sys.exit(1)
    
    print(f"✅ Поставщик: {supplier.name}")
    
    # Ищем товар K20PBR-S10
    article = "K20PBR-S10"
    print(f"🔍 Поиск товара: {article}")
    
    result = supplier.get_product_analogs(article)
    
    if isinstance(result, dict) and result.get('success'):
        products = result.get('products', [])
        print(f"📊 Найдено товаров: {len(products)}")
        
        for i, product in enumerate(products[:3], 1):
            print(f"\n{i}. Артикул: {product.get('article', 'N/A')}")
            print(f"   Название: {product.get('name', 'N/A')}")
            print(f"   Цена: {product.get('price', 'N/A')} руб.")
            print(f"   Бренд: {product.get('brand', 'N/A')}")
    else:
        print(f"❌ Ошибка поиска: {result}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
