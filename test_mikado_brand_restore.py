#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import MikadoProduct
from catalog.api_views import process_mikado_brand_update

def main():
    print("=== ТЕСТ ВОССТАНОВЛЕНИЯ БРЕНДОВ MIKADO КАК ВЧЕРА ===")
    
    # Проверяем начальное состояние
    print("1. Проверяем начальное состояние...")
    total_before = MikadoProduct.objects.count()
    brands_before = MikadoProduct.objects.values_list('brand', flat=True).distinct().count()
    
    print(f"Всего товаров Mikado: {total_before}")
    print(f"Уникальных брендов: {brands_before}")
    
    # Показываем первые 10 брендов
    first_brands = list(MikadoProduct.objects.values_list('brand', flat=True).distinct()[:10])
    print("Первые 10 брендов:")
    for i, brand in enumerate(first_brands, 1):
        count = MikadoProduct.objects.filter(brand=brand).count()
        print(f"  {i}. '{brand}' ({count} товаров)")
    
    # Проверяем проблемные бренды
    brake_discs_before = MikadoProduct.objects.filter(
        brand='MANN-FILTER',
        name__icontains='диск тормозной'
    ).count()
    print(f"\nТормозных дисков с брендом MANN-FILTER: {brake_discs_before}")
    
    # Запускаем восстановление брендов
    print(f"\n2. Запускаем восстановление брендов Mikado...")
    process_mikado_brand_update()
    
    # Проверяем результат
    print(f"\n3. Проверяем результат...")
    total_after = MikadoProduct.objects.count()
    brands_after = MikadoProduct.objects.values_list('brand', flat=True).distinct().count()
    brake_discs_after = MikadoProduct.objects.filter(
        brand='MANN-FILTER',
        name__icontains='диск тормозной'
    ).count()
    
    print(f"Всего товаров Mikado: {total_after}")
    print(f"Уникальных брендов: {brands_after}")
    print(f"Тормозных дисков с брендом MANN-FILTER: {brake_discs_after}")
    
    # Проверяем конкретные артикулы
    print(f"\n4. Проверяем конкретные артикулы...")
    test_articles = ['610.3719.20', '610.3715.20']
    
    for article in test_articles:
        products = MikadoProduct.objects.filter(article=article)
        if products.exists():
            product = products.first()
            print(f"✅ {article}: {product.brand}")
        else:
            print(f"❌ {article}: НЕ НАЙДЕН")
    
    # Проверяем нормализованные бренды
    print(f"\n5. Проверяем нормализованные бренды...")
    normalized_brands = [
        'BOSCH', 'MANN-FILTER', 'Knecht/Mahle', 'FILTRON', 
        'Zimmermann', 'BREMBO', 'FEBI BILSTEIN'
    ]
    
    for brand in normalized_brands:
        count = MikadoProduct.objects.filter(brand=brand).count()
        if count > 0:
            print(f"✅ {brand}: {count} товаров")
        else:
            print(f"❌ {brand}: нет товаров")
    
    # Итоговая оценка
    print(f"\n=== ИТОГОВАЯ ОЦЕНКА ===")
    
    changes = abs(total_after - total_before)
    brand_changes = abs(brands_after - brands_before)
    
    if changes == 0:
        print("✅ Количество товаров сохранено")
    else:
        print(f"⚠️ Изменилось товаров: {changes}")
    
    if brake_discs_after == 0:
        print("✅ Проблема с тормозными дисками решена!")
    elif brake_discs_after < brake_discs_before:
        print(f"🔶 Проблема частично решена: было {brake_discs_before}, стало {brake_discs_after}")
    else:
        print(f"❌ Проблема не решена: {brake_discs_after}")
    
    if brand_changes > 0:
        print(f"✅ Бренды нормализованы: было {brands_before}, стало {brands_after}")
    else:
        print("❌ Бренды не изменились")
    
    print(f"\n🎯 ГОТОВНОСТЬ К ЕЖЕДНЕВНОМУ ИСПОЛЬЗОВАНИЮ:")
    if changes == 0 and brake_discs_after == 0:
        print("🎉 ОТЛИЧНО! Система готова для ежедневного использования!")
    else:
        print("⚠️ Требуется дополнительная настройка")

if __name__ == '__main__':
    main() 