#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import MikadoProduct

def main():
    print("=== СТАТУС БРЕНДОВ MIKADO ===")
    
    # Проверяем статус проблемных артикулов
    test_articles = ['610.3718.20', '610.3719.20', '610.3715.20']
    print("Проверка проблемных артикулов:")
    for article in test_articles:
        products = MikadoProduct.objects.filter(article=article)
        if products.exists():
            product = products.first()
            print(f"  {article}: '{product.brand}' (должен быть 'Zimmermann')")
        else:
            print(f"  {article}: НЕ НАЙДЕН")
    
    # Проверяем количество проблемных записей
    mannfilter_brake_discs = MikadoProduct.objects.filter(
        brand='MANN-FILTER',
        name__icontains='диск тормозной'
    ).count()
    print(f"\nТормозных дисков с брендом MANN-FILTER: {mannfilter_brake_discs}")
    
    if mannfilter_brake_discs > 0:
        print("❌ ПРОБЛЕМА НЕ РЕШЕНА!")
        print("Нужно запустить fix_mikado_brands_safe.py снова")
        
        # Показываем несколько примеров
        examples = MikadoProduct.objects.filter(
            brand='MANN-FILTER',
            name__icontains='диск тормозной'
        )[:5]
        
        print("\nПримеры неправильных записей:")
        for ex in examples:
            print(f"  {ex.article}: {ex.brand} | {ex.name[:60]}...")
    else:
        print("✅ ПРОБЛЕМА РЕШЕНА!")
    
    # Общая статистика
    total_mikado = MikadoProduct.objects.count()
    print(f"\nВсего товаров Mikado: {total_mikado}")

if __name__ == '__main__':
    main() 