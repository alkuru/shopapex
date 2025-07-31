#!/usr/bin/env python
import os
import django
import pandas as pd
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import MikadoProduct

def main():
    print("=== БЕЗОПАСНОЕ ВОССТАНОВЛЕНИЕ БРЕНДОВ MIKADO ===")
    
    # Читаем оригинальный файл
    file_path = "import/mikado_price_1.xlsx"
    
    try:
        df = pd.read_excel(file_path)
        print(f"Загружен файл с {len(df)} товарами")
        
        # Создаем словарь: артикул -> правильный бренд
        article_to_brand = {}
        for _, row in df.iterrows():
            article = str(row['Code']).strip()
            brand = str(row['BrandName']).strip()
            article_to_brand[article] = brand
        
        print(f"Создан словарь для {len(article_to_brand)} артикулов")
        
        # Восстанавливаем правильные бренды в базе данных
        updated_count = 0
        total_products = MikadoProduct.objects.count()
        
        print("Начинаем восстановление брендов...")
        
        # Обрабатываем товары батчами для эффективности
        batch_size = 1000
        processed = 0
        
        with transaction.atomic():
            all_products = MikadoProduct.objects.all()
            
            for product in all_products:
                article = product.article.strip()
                
                if article in article_to_brand:
                    correct_brand = article_to_brand[article]
                    
                    # Если бренд отличается от правильного - исправляем
                    if product.brand != correct_brand:
                        old_brand = product.brand
                        
                        # Проверяем, не создаст ли это дубликат
                        existing = MikadoProduct.objects.filter(
                            brand=correct_brand, 
                            article=article
                        ).exclude(id=product.id)
                        
                        if existing.exists():
                            # Если дубликат существует, удаляем текущую запись
                            print(f"🗑️ Удаляем дубликат {article} ({old_brand})")
                            product.delete()
                        else:
                            # Безопасно обновляем бренд
                            product.brand = correct_brand
                            product.save()
                            updated_count += 1
                            
                            if updated_count <= 20:  # Показываем первые 20 исправлений
                                print(f"✅ {article}: '{old_brand}' -> '{correct_brand}'")
                
                processed += 1
                
                # Показываем прогресс каждые 10000 товаров
                if processed % 10000 == 0:
                    print(f"Обработано: {processed}/{total_products} товаров, исправлено: {updated_count}")
        
        print(f"\n=== РЕЗУЛЬТАТ ===")
        print(f"Всего товаров обработано: {processed}")
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
            else:
                expected_brand = article_to_brand.get(article, "НЕ НАЙДЕН")
                print(f"❌ {article}: НЕ НАЙДЕН В БАЗЕ (ожидался: {expected_brand})")
        
        # Финальная проверка проблемных брендов
        print(f"\n=== ПРОВЕРКА ПРОБЛЕМНЫХ БРЕНДОВ ===")
        mannfilter_brake_discs = MikadoProduct.objects.filter(
            brand="MANN-FILTER",
            name__icontains="диск тормозной"
        ).count()
        print(f"Тормозных дисков с брендом MANN-FILTER: {mannfilter_brake_discs}")
        
        if mannfilter_brake_discs == 0:
            print("✅ Проблема решена!")
        else:
            print(f"❌ Осталось {mannfilter_brake_discs} проблемных записей")
        
        print(f"\nВосстановление завершено!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 