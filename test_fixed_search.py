#!/usr/bin/env python3
"""
Тестирование поиска аналогов с исправленными данными
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
    from catalog.supplier_models import Supplier
    
    print("🔍 ТЕСТИРОВАНИЕ ПОИСКА АНАЛОГОВ")
    print("=" * 50)
    
    # Берем несколько товаров для тестирования
    test_products = Product.objects.all()[:5]
    
    print("📋 ТОВАРЫ ДЛЯ ТЕСТИРОВАНИЯ:")
    for i, product in enumerate(test_products, 1):
        print(f"   {i}. {product.article} - {product.brand.name} - {product.name}")
    
    print("\n🔧 ТЕСТИРОВАНИЕ ПОИСКА АНАЛОГОВ:")
    print("-" * 40)
    
    # Создаем экземпляр поставщика
    supplier = Supplier.objects.first()
    if not supplier:
        print("❌ Поставщик не найден в базе")
        sys.exit(1)
    
    for product in test_products:
        print(f"\n🔍 Поиск аналогов для {product.article}:")
        print(f"   Товар: {product.name}")
        print(f"   Бренд: {product.brand.name}")
        print(f"   Категория: {product.category.name}")
        
        # Пытаемся найти аналоги через API
        try:
            analogs_result = supplier.get_product_analogs(product.article)
            print(f"   API ответ: {analogs_result}")
            
            if isinstance(analogs_result, list) and analogs_result:
                print(f"   ✅ Найдено аналогов через API: {len(analogs_result)}")
                for analog in analogs_result[:3]:  # Показываем первые 3
                    if isinstance(analog, dict):
                        print(f"     - {analog.get('article', 'НЕТ')} ({analog.get('brand', 'НЕТ')})")
            else:
                print(f"   ℹ️  API аналогов не вернул или вернул ошибку")
        except Exception as e:
            print(f"   ❌ Ошибка API: {e}")
        
        # Проверяем локальные аналоги в базе
        local_analogs = ProductAnalog.objects.filter(product=product)
        if local_analogs.exists():
            print(f"   ✅ Локальных аналогов: {local_analogs.count()}")
            for analog in local_analogs:
                print(f"     - {analog.analog_product.article} ({analog.analog_product.brand.name})")
        else:
            print(f"   ℹ️  Локальных аналогов нет")
    
    print("\n📊 ОБЩАЯ СТАТИСТИКА:")
    print("-" * 25)
    print(f"   Всего товаров: {Product.objects.count()}")
    print(f"   Всего аналогов: {ProductAnalog.objects.count()}")
    print(f"   Товаров с аналогами: {Product.objects.filter(analogs__isnull=False).distinct().count()}")
    
    # Проверим несколько конкретных популярных артикулов
    print("\n🎯 ПРОВЕРКА ПОПУЛЯРНЫХ АРТИКУЛОВ:")
    print("-" * 35)
    
    popular_articles = ['FL1099', 'BK1085', 'CV1093', 'SP1091', 'WP1090']
    
    for article in popular_articles:
        try:
            product = Product.objects.get(article=article)
            print(f"   {article}: {product.brand.name} - {product.name[:40]}...")
        except Product.DoesNotExist:
            print(f"   {article}: НЕ НАЙДЕН")
    
    print("\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
