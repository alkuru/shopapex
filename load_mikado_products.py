#!/usr/bin/env python
import os
import sys
import django
import pandas as pd
import re
import json

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import MikadosProduct

def load_blocked_products():
    """Загружает список заблокированных товаров из файла"""
    blocked_file = '/app/blocked_mikado_products.json'
    if os.path.exists(blocked_file):
        try:
            with open(blocked_file, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_blocked_products(blocked_products):
    """Сохраняет список заблокированных товаров в файл"""
    blocked_file = '/app/blocked_mikado_products.json'
    try:
        with open(blocked_file, 'w', encoding='utf-8') as f:
            json.dump(list(blocked_products), f, ensure_ascii=False, indent=2)
        print(f"💾 Сохранено {len(blocked_products)} заблокированных товаров")
    except Exception as e:
        print(f"❌ Ошибка сохранения заблокированных товаров: {e}")

def parse_quantity(quantity_value):
    """
    Парсит количество товара, обрабатывая специальные символы
    """
    if pd.isna(quantity_value):
        return 0
    
    quantity_str = str(quantity_value).strip()
    
    # Если пустая строка
    if not quantity_str:
        return 0
    
    # Обрабатываем специальные символы
    if '>' in quantity_str:
        # Извлекаем число после '>'
        match = re.search(r'>(\d+)', quantity_str)
        if match:
            return int(match.group(1))
        else:
            return 1  # Если не можем извлечь число, считаем что есть 1
    
    if '<' in quantity_str:
        # Извлекаем число после '<'
        match = re.search(r'<(\d+)', quantity_str)
        if match:
            return int(match.group(1))
        else:
            return 0
    
    if '=' in quantity_str:
        # Извлекаем число после '='
        match = re.search(r'=(\d+)', quantity_str)
        if match:
            return int(match.group(1))
        else:
            return 0
    
    # Пробуем извлечь любое число из строки
    numbers = re.findall(r'\d+', quantity_str)
    if numbers:
        return int(numbers[0])
    
    # Если ничего не найдено, возвращаем 0
    return 0

def load_mikado_products(brand_name, count=5):
    """
    Загружает товары указанного бренда из прайса микадо
    
    Args:
        brand_name (str): Название бренда для поиска
        count (int): Количество товаров для загрузки (по умолчанию 5)
    """
    
    # Загружаем заблокированные товары
    blocked_products = load_blocked_products()
    print(f"🚫 Загружено {len(blocked_products)} заблокированных товаров")
    
    # Путь к файлу прайса
    excel_file = '/app/import/mikado_price_1.xlsx'
    
    if not os.path.exists(excel_file):
        print(f"❌ Файл {excel_file} не найден!")
        return
    
    try:
        # Читаем Excel файл
        df = pd.read_excel(excel_file)
        print(f"📊 Загружен файл с {len(df)} строками")
        
        # Фильтруем товары указанного бренда
        brand_products = df[df['BrandName'].str.contains(brand_name, case=False, na=False)]
        
        if brand_products.empty:
            print(f"❌ Товары бренда {brand_name} не найдены в прайсе")
            return
        
        print(f"🔍 Найдено {len(brand_products)} товаров бренда {brand_name}")
        
        # Берем указанное количество товаров
        selected_products = brand_products.head(count)
        
        created_count = 0
        skipped_blocked = 0
        
        for index, row in selected_products.iterrows():
            try:
                brand = str(row.get('BrandName', '')).strip()
                article = str(row.get('Code', '')).strip()  # Используем Code для артикула
                name = str(row.get('Prodname', '')).strip()
                
                # Создаем уникальный ключ для товара
                product_key = f"{brand}_{article}"
                prodnum_key = f"PRODNUM_{producer_number}"  # Блокировка по Prodnum
                
                # Проверяем, заблокирован ли товар по артикулу
                if product_key in blocked_products:
                    print(f"🚫 Товар {brand} {article} заблокирован по артикулу, пропускаем")
                    skipped_blocked += 1
                    continue
                
                # Проверяем, заблокирован ли товар по Prodnum
                if prodnum_key in blocked_products:
                    print(f"🚫 Товар с Prodnum {producer_number} заблокирован, пропускаем")
                    skipped_blocked += 1
                    continue
                
                price = float(row.get('PriceOut', 0)) if pd.notna(row.get('PriceOut')) else 0
                stock_quantity = parse_quantity(row.get('QTY', 0))
                multiplicity = int(row.get('BatchQty', 1)) if pd.notna(row.get('BatchQty')) else 1
                unit = 'шт'
                warehouse = 'Микадо'
                producer_number = str(row.get('Prodnum', '')).strip()  # Prodnum для producer_number
                code = str(row.get('Code', '')).strip()
                
                if brand and article and name:
                    # Проверяем, существует ли уже такой товар в базе
                    existing_product = MikadosProduct.objects.filter(
                        brand=brand,
                        article=article
                    ).first()
                    
                    if existing_product:
                        print(f"⚠️  Товар {brand} {article} уже существует в базе, блокируем")
                        blocked_products.add(product_key)
                        blocked_products.add(prodnum_key)  # Блокируем и по Prodnum
                        continue
                    
                    # Создаем новый товар
                    product = MikadosProduct.objects.create(
                        brand=brand,
                        article=article,
                        name=name,
                        price=price,
                        stock_quantity=stock_quantity,
                        multiplicity=multiplicity,
                        unit=unit,
                        warehouse=warehouse,
                        producer_number=producer_number,
                        code=code
                    )
                    
                    # Блокируем товар по артикулу и Prodnum
                    blocked_products.add(product_key)
                    blocked_products.add(prodnum_key)
                    
                    created_count += 1
                    print(f"✅ Создан товар: {brand} {article} - {name[:50]}... (количество: {stock_quantity})")
                    
            except Exception as e:
                print(f"❌ Ошибка при создании товара в строке {index + 2}: {str(e)}")
                continue
        
        # Сохраняем обновленный список заблокированных товаров
        save_blocked_products(blocked_products)
        
        print(f"\n🎉 Загружено {created_count} товаров бренда {brand_name}")
        print(f"🚫 Пропущено заблокированных: {skipped_blocked}")
        print(f"💾 Всего заблокировано: {len(blocked_products)} товаров")
        
    except Exception as e:
        print(f"❌ Ошибка при чтении файла: {str(e)}")

if __name__ == '__main__':
    # Пример использования
    if len(sys.argv) > 1:
        brand_name = sys.argv[1]
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        load_mikado_products(brand_name, count)
    else:
        print("Использование: python load_mikado_products.py <brand_name> [count]")
        print("Пример: python load_mikado_products.py BASBUG 5") 