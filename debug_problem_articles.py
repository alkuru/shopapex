#!/usr/bin/env python3
"""
Тест проблемных артикулов с детальным логированием
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

django.setup()

from catalog.models import Product
from catalog.abcp_api import get_purchase_price

# Проблемные артикулы
problem_articles = ['C 30 195', 'CUK 2545', 'W 914/2']

print("🔍 ДЕТАЛЬНЫЙ АНАЛИЗ ПРОБЛЕМНЫХ АРТИКУЛОВ")
print("=" * 50)

for article in problem_articles:
    try:
        product = Product.objects.get(article=article)
        brand = product.brand.name if product.brand else None
        print(f"\n📋 Артикул: {article}")
        print(f"🏷️  Бренд в базе: {brand}")
        
        price = get_purchase_price(article, brand)
        
        if price:
            print(f"✅ Итоговая цена: {price}")
        else:
            print("❌ Цена не найдена")
            
    except Product.DoesNotExist:
        print(f"❌ Товар {article} не найден в базе")
    
    print("-" * 50)
