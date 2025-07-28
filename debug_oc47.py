#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def debug_oc47():
    """Детальная отладка товара OC47"""
    
    print("=== Детальная отладка OC47 Knecht/Mahle ===\n")
    
    # 1. Проверяем API напрямую
    print("1. Запрос к FastAPI:")
    try:
        api_url = "http://localhost:8001/unified_search"
        params = {"article": "OC47", "brand": "Knecht/Mahle"}
        
        response = requests.get(api_url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', [])
            
            autokontinent_items = [item for item in items if item.get('source') == 'autokontinent_db']
            
            print(f"Найдено товаров АвтоКонтинент: {len(autokontinent_items)}")
            
            for i, item in enumerate(autokontinent_items):
                print(f"\nТовар {i+1}:")
                print(f"  Артикул: {item.get('article')}")
                print(f"  Бренд: {item.get('brand')}")
                print(f"  Склад (warehouse): {item.get('warehouse')}")
                print(f"  Наличие: {item.get('availability')}")
                print(f"  Источник: {item.get('source')}")
                print(f"  Цена: {item.get('price')}")
                print(f"  Описание: {item.get('description')[:100]}...")
        else:
            print(f"Ошибка API: {response.status_code}")
            
    except Exception as e:
        print(f"Ошибка запроса к API: {e}")
    
    # 2. Проверяем базу данных напрямую
    print("\n\n2. Проверка базы данных:")
    try:
        import os
        import sys
        import django
        
        # Настройка Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
        django.setup()
        
        from catalog.models import AutoKontinentProduct
        
        # Ищем товар в базе
        products = AutoKontinentProduct.objects.filter(
            article__icontains='OC47',
            brand__icontains='Knecht'
        )
        
        print(f"Найдено товаров в базе: {products.count()}")
        
        for product in products:
            print(f"\nТовар в базе:")
            print(f"  Артикул: {product.article}")
            print(f"  Бренд: {product.brand}")
            print(f"  СЕВ_СПб: {product.stock_spb_north}")
            print(f"  СПб: {product.stock_spb}")
            print(f"  МСК: {product.stock_msk}")
            print(f"  Цена: {product.price}")
            print(f"  Название: {product.name[:100]}...")
            
    except Exception as e:
        print(f"Ошибка проверки базы: {e}")

if __name__ == "__main__":
    debug_oc47() 