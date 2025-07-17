#!/usr/bin/env python
"""
Скрипт для загрузки следующей партии реальных товаров (10 штук) из ABCP API
"""
import os
import sys
import django
from django.conf import settings

# Настройка Django окружения
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex.settings')
django.setup()

from catalog.models import Supplier, Product, Category, Brand
import requests
import json
import time
from decimal import Decimal

def load_next_batch_products():
    """Загружает следующую партию товаров (10 штук)"""
    
    print("🔄 Начинаем загрузку следующей партии товаров...")
    
    # Получаем поставщика VintTop
    try:
        supplier = Supplier.objects.get(name="VintTop")
        print(f"✓ Найден поставщик: {supplier.name}")
    except Supplier.DoesNotExist:
        print("❌ Поставщик VintTop не найден!")
        return
    
    # Проверяем количество уже загруженных товаров
    existing_count = Product.objects.filter(supplier=supplier).count()
    print(f"📊 Уже загружено товаров: {existing_count}")
    
    # Получаем список различных типов товаров для разнообразия
    search_queries = [
        "масло моторное",      # Моторные масла
        "фильтр топливный",    # Топливные фильтры
        "свеча зажигания",     # Свечи зажигания
        "тормозные колодки",   # Тормозные колодки
        "амортизатор",         # Амортизаторы
        "радиатор",           # Радиаторы
        "генератор",          # Генераторы
        "стартер",            # Стартеры
        "ремень ГРМ",         # Ремни ГРМ
        "подшипник",          # Подшипники
    ]
    
    loaded_products = []
    
    for i, query in enumerate(search_queries, 1):
        print(f"\n🔍 Поиск товаров по запросу '{query}' ({i}/10)...")
        
        try:
            # Выполняем поиск
            search_results = supplier.search_products(query, limit=5)
            
            if not search_results:
                print(f"❌ Не найдено товаров по запросу '{query}'")
                continue
            
            # Берем первый товар из результатов поиска
            product_data = search_results[0]
            
            # Проверяем, не загружен ли уже этот товар
            existing_product = Product.objects.filter(
                supplier=supplier,
                supplier_product_id=product_data.get('id')
            ).first()
            
            if existing_product:
                print(f"⚠️ Товар {product_data.get('brand')} {product_data.get('number')} уже существует")
                continue
            
            # Создаем/получаем категорию
            category_name = "Автозапчасти"
            if "масло" in query.lower():
                category_name = "Масла и жидкости"
            elif "фильтр" in query.lower():
                category_name = "Фильтры"
            elif "свеча" in query.lower():
                category_name = "Система зажигания"
            elif "тормоз" in query.lower():
                category_name = "Тормозная система"
            elif any(word in query.lower() for word in ["амортизатор", "подвеска"]):
                category_name = "Подвеска"
            elif any(word in query.lower() for word in ["радиатор", "охлаждение"]):
                category_name = "Система охлаждения"
            elif any(word in query.lower() for word in ["генератор", "стартер", "электрика"]):
                category_name = "Электрооборудование"
            elif "ремень" in query.lower():
                category_name = "Ремни и цепи"
            elif "подшипник" in query.lower():
                category_name = "Подшипники"
            
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={'description': f'Категория {category_name}'}
            )
            if created:
                print(f"✓ Создана новая категория: {category_name}")
            
            # Создаем/получаем бренд
            brand_name = product_data.get('brand', 'Unknown').strip()
            if brand_name and brand_name != 'Unknown':
                brand, created = Brand.objects.get_or_create(
                    name=brand_name,
                    defaults={'description': f'Бренд {brand_name}'}
                )
                if created:
                    print(f"✓ Создан новый бренд: {brand_name}")
            else:
                brand = None
            
            # Улучшаем название товара
            original_name = product_data.get('name', '').strip()
            number = product_data.get('number', '').strip()
            
            improved_name = improve_product_name(original_name, brand_name, number, query)
            
            # Создаем товар
            product = Product.objects.create(
                name=improved_name,
                description=f"Артикул: {number}\nОригинальное название: {original_name}",
                price=Decimal(str(product_data.get('price', 0))),
                category=category,
                brand=brand,
                supplier=supplier,
                supplier_product_id=product_data.get('id'),
                article_number=number,
                stock_quantity=product_data.get('quantity', 0),
                is_active=True
            )
            
            loaded_products.append({
                'name': improved_name,
                'brand': brand_name,
                'number': number,
                'price': product.price,
                'category': category_name
            })
            
            print(f"✅ Создан товар: {improved_name} (ID: {product.id})")
            
            # Небольшая задержка между запросами
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Ошибка при загрузке товара по запросу '{query}': {str(e)}")
            continue
    
    # Выводим итоговую статистику
    print(f"\n📊 ИТОГИ ЗАГРУЗКИ:")
    print(f"✅ Успешно загружено товаров: {len(loaded_products)}")
    print(f"📦 Общее количество товаров у поставщика: {Product.objects.filter(supplier=supplier).count()}")
    
    if loaded_products:
        print(f"\n📋 ЗАГРУЖЕННЫЕ ТОВАРЫ:")
        for i, product in enumerate(loaded_products, 1):
            print(f"{i:2d}. {product['brand']} {product['number']} - {product['name']}")
            print(f"     💰 {product['price']} руб. | 📂 {product['category']}")
    
    print(f"\n✅ Загрузка завершена!")

def improve_product_name(original_name, brand, number, search_query):
    """Улучшает название товара для лучшего восприятия"""
    
    if not original_name:
        return f"{brand} {number}" if brand else number
    
    # Убираем артикул из названия если он уже есть в начале
    name = original_name
    if number and name.startswith(number):
        name = name[len(number):].strip()
        if name.startswith('-') or name.startswith(','):
            name = name[1:].strip()
    
    # Убираем бренд из названия если он уже есть в начале
    if brand and name.lower().startswith(brand.lower()):
        name = name[len(brand):].strip()
        if name.startswith('-') or name.startswith(','):
            name = name[1:].strip()
    
    # Если название стало пустым, используем оригинальное
    if not name.strip():
        name = original_name
    
    # Добавляем бренд в начало если его нет
    if brand and not name.lower().startswith(brand.lower()):
        name = f"{brand} {name}"
    
    # Специальные улучшения для разных типов товаров
    if "масло" in search_query.lower():
        if "моторное" not in name.lower() and "масло" in name.lower():
            name = name.replace("масло", "масло моторное", 1)
    elif "фильтр" in search_query.lower():
        if "фильтр" in name.lower() and "топливный" not in name.lower():
            if "топлив" in search_query.lower():
                name = name.replace("фильтр", "фильтр топливный", 1)
    elif "свеча" in search_query.lower():
        if "свеча" in name.lower() and "зажигания" not in name.lower():
            name = name.replace("свеча", "свеча зажигания", 1)
    elif "колодки" in search_query.lower():
        if "колодки" in name.lower() and "тормозные" not in name.lower():
            name = name.replace("колодки", "тормозные колодки", 1)
    
    return name.strip()

if __name__ == "__main__":
    load_next_batch_products()
