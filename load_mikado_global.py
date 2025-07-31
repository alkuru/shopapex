#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Глобальный загрузчик прайса Mikado с обработкой специальных значений
"""
import os
import sys
import django
import pandas as pd
from decimal import Decimal

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import MikadoProduct

def parse_quantity(qty_val) -> int:
    """Глобальное правило для обработки количества товара"""
    try:
        if pd.isna(qty_val):
            return 0
        elif isinstance(qty_val, str):
            qty_str = str(qty_val).strip().lower()
            if '>' in qty_str:
                # Если '>4', берем 5
                return 5
            elif qty_str in ['nan', 'none', '']:
                return 0
            else:
                return int(float(qty_str))
        else:
            return int(float(qty_val))
    except:
        return 0

def load_mikado_brand(brand_name, limit=5):
    """Загружает товары конкретного бренда с глобальными правилами"""
    
    print(f'🔍 Загрузка товаров {brand_name} (лимит: {limit})...')
    
    # Читаем Excel файл
    df = pd.read_excel('/app/import/mikado_price_1.xlsx')
    brand_items = df[df['BrandName'] == brand_name]
    
    if len(brand_items) == 0:
        print(f'❌ Товары бренда {brand_name} не найдены')
        return 0
    
    print(f'📦 Найдено товаров {brand_name}: {len(brand_items)}')
    
    created_count = 0
    error_count = 0
    
    for index, row in brand_items.head(limit).iterrows():
        try:
            article = str(row['Code']).strip()
            brand = brand_name
            name = str(row['Prodname']).strip()
            
            # Обработка цены
            try:
                price = float(row['PriceOut']) if pd.notna(row['PriceOut']) else 0
            except:
                price = 0
                
            # Глобальная обработка количества
            stock = parse_quantity(row['QTY'])
            
            # Обработка кратности
            try:
                multiplicity = int(float(row['BatchQty'])) if pd.notna(row['BatchQty']) else 1
            except:
                multiplicity = 1
            
            # Создаем товар
            MikadoProduct.objects.create(
                brand=brand,
                article=article,
                name=name,
                price=Decimal(str(price)),
                stock_quantity=stock,
                producer_number=article,
                code=article,
                warehouse='ЦС-МК',
                multiplicity=multiplicity,
                unit='шт'
            )
            
            created_count += 1
            print(f'  ✅ {article} | {name[:30]}... | stock: {stock}')
            
        except Exception as e:
            error_count += 1
            if error_count <= 5:
                print(f'  ❌ Ошибка в строке {index}: {e}')
            continue
    
    print(f'🎯 Загружено товаров {brand_name}: {created_count}')
    print(f'❌ Ошибок: {error_count}')
    
    return created_count

def load_all_mikado_brands():
    """Загружает все бренды по 5 товаров каждый"""
    
    print('🚀 Глобальная загрузка всех брендов Mikado...')
    print('=' * 50)
    
    # Читаем Excel файл
    df = pd.read_excel('/app/import/mikado_price_1.xlsx')
    all_brands = df['BrandName'].unique()
    
    print(f'📋 Найдено брендов: {len(all_brands)}')
    
    total_created = 0
    
    for brand in all_brands:
        if pd.notna(brand) and brand.strip():
            created = load_mikado_brand(brand.strip(), limit=5)
            total_created += created
            print('-' * 30)
    
    print(f'\n🎉 Глобальная загрузка завершена!')
    print(f'📊 Всего загружено товаров: {total_created}')
    
    # Проверка
    total_count = MikadoProduct.objects.count()
    print(f'📊 Всего товаров Mikado в базе: {total_count}')
    
    return total_created

if __name__ == '__main__':
    if len(sys.argv) > 1:
        brand_name = sys.argv[1]
        load_mikado_brand(brand_name)
    else:
        load_all_mikado_brands() 