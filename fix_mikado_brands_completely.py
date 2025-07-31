#!/usr/bin/env python
import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import MikadoProduct

def main():
    print("=== ПОЛНОЕ ВОССТАНОВЛЕНИЕ БРЕНДОВ MIKADO ===")
    
    # Читаем оригинальный файл
    file_path = "import/SPB-MSK_0033749_250725.xlsx"
    
    try:
        df = pd.read_excel(file_path)
        print(f"Загружен файл с {len(df)} товарами")
        
        # Создаем словарь: артикул -> правильный бренд
        article_to_brand = {}
        for _, row in df.iterrows():
            article = str(row['Код товара']).strip()
            brand = str(row['Бренд']).strip()
            article_to_brand[article] = brand
        
        print(f"Создан словарь для {len(article_to_brand)} артикулов")
        
        # Восстанавливаем правильные бренды в базе данных
        updated_count = 0
        total_products = MikadoProduct.objects.count()
        
        print("Начинаем восстановление брендов...")
        
        for i, product in enumerate(MikadoProduct.objects.all(), 1):
            article = product.article.strip()
            
            if article in article_to_brand:
                correct_brand = article_to_brand[article]
                
                # Если бренд отличается от правильного - исправляем
                if product.brand != correct_brand:
                    old_brand = product.brand
                    product.brand = correct_brand
                    product.save()
                    updated_count += 1
                    
                    if updated_count <= 10:  # Показываем первые 10 исправлений
                        print(f"✅ {article}: '{old_brand}' -> '{correct_brand}'")
            
            # Показываем прогресс каждые 10000 товаров
            if i % 10000 == 0:
                print(f"Обработано: {i}/{total_products} товаров, исправлено: {updated_count}")
        
        print(f"\n=== РЕЗУЛЬТАТ ===")
        print(f"Всего товаров: {total_products}")
        print(f"Исправлено брендов: {updated_count}")
        
        # Проверяем результат на проблемных артикулах
        print(f"\n=== ПРОВЕРКА РЕЗУЛЬТАТА ===")
        test_articles = ["610.3718.20", "610.3719.20", "610.3715.20"]
        
        for article in test_articles:
            products = MikadoProduct.objects.filter(article=article)
            if products.exists():
                product = products.first()
                expected_brand = article_to_brand.get(article, "НЕ НАЙДЕН")
                status = "✅" if product.brand == expected_brand else "❌"
                print(f"{status} {article}: {product.brand} (ожидался: {expected_brand})")
        
        print(f"\nВосстановление завершено!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main() 