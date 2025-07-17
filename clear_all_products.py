#!/usr/bin/env python3
"""
Удаление всех товаров из базы данных
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, ProductAnalog, ProductImage
    
    print("🗑️  УДАЛЕНИЕ ВСЕХ ТОВАРОВ ИЗ БАЗЫ ДАННЫХ")
    print("=" * 50)
    
    # Сначала посчитаем что удаляем
    products_count = Product.objects.count()
    analogs_count = ProductAnalog.objects.count()
    images_count = ProductImage.objects.count()
    
    print(f"📊 Найдено для удаления:")
    print(f"   Товаров: {products_count}")
    print(f"   Аналогов: {analogs_count}")
    print(f"   Изображений: {images_count}")
    
    if products_count > 0:
        print("\n⚠️  ВНИМАНИЕ! Все товары будут удалены!")
        
        # Удаляем связи аналогов
        if analogs_count > 0:
            ProductAnalog.objects.all().delete()
            print(f"✅ Удалено аналогов: {analogs_count}")
        
        # Удаляем изображения товаров
        if images_count > 0:
            ProductImage.objects.all().delete()
            print(f"✅ Удалено изображений: {images_count}")
        
        # Удаляем все товары
        Product.objects.all().delete()
        print(f"✅ Удалено товаров: {products_count}")
        
        print("\n🎉 ВСЕ ТОВАРЫ УДАЛЕНЫ!")
        print("📊 Осталось товаров в базе:", Product.objects.count())
    else:
        print("ℹ️  База данных уже пуста")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
