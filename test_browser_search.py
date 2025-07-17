#!/usr/bin/env python
"""
Подробный тест поиска через браузерную симуляцию
"""
import os
import django
import requests
from urllib.parse import urljoin, parse_qs, urlparse

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopapex_project.settings')
django.setup()

def test_browser_search():
    """Тест поиска как в браузере"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== Тест поиска как в браузере ===\n")
    
    session = requests.Session()
    
    # 1. Загружаем главную страницу
    print("1. Загрузка главной страницы...")
    try:
        response = session.get(base_url + "/")
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Главная страница загружена")
        else:
            print(f"   ❌ Ошибка загрузки: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return
    
    # 2. Отправляем поиск с главной страницы
    print("\n2. Отправка поиска 'масло' с главной страницы...")
    try:
        # Имитируем отправку формы поиска
        search_url = base_url + "/catalog/search/"
        search_params = {'q': 'масло'}
        
        # Добавляем referrer, чтобы показать, что запрос идет с главной
        headers = {
            'Referer': base_url + "/",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = session.get(search_url, params=search_params, headers=headers)
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Поиск выполнен успешно")
            
            # Проверяем содержимое ответа
            content = response.text.lower()
            if 'масло' in content:
                print("   ✅ Запрос обработан (найдено в ответе)")
            if 'товар' in content or 'product' in content:
                print("   ✅ Найдены товары")
            if 'результат' in content or 'найдено' in content:
                print("   ✅ Отображены результаты поиска")
                
        else:
            print(f"   ❌ Ошибка поиска: {response.status_code}")
            print(f"   Текст ошибки: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # 3. Аналогичный поиск со страницы каталога для сравнения
    print("\n3. Отправка поиска 'масло' со страницы каталога...")
    try:
        # Сначала загружаем страницу каталога
        catalog_response = session.get(base_url + "/catalog/")
        print(f"   Статус загрузки каталога: {catalog_response.status_code}")
        
        if catalog_response.status_code == 200:
            # Теперь отправляем поиск
            headers = {
                'Referer': base_url + "/catalog/",
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = session.get(search_url, params=search_params, headers=headers)
            print(f"   Статус поиска: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Поиск с каталога работает")
            else:
                print(f"   ❌ Ошибка поиска с каталога: {response.status_code}")
                
        else:
            print(f"   ❌ Ошибка загрузки каталога: {catalog_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # 4. Проверяем доступность поисковой страницы напрямую
    print("\n4. Прямая проверка страницы поиска...")
    try:
        response = session.get(search_url)
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Страница поиска доступна")
        else:
            print(f"   ❌ Страница поиска недоступна: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # 5. Тест разных запросов
    print("\n5. Тест разных поисковых запросов...")
    test_queries = ['тормозные', 'brembo', 'фильтр', '123']
    
    for query in test_queries:
        try:
            response = session.get(search_url, params={'q': query})
            if response.status_code == 200:
                print(f"   ✅ Запрос '{query}': OK")
            else:
                print(f"   ❌ Запрос '{query}': ошибка {response.status_code}")
        except Exception as e:
            print(f"   ❌ Запрос '{query}': исключение {e}")


if __name__ == "__main__":
    test_browser_search()
