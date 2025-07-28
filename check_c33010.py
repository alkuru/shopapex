#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import AutoKontinentProduct

def check_c33010():
    """Проверяет наличие C33010 AZUMI в базе АвтоКонтинента"""
    
    print("=== Проверка C33010 AZUMI в базе АвтоКонтинента ===\n")
    
    # Ищем C33010
    products = AutoKontinentProduct.objects.filter(
        article__icontains='C33010'
    )
    
    print(f"Найдено товаров с артикулом C33010: {products.count()}")
    
    for product in products:
        print(f"\nТовар:")
        print(f"  Артикул: {product.article}")
        print(f"  Бренд: {product.brand}")
        print(f"  Название: {product.name[:100]}...")
        print(f"  Цена: {product.price}")
        print(f"  СЕВ_СПб: {product.stock_spb_north}")
        print(f"  СПб: {product.stock_spb}")
        print(f"  МСК: {product.stock_msk}")
    
    # Ищем AZUMI
    azumi_products = AutoKontinentProduct.objects.filter(
        brand__icontains='AZUMI'
    )
    
    print(f"\nНайдено товаров бренда AZUMI: {azumi_products.count()}")
    
    for product in azumi_products[:5]:  # Показываем первые 5
        print(f"\nAZUMI товар:")
        print(f"  Артикул: {product.article}")
        print(f"  Бренд: {product.brand}")
        print(f"  Название: {product.name[:100]}...")
        print(f"  Цена: {product.price}")

if __name__ == "__main__":
    check_c33010() 