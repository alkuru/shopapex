#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import MikadoProduct

def main():
    print("=== ИСПРАВЛЕНИЕ ТОРМОЗНЫХ ДИСКОВ НА ZIMMERMANN ===")
    
    # Находим все тормозные диски с неправильным брендом MANN-FILTER
    wrong_brake_discs = MikadoProduct.objects.filter(
        brand='MANN-FILTER',
        name__icontains='диск тормозной'
    )
    
    print(f"Найдено {wrong_brake_discs.count()} тормозных дисков с неправильным брендом")
    
    # Анализируем артикулы - тормозные диски Zimmermann обычно имеют формат XXX.XXXX.XX
    zimmermann_pattern = True  # Практически все диски с таким форматом - это Zimmermann
    
    fixed_count = 0
    
    for product in wrong_brake_discs:
        article = product.article.strip()
        
        # Тормозные диски с таким форматом номера почти всегда Zimmermann
        if '.' in article and 'диск тормозной' in product.name.lower():
            print(f"Исправляю {article}: 'MANN-FILTER' -> 'Zimmermann'")
            
            # Проверяем на дубликаты
            existing = MikadoProduct.objects.filter(
                brand='Zimmermann',
                article=article
            ).exclude(id=product.id)
            
            if existing.exists():
                print(f"  Удаляю дубликат с брендом MANN-FILTER")
                product.delete()
            else:
                product.brand = 'Zimmermann'
                product.save()
            
            fixed_count += 1
        else:
            print(f"❓ Пропускаю {article} - нестандартный формат")
    
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
    
    # Проверяем количество дисков Zimmermann
    zimmermann_discs = MikadoProduct.objects.filter(
        brand='Zimmermann',
        name__icontains='диск тормозной'
    ).count()
    
    print(f"\nВсего тормозных дисков Zimmermann: {zimmermann_discs}")

if __name__ == '__main__':
    main() 