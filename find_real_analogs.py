#!/usr/bin/env python3
"""
Поиск реальных аналогов для товаров с реальными брендами
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, Brand, ProductAnalog
    from catalog.supplier_models import Supplier
    
    print("🔍 ПОИСК РЕАЛЬНЫХ АНАЛОГОВ")
    print("=" * 50)
    
    # Реальные бренды автозапчастей
    real_brands = ['ATE', 'Bosch', 'Brembo', 'Continental', 'Denso', 'Febi', 'Hella', 'Lemförder', 'Mahle', 'NGK', 'Sachs', 'Valeo']
    
    # Найдем товары с реальными брендами
    real_products = Product.objects.filter(brand__name__in=real_brands)
    print(f"📊 Товаров с реальными брендами: {real_products.count()}")
    
    # Попробуем найти аналоги для нескольких товаров
    test_products = real_products[:10]  # Возьмем первые 10 товаров
    
    supplier = Supplier.objects.first()
    if not supplier:
        print("❌ Поставщик не найден")
        sys.exit(1)
    
    analogs_found = 0
    
    for product in test_products:
        print(f"\n🔍 Ищем аналоги для: {product.article} ({product.brand.name})")
        print(f"   Название: {product.name}")
        
        try:
            # Попробуем найти аналоги через API
            analogs_result = supplier.get_product_analogs(product.article)
            print(f"   API результат: {analogs_result}")
            
            # Если результат не является списком, значит это ошибка
            if not isinstance(analogs_result, list):
                print(f"   ⚠️  API вернул ошибку: {analogs_result}")
                continue
            
            if analogs_result:
                print(f"   ✅ Найдено аналогов: {len(analogs_result)}")
                analogs_found += len(analogs_result)
                
                # Показываем первые несколько аналогов
                for i, analog in enumerate(analogs_result[:3]):
                    if isinstance(analog, dict):
                        article = analog.get('article', 'N/A')
                        brand = analog.get('brand', 'N/A')
                        name = analog.get('name', 'N/A')
                        print(f"      {i+1}. {article} ({brand}): {name}")
                    else:
                        print(f"      {i+1}. {analog}")
            else:
                print(f"   ❌ Аналогов не найдено")
                
        except Exception as e:
            print(f"   ❌ Ошибка при поиске аналогов: {e}")
    
    print(f"\n📊 ИТОГ:")
    print(f"   Проверено товаров: {len(test_products)}")
    print(f"   Найдено аналогов: {analogs_found}")
    
    # Проверим, есть ли уже аналоги в базе
    existing_analogs = ProductAnalog.objects.count()
    print(f"   Аналогов в базе: {existing_analogs}")
    
    # Покажем примеры существующих аналогов
    if existing_analogs > 0:
        print(f"\n🔗 СУЩЕСТВУЮЩИЕ АНАЛОГИ:")
        for analog in ProductAnalog.objects.all()[:5]:
            print(f"   {analog.product.article} → {analog.analog_product.article}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
