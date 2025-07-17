#!/usr/bin/env python
"""
Скрипт для улучшения данных загруженных товаров
"""
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier, Product
from django.db import models

def improve_product_data():
    """Улучшает данные товаров, получая детальную информацию"""
    
    print("🔍 Улучшение данных товаров...")
    
    try:
        supplier = Supplier.objects.get(name__icontains='vinttop')
        print(f"✅ Найден поставщик: {supplier.name}")
        
    except Supplier.DoesNotExist:
        print("❌ Поставщик VintTop.ru не найден!")
        return False
    
    # Получаем товары без нормальных названий
    products = Product.objects.filter(
        primary_supplier=supplier,
        name__in=['Товар без названия', 'Без названия']
    )
    
    print(f"📦 Найдено {products.count()} товаров для улучшения")
    
    improved_count = 0
    
    for product in products:
        print(f"\n🔧 Улучшение товара: {product.article}")
        
        try:
            # Ищем детальную информацию о товаре
            success, result = supplier.search_products_by_article(product.article)
            
            if success and isinstance(result, list) and len(result) > 0:
                # Берем первый результат
                item_data = result[0]
                
                if isinstance(item_data, dict):
                    # Пытаемся извлечь лучшее название
                    possible_names = [
                        item_data.get('name'),
                        item_data.get('title'), 
                        item_data.get('description'),
                        f"{item_data.get('brand', 'NoName')} {product.article}"
                    ]
                    
                    # Находим первое непустое название
                    new_name = None
                    for name in possible_names:
                        if name and name.strip() and name.strip() not in ['Без названия', 'Товар без названия']:
                            new_name = name.strip()[:300]  # Ограничиваем длину
                            break
                    
                    if new_name:
                        old_name = product.name
                        product.name = new_name
                        product.save()
                        
                        print(f"   ✅ Обновлено название:")
                        print(f"      Было: {old_name}")
                        print(f"      Стало: {new_name}")
                        improved_count += 1
                    else:
                        print(f"   ⚠️  Название не найдено, оставляем как есть")
                        
                    # Выводим дополнительную информацию
                    print(f"   📋 Доступные данные:")
                    for key, value in item_data.items():
                        if key not in ['name', 'title'] and value:
                            print(f"      {key}: {str(value)[:100]}")
                else:
                    print(f"   ❌ Неправильный формат данных")
            else:
                print(f"   ⚠️  Товар не найден в API")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
    
    print(f"\n🎯 РЕЗУЛЬТАТ УЛУЧШЕНИЯ:")
    print(f"   ✅ Улучшено товаров: {improved_count}")
    print(f"   📊 Обработано всего: {products.count()}")
    
    return improved_count > 0

def test_search_functionality():
    """Тестирует функциональность поиска на сайте"""
    
    print(f"\n🔍 ТЕСТИРОВАНИЕ ПОИСКА НА САЙТЕ")
    print("=" * 50)
    
    # Получаем несколько товаров для тестирования
    products = Product.objects.filter(
        primary_supplier__name__icontains='vinttop'
    )[:5]
    
    if not products:
        print("❌ Нет товаров для тестирования")
        return False
    
    print(f"📦 Тестируем поиск по {products.count()} товарам")
    
    test_queries = []
    
    for product in products:
        # Собираем различные поисковые запросы
        test_queries.extend([
            product.article,
            product.brand.name,
            product.name.split()[0] if product.name.split() else product.article
        ])
    
    # Убираем дубликаты и пустые
    test_queries = list(set([q for q in test_queries if q and len(q) >= 2]))
    
    print(f"🔎 Тестовые запросы: {test_queries[:5]}")  # Показываем первые 5
    
    for query in test_queries[:3]:  # Тестируем первые 3
        print(f"\n🔍 Поиск: '{query}'")
        
        # Поиск в локальной базе
        local_results = Product.objects.filter(
            models.Q(name__icontains=query) |
            models.Q(article__icontains=query) |
            models.Q(brand__name__icontains=query)
        )[:5]
        
        print(f"   📋 Локальных результатов: {local_results.count()}")
        
        for result in local_results:
            print(f"      • {result.article} - {result.name[:50]}")
    
    print(f"\n✅ Поиск протестирован!")
    return True

if __name__ == "__main__":
    print("🚀 Улучшение данных товаров и тестирование поиска")
    print("=" * 60)
    
    try:
        # Улучшаем данные товаров
        improve_product_data()
        
        # Тестируем поиск
        test_search_functionality()
        
        print(f"\n🎉 ПРОЦЕСС ЗАВЕРШЕН УСПЕШНО!")
        print(f"📝 Рекомендации:")
        print(f"   • Проверьте товары в админке: http://127.0.0.1:8000/admin/catalog/product/")
        print(f"   • Протестируйте каталог: http://127.0.0.1:8000/catalog/")
        print(f"   • Протестируйте поиск: http://127.0.0.1:8000/catalog/search/")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
