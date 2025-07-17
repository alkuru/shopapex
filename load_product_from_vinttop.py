#!/usr/bin/env python3
"""
Загрузка товара K20PBR-S10 с VintTop через ABCP API
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.models import Product, Brand, ProductCategory
    from catalog.supplier_models import Supplier
    
    print("🔄 ЗАГРУЗКА ТОВАРА K20PBR-S10 С VINTTOP")
    print("=" * 50)
    
    # Найдем поставщика VintTop
    try:
        supplier = Supplier.objects.get(name__icontains='VintTop')
        print(f"✅ Найден поставщик: {supplier.name}")
    except Supplier.DoesNotExist:
        print("❌ Поставщик VintTop не найден")
        sys.exit(1)
    
    # Параметры товара для поиска
    article_code = "K20PBR-S10"
    
    print(f"🔍 Ищем товар: {article_code}")
    
    # Используем метод поиска аналогов для получения данных о товаре
    result = supplier.get_product_analogs(article_code)
    
    print(f"� Тип результата: {type(result)}")
    print(f"📊 Результат: {result}")
    
    # Проверим, что result - это dict
    if not isinstance(result, dict):
        print("❌ Метод вернул не словарь, попробуем другой подход")
        result = {'success': False, 'error': 'Неожиданный тип результата'}
    
    print(f"�📊 Результат поиска: success={result.get('success')}")
    
    if result.get('success') and result.get('analogs'):
        analogs = result.get('analogs', [])
        print(f"✅ Найдено товаров: {len(analogs)}")
        
        for i, analog in enumerate(analogs, 1):
            print(f"\n{i}. Товар:")
            print(f"   Артикул: {analog.get('article', 'N/A')}")
            print(f"   Бренд: {analog.get('brand', 'N/A')}")
            print(f"   Описание: {analog.get('description', 'N/A')}")
            print(f"   Цена: {analog.get('price', 'N/A')}")
            
            # Создадим товар в нашей базе
            brand_name = analog.get('brand', 'Unknown')
            
            # Найдем или создадим бренд
            brand, created = Brand.objects.get_or_create(
                name=brand_name,
                defaults={'is_active': True}
            )
            if created:
                print(f"   ✅ Создан бренд: {brand_name}")
            
            # Найдем категорию или создадим дефолтную
            category, created = ProductCategory.objects.get_or_create(
                name='Автозапчасти',
                defaults={
                    'description': 'Автозапчасти с внешних поставщиков',
                    'is_active': True
                }
            )
            if created:
                print(f"   ✅ Создана категория: Автозапчасти")
            
            # Создадим товар
            product, created = Product.objects.get_or_create(
                article=analog.get('article', article_code),
                defaults={
                    'name': analog.get('description', f'Товар {analog.get("article", article_code)}'),
                    'brand': brand,
                    'category': category,
                    'price': float(analog.get('price', 0)) if analog.get('price') else 100.0,
                    'description': f'Загружен с {supplier.name}',
                    'stock_quantity': 1,
                    'is_active': True
                }
            )
            
            if created:
                print(f"   ✅ Товар создан в базе: {product.article}")
            else:
                print(f"   ℹ️  Товар уже существует: {product.article}")
                
    else:
        print(f"❌ Товар не найден или ошибка: {result.get('error', 'Неизвестная ошибка')}")
        print("\n💡 Попробуем создать товар вручную с базовыми данными:")
        
        # Создадим товар с базовыми данными
        brand, _ = Brand.objects.get_or_create(
            name='Unknown',
            defaults={'is_active': True}
        )
        
        category, _ = ProductCategory.objects.get_or_create(
            name='Автозапчасти',
            defaults={
                'description': 'Автозапчасти с внешних поставщиков',
                'is_active': True
            }
        )
        
        product, created = Product.objects.get_or_create(
            article=article_code,
            defaults={
                'name': f'Товар {article_code}',
                'brand': brand,
                'category': category,
                'price': 100.0,
                'description': f'Товар {article_code} - требует уточнения данных',
                'stock_quantity': 0,
                'is_active': True
            }
        )
        
        if created:
            print(f"   ✅ Базовый товар создан: {product.article}")
        else:
            print(f"   ℹ️  Товар уже существует: {product.article}")
    
    print(f"\n🎯 ЗАГРУЗКА ЗАВЕРШЕНА!")
    print(f"🧪 ТЕСТ В БРАУЗЕРЕ:")
    print(f"http://127.0.0.1:8000/catalog/search/?q={article_code}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
