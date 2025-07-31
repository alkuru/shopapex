#!/usr/bin/env python
import os
import pandas as pd
import glob

def main():
    print("=== ПОИСК ОРИГИНАЛЬНЫХ ФАЙЛОВ MIKADO ===")
    
    # Ищем Excel файлы Mikado
    possible_paths = [
        "*.xlsx",
        "*.xls", 
        "Mikado*.xlsx",
        "mikado*.xlsx",
        "MIKADO*.xlsx",
        "**/*.xlsx",
        "**/*mikado*.xlsx"
    ]
    
    mikado_files = []
    for pattern in possible_paths:
        files = glob.glob(pattern, recursive=True)
        mikado_files.extend([f for f in files if 'mikado' in f.lower()])
    
    if not mikado_files:
        print("❌ Файлы Mikado не найдены в текущей директории")
        print("Доступные Excel файлы:")
        all_excel = glob.glob("**/*.xlsx", recursive=True)
        for f in all_excel[:10]:
            print(f"  {f}")
        return
    
    print(f"Найдено файлов Mikado: {len(mikado_files)}")
    for f in mikado_files:
        print(f"  {f}")
    
    # Анализируем первый найденный файл
    test_file = mikado_files[0]
    print(f"\n=== АНАЛИЗ ФАЙЛА: {test_file} ===")
    
    try:
        # Читаем Excel файл
        df = pd.read_excel(test_file)
        print(f"Колонки в файле: {list(df.columns)}")
        
        # Ищем колонку с брендами
        brand_columns = [col for col in df.columns if any(word in col.lower() for word in ['brand', 'бренд', 'марка', 'manufacturer'])]
        
        if brand_columns:
            brand_col = brand_columns[0]
            print(f"Колонка с брендами: {brand_col}")
            
            # Анализируем бренды проблемных артикулов
            problem_articles = ["610.3718.20", "610.3719.20", "610.3715.20"]
            
            # Ищем колонку с артикулами
            article_columns = [col for col in df.columns if any(word in col.lower() for word in ['article', 'артикул', 'код', 'part'])]
            
            if article_columns:
                article_col = article_columns[0]
                print(f"Колонка с артикулами: {article_col}")
                
                for article in problem_articles:
                    # Ищем товар в файле
                    mask = df[article_col].astype(str).str.contains(article, case=False, na=False)
                    found_products = df[mask]
                    
                    if not found_products.empty:
                        product = found_products.iloc[0]
                        original_brand = product[brand_col]
                        print(f"\n📋 Артикул: {article}")
                        print(f"   Оригинальный бренд: {original_brand}")
                        if 'name' in df.columns:
                            print(f"   Описание: {product.get('name', 'N/A')}")
                        elif 'наименование' in df.columns.str.lower():
                            name_col = [col for col in df.columns if 'наименование' in col.lower()][0]
                            print(f"   Описание: {product.get(name_col, 'N/A')}")
                        else:
                            desc_cols = [col for col in df.columns if any(word in col.lower() for word in ['name', 'description', 'наименование', 'описание'])]
                            if desc_cols:
                                print(f"   Описание: {product.get(desc_cols[0], 'N/A')}")
                    else:
                        print(f"\n❌ Артикул {article} не найден в файле")
            
            # Показываем уникальные бренды
            unique_brands = df[brand_col].dropna().unique()[:20]
            print(f"\nПервые 20 уникальных брендов в файле:")
            for i, brand in enumerate(unique_brands, 1):
                print(f"  {i:2d}. {brand}")
                
        else:
            print("❌ Колонка с брендами не найдена")
            
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")

if __name__ == '__main__':
    main() 