#!/usr/bin/env python3
"""
Удаление всех тестовых товаров
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, ProductAnalog
    
    print("🗑️  УДАЛЕНИЕ ТЕСТОВЫХ ТОВАРОВ")
    print("=" * 40)
    
    # Подсчитаем товары до удаления
    total_before = Product.objects.count()
    print(f"📊 Товаров до удаления: {total_before}")
    
    # Удаляем тестовые товары по паттернам
    test_patterns = [
        'BRP1',  # Тестовые тормозные колодки
        'FL1',   # Тестовые фильтры
        'AF1',   # Тестовые воздушные фильтры
        'SP1',   # Тестовые свечи
        'SH1',   # Тестовые амортизаторы
        'CV1',   # Тестовые ШРУСы
        'BK1',   # Тестовые диски
        'WP1',   # Тестовые насосы
        'TB1',   # Тестовые ремни
        'CL1',   # Тестовые сцепления
        '-ANALOG',  # Все аналоги
        'K20PBR-S10',  # Тестовый товар
        'TRW-',    # Тестовые аналоги
        'ATE-',    # Тестовые аналоги
        'Febi-',   # Тестовые аналоги
    ]
    
    deleted_count = 0
    
    for pattern in test_patterns:
        # Удаляем товары по паттерну
        products_to_delete = Product.objects.filter(article__contains=pattern)
        count = products_to_delete.count()
        
        if count > 0:
            print(f"🗑️  Удаляем {count} товаров с паттерном '{pattern}'")
            products_to_delete.delete()
            deleted_count += count
    
    # Удаляем товары с названием "Товар"
    test_products = Product.objects.filter(name__startswith='Товар ')
    count = test_products.count()
    if count > 0:
        print(f"🗑️  Удаляем {count} товаров с названием 'Товар'")
        test_products.delete()
        deleted_count += count
    
    # Удаляем товары с названием "Аналог"
    analog_products = Product.objects.filter(name__contains='Аналог')
    count = analog_products.count()
    if count > 0:
        print(f"🗑️  Удаляем {count} товаров с названием 'Аналог'")
        analog_products.delete()
        deleted_count += count
    
    # Подсчитаем товары после удаления
    total_after = Product.objects.count()
    
    print(f"\n📊 РЕЗУЛЬТАТ УДАЛЕНИЯ:")
    print(f"   Товаров было: {total_before}")
    print(f"   Удалено: {deleted_count}")
    print(f"   Осталось: {total_after}")
    
    # Покажем оставшиеся товары
    remaining_products = Product.objects.all()[:10]
    print(f"\n📋 ОСТАВШИЕСЯ ТОВАРЫ (первые 10):")
    
    if remaining_products.count() == 0:
        print("   Нет товаров в базе")
    else:
        for i, product in enumerate(remaining_products, 1):
            print(f"   {i}. {product.article} - {product.name}")
    
    print(f"\n✅ ОЧИСТКА ЗАВЕРШЕНА!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
