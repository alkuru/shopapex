#!/usr/bin/env python3
"""
Проверка поиска реальных аналогов для товаров из базы
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, ProductAnalog, Brand, ProductCategory
    from catalog.supplier_models import Supplier
    
    print("🔍 ПОИСК РЕАЛЬНЫХ АНАЛОГОВ")
    print("=" * 50)
    
    # Берем несколько товаров из разных категорий
    test_products = Product.objects.all()[:10]
    
    print(f"📦 Тестируем {test_products.count()} товаров:")
    for product in test_products:
        print(f"   {product.article}: {product.name} ({product.category})")
    
    print("\n🔄 Начинаем поиск аналогов...")
    
    # Создаем экземпляр поставщика
    supplier = Supplier.objects.first()
    if not supplier:
        print("❌ Поставщик не найден в базе")
        sys.exit(1)
    
    for i, product in enumerate(test_products, 1):
        print(f"\n{i}. Поиск аналогов для {product.article}:")
        
        try:
            # Используем метод поиска аналогов
            analogs_result = supplier.get_product_analogs(product.article)
            
            print(f"   📊 Результат API: {type(analogs_result)}")
            
            if isinstance(analogs_result, dict):
                if 'analogs' in analogs_result:
                    analogs = analogs_result['analogs']
                    print(f"   ✅ Найдено аналогов: {len(analogs)}")
                    
                    # Показываем первые 3 аналога
                    for j, analog in enumerate(analogs[:3], 1):
                        if isinstance(analog, dict):
                            article = analog.get('article', 'N/A')
                            name = analog.get('name', 'N/A')
                            brand = analog.get('brand', 'N/A')
                            print(f"     {j}. {article} - {name} ({brand})")
                        else:
                            print(f"     {j}. {analog}")
                else:
                    print(f"   ⚠️  Нет поля 'analogs' в ответе: {analogs_result}")
            
            elif isinstance(analogs_result, list):
                print(f"   ✅ Найдено аналогов: {len(analogs_result)}")
                for j, analog in enumerate(analogs_result[:3], 1):
                    print(f"     {j}. {analog}")
            
            elif isinstance(analogs_result, str):
                print(f"   ⚠️  Строковый ответ: {analogs_result}")
            
            else:
                print(f"   ❌ Неизвестный тип ответа: {analogs_result}")
                
        except Exception as e:
            print(f"   ❌ Ошибка при поиске аналогов: {e}")
    
    print(f"\n📈 СТАТИСТИКА:")
    print(f"   Всего товаров в базе: {Product.objects.count()}")
    print(f"   Товаров с аналогами: {Product.objects.filter(analogs__isnull=False).distinct().count()}")
    print(f"   Всего связей аналогов: {ProductAnalog.objects.count()}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
