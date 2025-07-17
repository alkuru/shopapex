#!/usr/bin/env python3
"""
Исправление категорий товаров - правильная привязка по артикулам
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, ProductCategory, Brand
    
    print("🔧 ИСПРАВЛЕНИЕ КАТЕГОРИЙ ТОВАРОВ")
    print("=" * 50)
    
    # Определяем правильные категории по артикулам/названиям
    category_mapping = {
        # Фильтры
        'FL': 'Фильтры',      # Масляные фильтры
        'AF': 'Фильтры',      # Воздушные фильтры
        'FF': 'Фильтры',      # Топливные фильтры
        
        # Тормозная система
        'BK': 'Тормозная система',  # Тормозные диски (Brake disc)
        'BP': 'Тормозная система',  # Тормозные колодки (Brake pads)
        'BR': 'Тормозная система',  # Тормозные
        
        # Двигатель
        'SP': 'Двигатель',    # Свечи зажигания (Spark plugs)
        'WP': 'Двигатель',    # Водяные насосы (Water pump)
        'TB': 'Двигатель',    # Ремни ГРМ (Timing belt)
        
        # Трансмиссия
        'CL': 'Трансмиссия',  # Сцепление (Clutch)
        'CV': 'Трансмиссия',  # ШРУС (CV joint)
        
        # Подвеска
        'SH': 'Подвеска',     # Амортизаторы (Shock absorber)
        'ST': 'Подвеска',     # Стойки (Strut)
        'SP': 'Подвеска',     # Пружины (Spring)
        
        # Электрика
        'AL': 'Электрика',    # Генераторы (Alternator)
        'ST': 'Электрика',    # Стартеры (Starter)
        'IG': 'Электрика',    # Зажигание (Ignition)
    }
    
    # Получаем все категории
    categories = {}
    for cat in ProductCategory.objects.all():
        categories[cat.name] = cat
    
    print("📋 Доступные категории:")
    for name in categories.keys():
        print(f"   - {name}")
    
    print("\n🔄 Начинаем исправление...")
    
    updated_count = 0
    total_products = Product.objects.count()
    
    for product in Product.objects.all():
        # Определяем правильную категорию по артикулу
        article_prefix = product.article[:2]
        new_category_name = category_mapping.get(article_prefix)
        
        # Если нет точного соответствия, определяем по названию
        if not new_category_name:
            name_lower = product.name.lower()
            if any(word in name_lower for word in ['фильтр', 'filter']):
                new_category_name = 'Фильтры'
            elif any(word in name_lower for word in ['тормоз', 'brake', 'колодки', 'диск']):
                new_category_name = 'Тормозная система'
            elif any(word in name_lower for word in ['свеча', 'ремень', 'насос', 'водяной']):
                new_category_name = 'Двигатель'
            elif any(word in name_lower for word in ['сцепление', 'шрус', 'clutch']):
                new_category_name = 'Трансмиссия'
            elif any(word in name_lower for word in ['амортизатор', 'стойка', 'пружина']):
                new_category_name = 'Подвеска'
            else:
                new_category_name = 'Автозапчасти'  # Общая категория
        
        # Получаем объект категории
        if new_category_name in categories:
            new_category = categories[new_category_name]
            
            # Обновляем категорию если она изменилась
            if product.category != new_category:
                old_category = product.category.name if product.category else 'Нет'
                product.category = new_category
                product.save()
                updated_count += 1
                print(f"✅ {product.article}: {old_category} → {new_category_name}")
    
    print(f"\n🎯 ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!")
    print(f"📊 Обновлено товаров: {updated_count} из {total_products}")
    
    # Показываем финальную статистику
    print("\n📈 ФИНАЛЬНАЯ СТАТИСТИКА:")
    for category in ProductCategory.objects.all():
        count = Product.objects.filter(category=category).count()
        print(f"   {category.name}: {count} товаров")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
