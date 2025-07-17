#!/usr/bin/env python
"""
Тестирование функционала OEM номеров
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex.settings')
django.setup()

from catalog.models import Product, OemNumber, ProductOem, Brand, ProductCategory
from django.db.models import Q

def test_oem_functionality():
    """Тестирование всех функций OEM номеров"""
    
    print("🧪 ТЕСТИРОВАНИЕ ФУНКЦИОНАЛА OEM НОМЕРОВ")
    print("=" * 50)
    
    # 1. Проверяем существование OEM номера
    oem_number = OemNumber.objects.filter(number="BMW 13717521023").first()
    if oem_number:
        print(f"✅ OEM номер найден: {oem_number.number}")
        print(f"   Описание: {oem_number.description}")
    else:
        print("❌ OEM номер не найден")
        return
    
    # 2. Проверяем товары с этим OEM номером
    products_with_oem = Product.objects.filter(
        oem_numbers__oem_number=oem_number,
        is_active=True
    ).select_related('brand', 'category')
    
    print(f"\n📦 Товары с OEM номером {oem_number.number}:")
    for product in products_with_oem:
        print(f"   • {product.name} - {product.brand.name} - {product.price}₽")
    
    # 3. Тестируем поиск по OEM номеру
    print(f"\n🔍 Поиск по OEM номеру 'BMW 13717521023':")
    search_results = Product.objects.filter(
        oem_numbers__oem_number__number__icontains="BMW 13717521023",
        is_active=True
    ).select_related('brand', 'category').distinct()
    
    for product in search_results:
        print(f"   • {product.name} - {product.brand.name}")
    
    # 4. Тестируем поиск в общем поиске
    print(f"\n🔍 Общий поиск по 'BMW':")
    general_search = Product.objects.filter(
        Q(article__icontains="BMW") | 
        Q(name__icontains="BMW") | 
        Q(description__icontains="BMW") |
        Q(oem_numbers__oem_number__number__icontains="BMW"),
        is_active=True
    ).select_related('brand', 'category').distinct()
    
    for product in general_search:
        print(f"   • {product.name} - {product.brand.name}")
    
    # 5. Проверяем аналоги для конкретного товара
    original_product = Product.objects.filter(article="C 30 195").first()
    if original_product:
        print(f"\n🔗 Аналоги для товара '{original_product.name}':")
        
        # Получаем все OEM номера этого товара
        oem_numbers = original_product.oem_numbers.all()
        for product_oem in oem_numbers:
            print(f"   OEM: {product_oem.oem_number.number}")
            
            # Находим аналоги по этому OEM
            analogs = Product.objects.filter(
                oem_numbers__oem_number=product_oem.oem_number,
                is_active=True
            ).exclude(id=original_product.id).select_related('brand', 'category')
            
            for analog in analogs:
                print(f"     → {analog.name} - {analog.brand.name} - {analog.price}₽")
    
    print(f"\n✅ Тестирование завершено!")

if __name__ == "__main__":
    test_oem_functionality()
