#!/usr/bin/env python
import os
import sys
import django
import pandas as pd
import re

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import MikadosProduct

def parse_quantity(quantity_value):
    """
    Парсит количество товара, обрабатывая специальные символы
    """
    if pd.isna(quantity_value):
        return 0
    
    quantity_str = str(quantity_value).strip()
    
    if not quantity_str:
        return 0
    
    if '>' in quantity_str:
        match = re.search(r'>(\d+)', quantity_str)
        if match:
            return int(match.group(1))
        else:
            return 1
    
    if '<' in quantity_str:
        match = re.search(r'<(\d+)', quantity_str)
        if match:
            return int(match.group(1))
        else:
            return 0
    
    if '=' in quantity_str:
        match = re.search(r'=(\d+)', quantity_str)
        if match:
            return int(match.group(1))
        else:
            return 0
    
    numbers = re.findall(r'\d+', quantity_str)
    if numbers:
        return int(numbers[0])
    
    return 0

def load_mikado_products(brand_name, count=5):
    """
    Загружает товары из прайса Микадо для указанного бренда
    """
    try:
        # Читаем Excel файл
        excel_file = '/app/import/mikado_price_1.xlsx'
        df = pd.read_excel(excel_file)
        
        print(f"📊 Загружено {len(df)} строк из прайса")
        print(f"🔍 Ищем товары бренда: {brand_name}")
        
        # Фильтруем по бренду
        brand_products = df[df['BrandName'].str.contains(brand_name, case=False, na=False)]
        
        if brand_products.empty:
            print(f"❌ Товары бренда {brand_name} не найдены в прайсе")
            return
        
        print(f"✅ Найдено {len(brand_products)} товаров бренда {brand_name}")
        
        # Берем первые count товаров
        selected_products = brand_products.head(count)
        
        created_count = 0
        skipped_count = 0
        
        for index, row in selected_products.iterrows():
            try:
                brand = str(row.get('BrandName', '')).strip()
                article = str(row.get('Code', '')).strip()
                name = str(row.get('Prodname', '')).strip()
                price = float(row.get('PriceOut', 0)) if pd.notna(row.get('PriceOut')) else 0
                stock_quantity = parse_quantity(row.get('QTY', 0))
                multiplicity = int(row.get('BatchQty', 1)) if pd.notna(row.get('BatchQty')) else 1
                unit = 'шт'
                warehouse = 'ЦС-МК'
                code = str(row.get('Code', '')).strip()

                if brand and article and name:
                    # Проверяем существование товара
                    existing_product = MikadosProduct.objects.filter(
                        brand=brand,
                        article=article
                    ).first()

                    if existing_product:
                        print(f"⚠️  Товар {brand} {article} уже существует в базе, пропускаем")
                        skipped_count += 1
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
                        code=code
                    )
                    
                    created_count += 1
                    print(f"✅ Создан товар: {brand} {article} - {name[:50]}... (количество: {stock_quantity})")
                    
            except Exception as e:
                print(f"❌ Ошибка при создании товара в строке {index + 2}: {str(e)}")
                continue
        
        print(f"\n📈 ИТОГО:")
        print(f"✅ Создано товаров: {created_count}")
        print(f"⚠️  Пропущено (уже существуют): {skipped_count}")
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке прайса: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python add_basbug_products.py <brand_name> [count]")
        print("Пример: python add_basbug_products.py BASBUG 5")
        sys.exit(1)
    
    brand_name = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    print(f"🚀 Загружаем {count} товаров бренда {brand_name} из прайса Микадо...")
    load_mikado_products(brand_name, count) 