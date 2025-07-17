#!/usr/bin/env python
"""
Детальная отладка метода get_product_analogs
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

def detailed_debug():
    """Детальная отладка метода get_product_analogs"""
    
    print("🔍 Детальная отладка get_product_analogs...")
    print("=" * 60)
    
    try:
        supplier = Supplier.objects.filter(is_active=True, api_type='autoparts').first()
        
        if not supplier:
            print("❌ Нет активных поставщиков")
            return
        
        print(f"📦 Поставщик: {supplier.name}")
        
        # Шаг 1: Получаем бренды
        print("\n🔍 Шаг 1: Получение брендов...")
        success, brands_data = supplier.get_abcp_brands('test123')
        print(f"✅ Успех: {success}")
        print(f"📊 Тип данных: {type(brands_data)}")
        print(f"📊 Данные: {brands_data}")
        
        if not success:
            print(f"❌ Ошибка получения брендов: {brands_data}")
            return
        
        # Шаг 2: Проверяем формат данных
        print(f"\n🔍 Шаг 2: Анализ структуры данных...")
        if isinstance(brands_data, dict):
            print(f"📊 Это словарь с {len(brands_data)} элементами")
            for i, (key, value) in enumerate(brands_data.items()):
                print(f"   {i+1}. Ключ: {key}")
                print(f"      Значение: {value}")
                print(f"      Тип значения: {type(value)}")
                if i >= 2:  # Показываем только первые 3
                    break
        else:
            print(f"📊 Это {type(brands_data)} с {len(brands_data)} элементами")
        
        # Шаг 3: Тестируем _search_articles_by_brand
        print(f"\n🔍 Шаг 3: Тестирование _search_articles_by_brand...")
        
        if isinstance(brands_data, dict):
            first_item = list(brands_data.values())[0]
            brand_name = first_item.get('brand', '')
            article_code = first_item.get('number', 'test123')
            
            print(f"   Тестируем с brand_name='{brand_name}', article_code='{article_code}'")
            
            try:
                success, articles_data = supplier._search_articles_by_brand(article_code, brand_name)
                print(f"   ✅ Успех: {success}")
                print(f"   📊 Результат: {articles_data}")
                print(f"   📊 Тип результата: {type(articles_data)}")
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
                traceback.print_exc()
        
        # Шаг 4: Пытаемся вызвать полный метод с отладкой
        print(f"\n🔍 Шаг 4: Полный тест get_product_analogs...")
        try:
            success, result = supplier.get_product_analogs('test123')
            print(f"✅ Успех: {success}")
            print(f"📊 Результат: {result}")
        except Exception as e:
            print(f"❌ Ошибка в get_product_analogs: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    detailed_debug()
