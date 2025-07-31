#!/usr/bin/env python
import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import MikadoProduct

def main():
    print("=== ИСПРАВЛЕНИЕ ОСТАВШИХСЯ ТОРМОЗНЫХ ДИСКОВ ===")
    
    # Читаем оригинальный файл для получения правильных брендов
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
        
        # Находим все тормозные диски с неправильным брендом MANN-FILTER
        wrong_brake_discs = MikadoProduct.objects.filter(
            brand='MANN-FILTER',
            name__icontains='диск тормозной'
        )
        
        print(f"Найдено {wrong_brake_discs.count()} тормозных дисков с неправильным брендом")
        
        fixed_count = 0
        
        for product in wrong_brake_discs:
            article = product.article.strip()
            
            if article in article_to_brand:
                correct_brand = article_to_brand[article]
                
                print(f"Исправляю {article}: 'MANN-FILTER' -> '{correct_brand}'")
                
                # Проверяем на дубликаты
                existing = MikadoProduct.objects.filter(
                    brand=correct_brand,
                    article=article
                ).exclude(id=product.id)
                
                if existing.exists():
                    print(f"  Удаляю дубликат")
                    product.delete()
                else:
                    product.brand = correct_brand
                    product.save()
                
                fixed_count += 1
            else:
                print(f"❌ Артикул {article} не найден в оригинальном файле")
        
        print(f"\n=== РЕЗУЛЬТАТ ===")
        print(f"Исправлено записей: {fixed_count}")
        
        # Финальная проверка
        remaining = MikadoProduct.objects.filter(
            brand='MANN-FILTER',
            name__icontains='диск тормозной'
        ).count()
        
        print(f"Осталось неправильных записей: {remaining}")
        
        if remaining == 0:
            print("✅ ВСЕ ТОРМОЗНЫЕ ДИСКИ ИСПРАВЛЕНЫ!")
        else:
            print(f"❌ Осталось {remaining} проблемных записей")
            
            # Показываем оставшиеся проблемы
            remaining_discs = MikadoProduct.objects.filter(
                brand='MANN-FILTER',
                name__icontains='диск тормозной'
            )[:5]
            
            print("Оставшиеся проблемы:")
            for disc in remaining_discs:
                print(f"  {disc.article}: {disc.name[:60]}...")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 