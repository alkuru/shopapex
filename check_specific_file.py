#!/usr/bin/env python
import pandas as pd

def main():
    file_path = "import/SPB-MSK_0033749_250725.xlsx"
    
    print(f"=== АНАЛИЗ ФАЙЛА: {file_path} ===")
    
    try:
        # Читаем Excel файл
        df = pd.read_excel(file_path)
        print(f"Количество строк: {len(df)}")
        print(f"Колонки в файле: {list(df.columns)}")
        
        # Ищем колонку с брендами
        brand_columns = [col for col in df.columns if any(word in col.lower() for word in ['brand', 'бренд', 'марка', 'manufacturer'])]
        
        if brand_columns:
            brand_col = brand_columns[0]
            print(f"\nКолонка с брендами: {brand_col}")
            
            # Ищем колонку с артикулами
            article_columns = [col for col in df.columns if any(word in col.lower() for word in ['article', 'артикул', 'код', 'part', 'номер'])]
            
            if article_columns:
                article_col = article_columns[0]
                print(f"Колонка с артикулами: {article_col}")
                
                # Анализируем проблемные артикулы
                problem_articles = ["610.3718.20", "610.3719.20", "610.3715.20"]
                
                for article in problem_articles:
                    # Ищем товар в файле (точное совпадение и частичное)
                    exact_mask = df[article_col].astype(str) == article
                    partial_mask = df[article_col].astype(str).str.contains(article, case=False, na=False)
                    
                    found_products = df[exact_mask | partial_mask]
                    
                    if not found_products.empty:
                        product = found_products.iloc[0]
                        original_brand = product[brand_col]
                        original_article = product[article_col]
                        print(f"\n📋 НАЙДЕН: {original_article}")
                        print(f"   Оригинальный бренд: '{original_brand}'")
                        
                        # Ищем описание
                        desc_cols = [col for col in df.columns if any(word in col.lower() for word in ['name', 'description', 'наименование', 'описание', 'товар'])]
                        if desc_cols:
                            desc_col = desc_cols[0]
                            print(f"   Описание: {product[desc_col]}")
                    else:
                        print(f"\n❌ Артикул {article} не найден в файле")
                
                # Показываем уникальные бренды из файла
                unique_brands = df[brand_col].dropna().unique()
                print(f"\nВсего уникальных брендов в файле: {len(unique_brands)}")
                print(f"Первые 30 брендов:")
                for i, brand in enumerate(unique_brands[:30], 1):
                    count = (df[brand_col] == brand).sum()
                    print(f"  {i:2d}. '{brand}' ({count} товаров)")
                
                # Ищем бренды тормозных дисков
                print(f"\n=== ПОИСК БРЕНДОВ ТОРМОЗНЫХ ДИСКОВ ===")
                desc_cols = [col for col in df.columns if any(word in col.lower() for word in ['name', 'description', 'наименование', 'описание', 'товар'])]
                if desc_cols:
                    desc_col = desc_cols[0]
                    brake_discs = df[df[desc_col].str.contains('диск тормозной', case=False, na=False)]
                    
                    if not brake_discs.empty:
                        brake_brands = brake_discs[brand_col].value_counts()
                        print(f"Бренды тормозных дисков:")
                        for brand, count in brake_brands.head(10).items():
                            print(f"  {brand}: {count} товаров")
                    else:
                        print("Тормозные диски не найдены в описаниях")
                
            else:
                print("❌ Колонка с артикулами не найдена")
                
        else:
            print("❌ Колонка с брендами не найдена")
            print("Первые 5 строк файла:")
            print(df.head())
            
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")

if __name__ == '__main__':
    main() 