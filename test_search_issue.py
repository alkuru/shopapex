#!/usr/bin/env python
"""
Тест для проверки проблемы с поиском с главной страницы
"""
import os
import django
import requests
from urllib.parse import urljoin

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

def test_search_endpoints():
    """Тестирование эндпоинтов поиска"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== Тест поиска с главной и страницы каталога ===\n")
    
    # 1. Проверяем главную страницу
    print("1. Проверка главной страницы...")
    try:
        response = requests.get(base_url + "/")
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            # Проверяем, есть ли форма поиска на главной
            if 'action="/catalog/search/"' in response.text:
                print("   ✅ Форма поиска найдена с правильным action")
            elif 'catalog/search' in response.text:
                print("   ⚠️  Форма поиска найдена, но возможно с неправильным action")
            else:
                print("   ❌ Форма поиска не найдена")
                
            if 'name="q"' in response.text:
                print("   ✅ Поле ввода поиска найдено")
            else:
                print("   ❌ Поле ввода поиска не найдено")
        else:
            print(f"   ❌ Ошибка загрузки главной страницы: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка при обращении к главной странице: {e}")
    
    print()
    
    # 2. Проверяем страницу каталога
    print("2. Проверка страницы каталога...")
    try:
        response = requests.get(base_url + "/catalog/")
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            if 'search' in response.text.lower():
                print("   ✅ Поиск доступен на странице каталога")
            else:
                print("   ❌ Поиск не найден на странице каталога")
        else:
            print(f"   ❌ Ошибка загрузки страницы каталога: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка при обращении к странице каталога: {e}")
    
    print()
    
    # 3. Прямой тест поиска
    print("3. Прямой тест поиска...")
    search_url = base_url + "/catalog/search/"
    test_queries = ["масло", "тормозные", "brembo"]
    
    for query in test_queries:
        try:
            response = requests.get(search_url, params={'q': query})
            print(f"   Поиск '{query}': статус {response.status_code}")
            if response.status_code == 200:
                if 'результат' in response.text.lower() or 'товар' in response.text.lower():
                    print(f"   ✅ Поиск '{query}' работает")
                else:
                    print(f"   ⚠️  Поиск '{query}' возвращает ответ, но возможно без результатов")
            else:
                print(f"   ❌ Ошибка поиска '{query}': {response.status_code}")
        except Exception as e:
            print(f"   ❌ Ошибка при поиске '{query}': {e}")
    
    print()
    
    # 4. Тест перенаправления с главной страницы
    print("4. Тест отправки формы с главной страницы...")
    try:
        # Имитируем отправку формы с главной страницы
        response = requests.get(base_url + "/catalog/search/", 
                              params={'q': 'масло'}, 
                              headers={'Referer': base_url + "/"})
        print(f"   Статус поиска с главной: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Поиск с главной страницы работает")
        else:
            print(f"   ❌ Ошибка поиска с главной: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка при тесте с главной: {e}")


if __name__ == "__main__":
    test_search_endpoints()
