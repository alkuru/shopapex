import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import AutoKontinentProduct

def check_brand_update_results():
    """Проверяет результаты обновления брендов"""
    print("=== ПРОВЕРКА РЕЗУЛЬТАТОВ ОБНОВЛЕНИЯ БРЕНДОВ ===\n")
    
    # Проверяем базу данных
    total_products = AutoKontinentProduct.objects.count()
    print(f"Всего товаров в базе: {total_products}")
    
    # Проверяем конкретные бренды
    print("\n=== ПРОВЕРКА КОНКРЕТНЫХ БРЕНДОВ ===")
    
    # Проверяем Mahle
    mahle_products = AutoKontinentProduct.objects.filter(brand__icontains='Mahle')
    print(f"Товары с брендом 'Mahle': {mahle_products.count()}")
    
    for product in mahle_products[:5]:  # Показываем первые 5
        print(f"  - {product.brand} | {product.article} | {product.name[:50]}...")
    
    # Проверяем Knecht/Mahle
    knecht_mahle_products = AutoKontinentProduct.objects.filter(brand='Knecht/Mahle')
    print(f"\nТовары с брендом 'Knecht/Mahle': {knecht_mahle_products.count()}")
    
    if knecht_mahle_products.count() > 0:
        print("Примеры товаров Knecht/Mahle:")
        for product in knecht_mahle_products[:3]:
            print(f"  - {product.article} | {product.name[:50]}...")
    
    # Проверяем Mann
    mann_products = AutoKontinentProduct.objects.filter(brand__icontains='Mann')
    print(f"\nТовары с брендом 'Mann': {mann_products.count()}")
    
    for product in mann_products[:5]:  # Показываем первые 5
        print(f"  - {product.brand} | {product.article} | {product.name[:50]}...")
    
    # Статистика по брендам
    print("\n=== СТАТИСТИКА ПО БРЕНДАМ ===")
    from django.db.models import Count
    brand_stats = AutoKontinentProduct.objects.values('brand').annotate(count=Count('id')).order_by('-count')[:10]
    
    print("Топ-10 брендов по количеству товаров:")
    for stat in brand_stats:
        print(f"  {stat['brand']}: {stat['count']} товаров")
    
    # Проверяем уникальные бренды
    unique_brands = AutoKontinentProduct.objects.values_list('brand', flat=True).distinct()
    print(f"\nВсего уникальных брендов: {unique_brands.count()}")

if __name__ == "__main__":
    check_brand_update_results() 