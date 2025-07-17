#!/usr/bin/env python3
"""
Создание тестовых аналогов для товара C30005
"""

import os
import sys
import django
from decimal import Decimal

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, ProductAnalog, Brand, ProductCategory, OemNumber, ProductOem
    
    print("🔧 СОЗДАНИЕ ТЕСТОВЫХ АНАЛОГОВ ЧЕРЕЗ OEM НОМЕРА")
    print("=" * 50)
    
    # Найдем товар C 30 195
    try:
        product = Product.objects.get(article='C 30 195')
        print(f"✅ Найден товар: {product.name}")
    except Product.DoesNotExist:
        print("❌ Товар C 30 195 не найден в базе")
        sys.exit(1)
    
    # Создадим OEM номер для этого товара
    oem_number, created = OemNumber.objects.get_or_create(
        number='13717521023',
        manufacturer='BMW',
        defaults={
            'description': 'Воздушный фильтр BMW оригинальный номер'
        }
    )
    
    if created:
        print(f"✅ Создан OEM номер: {oem_number}")
    else:
        print(f"ℹ️  OEM номер уже существует: {oem_number}")
    
    # Привязываем товар к OEM номеру
    product_oem, created = ProductOem.objects.get_or_create(
        product=product,
        oem_number=oem_number,
        defaults={'is_main': True}
    )
    
    if created:
        print(f"✅ Привязан товар к OEM: {product.article} -> {oem_number}")
    
    # Создаем аналоги с тем же OEM номером
    analogs_data = [
        {
            'article': 'BOSCH-F026400195', 
            'name': 'Воздушный фильтр BOSCH F026400195',
            'brand_name': 'BOSCH'
        },
        {
            'article': 'FRAM-CA10195', 
            'name': 'Воздушный фильтр FRAM CA10195',
            'brand_name': 'FRAM'
        },
        {
            'article': 'KNECHT-LX1780', 
            'name': 'Воздушный фильтр KNECHT LX1780',
            'brand_name': 'KNECHT'
        },
    ]
    
    for analog_data in analogs_data:
        # Создаем или получаем бренд
        brand, _ = Brand.objects.get_or_create(
            name=analog_data['brand_name'],
            defaults={'is_active': True}
        )
        
        # Создаем товар-аналог если его нет
        analog_product, created = Product.objects.get_or_create(
            article=analog_data['article'],
            defaults={
                'name': analog_data['name'],
                'category': product.category,
                'brand': brand,
                'price': product.price * Decimal('0.9'),  # Немного дешевле оригинала
                'description': f"Аналог для OEM {oem_number}"
            }
        )
        
        if created:
            print(f"✅ Создан товар-аналог: {analog_product.article}")
        
        # Привязываем аналог к тому же OEM номеру
        analog_oem, created = ProductOem.objects.get_or_create(
            product=analog_product,
            oem_number=oem_number,
            defaults={'is_main': False}
        )
        
        if created:
            print(f"✅ Привязан аналог к OEM: {analog_product.article} -> {oem_number}")
    
    print("\n🎯 ТЕСТОВЫЕ АНАЛОГИ ЧЕРЕЗ OEM СОЗДАНЫ!")
    
    # Показываем все товары с этим OEM номером
    related_products = Product.objects.filter(oem_numbers__oem_number=oem_number)
    print(f"📊 Всего товаров с OEM {oem_number}: {related_products.count()}")
    
    for prod in related_products:
        is_main = prod.oem_numbers.filter(oem_number=oem_number, is_main=True).exists()
        status = "🔹 Оригинал" if is_main else "🔸 Аналог"
        print(f"  {status} {prod.article} - {prod.brand.name} - {prod.price}₽")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
