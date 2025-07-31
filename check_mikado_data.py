#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import MikadoProduct

def main():
    print("=== ДИАГНОСТИКА MIKADO ===")
    
    total = MikadoProduct.objects.count()
    print(f"Всего товаров: {total}")
    
    if total == 0:
        print("❌ Товаров Mikado нет в базе!")
        print("Возможные причины:")
        print("1. Загрузка прайса не была выполнена")
        print("2. Ошибка при загрузке данных")
        print("3. Данные загружены в другую таблицу")
        return
    
    # Получаем бренды
    brands = list(MikadoProduct.objects.values_list('brand', flat=True).distinct())
    print(f"Уникальных брендов: {len(brands)}")
    
    print("\nПервые 10 брендов:")
    for i, brand in enumerate(brands[:10]):
        count = MikadoProduct.objects.filter(brand=brand).count()
        print(f"{i+1:2d}. '{brand}' ({count} товаров)")
    
    # Проверяем нормализацию
    def normalize_brand(brand_name):
        return str(brand_name).strip().lower().replace(' ', '').replace('-', '').replace('/', '')
    
    print("\nНормализованные версии первых 5 брендов:")
    for brand in brands[:5]:
        norm = normalize_brand(brand)
        print(f"'{brand}' -> '{norm}'")
    
    # Проверяем специальные бренды
    special_brands = ['mahle', 'mann', 'bosch', 'filtron', 'knecht']
    print(f"\nПоиск специальных брендов:")
    for special in special_brands:
        found_brands = [b for b in brands if special.lower() in b.lower()]
        if found_brands:
            for fb in found_brands:
                count = MikadoProduct.objects.filter(brand=fb).count()
                print(f"✅ Найден '{fb}' ({count} товаров)")
        else:
            print(f"❌ '{special}' не найден")

if __name__ == '__main__':
    main() 