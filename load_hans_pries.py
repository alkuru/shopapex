#!/usr/bin/env python
import os
import sys
import django
import pandas as pd

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import MikadosProduct

# Загружаем прайс
df = pd.read_excel('/app/import/mikado_price_1.xlsx')

# Фильтруем товары Hans Pries
hans_pries_df = df[df['BrandName'] == 'Hans Pries'].head(5)

print(f'Найдено товаров Hans Pries в прайсе: {len(hans_pries_df)}')

# Добавляем товары в базу
added = 0
for _, row in hans_pries_df.iterrows():
    try:
        # Обрабатываем количество (может быть '>4' или число)
        qty = row['QTY']
        if isinstance(qty, str) and qty.startswith('>'):
            stock_qty = int(qty[1:])  # Берем число после '>'
        elif str(qty).isdigit():
            stock_qty = int(qty)
        else:
            stock_qty = 0
            
        MikadosProduct.objects.create(
            brand=row['BrandName'],
            article=row['Code'],
            name=row['Prodname'],
            price=row['PriceOut'],
            stock_quantity=stock_qty,
            producer_number=row['Prodnum'],
            code=row['Code'],
            multiplicity=row['BatchQty'],
            unit='шт',
            warehouse='ЦС-МК'
        )
        added += 1
        print(f'Добавлен: {row["Code"]} - {row["Prodname"]} - {row["PriceOut"]}₽')
        
    except Exception as e:
        print(f'Ошибка при добавлении {row["Code"]}: {e}')

print(f'\nВсего добавлено товаров Hans Pries: {added}')
print(f'Общее количество товаров в базе: {MikadosProduct.objects.count()}') 