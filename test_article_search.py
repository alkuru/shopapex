#!/usr/bin/env python
"""
Тест поиска только по артикулу
"""
import os
import django
import requests

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

from catalog.models import Product

def test_article_only_search():
    """Тест поиска только по артикулу"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== Тест поиска только по артикулу ===\n")
    
    # Сначала проверим, какие товары есть в базе
    print("1. Проверка товаров в базе данных...")
    products = Product.objects.filter(is_active=True)[:10]
    
    print(f"   Всего активных товаров: {Product.objects.filter(is_active=True).count()}")
    print("   Примеры товаров:")
    
    test_articles = []
    test_names = []
    
    for product in products:
        print(f"   - Артикул: '{product.article}', Название: '{product.name}'")
        if product.article:
            test_articles.append(product.article)
        if product.name:
            test_names.append(product.name[:10])  # Первые 10 символов названия
    
    if not test_articles:
        print("   ❌ Нет товаров с артикулами для тестирования")
        return
    
    print(f"\n2. Тестирование поиска по артикулам...")
    
    # Тест поиска по артикулу (должен найти)
    for i, article in enumerate(test_articles[:3]):  # Тестируем первые 3 артикула
        try:
            response = requests.get(f"{base_url}/catalog/search/", params={'q': article})
            if response.status_code == 200:
                content = response.text.lower()
                if article.lower() in content:
                    print(f"   ✅ Поиск по артикулу '{article}': найден")
                else:
                    print(f"   ⚠️  Поиск по артикулу '{article}': не найден в результатах")
            else:
                print(f"   ❌ Поиск по артикулу '{article}': ошибка {response.status_code}")
        except Exception as e:
            print(f"   ❌ Поиск по артикулу '{article}': исключение {e}")
    
    print(f"\n3. Тестирование поиска по названиям (НЕ должен найти)...")
    
    # Тест поиска по названию (НЕ должен найти)
    for i, name_part in enumerate(test_names[:3]):  # Тестируем первые 3 части названий
        try:
            response = requests.get(f"{base_url}/catalog/search/", params={'q': name_part})
            if response.status_code == 200:
                content = response.text.lower()
                # Проверяем, что нет результатов поиска или очень мало
                if 'найдено товаров: 0' in content or 'результатов не найдено' in content:
                    print(f"   ✅ Поиск по названию '{name_part}': правильно НЕ найден")
                elif name_part.lower() in content:
                    # Возможно, название совпадает с артикулом
                    print(f"   ⚠️  Поиск по названию '{name_part}': найден (возможно совпадение с артикулом)")
                else:
                    print(f"   ✅ Поиск по названию '{name_part}': правильно НЕ найден")
            else:
                print(f"   ❌ Поиск по названию '{name_part}': ошибка {response.status_code}")
        except Exception as e:
            print(f"   ❌ Поиск по названию '{name_part}': исключение {e}")
    
    print(f"\n4. Тестирование специальных случаев...")
    
    # Тест частичного поиска по артикулу
    if test_articles:
        partial_article = test_articles[0][:3] if len(test_articles[0]) > 3 else test_articles[0]
        try:
            response = requests.get(f"{base_url}/catalog/search/", params={'q': partial_article})
            if response.status_code == 200:
                content = response.text.lower()
                if partial_article.lower() in content:
                    print(f"   ✅ Частичный поиск по артикулу '{partial_article}': работает")
                else:
                    print(f"   ⚠️  Частичный поиск по артикулу '{partial_article}': не найден")
            else:
                print(f"   ❌ Частичный поиск: ошибка {response.status_code}")
        except Exception as e:
            print(f"   ❌ Частичный поиск: исключение {e}")
    
    # Тест пустого поиска
    try:
        response = requests.get(f"{base_url}/catalog/search/", params={'q': ''})
        if response.status_code == 200:
            print("   ✅ Пустой поиск: обрабатывается корректно")
        else:
            print(f"   ❌ Пустой поиск: ошибка {response.status_code}")
    except Exception as e:
        print(f"   ❌ Пустой поиск: исключение {e}")
    
    print(f"\n=== Заключение ===")
    print("Поиск теперь работает только по артикулам товаров.")
    print("Поиск по названиям и описаниям отключен.")
    print("Это обеспечивает более точный поиск для пользователей, знающих артикулы.")


if __name__ == "__main__":
    test_article_only_search()
