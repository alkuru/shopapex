#!/usr/bin/env python3
"""
Исправление всех проблем с артикулами и брендами
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, Brand, ProductCategory
    
    print("🔧 ИСПРАВЛЕНИЕ ПРОБЛЕМ С АРТИКУЛАМИ И БРЕНДАМИ")
    print("=" * 60)
    
    # Правильное соответствие артикул-бренд для автозапчастей
    correct_brand_mapping = {
        # Фильтры
        'FL': ['Mann', 'Mahle', 'Bosch', 'Hella'],  # Масляные фильтры
        'AF': ['Mann', 'Mahle', 'Bosch', 'Hella'],  # Воздушные фильтры
        'FF': ['Mann', 'Mahle', 'Bosch'],           # Топливные фильтры
        
        # Тормозная система
        'BK': ['Brembo', 'ATE', 'TRW', 'Bosch'],   # Тормозные диски
        'BP': ['Brembo', 'ATE', 'TRW', 'Bosch'],   # Тормозные колодки
        'BR': ['Brembo', 'ATE', 'TRW'],            # Тормозные (общие)
        
        # Двигатель
        'SP': ['NGK', 'Bosch', 'Denso'],           # Свечи зажигания
        'WP': ['Continental', 'Febi', 'SKF'],      # Водяные насосы
        'TB': ['Continental', 'Febi', 'SKF'],      # Ремни ГРМ
        
        # Трансмиссия
        'CL': ['Sachs', 'Valeo', 'LuK'],           # Сцепление (LuK нет, используем Sachs)
        'CV': ['SKF', 'Febi', 'Lemförder'],        # ШРУС
        
        # Подвеска
        'SH': ['Sachs', 'Lemförder', 'TRW'],       # Амортизаторы
        'ST': ['Sachs', 'Lemförder', 'TRW'],       # Стойки
    }
    
    # Получаем все бренды
    all_brands = {brand.name: brand for brand in Brand.objects.all()}
    print(f"📋 Доступные бренды: {list(all_brands.keys())}")
    
    # Счетчики
    updated_count = 0
    total_products = Product.objects.count()
    
    print(f"\n🔄 Исправляем {total_products} товаров...")
    
    for product in Product.objects.all():
        article = product.article
        current_brand = product.brand.name if product.brand else "НЕТ"
        
        # Определяем правильный бренд по артикулу
        article_prefix = article[:2]
        correct_brands = correct_brand_mapping.get(article_prefix, [])
        
        if not correct_brands:
            # Если префикс не найден, оставляем как есть
            continue
        
        # Проверяем, правильный ли бренд сейчас
        if current_brand in correct_brands:
            # Бренд правильный, ничего не делаем
            continue
        
        # Назначаем правильный бренд
        # Берем первый доступный бренд из списка правильных
        new_brand_name = None
        for brand_name in correct_brands:
            if brand_name in all_brands:
                new_brand_name = brand_name
                break
        
        if new_brand_name:
            old_brand = current_brand
            product.brand = all_brands[new_brand_name]
            product.save()
            updated_count += 1
            print(f"✅ {article:10} | {old_brand:15} → {new_brand_name:15} | {product.name[:40]}")
        else:
            print(f"⚠️  {article:10} | Нет подходящего бренда для префикса {article_prefix}")
    
    print(f"\n🎯 ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!")
    print(f"📊 Обновлено товаров: {updated_count} из {total_products}")
    
    # Финальная проверка
    print("\n📈 ФИНАЛЬНАЯ СТАТИСТИКА ПО БРЕНДАМ:")
    for brand in Brand.objects.all():
        count = Product.objects.filter(brand=brand).count()
        print(f"   {brand.name:15} | товаров: {count:3d}")
    
    # Проверяем оставшиеся несоответствия
    print("\n🔍 ПРОВЕРКА ОСТАВШИХСЯ ПРОБЛЕМ:")
    remaining_issues = 0
    
    for product in Product.objects.all():
        article = product.article
        brand_name = product.brand.name if product.brand else "НЕТ"
        article_prefix = article[:2]
        correct_brands = correct_brand_mapping.get(article_prefix, [])
        
        if correct_brands and brand_name not in correct_brands:
            remaining_issues += 1
            if remaining_issues <= 10:  # Показываем первые 10
                print(f"   ⚠️  {article} -> {brand_name} (должен быть из {correct_brands})")
    
    if remaining_issues == 0:
        print("   ✅ Все проблемы исправлены!")
    else:
        print(f"   ⚠️  Осталось проблем: {remaining_issues}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
