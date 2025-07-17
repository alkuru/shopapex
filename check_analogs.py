#!/usr/bin/env python3
"""
Проверка аналогов для C30005
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
    from django.db import models
    
    print("🔍 ПРОВЕРКА АНАЛОГОВ ДЛЯ C30005")
    print("=" * 40)
    
    # Найдем основной товар
    main_product = Product.objects.get(article='C30005')
    print(f"✅ Основной товар: {main_product.article} - {main_product.name}")
    
    # Проверим аналоги
    analogs = main_product.analogs.all()
    print(f"📊 Количество аналогов: {analogs.count()}")
    
    for i, analog_relation in enumerate(analogs, 1):
        analog = analog_relation.analog_product
        print(f"{i}. {analog.article} - {analog.name}")
        print(f"   Бренд: {analog.brand.name}")
        print(f"   Цена: {analog.price} руб.")
        print()
    
    # Проверим, что должно показываться в поиске
    search_results = Product.objects.filter(
        models.Q(article__icontains='C30005') | 
        models.Q(name__icontains='C30005')
    ).distinct()
    
    print(f"🔍 Результаты поиска по 'C30005': {search_results.count()}")
    for product in search_results:
        print(f"   - {product.article}: {product.name}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
