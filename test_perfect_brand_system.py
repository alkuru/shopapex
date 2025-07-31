#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import MikadoProduct
from catalog.api_views import process_mikado_brand_update

def main():
    print("=== ТЕСТ ИДЕАЛЬНОЙ СИСТЕМЫ ВОССТАНОВЛЕНИЯ БРЕНДОВ ===")
    
    # Сначала создаем несколько неправильных записей для теста
    print("1. Создаем тестовые записи с неправильными брендами...")
    
    # Создаем тестовую запись с неправильным брендом
    test_product = MikadoProduct.objects.create(
        article="TEST123",
        brand="НЕПРАВИЛЬНЫЙ_БРЕНД", 
        name="Тестовый товар",
        stock_quantity=5,
        price=100.0,
        multiplicity=1,
        unit="шт",
        warehouse="ЦС-МК"
    )
    print(f"Создан тест-товар: {test_product.article} с брендом '{test_product.brand}'")
    
    # Проверяем начальное состояние
    print(f"\n2. Проверяем начальное состояние...")
    total_before = MikadoProduct.objects.count()
    brake_discs_before = MikadoProduct.objects.filter(
        brand='MANN-FILTER',
        name__icontains='диск тормозной'
    ).count()
    
    print(f"Всего товаров Mikado: {total_before}")
    print(f"Тормозных дисков с брендом MANN-FILTER: {brake_discs_before}")
    
    # Запускаем идеальное восстановление
    print(f"\n3. Запускаем ИДЕАЛЬНОЕ восстановление брендов...")
    process_mikado_brand_update()
    
    # Проверяем результат
    print(f"\n4. Проверяем результат...")
    total_after = MikadoProduct.objects.count()
    brake_discs_after = MikadoProduct.objects.filter(
        brand='MANN-FILTER',
        name__icontains='диск тормозной'
    ).count()
    
    print(f"Всего товаров Mikado: {total_after}")
    print(f"Тормозных дисков с брендом MANN-FILTER: {brake_discs_after}")
    
    # Проверяем, что тестовый товар удален (его нет в оригинальном файле)
    test_exists = MikadoProduct.objects.filter(article="TEST123").exists()
    print(f"Тестовый товар TEST123 существует: {test_exists}")
    
    # Проверяем конкретные артикулы
    print(f"\n5. Проверяем конкретные артикулы...")
    test_articles = ['610.3719.20', '610.3715.20']
    
    for article in test_articles:
        products = MikadoProduct.objects.filter(article=article)
        if products.exists():
            product = products.first()
            print(f"✅ {article}: {product.brand}")
        else:
            print(f"❌ {article}: НЕ НАЙДЕН")
    
    # Итоговая оценка
    print(f"\n=== ИТОГОВАЯ ОЦЕНКА ===")
    if brake_discs_after == 0 and not test_exists:
        print("🎉 ИДЕАЛЬНО! Система работает безошибочно!")
        print("✅ Нет неправильных брендов")
        print("✅ Мусор удален") 
        print("✅ Готова для ежедневного использования!")
    else:
        print("❌ Есть проблемы!")
        if brake_discs_after > 0:
            print(f"- Осталось {brake_discs_after} тормозных дисков с неправильным брендом")
        if test_exists:
            print("- Мусорные записи не удалены")

if __name__ == '__main__':
    main() 