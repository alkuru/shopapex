#!/usr/bin/env python3
"""
Загрузка реального товара K20PBR-S10 в базу данных
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
sys.path.append('.')

try:
    django.setup()
    from catalog.supplier_models import Supplier
    from catalog.models import Product, Brand, ProductCategory
    
    print("🔍 ЗАГРУЗКА РЕАЛЬНОГО ТОВАРА K20PBR-S10")
    print("=" * 50)
    
    # Найдем поставщика VintTop
    supplier = Supplier.objects.filter(name__icontains='VintTop').first()
    
    if not supplier:
        print("❌ Поставщик VintTop не найден")
        sys.exit(1)
    
    print(f"✅ Поставщик: {supplier.name}")
    
    # Ищем товар через API
    article = "K20PBR-S10"
    print(f"🔍 Поиск товара: {article}")
    
    success, result = supplier.search_products_by_article(article)
    
    if success and result:
        print(f"✅ API вернул данные: {type(result)}")
        print(f"📊 Длина результата: {len(str(result))}")
        
        # Если result это список товаров
        if isinstance(result, list) and result:
            for i, product_data in enumerate(result[:3], 1):
                if isinstance(product_data, dict):
                    print(f"\n{i}. Найден товар:")
                    print(f"   Артикул: {product_data.get('article', 'N/A')}")
                    print(f"   Название: {product_data.get('name', 'N/A')}")
                    print(f"   Цена: {product_data.get('price', 'N/A')}")
                    print(f"   Бренд: {product_data.get('brand', 'N/A')}")
                    
                    # Попробуем создать товар в базе
                    try:
                        # Найдем или создадим бренд
                        brand_name = product_data.get('brand', 'Unknown')
                        brand, _ = Brand.objects.get_or_create(
                            name=brand_name,
                            defaults={'is_active': True}
                        )
                        
                        # Найдем или создадим категорию
                        category, _ = ProductCategory.objects.get_or_create(
                            name='Автозапчасти',
                            defaults={'is_active': True}
                        )
                        
                        # Создадим товар
                        product, created = Product.objects.get_or_create(
                            article=product_data.get('article', article),
                            defaults={
                                'name': product_data.get('name', f'Товар {article}'),
                                'brand': brand,
                                'category': category,
                                'price': float(product_data.get('price', 0)),
                                'description': f'Загружен с {supplier.name}',
                                'stock_quantity': 1,
                                'is_active': True
                            }
                        )
                        
                        if created:
                            print(f"   ✅ Товар создан в базе: {product.article}")
                        else:
                            print(f"   ℹ️  Товар уже существует: {product.article}")
                            
                    except Exception as e:
                        print(f"   ❌ Ошибка создания товара: {e}")
        else:
            print(f"⚠️  Неожиданный формат результата: {result}")
    else:
        print(f"❌ Поиск не удался: {result}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
