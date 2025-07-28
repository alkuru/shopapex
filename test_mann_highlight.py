#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import AutoKontinentProduct

def test_mann_highlight():
    """Тестирует подсветку бренда Mann"""
    
    print("🧪 Тестирование подсветки бренда Mann...")
    
    # Тест 1: Поиск товаров Mann
    print("\n1️⃣ Тест: Поиск товаров Mann")
    mann_products = AutoKontinentProduct.objects.filter(
        brand__icontains='mann'
    )[:3]  # Показываем первые 3
    
    print(f"   Найдено товаров с 'mann': {AutoKontinentProduct.objects.filter(brand__icontains='mann').count()}")
    for product in mann_products:
        print(f"   ✅ {product.brand} {product.article} - {product.name[:50]}...")
    
    # Тест 2: Проверка URL для тестирования
    print("\n2️⃣ Тест: URL для проверки подсветки")
    if mann_products:
        first_product = mann_products[0]
        print(f"   Поиск: http://localhost/catalog/search/?q={first_product.article}")
        print(f"   Ожидается: бренд '{first_product.brand}' должен быть подсвечен зеленым")
    
    print("\n🎯 Тестирование завершено!")
    print("\n📋 Инструкция по проверке:")
    print("1. Откройте: http://localhost/catalog/search/?q=C15300")
    print("2. Выберите бренд 'Mann'")
    print("3. В результатах поиска бренд 'Mann' должен быть подсвечен зеленым цветом")
    print("4. Другие бренды должны отображаться обычным цветом")

if __name__ == '__main__':
    test_mann_highlight() 