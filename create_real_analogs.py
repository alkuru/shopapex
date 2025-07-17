#!/usr/bin/env python3
"""
Создание аналогов для реального товара Bosch
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, ProductAnalog, Brand, ProductCategory
    
    print("🔧 СОЗДАНИЕ АНАЛОГОВ ДЛЯ РЕАЛЬНОГО ТОВАРА")
    print("=" * 50)
    
    # Найдем любой товар Bosch (автозапчасти)
    bosch_products = Product.objects.filter(brand__name__icontains='Bosch', is_active=True)
    
    if not bosch_products.exists():
        print("❌ Нет товаров Bosch в базе")
        # Попробуем любой другой товар с автозапчастями
        product = Product.objects.filter(is_active=True).first()
        if not product:
            print("❌ Нет товаров в базе")
            sys.exit(1)
    else:
        product = bosch_products.first()
    
    print(f"✅ Выбран товар: {product.article} - {product.name}")
    print(f"   Бренд: {product.brand.name}")
    
    # Создадим реалистичные аналоги
    analogs_data = [
        {
            'article': f'{product.article}-MANN',
            'name': f'Mann аналог для {product.article}',
            'brand': 'Mann Filter'
        },
        {
            'article': f'{product.article}-MAHLE',
            'name': f'Mahle аналог для {product.article}',
            'brand': 'Mahle'
        }
    ]
    
    for analog_data in analogs_data:
        # Найдем или создадим бренд
        brand, _ = Brand.objects.get_or_create(
            name=analog_data['brand'],
            defaults={'is_active': True}
        )
        
        # Создаем товар-аналог
        analog_product, created = Product.objects.get_or_create(
            article=analog_data['article'],
            defaults={
                'name': analog_data['name'],
                'category': product.category,
                'brand': brand,
                'price': float(product.price) * 0.9,  # Чуть дешевле
                'description': f"Аналог для {product.article}",
                'stock_quantity': 5
            }
        )
        
        if created:
            print(f"✅ Создан аналог: {analog_product.article} ({brand.name})")
        
        # Создаем связь аналога
        analog_relation, created = ProductAnalog.objects.get_or_create(
            product=product,
            analog_product=analog_product
        )
        
        if created:
            print(f"✅ Связь создана: {product.article} -> {analog_product.article}")
    
    print(f"\n🎯 АНАЛОГИ СОЗДАНЫ ДЛЯ ТОВАРА: {product.article}")
    print(f"📊 Всего аналогов: {product.analogs.count()}")
    print(f"\n🧪 ТЕСТ В БРАУЗЕРЕ:")
    print(f"http://127.0.0.1:8000/catalog/search/?q={product.article}")
    print(f"http://127.0.0.1:8000/catalog/supplier-api-search/?q={product.article}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
