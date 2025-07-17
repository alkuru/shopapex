#!/usr/bin/env python
"""
Детальная отладка ошибки 'str' object has no attribute 'get'
"""
import os
import sys
import django
import traceback

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def debug_get_product_analogs_step_by_step():
    """Пошаговая отладка метода get_product_analogs"""
    
    print("🔍 Пошаговая отладка get_product_analogs...")
    print("=" * 60)
    
    try:
        supplier = Supplier.objects.filter(is_active=True, api_type='autoparts').first()
        
        if not supplier:
            print("❌ Нет поставщиков")
            return
        
        print(f"📦 Поставщик: {supplier.name}")
        article = 'test123'
        
        # Шаг 1: Получаем бренды
        print(f"\n🔍 Шаг 1: Получение брендов для '{article}'...")
        success, brands_data = supplier.get_abcp_brands(article)
        print(f"   Успех: {success}")
        print(f"   Тип данных: {type(brands_data)}")
        
        if not success:
            print(f"   ❌ Ошибка: {brands_data}")
            return
        
        print(f"   Данные (первые 200 символов): {str(brands_data)[:200]}...")
        
        # Шаг 2: Преобразуем данные
        print(f"\n🔍 Шаг 2: Преобразование данных...")
        filtered_brands = []
        
        if isinstance(brands_data, dict):
            print(f"   Это словарь с {len(brands_data)} элементами")
            for i, (key, brand_info) in enumerate(brands_data.items()):
                print(f"   {i+1}. Ключ: {key}")
                print(f"      Значение: {brand_info}")
                print(f"      Тип значения: {type(brand_info)}")
                
                if isinstance(brand_info, dict):
                    filtered_brands.append(brand_info)
                    print(f"      ✅ Добавлен в filtered_brands")
                else:
                    print(f"      ⚠️ Пропущен (не словарь)")
                
                if i >= 2:  # Показываем только первые 3
                    break
        
        print(f"   Итого в filtered_brands: {len(filtered_brands)}")
        
        # Шаг 3: Обрабатываем каждый бренд
        print(f"\n🔍 Шаг 3: Обработка каждого бренда...")
        
        for i, brand_info in enumerate(filtered_brands):
            print(f"\n   --- Бренд {i+1} ---")
            print(f"   brand_info: {brand_info}")
            print(f"   Тип brand_info: {type(brand_info)}")
            
            if not isinstance(brand_info, dict):
                print(f"   ❌ brand_info не является словарем!")
                continue
            
            try:
                brand_name = brand_info.get('brand', '')
                article_code = brand_info.get('number', article)
                
                print(f"   brand_name: '{brand_name}'")
                print(f"   article_code: '{article_code}'")
                
                # Тестируем _search_articles_by_brand
                print(f"   Тестируем _search_articles_by_brand...")
                success, articles_data = supplier._search_articles_by_brand(article_code, brand_name)
                
                print(f"   Результат: success={success}")
                print(f"   articles_data тип: {type(articles_data)}")
                print(f"   articles_data: {str(articles_data)[:100]}...")
                
                if success and articles_data and isinstance(articles_data, (list, dict)):
                    print(f"   ✅ Данные корректны")
                    
                    products_list = articles_data if isinstance(articles_data, list) else [articles_data]
                    print(f"   Количество товаров: {len(products_list)}")
                    
                    for j, product in enumerate(products_list):
                        print(f"   Товар {j+1}: тип={type(product)}, данные={str(product)[:50]}...")
                        
                        if not isinstance(product, dict):
                            print(f"   ❌ НАЙДЕНА ОШИБКА: product не является словарем!")
                            print(f"   product = {product}")
                            print(f"   type(product) = {type(product)}")
                            break
                        
                        # Тестируем .get() вызовы
                        try:
                            article_val = product.get('articleCode', article_code)
                            print(f"   ✅ product.get('articleCode') работает: {article_val}")
                        except Exception as e:
                            print(f"   ❌ ОШИБКА в product.get(): {e}")
                            break
                else:
                    print(f"   ⚠️ Данные некорректны или пустые")
                    
            except Exception as e:
                print(f"   ❌ ОШИБКА в обработке бренда: {e}")
                traceback.print_exc()
                break
                
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_get_product_analogs_step_by_step()
