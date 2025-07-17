#!/usr/bin/env python
"""
Финальное тестирование API VintTop.ru с исправленными методами
"""
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Supplier

def final_api_test():
    """Финальное тестирование API с правильными параметрами"""
    
    print("🔍 Получение поставщика VintTop.ru...")
    
    try:
        supplier = Supplier.objects.get(name__icontains='vinttop')
        print(f"✅ Поставщик: {supplier.name}")
        print(f"   API URL: {supplier.api_url}")
        print(f"   Логин: {supplier.api_login}")
        print(f"   Пароль: {'*' * len(supplier.api_password)}")
        
    except Supplier.DoesNotExist:
        print("❌ Поставщик не найден!")
        return
    
    print(f"\n" + "="*60)
    print(f"🧪 ТЕСТ 1: Проверка подключения к API")
    print(f"="*60)
    
    try:
        success, message = supplier.test_api_connection()
        if success:
            print(f"✅ Подключение успешно: {message}")
        else:
            print(f"❌ Ошибка подключения: {message}")
    except Exception as e:
        print(f"❌ Исключение: {e}")
    
    print(f"\n" + "="*60)
    print(f"🧪 ТЕСТ 2: Получение брендов по артикулу")
    print(f"="*60)
    
    test_article = "0986424815"  # Bosch артикул
    print(f"🔎 Поиск брендов для артикула: {test_article}")
    
    try:
        success, brands_data = supplier.get_abcp_brands(number=test_article)
        if success:
            print(f"✅ Бренды найдены!")
            if isinstance(brands_data, list):
                print(f"   Количество брендов: {len(brands_data)}")
                for i, brand in enumerate(brands_data[:3]):
                    brand_name = brand.get('brand', brand.get('name', 'Неизвестно'))
                    print(f"   {i+1}. {brand_name}")
            else:
                print(f"   Результат: {brands_data}")
        else:
            print(f"❌ Ошибка: {brands_data}")
    except Exception as e:
        print(f"❌ Исключение: {e}")
    
    print(f"\n" + "="*60)
    print(f"🧪 ТЕСТ 3: Поиск товаров по артикулу и бренду")
    print(f"="*60)
    
    test_brand = "BOSCH"
    print(f"🔎 Поиск товаров: артикул={test_article}, бренд={test_brand}")
    
    try:
        success, articles_data = supplier.search_products_by_article(test_article, test_brand)
        if success:
            print(f"✅ Товары найдены!")
            if isinstance(articles_data, list):
                print(f"   Количество товаров: {len(articles_data)}")
                for i, article in enumerate(articles_data[:3]):
                    name = article.get('name', article.get('title', 'Без названия'))
                    price = article.get('price', 'N/A')
                    print(f"   {i+1}. {name} - {price}")
            elif isinstance(articles_data, dict):
                print(f"   Результат (объект): {articles_data}")
            else:
                print(f"   Результат: {articles_data}")
        else:
            print(f"❌ Ошибка: {articles_data}")
    except Exception as e:
        print(f"❌ Исключение: {e}")
    
    print(f"\n" + "="*60)
    print(f"🧪 ТЕСТ 4: Поиск товаров без указания бренда")
    print(f"="*60)
    
    print(f"🔎 Поиск товаров для артикула: {test_article} (автоматический поиск брендов)")
    
    try:
        success, result = supplier.search_products_by_article(test_article)
        if success:
            print(f"✅ Поиск завершен!")
            if isinstance(result, list):
                print(f"   Найдено товаров: {len(result)}")
                for i, item in enumerate(result[:3]):
                    if isinstance(item, dict):
                        name = item.get('name', item.get('title', 'Без названия'))
                        price = item.get('price', 'N/A')
                        brand = item.get('brand', 'N/A')
                        print(f"   {i+1}. {name} ({brand}) - {price}")
                    else:
                        print(f"   {i+1}. {item}")
            else:
                print(f"   Результат: {result}")
        else:
            print(f"❌ Ошибка: {result}")
    except Exception as e:
        print(f"❌ Исключение: {e}")
    
    print(f"\n" + "="*60)
    print(f"📋 РЕЗЮМЕ ТЕСТИРОВАНИЯ")
    print(f"="*60)
    print(f"✅ Логин исправлен на: {supplier.api_login}")
    print(f"✅ Методы обновлены для работы с ABCP API")
    print(f"✅ Добавлена поддержка обязательных параметров")
    print(f"📝 Проверьте результаты тестов выше")

if __name__ == "__main__":
    print("🚀 ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ VINTTOP.RU API")
    print("=" * 60)
    final_api_test()
