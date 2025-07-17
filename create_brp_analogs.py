#!/usr/bin/env python3
"""
Создание аналогов для товара BRP1078
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, ProductAnalog, Brand
    
    print("🔧 СОЗДАНИЕ АНАЛОГОВ ДЛЯ BRP1078")
    print("=" * 40)
    
    # Найдем товар BRP1078
    main_product = Product.objects.get(article='BRP1078')
    print(f"✅ Основной товар: {main_product.article} - {main_product.name}")
    
    # Найдем или создадим бренды для аналогов
    brands = ['TRW', 'ATE', 'Febi']
    analogs_created = 0
    
    for brand_name in brands:
        brand = Brand.objects.get(name=brand_name)
        
        # Создаем товар-аналог
        analog_article = f"{brand_name}-{main_product.article[-4:]}"  # TRW-1078
        
        analog_product, created = Product.objects.get_or_create(
            article=analog_article,
            defaults={
                'name': f"Тормозные колодки {brand_name} {analog_article}",
                'brand': brand,
                'category': main_product.category,
                'price': float(main_product.price) * 0.95,  # Немного дешевле
                'description': f"Аналог тормозных колодок для {main_product.article}",
                'stock_quantity': 10,
                'is_active': True
            }
        )
        
        if created:
            print(f"✅ Создан товар-аналог: {analog_product.article}")
        
        # Создаем связь аналога
        analog_relation, created = ProductAnalog.objects.get_or_create(
            product=main_product,
            analog_product=analog_product
        )
        
        if created:
            print(f"✅ Связь создана: {main_product.article} -> {analog_product.article}")
            analogs_created += 1
        else:
            print(f"ℹ️  Связь уже существует: {main_product.article} -> {analog_product.article}")
    
    print(f"\n🎯 АНАЛОГИ СОЗДАНЫ ДЛЯ {main_product.article}")
    print(f"📊 Всего аналогов: {main_product.analogs.count()}")
    
    # Покажем все аналоги
    for analog_relation in main_product.analogs.all():
        analog = analog_relation.analog_product
        print(f"   - {analog.article}: {analog.name} ({analog.price} руб.)")
    
    print(f"\n🧪 ТЕСТ В БРАУЗЕРЕ:")
    print(f"http://127.0.0.1:8000/catalog/search/?q={main_product.article}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
